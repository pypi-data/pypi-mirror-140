from typing import Type, Optional, Iterable
from unittest import TestCase, TestLoader

from respec.core.dsl import Dsl
from respec.core.driver import Driver


class Specification(TestCase):
    def __init__(self, *args, **kwargs):
        super(Specification, self).__init__(*args, **kwargs)
        self._is_using_driver: bool = _is_using_driver(self.__class__)
        self._is_using_dsl: bool = _is_using_dsl(self.__class__)

    def setUp(self) -> None:
        if self._is_using_driver:
            driver: Driver = getattr(self, 'driver')
            driver.setup()

    def tearDown(self) -> None:
        if self._is_using_driver:
            driver: Driver = getattr(self, 'driver')
            driver.cleanup()

    @classmethod
    def using(cls, driver: Driver) -> 'SpecificationBuilder':
        builder = SpecificationBuilder(cls)
        builder.using(driver)
        return builder

    def _inject_dependencies(self, driver: Driver = None):
        if self._is_using_dsl:
            dsl_type: Type[Dsl] = self.__annotations__['dsl']
            setattr(self, 'dsl', dsl_type._with_dependencies(driver))
        if self._is_using_driver:
            setattr(self, 'driver', driver)


class SpecificationBuilder:
    def __init__(self, spec_type: Type[Specification]):
        self._spec_type: Type[Specification] = spec_type
        self._driver: Optional[Driver] = None

    def using(self, driver: Driver):
        if self._driver is not None:
            raise KeyError('Driver already exists')

        self._driver = driver

    def get_test_cases(self, loader: TestLoader) -> Iterable[TestCase]:
        names = loader.getTestCaseNames(self._spec_type)
        for name in names:
            test = self._spec_type(name)
            test._inject_dependencies(self._driver)
            yield test


def _is_using_driver(spec_type: Type[Specification]):
    annotations = spec_type.__annotations__
    if 'driver' not in annotations:
        return False
    driver_type = annotations['driver']
    return isinstance(driver_type, type) and issubclass(driver_type, Driver)


def _is_using_dsl(spec_type: Type[Specification]):
    annotations = spec_type.__annotations__
    if 'dsl' not in annotations:
        return False
    dsl_type = annotations['dsl']
    return isinstance(dsl_type, type) and issubclass(dsl_type, Dsl)
