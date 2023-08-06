from abc import ABC, abstractmethod
from typing import Dict

from pyspark.sql import SparkSession


class Expectation(ABC):
    expectation_type: str = "undefined"
    success: bool = False
    kwargs: Dict = {}
    unexpected_info: Dict = None
    check_result: Dict = {}

    @abstractmethod
    def verify(self):
        pass

    def is_success(self):
        return self.success

    def get_unexpected_info(self):
        return self.unexpected_info


class TableExpectation(Expectation, ABC):
    spark: SparkSession = None

    def set_kwargs(self, kwargs: Dict = None):
        if kwargs is not None:
            self.kwargs = kwargs

    def set_spark(self, spark: SparkSession = None):
        if spark is not None:
            self.spark = spark
