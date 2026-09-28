"""The candidate extractor: one image goes to one vision model call."""

import base64
import json
import os

from harbor.agents.base import BaseAgent
from harbor.agents.capabilities import AgentCapabilities
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trajectories import Agent, Step, Trajectory
from harbor.models.trajectories.content import ContentPart, ImageSource
from openai import AsyncOpenAI


class InvoiceExtractorAgent(BaseAgent):
    capabilities = AgentCapabilities(atif=True)

    @staticmethod
    def name() -> str:
        return "invoice-extractor"

    def version(self) -> str:
        return "1.0.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        pass

    async def run(
        self, instruction: str, environment: BaseEnvironment, context: AgentContext
    ) -> None:
        if not self.model_name or not self.model_name.startswith("openrouter/"):
            raise ValueError("Pass an OpenRouter vision model with --model")
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("Set OPENROUTER_API_KEY before running Harbor")

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        image_path = self.logs_dir / "invoice.jpg"
        await environment.download_file("/app/invoice.jpg", image_path)

        image_url = "data:image/jpeg;base64," + base64.b64encode(
            image_path.read_bytes()
        ).decode("ascii")
        model = self.model_name.removeprefix("openrouter/")
        async with AsyncOpenAI(
            api_key=key, base_url="https://openrouter.ai/api/v1", max_retries=0
        ) as client:
            raw_result = await client.chat.completions.with_raw_response.create(
                model=model,
                # Reasoning is off on purpose. It dominated the run: with it on,
                # these calls emitted 1.7k-6.8k tokens of chain-of-thought (96% of
                # all output tokens) and took 21s-189s per trial depending on which
                # OpenRouter provider was picked. Off, the same answer is ~95
                # tokens in 1-5s. The instruction forbids code fences, so the bare
                # JSON still passes json_validity.
                extra_body={"reasoning": {"enabled": False}},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": instruction},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url, "detail": "high"},
                            },
                        ],
                    }
                ],
            )

        # Keep the complete HTTP response body, including provider-specific fields.
        (self.logs_dir / "api-response.json").write_bytes(raw_result.content)
        result = raw_result.parse()

        # Unwrap the API envelope; never parse or repair the model's answer.
        # A missing text answer is an empty submission for the verifier to grade.
        answer = result.choices[0].message.content or ""
        answer_path = self.logs_dir / "response.json"
        answer_path.write_bytes(answer.encode("utf-8"))
        await environment.upload_file(answer_path, "/app/response.json")

        if result.usage:
            context.n_input_tokens = result.usage.prompt_tokens
            context.n_output_tokens = result.usage.completion_tokens
        trajectory = Trajectory(
            session_id=self.session_id,
            agent=Agent(
                name=self.name(), version=self.version(), model_name=self.model_name
            ),
            steps=[
                Step(
                    step_id=1,
                    source="user",
                    message=[
                        ContentPart(type="text", text=instruction),
                        ContentPart(
                            type="image",
                            source=ImageSource(
                                media_type="image/jpeg", path="invoice.jpg"
                            ),
                        ),
                    ],
                ),
                Step(step_id=2, source="agent", message=answer),
            ],
        )
        (self.logs_dir / "trajectory.json").write_text(
            json.dumps(trajectory.to_json_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
