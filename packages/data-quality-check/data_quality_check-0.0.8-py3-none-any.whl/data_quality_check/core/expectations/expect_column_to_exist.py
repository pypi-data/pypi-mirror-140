from collections import Counter
from typing import Dict

from pyspark.sql import SparkSession

from data_quality_check.core.expectations.expectation import TableExpectation


class ExpectColumnToExist(TableExpectation):
    spark: SparkSession = None
    expectation_type = 'expect_columns_to_exist'
    kwargs = {
        'table_name': 'my_db.my_table',  # Table that you would like to verify
        'expected_columns': ['col1', 'col2']  # Expected columns to be in the table
    }

    def __init__(self, kwargs: Dict = None, spark: SparkSession = None):
        self.set_kwargs(kwargs)
        if spark is not None:
            self.spark = spark

    def verify(self):
        table_name = self.kwargs.get('table_name')
        columns = self.spark.sql(f'SELECT * FROM {table_name} limit 1').columns
        if Counter(columns) == Counter(self.kwargs.get('expected_columns')):
            self.success = True
        else:
            self.success = False
            self.unexpected_info = {
                'message': 'The columns from table DO NOT match the given expected columns.',
                'columns_from_table': columns
            }
        return self.is_success()
