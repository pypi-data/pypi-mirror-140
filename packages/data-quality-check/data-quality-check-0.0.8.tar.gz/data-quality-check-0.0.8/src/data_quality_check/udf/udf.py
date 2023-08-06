import re
import datetime as d
from datetime import datetime

__all__ = [
    'check_military_id', 'check_passport_id', 'check_residence_id', 'check_driver_id',
    'check_HongKong_and_Macao_permit_id',
    'check_national_id', 'check_national_id_detail',
    'check_mobile', 'check_mobile_is_reachable', 'check_car_plate_no',
    'get_gender_from_identity_no', 'get_age_from_identity_no', 'get_vehicle_age_of_months',
    'get_valid_prepaid_sales_dates',
    'get_valid_prepaid_dates_in_activity'
]


def check_regex_func(pattern):
    return lambda any_str: any_str if any_str and re.match(pattern, any_str) else None


area = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江",
        "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南", "42": "湖北",
        "43": "湖南", "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏",
        "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门", "91": "国外"}


### 检验身份证号码的函数
def _check_national_id_detail(id_card):
    errors = ['身份证号码位数不对', '验证通过', '身份证号码出生日期超出范围或含有非法字符', '身份证号码校验错误', '身份证地区非法', '其他']
    id_card = str(id_card).upper()
    id_card = id_card.strip()
    id_card_list = list(id_card)

    try:
        # 15位身份号码检测
        if len(id_card) == 15:
            if id_card[0:2] not in area.keys():
                return 4, errors[4]
            try:
                datetime.strptime('19' + id_card[6:12], '%Y%m%d')
                return 1, errors[1]
            except ValueError:
                return 2, errors[2]

        # 18位身份号码检测
        elif len(id_card) == 18:
            # 地区校验
            if id_card[0:2] not in area.keys():
                return 4, errors[4]
            # 出生日期的合法性检查
            try:
                if datetime.strptime(id_card[6:14], '%Y%m%d'):
                    # //计算校验位
                    S = (int(id_card_list[0]) + int(id_card_list[10])) * 7 + \
                        (int(id_card_list[1]) + int(id_card_list[11])) * 9 + \
                        (int(id_card_list[2]) + int(id_card_list[12])) * 10 + \
                        (int(id_card_list[3]) + int(id_card_list[13])) * 5 + \
                        (int(id_card_list[4]) + int(id_card_list[14])) * 8 + \
                        (int(id_card_list[5]) + int(id_card_list[15])) * 4 + \
                        (int(id_card_list[6]) + int(id_card_list[16])) * 2 + \
                        int(id_card_list[7]) * 1 + int(id_card_list[8]) * 6 + int(id_card_list[9]) * 3
                    Y = S % 11
                    M = "F"
                    JYM = "10X98765432"
                    M = JYM[Y]  # 判断校验位
                    if M == id_card_list[17]:  # 检测ID的校验位
                        return 1, errors[1]
                    else:
                        return 3, errors[3]
            except ValueError:
                return 2, errors[2]
        else:
            return 0, errors[0]

    except Exception as e:
        return 5, errors[5] + f":{e.args[0]}"


# 检查居民身份证 id
def check_national_id(id_card):
    return id_card if _check_national_id_detail(id_card)[0] == 1 else None


def check_national_id_detail(id_card):
    return _check_national_id_detail(id_card)[1] if id_card else None


check_military_id = check_regex_func(r'^[\u4E00-\u9FA5](字第)([0-9a-zA-Z]{4,8})(号?)$')  # 检查军官证 id
check_passport_id = check_regex_func('^([a-zA-z]|[0-9]){9}$')  # 检查护照 id
check_residence_id = check_regex_func(r'^\d{9}$')  # 检查户口 id
check_driver_id = lambda id: check_regex_func(r'^\d{12}$')(id) if id and id[:2] in area else None  # 检查驾驶证 id
check_HongKong_and_Macao_permit_id = check_regex_func('^[HMhm]{1}([0-9]{10}|[0-9]{8})$')  # 检查港澳通行证 id
check_mobile = check_regex_func(r'^1[3-9]\d{9}$')
# 参考：https://cloud.tencent.com/developer/article/1361209
check_car_plate_no = check_regex_func(
    r'^(([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z](([0-9]{5}[DF])|([DF]([A-HJ-NP-Z0-9])[0-9]{4})))'
    r'|([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-HJ-NP-Z0-9]{4}[A-HJ-NP-Z0-9挂学警港澳使领]))$')


def check_adms_reachable(phase_detail, lose_remark):
    import re
    error_msg = lambda check_field_msg, value: (
        f'检查 {check_field_msg} 通过: {value}', f'检查 {check_field_msg} 失败: {value}')

    class Check:
        def __init__(self, pass_condition: bool, check_field_name: str, check_field_value):
            self.is_passed = pass_condition
            self.msgs = error_msg(check_field_name, check_field_value)

        def msg(self):
            return self.msgs[0] if self.is_passed else self.msgs[1]

    reachable_state = ['跟进中已联系', '跟进中申请战败', '线索战败', '邀约成功未分配顾问', '邀约成功已分配顾问未到店', 'A卡', '订车申请', '订车',
                       '成交申请', '成交', '申请战败', '退订申请', '退订', '退车申请', '退车', 'A卡战败', ]
    empty_phone_remark_pattern = r'.*(空号|停机|假号|暂停服务|虚假|假的|无效号码|号码不存在|打不通|联系不上|无法接通|不接|关机|无人接听).*'

    reachable_phase = Check(phase_detail in reachable_state, 'ADMS phase_detail', phase_detail)
    reachable_remark = Check(not lose_remark or not (re.match(empty_phone_remark_pattern, lose_remark)),
                             'ADMS lose_remark', lose_remark)
    return reachable_phase.is_passed and reachable_remark.is_passed, '  &  '.join(
        [reachable_phase.msg(), reachable_remark.msg()])


from pyspark.sql.types import StructType, BooleanType, StringType, StructField, ArrayType
from pyspark.sql.functions import udf

check_mobile_is_reachable = udf(check_adms_reachable, StructType(
    [StructField('is_reachable', BooleanType()), StructField('detail', StringType())]))


def get_gender_from_identity_no(id_no):
    if check_national_id(id_no):
        if len(id_no) == 15 and id_no[14].isdigit() and int(id_no[14]) % 2 == 0:
            return '女'
        if len(id_no) == 15 and id_no[14].isdigit() and int(id_no[14]) % 2 == 1:
            return '男'
        if len(id_no) == 18 and id_no[16].isdigit() and int(id_no[16]) % 2 == 0:
            return '女'
        if len(id_no) == 18 and id_no[16].isdigit() and int(id_no[16]) % 2 == 1:
            return '男'
    return None


def get_age_from_identity_no(data_date, id_no) -> int:
    if check_national_id(id_no):
        birthdate_start_index_old = 6
        birthdate_end_index_old = 12
        birthdate_start_index = 6
        birthdate_end_index = 14
        if len(id_no) == 15:
            age = int(data_date[0:4]) - int('19' + id_no[birthdate_start_index_old: birthdate_start_index_old + 2])
            if data_date[4:] >= id_no[birthdate_start_index_old + 2: birthdate_end_index_old]:
                age += 1
            return age
        if len(id_no) == 18:
            age = int(data_date[0:4]) - int(id_no[birthdate_start_index: birthdate_start_index + 4])
            if data_date[4:] >= id_no[birthdate_start_index + 4: birthdate_end_index]:
                age += 1
            return age
    return None


def valid_prepaid_sales_dates(dates: []) -> []:
    if not dates:
        return []
    elif len(dates) == 0:
        return []
    elif len(dates) == 1:
        return dates
    else:
        dates = sorted(dates)
        valid_dates = [dates[0]]
        last_valid_date = dates[0]
        try:
            valid_boundary = (datetime.strptime(last_valid_date, "%Y-%m-%d")
                              + d.timedelta(days=30)).strftime("%Y-%m-%d")
            for date in dates[1:]:
                if (datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(valid_boundary, "%Y-%m-%d")).days >= 0:
                    last_valid_date = date
                    valid_dates.append(last_valid_date)
                    valid_boundary = (datetime.strptime(last_valid_date, "%Y-%m-%d")
                                      + d.timedelta(days=30)).strftime("%Y-%m-%d")
                    continue
                else:
                    continue

        except Exception as e:
            raise e
        return valid_dates


get_valid_prepaid_sales_dates = udf(valid_prepaid_sales_dates, ArrayType(StringType()))


def check_if_new_prepaid(valid_dates: [], data_date: str) -> bool:
    if not valid_dates:
        return True
    elif len(valid_dates) == 0:
        return True
    for date in valid_dates:
        if (datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(data_date, "%Y-%m-%d")).days < 0:
            return False
    return True


def valid_prepaid_dates_in_activity(valid_dates: [], start_date: str, duration: int) -> []:
    if not valid_dates:
        return []
    elif len(valid_dates) == 0:
        return []
    prepaid_dates_in_activity = []
    for date in valid_dates:
        if 0 <= (datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days <= duration:
            prepaid_dates_in_activity.append(date)
    return prepaid_dates_in_activity


def get_vehicle_age_of_months(sales_date_key: int, data_date: str):
    if sales_date_key is None:
        return None
    current_date = datetime.strptime(data_date, '%Y-%m-%d')
    sales_date = datetime.strptime(str(sales_date_key), '%Y%m%d')
    sales_date_previous = sales_date
    months_gap = (current_date.year - sales_date_previous.year) * 12 + current_date.month - sales_date_previous.month
    if current_date.day < sales_date_previous.day:
        months_gap -= 1
    return months_gap


get_valid_prepaid_dates_in_activity = udf(valid_prepaid_dates_in_activity, ArrayType(StringType()))
