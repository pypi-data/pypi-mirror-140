from typing import List

from data_quality_check.core.check import Check


class Runner:
    def __init__(self):
        pass

    def run(self, check: Check):
        return check.run()

    def run_all(self, checks: List[Check]):
        result = []
        for c in checks:
            result.append(c.run())
