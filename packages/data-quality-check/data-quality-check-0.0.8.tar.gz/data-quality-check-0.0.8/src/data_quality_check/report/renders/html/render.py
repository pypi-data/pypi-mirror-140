from typing import List

from data_quality_check.core.expectations.expectation import Expectation
from data_quality_check.profiler.customized_profiler import CustomizedProfilerResult, CodeCheckResult, \
    KeyMappingCheckResult
from data_quality_check.profiler.general_profiler import GeneralProfilerResult, GeneralFieldResult
from data_quality_check.report.renders.html import templates


def render_page_top_section():
    return templates.template("page_top.html").render()


def render_page_bottom_section():
    return templates.template("page_bottom.html").render()


def render_general_profiler_section(gfr: GeneralFieldResult = None):
    if gfr is None:
        return ''

    general_profiler_kwargs = {}
    total_row_count = (gfr.null_count or 0) + (gfr.valued_row_count or 0)
    general_profiler_kwargs['field_name'] = gfr.field_name
    general_profiler_kwargs['data_type'] = str(type(gfr.max_value))

    general_profiler_kwargs['distinct_values_count'] = gfr.unique_valued_row_count

    general_profiler_kwargs['null_row_count'] = gfr.null_count
    general_profiler_kwargs['null_row_count_percent'] = \
        gfr.null_count / total_row_count if total_row_count != 0 else 0

    general_profiler_kwargs['empty_value_row_count'] = gfr.empty_count
    general_profiler_kwargs['empty_value_row_count_percent'] = \
        gfr.empty_count / total_row_count if total_row_count != 0 else 0

    general_profiler_kwargs['zero_value_row_count'] = gfr.zero_count
    general_profiler_kwargs['zero_value_row_count_percent'] = \
        gfr.zero_count / total_row_count if total_row_count != 0 else 0

    general_profiler_kwargs['valued_row_count'] = gfr.valued_row_count
    general_profiler_kwargs['valued_row_count_percent'] = \
        gfr.valued_row_count / total_row_count if total_row_count != 0 else 0

    general_profiler_kwargs['total_row_count'] = total_row_count
    general_profiler_kwargs['unique_row_count'] = gfr.unique_valued_row_count
    general_profiler_kwargs['unique_row_count_percent'] = \
        gfr.unique_valued_row_count / total_row_count if total_row_count != 0 else 0

    general_profiler_kwargs['duplicated_valued_row_count'] = gfr.duplicated_valued_row_count
    general_profiler_kwargs['duplicated_valued_row_count_percent'] = \
        gfr.duplicated_valued_row_count / total_row_count if total_row_count != 0 else 0

    general_profiler_kwargs['min_value'] = gfr.min_value
    general_profiler_kwargs['max_value'] = gfr.max_value
    general_profiler_kwargs['mean_value'] = gfr.mean_value
    general_profiler_kwargs['stddev_value'] = gfr.stddev_value
    general_profiler_kwargs['values_count'] = gfr.value_count

    general_profiler_kwargs['top_freq_values_counts'] = gfr.top_freq_count_by_values

    return templates.template("general_profiler_template.html").render(general_profiler_kwargs)


def render_all_general_profiler_sections(general_profiler_results: GeneralProfilerResult):
    html_elements = []
    for vi in list(general_profiler_results.field_results.values()):
        html_elements.append(render_general_profiler_section(vi))
    if len(html_elements) == 0:
        return ''
    else:
        return '\n'.join(html_elements)


def render_customized_code_check_section(ccr: CodeCheckResult = None):
    if ccr is None:
        return ''

    code_check_kwargs = {}
    total_row_count = ccr.total_row_count or 0

    code_check_kwargs['field_name'] = ccr.field_name
    code_check_kwargs['total_row_count'] = total_row_count
    code_check_kwargs['null_row_count'] = ccr.null_row_count
    code_check_kwargs['null_row_count_percent'] = \
        ccr.null_row_count / total_row_count if total_row_count != 0 else 0

    code_check_kwargs['unexpected_valued_row_count'] = ccr.unexpected_valued_row_count
    code_check_kwargs['unexpected_valued_row_count_percent'] = \
        ccr.unexpected_valued_row_count / total_row_count if total_row_count != 0 else 0

    code_check_kwargs['expected_codes_samples'] = ccr.unexpected_code_samples
    code_check_kwargs['config_expected_codes'] = ccr.config_expected_codes

    return templates.template("customized_profiler_code_check_template.html").render(code_check_kwargs)


def render_customized_key_mapping_section(kmc: KeyMappingCheckResult = None):
    # TBD
    return ''


def render_all_customized_profiler_sections(customized_profiler_results: CustomizedProfilerResult):
    html_elements = []
    for vi in customized_profiler_results.code_check_result:
        html_elements.append(render_customized_code_check_section(ccr=vi))

    for vi in customized_profiler_results.key_mapping_check_result:
        html_elements.append(render_customized_key_mapping_section(vi))

    if len(html_elements) == 0:
        return ''
    else:
        return '\n'.join(html_elements)


def render_all_expectation_sections(all_expectations: List[Expectation] = None):
    # TBD
    return ''


def render_all(gprs: GeneralProfilerResult = None, cprs: CustomizedProfilerResult = None, expectation_result=None):
    head = render_page_top_section()
    body = ''
    if expectation_result is not None:
        body += render_all_expectaion_sections(expectation_result)

    if gprs is not None:
        body += render_all_general_profiler_sections(gprs)

    if cprs is not None:
        body += render_all_customized_profiler_sections(cprs)

    foot = render_page_bottom_section()
    combined_html = head + body + foot
    return combined_html
