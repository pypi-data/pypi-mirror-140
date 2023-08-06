from respec import Driver, Specification, Verification


class MyDriver(Driver):
    def __init__(self):
        self.count_setup = 0
        self.count_cleanup = 0

    def setup(self) -> None:
        self.count_setup += 1

    def get_result(self) -> bool:
        return True

    def cleanup(self) -> None:
        self.count_cleanup += 1


class MySpec(Specification):
    driver: MyDriver

    def should_do_something(self):
        self.assertTrue(self.driver.get_result())

    def should_do_something_else(self):
        self.assertTrue(True)


def test_should_setup_driver():
    driver = MyDriver()
    Verification(quiet=True).include(MySpec.using(driver)).verify()
    assert driver.count_setup == 2


def test_should_cleanup_driver():
    driver = MyDriver()
    Verification(quiet=True).include(MySpec.using(driver)).verify()
    assert driver.count_cleanup == 2
