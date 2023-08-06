import os
from typing import Type, Union
from unittest import TestSuite, TestLoader, TextTestRunner
from unittest.result import TestResult

from respec.core.specification import Specification, SpecificationBuilder


class Verification:
    def __init__(self, *, test_method_prefix=None, quiet=False):
        self._quiet = quiet
        self._suite = TestSuite()
        self._loader = TestLoader()
        self._loader.testMethodPrefix = test_method_prefix or 'should'

    def include(self, *spec_list: Union[Type[Specification], SpecificationBuilder]) -> 'Verification':
        for spec in spec_list:
            if isinstance(spec, type) and issubclass(spec, Specification):
                self._include_spec_type(spec)
            elif isinstance(spec, SpecificationBuilder):
                self._include_spec_builder(spec)
            else:
                raise NotImplementedError()
        return self

    def _include_spec_type(self, spec_type: Type[Specification]):
        self._include_spec_builder(SpecificationBuilder(spec_type))

    def _include_spec_builder(self, builder: SpecificationBuilder):
        tests = builder.get_test_cases(self._loader)
        for test in tests:
            self._suite.addTest(test)

    def verify(self) -> TestResult:
        if self._quiet:
            runner = TextTestRunner(stream=open(os.devnull, 'w'))
        else:
            runner = TextTestRunner()
        return runner.run(self._suite)
