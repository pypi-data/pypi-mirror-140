from unittest import TestResult

from respec import Verification, Specification


class AlwaysPass(Specification):
    def should_do_something(self):
        self.assertTrue(True)


class AlwaysFail(Specification):
    def should_do_something(self):
        self.assertTrue(False)


class AlwaysErr(Specification):
    def should_do_something(self):
        self.assertTrue(0/0)


def test_should_run_test_and_pass():
    verification = Verification(quiet=True)
    verification.include(AlwaysPass)
    result: TestResult = verification.verify()
    assert result.testsRun == 1 and len(result.failures) == 0 and len(result.errors) == 0


def test_should_run_test_and_failed():
    verification = Verification(quiet=True)
    verification.include(AlwaysFail)
    result: TestResult = verification.verify()
    assert result.testsRun == 1 and len(result.failures) == 1 and len(result.errors) == 0


def test_should_run_test_and_err():
    verification = Verification(quiet=True)
    verification.include(AlwaysErr)
    result: TestResult = verification.verify()
    assert result.testsRun == 1 and len(result.failures) == 0 and len(result.errors) == 1


def test_should_run_multiple_tests():
    verification = Verification(quiet=True)
    verification.include(AlwaysPass)
    verification.include(AlwaysFail)
    verification.include(AlwaysErr)
    result: TestResult = verification.verify()
    assert result.testsRun == 3 and len(result.failures) == 1 and len(result.errors) == 1


def test_should_run_multiple_tests_in_one_include():
    verification = Verification(quiet=True)
    verification.include(
        AlwaysPass,
        AlwaysFail,
        AlwaysErr,
    )
    result: TestResult = verification.verify()
    assert result.testsRun == 3 and len(result.failures) == 1 and len(result.errors) == 1


def test_should_support_chaining():
    result: TestResult = Verification(quiet=True).include(
        AlwaysPass,
        AlwaysFail,
    ).include(AlwaysErr).verify()
    assert result.testsRun == 3 and len(result.failures) == 1 and len(result.errors) == 1
