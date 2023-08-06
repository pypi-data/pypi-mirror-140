from data_quality_check.core.checks.check import Check


class KeyMappingCheck(Check):
    def __init__(self, spark, table_name, column_name: str, target_table_name: str, target_column_name: str):
        self.spark = spark
        self.table_name = table_name
        self.column_name = column_name
        self.target_table_name = target_table_name
        self.target_column_name = target_column_name

    def run(self):
        spark = self.spark
        table_name = self.table_name
        column_name = self.column_name
        target_table_name = self.target_table_name
        target_column_name = self.target_column_name

        sql = f'SELECT COLLECT_SET(result) AS result_set, 1 AS one from ' \
              f' (SELECT DISTINCT(aa.{column_name}) as result FROM {table_name} aa ' \
              f' LEFT ANTI JOIN {target_table_name} bb ' \
              f' ON (aa.{column_name} = bb.{target_column_name}) ' \
              f' WHERE TRIM(aa.{column_name})!=\'\' AND aa.{column_name} IS NOT NULL order by result asc LIMIT 100) ' \
              f' GROUP BY one'
        sql_result = spark.sql(sql).collect()
        if len(sql_result) > 0:
            outstanding_value_samples = sql_result[0]['result_set']
        else:
            outstanding_value_samples = []

        sql = f' SELECT 1 FROM {table_name} aa ' \
              f' LEFT ANTI JOIN {target_table_name} bb ' \
              f' ON (aa.{column_name} = bb.{target_column_name}) ' \
              f' WHERE TRIM(aa.{column_name})!=\'\' AND aa.{column_name} IS NOT NULL'
        outstanding_row_count = spark.sql(sql).count()

        sql = f'SELECT 1 FROM {table_name} '
        total_row_count = spark.sql(sql).count()

        sql = f' SELECT 1 FROM {table_name} WHERE TRIM({column_name})=\'\' OR {column_name} IS NULL'
        null_and_empty_row_count = spark.sql(sql).count()

        return {
            'table_name': table_name,
            'column_name': column_name,
            'target_table_name': target_table_name,
            'target_column_name': target_column_name,
            'outstanding_value_samples': outstanding_value_samples,
            'outstanding_row_count': outstanding_row_count,
            'null_and_empty_row_count': null_and_empty_row_count,
            'total_row_count': total_row_count
        }


class CodeInSetCheck(Check):
    def __init__(self, spark, table_name, column_name, config_expected_codes=[]):
        self.spark = spark
        self.table_name = table_name
        self.column_name = column_name
        self.config_expected_codes = config_expected_codes

    def run(self):
        spark = self.spark
        table_name = self.table_name
        column_name = self.column_name
        config_expected_codes = self.config_expected_codes
        config_expected_codes.sort()
        expected_codes_raw_str = str(config_expected_codes)
        expected_codes_str = str(expected_codes_raw_str).replace('[', '').replace(']', '')

        sql = f'SELECT 1 FROM {table_name}  WHERE `{column_name}` IS NULL '
        null_row_count = spark.sql(sql).count()

        sql = f'SELECT 1 FROM {table_name} ' \
              f' WHERE `{column_name}` NOT IN ({expected_codes_str}) AND `{column_name}` IS NOT NULL'
        unexpected_valued_row_count = spark.sql(sql).count()

        sql = f'SELECT 1 FROM {table_name} '
        total_row_count = spark.sql(sql).count()

        sql = f'SELECT COLLECT_SET(DISTINCT(`{column_name}`)) AS result_set, 1 AS one FROM {table_name} ' \
              f' WHERE `{column_name}` NOT IN ({expected_codes_str}) GROUP BY one LIMIT 20'
        sql_result = spark.sql(sql).collect()
        if len(sql_result) > 0:
            unexpected_code_samples = sql_result[0]['result_set']
        else:
            unexpected_code_samples = []

        return {'table_name': table_name,
                'column_name': column_name,
                'config_expected_codes': config_expected_codes,
                'null_row_count': null_row_count,
                'unexpected_valued_row_count': unexpected_valued_row_count,
                'unexpected_code_samples': unexpected_code_samples,
                'total_row_count': total_row_count}
