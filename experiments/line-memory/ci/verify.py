#!/usr/bin/env python3
"""Verify archive bytes and compare an isolated rerun; never rewrite the baseline."""
import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ATOL = 1e-12
RTOL = 1e-12


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_json(expected, actual, path='$'):
    errors = []
    if type(expected) is not type(actual):
        return [f'{path}: type {type(expected).__name__} != {type(actual).__name__}']
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            errors.append(f'{path}: different keys')
        for key in sorted(expected.keys() & actual.keys()):
            errors.extend(compare_json(expected[key], actual[key], f'{path}.{key}'))
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            errors.append(f'{path}: different lengths')
        for i, (a, b) in enumerate(zip(expected, actual)):
            errors.extend(compare_json(a, b, f'{path}[{i}]'))
    elif isinstance(expected, float):
        if not (math.isfinite(expected) and math.isfinite(actual)
                and math.isclose(expected, actual, rel_tol=RTOL, abs_tol=ATOL)):
            errors.append(f'{path}: {expected!r} != {actual!r}')
    elif expected != actual:
        errors.append(f'{path}: {expected!r} != {actual!r}')
    return errors


def compare_csv(expected_path, actual_path):
    expected = list(csv.reader(io.StringIO(expected_path.read_text())))
    actual = list(csv.reader(io.StringIO(actual_path.read_text())))
    if len(expected) != len(actual):
        return ['permutation_distributions.csv: different row counts']
    errors = []
    for i, (a, b) in enumerate(zip(expected, actual)):
        if len(a) != len(b):
            errors.append(f'CSV row {i}: different columns')
            continue
        for j, (x, y) in enumerate(zip(a, b)):
            # Stored CSV values are already rounded to eight decimals.
            # Their exact textual representation must be reproduced.
            if x != y:
                errors.append(f'CSV row {i}, column {j}: {x!r} != {y!r}')
    return errors


def verify_integrity():
    entries = json.loads((ROOT/'ci/integrity.json').read_text())
    errors = []
    for name, entry in entries.items():
        path = ROOT/name
        if not path.is_file():
            errors.append(f'MISSING {name}')
        elif path.stat().st_size != entry['bytes'] or digest(path) != entry['sha256']:
            errors.append(f'HASH_OR_SIZE_MISMATCH {name}')
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check-only', action='store_true')
    ap.add_argument('--compare-existing', type=Path)
    ap.add_argument('--output', type=Path, default=ROOT/'ci-output')
    args = ap.parse_args()
    errors = verify_integrity()
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print('PASS: input, script and expected-result hashes match.')
    if args.check_only:
        return 0
    import numpy
    if numpy.__version__ != '2.3.5' or sys.version_info[:3] != (3, 12, 14):
        raise SystemExit('ENVIRONMENT_MISMATCH: requires Python 3.12.14 and NumPy 2.3.5')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {'scope': 'EXP_SEQ_LINE_MEMORY_01', 'status': 'FAIL',
              'scientific_status': 'ESPLORATIVO', 'gate': 'CLOSED_PENDING_VALIDATION',
              'python': platform.python_version(), 'numpy': numpy.__version__,
              'platform': platform.platform(),
              'comparison': {'json_absolute_tolerance': ATOL, 'json_relative_tolerance': RTOL,
                             'integer_string_bool_and_structure': 'exact',
                             'csv_cells': 'exact; archived eight-decimal representation'},
              'baseline': 'unchanged archive results; no refitting or regenerated baseline'}
    with tempfile.TemporaryDirectory(prefix='voynich-line-memory-') as work:
        work = Path(work)
        if args.compare_existing:
            generated = args.compare_existing.resolve()
            report['execution'] = 'compare_existing; execution recorded separately in run.log'
        else:
            shutil.copytree(ROOT/'experiment', work/'experiment')
            generated = work/'experiment'
            env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                       PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0')
            with (output/'execution.log').open('w') as log:
                completed = subprocess.run([sys.executable, '-B', str(generated/'exp_line_memory.py')],
                                           cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT)
            if completed.returncode:
                report['errors'] = [f'Execution exit code {completed.returncode}']
                (output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
                return 1
            for p in (generated/'inputs').iterdir():
                source = ROOT/'experiment/inputs'/p.name
                if not source.is_file() or digest(source) != digest(p):
                    errors.append(f'INPUT_CHANGED {p.name}')
            if digest(generated/'exp_line_memory.py') != digest(ROOT/'experiment/exp_line_memory.py'):
                errors.append('SCRIPT_CHANGED')
            report['execution'] = 'isolated unchanged archive script'
        for name in ['results.json', 'permutation_distributions.csv']:
            path = generated/name
            if not path.is_file():
                errors.append(f'MISSING_OUTPUT {name}')
                continue
            expected = ROOT/'expected'/name
            if name.endswith('.json'):
                errors.extend(compare_json(json.loads(expected.read_text()), json.loads(path.read_text())))
            else:
                errors.extend(compare_csv(expected, path))
            report.setdefault('output_files', {})[name] = {
                'sha256': digest(path), 'expected_sha256': digest(expected),
                'byte_identical': path.read_bytes() == expected.read_bytes()}
            shutil.copyfile(path, output/name)
        errors.extend(verify_integrity())
        report['errors'] = errors
        report['status'] = 'FAIL' if errors else 'PASS'
        (output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['status'] + ': archived-result comparison')
    for error in errors[:30]:
        print(error)
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
