import unittest

from dataplat.base_test import LocalSpark
from dataplat.data_process.sql_processor import SqlProcessor
import udf
from udf import *
from udf import _check_national_id_detail


class UDFTest(unittest.TestCase):
    def test_check_mobile(self):
        self.assertIsNone(check_mobile(''))
        self.assertIsNone(check_mobile('123'))
        self.assertIsNone(check_mobile('0123456789j'))
        self.assertIsNone(check_mobile('01234567899'))
        self.assertIsNone(check_mobile('11234567899'))
        self.assertIsNone(check_mobile(None))
        self.assertEqual('13234567899', check_mobile('13234567899'))

    def test_check_id(self):
        ids = ['TEL15874001947', '000000000000000000', '000000000000', '', None]
        for id in ids:
            self.assertIsNone(udf.check_national_id(id))
            self.assertIsNone(udf.check_military_id(id))
            self.assertIsNone(udf.check_driver_id(id))
            self.assertIsNone(udf.check_HongKong_and_Macao_permit_id(id))
            self.assertIsNone(udf.check_passport_id(id))
            self.assertIsNone(udf.check_residence_id(id))

    def test_register_udf(self):
        spark = LocalSpark.get()
        SqlProcessor(spark, "").register_udfs_from_pyfile("./udf.py")

    def test_check_reachable(self):
        self.assertFalse(udf.check_adms_reachable(None, None)[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', '空号')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', '空号！！！！')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', '  空号！！！！')[0])

        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 停机！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 假号！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 暂停服务！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 虚假！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 号码不存在！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 假的！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 无效号码！！！ ')[0])

        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 联系不上！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 无法接通！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 不接！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 关机！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 无人接听！！！ ')[0])
        self.assertFalse(udf.check_adms_reachable('跟进中已联系', ' 打不通！！！ ')[0])

    def test_check_national_id_date_part_with_15_digits(self):
        dates = [
            ('950218', 1, '验证通过!'),
            ('960229', 1, '验证通过!'),
            ('000229', 2, '身份证号码出生日期超出范围或含有非法字符!'),
            ('961418', 2, '身份证号码出生日期超出范围或含有非法字符!'),
            ('951045', 2, '身份证号码出生日期超出范围或含有非法字符!')]
        for (date, code, msg) in dates:
            with self.subTest(msg):
                self.assertEqual(code, _check_national_id_detail('372525' + date + '000')[0])

    def test_check_national_id_date_part_with_18_digits(self):
        dates = [
            ('19960229', 1, '验证通过!'),
            ('19000229', 2, '身份证号码出生日期超出范围或含有非法字符!'),
            ('19941418', 2, '身份证号码出生日期超出范围或含有非法字符!'),
            ('19941045', 2, '身份证号码出生日期超出范围或含有非法字符!')]
        for (date, code, msg) in dates:
            with self.subTest(msg):
                self.assertEqual(code, _check_national_id_detail('372525' + date + '0000')[0])

    def test_check_national_id_date_part_and_check_bit_with_18_digits(self):
        self.assertEqual(1, _check_national_id_detail('372525199502180007')[0])
        self.assertEqual(3, _check_national_id_detail('372525199502180000')[0])  # 校验位错误：'身份证号码校验错误!'

    def test_check_car_plate_no(self):
        self.assertEqual('闽D12345', check_car_plate_no('闽D12345'))
        self.assertEqual('闽F12345', check_car_plate_no('闽F12345'))
        self.assertEqual(None, check_car_plate_no('闽F12345ab'))

    def test_get_gender_from_id_no(self):
        self.assertEqual('男', get_gender_from_identity_no('510781199402209411'))
        self.assertEqual('男', get_gender_from_identity_no('510781940220941'))
        self.assertEqual('女', get_gender_from_identity_no('110116198606040620'))
        self.assertEqual('女', get_gender_from_identity_no('110116860604062'))
        self.assertEqual(None, get_gender_from_identity_no('110116198606040621'))
        self.assertEqual(None, get_gender_from_identity_no('770116860604062'))
        self.assertEqual(None, get_gender_from_identity_no('1234567'))

    def test_get_age_from_id_no(self):
        self.assertEqual(28, get_age_from_identity_no('20210220', '510781199402209411'))
        self.assertEqual(28, get_age_from_identity_no('20210220', '510781940220941'))
        self.assertEqual(27, get_age_from_identity_no('20210219', '510781199402209411'))
        self.assertEqual(27, get_age_from_identity_no('20210219', '510781940220941'))
        self.assertEqual(27, get_age_from_identity_no('20200220', '510781199402209411'))
        self.assertEqual(27, get_age_from_identity_no('20200220', '510781940220941'))
        self.assertEqual(None, get_age_from_identity_no('20210220', '510781199402209412'))
        self.assertEqual(None, get_age_from_identity_no('20210220', '770116860604062'))

    def test_return_valid_prepaid_sales_dates(self):
        # 测试1：传入空串应返回空串
        case1, result1 = [], []

        # 测试2：list长度为1时原样返回
        case2, result2 = ['2021-01-01'], ['2021-01-01']

        # 测试3：排除30天内的无效订单
        case3, result3 = ['2021-01-01', '2021-01-30'], ['2021-01-01']

        # 测试4：不排除30天外的有效订单
        case4, result4 = ['2021-01-01', '2021-01-31'], ['2021-01-01', '2021-01-31']

        # 测试5：第3个订单距离上一个有效订单超过30天，距离上一个无效订单小于30天，应排除中间的无效订单，保留两个有效订单
        case5, result5 = ['2021-01-01', '2021-01-30', '2021-01-31'], ['2021-01-01', '2021-01-31']

        # 测试6：第3个订单距离上一个有效订单小于30天，距离上上个有效订单大于30天，应排除最后的订单，保留前两个有效订单
        case6, result6 = ['2021-01-01', '2021-03-01', '2021-03-05'], ['2021-01-01', '2021-03-01']

        # 测试7：第3个订单日期应该无效
        case7, result7 = ['2021-01-01', '2021-03-01', '2021-03-05', '2021-04-02'], ['2021-01-01', '2021-03-01', '2021-04-02']
        self.assertEqual(result1, udf.valid_prepaid_sales_dates(case1))
        self.assertEqual(result2, udf.valid_prepaid_sales_dates(case2))
        self.assertEqual(result3, udf.valid_prepaid_sales_dates(case3))
        self.assertEqual(result4, udf.valid_prepaid_sales_dates(case4))
        self.assertEqual(result5, udf.valid_prepaid_sales_dates(case5))
        self.assertEqual(result6, udf.valid_prepaid_sales_dates(case6))
        self.assertEqual(result7, udf.valid_prepaid_sales_dates(case7))

    def test_check_if_new_prepaid(self):
        # 测试1：如果没有历史订单记录，则视为新购
        case1, data_date1, result1 = [], '2021-01-01', True

        # 测试2：购买日期在活动开始之后，视为新购
        case2, data_date2, result2 = ['2021-01-01'], '2020-12-01', True

        # 测试3：购买日期在活动开始当天，视为新购
        case3, data_date3, result3 = ['2021-01-01'], '2021-01-01', True

        # 测试4：购买日期在活动开始之前，不视为新购
        case4, data_date4, result4 = ['2021-01-01'], '2021-01-15', False

        # 测试5：购买日期分布在在活动开始前后，不视为新购
        case5, data_date5, result5 = ['2021-01-01', '2021-01-31'], '2021-01-15', False
        self.assertEqual(result1, udf.check_if_new_prepaid(case1, data_date1))
        self.assertEqual(result2, udf.check_if_new_prepaid(case2, data_date2))
        self.assertEqual(result3, udf.check_if_new_prepaid(case3, data_date3))
        self.assertEqual(result4, udf.check_if_new_prepaid(case4, data_date4))
        self.assertEqual(result5, udf.check_if_new_prepaid(case5, data_date5))

    def test_check_valid_prepaid_dates_in_activity(self):
        # 测试1：
        case1, data_date1, duration1, result1 = [], '2021-01-01', 90, []
        case2, data_date2, duration2, result2 = ['2021-01-01'], '2020-12-01', 90, ['2021-01-01']
        case3, data_date3, duration3, result3 = ['2021-01-01'], '2021-01-01', 90, ['2021-01-01']
        case4, data_date4, duration4, result4 = ['2021-01-01'], '2021-01-15', 90, []
        case5, data_date5, duration5, result5 = ['2021-01-01', '2021-01-31', '2021-12-31'], '2021-01-15', 90, ['2021-01-31']
        self.assertEqual(result1, udf.valid_prepaid_dates_in_activity(case1, data_date1, duration1))
        self.assertEqual(result2, udf.valid_prepaid_dates_in_activity(case2, data_date2, duration2))
        self.assertEqual(result3, udf.valid_prepaid_dates_in_activity(case3, data_date3, duration3))
        self.assertEqual(result4, udf.valid_prepaid_dates_in_activity(case4, data_date4, duration4))
        self.assertEqual(result5, udf.valid_prepaid_dates_in_activity(case5, data_date5, duration5))

    def test_get_vehicle_age(self):
        v1_sales_data = '20210109'
        v2_sales_data = '20210110'
        v3_sales_data = '20210111'
        data_date = '2022-01-10'
        v1_age = get_vehicle_age_of_months(v1_sales_data, data_date)
        v2_age = get_vehicle_age_of_months(v2_sales_data, data_date)
        v3_age = get_vehicle_age_of_months(v3_sales_data, data_date)
        v4_age = get_vehicle_age_of_months(None, data_date)
        self.assertEqual(v1_age, 12)
        self.assertEqual(v2_age, 12)
        self.assertEqual(v3_age, 11)
        self.assertEqual(v4_age, None)


if __name__ == '__main__':
    unittest.main()
