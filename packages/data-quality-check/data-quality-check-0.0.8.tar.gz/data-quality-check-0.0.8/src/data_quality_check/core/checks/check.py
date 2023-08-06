from abc import ABC, abstractmethod
from pyspark.sql import SparkSession


class Check(ABC):
    spark: SparkSession

    @abstractmethod
    def run(self):
        # TBD
        pass
