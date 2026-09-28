"""Run real Harbor trials with known submissions, then check the resulting scores."""

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, help='Check an existing job without rerunning it')
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    name = f'grader-checks-{stamp}'
    inputs = ROOT / 'jobs' / f'{name}-inputs'
    cases = json.loads((ROOT / 'examples/grader-checks/cases.json').read_text())
    # Every real task gets a positive control using its reference answer.
    for task in sorted((ROOT / 'tasks').glob('invoice-*')):
        cases[f'{task.name}-reference'] = {
            'task': task.name,
            'response': str(task / 'solution/response.json'),
            'expected': {'json_validity': 1, 'field_accuracy': 1, 'summary': 1},
        }

    job = args.results.resolve() if args.results else ROOT / 'jobs' / name
    returncode = 0
    if not args.results:
        for case, config in cases.items():
            target = inputs / case
            shutil.copytree(ROOT / 'tasks' / config['task'], target)
            shutil.copyfile(ROOT / config['response'], target / 'solution/response.json')
            config_path = target / 'task.toml'
            config_path.write_text(config_path.read_text().replace(
                f'ouachitalabs/{config["task"]}', f'ouachitalabs/{case}'
            ))

        run = subprocess.run([
            'uv', 'run', 'harbor', 'run', '--yes', '--path', str(inputs),
            '--agent', 'oracle', '--job-name', name,
            '--jobs-dir', str(ROOT / 'jobs'), '-n', '2',
        ], cwd=ROOT)
        returncode = run.returncode
    # Harbor truncates long trial directory names; use the task identity instead.
    result_files = {}
    for path in job.glob('*/result.json'):
        task_name = json.loads(path.read_text()).get('task_name')
        result_files.setdefault(task_name, []).append(path)
    failures = []
    report = {}
    for case, config in cases.items():
        trials = result_files.get(f'ouachitalabs/{case}', [])
        observed = None
        error = None
        failed_fields = None
        if len(trials) == 1:
            result = json.loads(trials[0].read_text())
            error = result.get('exception_info')
            reward = trials[0].parent / 'verifier/reward.json'
            if reward.exists():
                observed = json.loads(reward.read_text())
            details_path = trials[0].parent / 'verifier/reward-details.json'
            if details_path.exists():
                details = json.loads(details_path.read_text())
                failed_fields = sorted(c['name'] for c in details['field_accuracy']['criteria']
                                       if c['value'] != 1)
        passed = (
            not error and observed is not None
            and set(observed) == set(config['expected'])
            and failed_fields == sorted(config.get('failed_fields', []))
            # Rewardkit serializes rewards to four decimal places.
            and all(math.isclose(observed[k], v, abs_tol=0.00005)
                    for k, v in config['expected'].items())
        )
        report[case] = {
            'expected': config['expected'], 'observed': observed,
            'passed': passed, 'error': error, 'failed_fields': failed_fields,
            'trial': str(trials[0].parent.relative_to(ROOT)) if trials else None,
        }
        print(f'{"PASS" if passed else "FAIL"} {case}: {observed}')
        if not passed:
            failures.append(case)
    job.mkdir(parents=True, exist_ok=True)
    (job / 'grader-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Report: {job / "grader-checks.json"}')
    return 1 if failures or returncode else 0


if __name__ == '__main__':
    sys.exit(main())
