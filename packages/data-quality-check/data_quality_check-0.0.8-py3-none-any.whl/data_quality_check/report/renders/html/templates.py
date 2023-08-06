# Initializing Jinja
import jinja2

from data_quality_check.report.renders.html.formatters import fmt_badge, fmt_percent, fmt_numeric, fmt

package_loader = jinja2.PackageLoader(
    "data_quality_check", "report/renders/html/templates"
)
jinja2_env = jinja2.Environment(
    lstrip_blocks=True, trim_blocks=True, autoescape=True,
    loader=package_loader
)

jinja2_env.filters["is_list"] = lambda x: isinstance(x, list)
jinja2_env.filters["fmt_badge"] = fmt_badge
jinja2_env.filters["fmt_percent"] = fmt_percent
jinja2_env.filters["fmt_numeric"] = fmt_numeric
jinja2_env.filters["fmt"] = fmt


def template(template_name: str) -> jinja2.Template:
    """Get the template object given the name.

    Args:
      template_name: The name of the template file (.html)

    Returns:
      The jinja2 environment.

    """
    return jinja2_env.get_template(template_name)
