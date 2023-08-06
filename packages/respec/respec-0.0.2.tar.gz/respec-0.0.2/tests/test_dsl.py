from respec import Dsl, Specification, Verification


class MyDsl(Dsl):
    def __init__(self):
        self._did_init = True

    def is_initialized(self):
        return self._did_init


class MySpec(Specification):
    dsl: MyDsl

    def should_do_something(self):
        self.assertTrue(self.dsl.is_initialized())


def test_should_init_dsl():
    result = Verification(quiet=True).include(MySpec).verify()
    assert result.testsRun == 1 and len(result.errors) == 0 and len(result.failures) == 0
