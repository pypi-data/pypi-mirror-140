from respec import Dsl, Specification, Verification, Driver


class MyDriver(Driver):
    def get_driver_result(self) -> bool:
        return True


class MyDsl(Dsl):
    driver: MyDriver

    def get_dsl_result(self) -> bool:
        return self.driver.get_driver_result()


class MySpec(Specification):
    dsl: MyDsl

    def should_do_something(self):
        self.assertTrue(self.dsl.get_dsl_result())


def test_should_inject_driver_to_dsl():
    result = Verification(quiet=True).include(MySpec.using(MyDriver())).verify()
    assert result.testsRun == 1 and len(result.errors) == 0 and len(result.failures) == 0
