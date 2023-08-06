from typing import Type

from respec.core.driver import Driver


class Dsl:
    @classmethod
    def _with_dependencies(cls, driver: Driver = None) -> 'Dsl':
        dsl = cls()
        annotations = cls.__annotations__
        if 'driver' in annotations:
            driver_type: Type[Driver] = annotations['driver']
            if isinstance(driver_type, type) and issubclass(driver_type, Driver):
                setattr(dsl, 'driver', driver)
        return dsl
