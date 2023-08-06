from respec import Specification, Driver, Verification


class MyDriver(Driver):
    def get_result(self):
        return True


class MySpec(Specification):
    driver: MyDriver

    def should_do_something(self):
        self.assertTrue(self.driver.get_result())


def test_should_allow_inject_driver():
    result = Verification(quiet=True) \
        .include(MySpec.using(MyDriver())) \
        .verify()
    assert result.testsRun == 1 and len(result.failures) == 0 and len(result.errors) == 0
