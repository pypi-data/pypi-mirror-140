"Python wrapper for mkp224o CLI tool."

import os
import time
import threading
from collections import defaultdict
from queue import Queue, Empty
from subprocess import Popen, PIPE, TimeoutExpired

from .version import __version__


COMMAND = os.getenv('MKP224O_PATH', 'mkp224o')


class _Mkpy224o:  # pylint: disable=too-few-public-methods
    def __init__(self, pattern, on_progress=None):
        self._pattern = pattern
        self._total_calcs = pow(32, len(pattern))
        self._on_progress = on_progress
        self._stats_reports = 0
        self._stats = defaultdict(lambda: 0)
        self._start = time.time()

    def _update_stats(self, stats):
        # Update totals.
        self._stats_reports += 1
        for key, value in stats.items():
            self._stats[key] += value

        # Find averages.
        averages = {}
        for key in ('calc/sec', 'succ/sec', 'rest/sec'):
            averages[key] = self._stats[key] / self._stats_reports
        averages['elapsed'] = time.time() - self._start

        # Estimate time.
        averages['estimate'] = self._total_calcs / averages['calc/sec']
        averages['remaining'] = averages['estimate'] - averages['elapsed']
        return averages

    def _tail_stderr(self, stream):
        def _tail():
            while True:
                try:
                    line = stream.readline()

                except ValueError:
                    break

                if line == '':
                    break
                if not line.startswith('>'):
                    continue

                line = line.strip().lstrip('>').rstrip('sec')
                stats = {
                    k: float(v) for k, v in [
                        p.split(':') for p in line.split(', ')
                    ]
                }
                stats = self._update_stats(stats)
                self._on_progress(stats)

        threading.Thread(target=_tail, daemon=True).start()

    def __call__(self, count=1, interval=3):
        cmd, keys = [
            COMMAND, self._pattern, '-n', str(count), '-S', str(interval), '-y',
        ], []

        with Popen(cmd, stdout=PIPE, stderr=PIPE, encoding='utf8') as proc:
            self._tail_stderr(proc.stderr)
            while True:
                try:
                    proc.wait(0.1)

                except TimeoutExpired:
                    continue

                else:
                    break

            # Parse our keys.
            lines = iter(proc.stdout.read().split('\n'))
            while True:
                header = next(lines)
                if header != '---':
                    break
                args = {
                    'hostname': next(lines).split()[1],
                    'public': next(lines).split()[1],
                    'secret': next(lines).split()[1],
                }
                # Sanity check.
                assert next(lines).startswith('time:')
                keys.append(args)

        return keys


def find_keys(pattern, count=1, on_progress=None, interval=None):
    """
    Main interface for this module.
    """
    return _Mkpy224o(pattern, on_progress=on_progress)(count, interval)
