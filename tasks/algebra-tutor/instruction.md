# Help a student with one algebra mistake

A student is solving `3(x - 2) = 12`. They wrote: “I distributed the 3 and got
`3x - 2 = 12`, so `x = 14/3`. Is that right?”

Write a helpful, concise reply that identifies their mistake, shows a sound way
to solve the equation, and helps them check the result. Do not simply give the
number.

Save a UTF-8 JSON object to `/app/response.json` with exactly these fields:

```json
{
  "final_answer": 0,
  "reply": "Your response to the student, with exactly one explicit solution in the form x = <number>."
}
```

`final_answer` must be a JSON number. The zero above is only a schema placeholder;
derive the value from the equation yourself. In `reply`, state your
conclusion exactly once as `x = <number>` so it can be read unambiguously.
