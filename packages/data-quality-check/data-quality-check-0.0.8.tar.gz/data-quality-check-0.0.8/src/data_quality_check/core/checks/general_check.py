from abc import ABC
from typing import Dict

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException

from data_quality_check.constants import PROFILE_TMP_VIEW
from data_quality_check.core.checks.check import Check


def create_profile_tmp_view_using_column(spark, table_name, column_name, df=None):
    if df is not None:
        tmp_view = df.select(column_name)
        tmp_view.createOrReplaceTempView(PROFILE_TMP_VIEW)
    else:
        tmp_view = spark.sql(f'SELECT {column_name} FROM {table_name}')
        tmp_view.createOrReplaceTempView(PROFILE_TMP_VIEW)
    return PROFILE_TMP_VIEW, tmp_view


class TopFreqCountByValuesCheck(Check):
    def __init__(self, spark: SparkSession, table_name: str = None, column_name: str = None, df: DataFrame = None,
                 top_freq_values_number: int = 10):
        self.table_name, self.df = create_profile_tmp_view_using_column(spark=spark, table_name=table_name,
                                                                        column_name=column_name, df=df)
        self.spark = spark
        self.column_name = column_name
        self.top_freq_values_number = top_freq_values_number

    def run(self) -> Dict:
        query = f'SELECT SUM(1) as ct, `{self.column_name}` as value from {self.table_name} ' \
                f' GROUP BY (`{self.column_name}`) ' \
                f' ORDER BY ct DESC limit {self.top_freq_values_number}'
        rows = self.spark.sql(query).collect()
        top_values = [row['value'] for row in rows]
        top_values_ct = [row['ct'] for row in rows]
        return {
            'top_values': top_values,
            'top_values_ct': top_values_ct
        }

    def get_profile_result(self):
        return self.run()


class GeneralBasicCheck(Check, ABC):
    table_name: str
    column_name: str
    df: DataFrame
    spark: SparkSession
    result_key_word: str

    def __init__(self, spark: SparkSession, table_name: str = None, column_name: str = None, df: DataFrame = None):
        self.table_name, self.df = create_profile_tmp_view_using_column(spark=spark, table_name=table_name,
                                                                        column_name=column_name, df=df)
        self.column_name = column_name
        self.spark = spark

    def get_profile_result(self):
        return self.run().get(self.result_key_word)


class ValuesCountCheck(GeneralBasicCheck):
    result_key_word = 'values_count'

    def run(self) -> Dict:
        query = f'SELECT 1 FROM {self.table_name} WHERE `{self.column_name}` IS NOT NULL ' \
                f' GROUP BY (`{self.column_name}`)'
        ct = self.spark.sql(query).count()
        return {self.result_key_word: ct}


class UniqueValuedRowCheck(GeneralBasicCheck):
    result_key_word = 'unique_valued_row_count'

    def run(self) -> Dict:
        query = f'SELECT SUM(1) as ct, `{self.column_name}` as value from {self.table_name} ' \
                f' WHERE `{self.column_name}` IS NOT NULL' \
                f' GROUP BY ({self.column_name}) ' \
                f' HAVING ct=1'
        ct = self.spark.sql(query).count()
        return {self.result_key_word: ct}


class DuplicatedValuedRowCheck(GeneralBasicCheck):
    result_key_word = 'duplicated_valued_rows'

    def run(self) -> Dict:
        query = f' SELECT COALESCE(SUM(ct),0) AS ct FROM ' \
                f'(' \
                f' SELECT SUM(1) as ct, `{self.column_name}` as value from {self.table_name} ' \
                f' WHERE  `{self.column_name}` IS NOT NULL' \
                f' GROUP BY ( `{self.column_name}`) ' \
                f' HAVING ct>1' \
                f')'
        ct = self.spark.sql(query).collect().pop()['ct']
        return {self.result_key_word: ct}


class ZeroValueRowCheck(GeneralBasicCheck):
    result_key_word = 'zero_row_count'

    def run(self) -> Dict:
        query = f'SELECT 1 FROM {self.table_name} WHERE `{self.column_name}` == 0 '
        row_ct = self.spark.sql(query).count()
        return {self.result_key_word: row_ct}


class EmptyRowCheck(GeneralBasicCheck):
    result_key_word = 'empty_row_count'

    def run(self) -> Dict:
        query = f'SELECT 1 FROM {self.table_name} WHERE `{self.column_name}` == "" '
        row_ct = self.spark.sql(query).count()
        return {self.result_key_word: row_ct}


def get_column_summary_by_type(df, column_name, op_type):
    try:
        result_df = df.select(column_name).where(f'`{column_name}` IS NOT NULL') \
            .selectExpr(f'{op_type}(`{column_name}`) as value')
    except AnalysisException:
        return None
    return result_df.collect().pop()['value']


class MinValueCheck(GeneralBasicCheck):
    result_key_word = 'min_value'

    def run(self) -> Dict:
        result = get_column_summary_by_type(df=self.df, column_name=self.column_name, op_type='min')
        if result is None:
            return {'error': f'Not able to grab min value from {self.column_name}'}
        return {self.result_key_word: result}


class MaxValueCheck(GeneralBasicCheck):
    result_key_word = 'max_value'

    def run(self) -> Dict:
        val = get_column_summary_by_type(df=self.df, column_name=self.column_name, op_type='max')
        if val is None:
            return {'error': f'Not able to grab max value from {self.column_name}'}
        return {self.result_key_word: val}


class MeanValueCheck(GeneralBasicCheck):
    result_key_word = 'mean_value'

    def run(self) -> Dict:
        ct = get_column_summary_by_type(df=self.df, column_name=self.column_name, op_type='mean')
        if ct is None:
            return {'error': f'Not able to grab mean value from {self.column_name}'}
        return {self.result_key_word: ct}


class StddevValueCheck(GeneralBasicCheck):
    result_key_word = 'stddev_value'

    def run(self) -> Dict:
        ct = get_column_summary_by_type(df=self.df, column_name=self.column_name, op_type='stddev')
        if ct is None:
            return {'error': f'Not able to grab stddev value from {self.column_name}'}
        return {self.result_key_word: ct}


class ValuedRowCountCheck(GeneralBasicCheck):
    result_key_word = 'valued_row_count'

    def run(self) -> Dict:
        ct = get_column_summary_by_type(df=self.df, column_name=self.column_name, op_type='count')
        if ct is None:
            return {'error': f'Not able to grab valued row count from {self.column_name}'}
        return {self.result_key_word: ct}


class NullRowCheck(GeneralBasicCheck):
    result_key_word = 'null_row_count'

    def run(self) -> Dict:
        query = f'SELECT 1 FROM {self.table_name} WHERE `{self.column_name}` IS NULL '
        ct = self.spark.sql(query).count()
        return {self.result_key_word: ct}
