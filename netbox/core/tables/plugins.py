import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.tables import BaseTable, columns
from .template_code import PLUGIN_IS_INSTALLED

__all__ = (
    'CatalogPluginTable',
    'PluginVersionTable',
)


PLUGIN_NAME_TEMPLATE = """
<img class="plugin-icon" src="{{ record.icon_url }}">
<a href="{% url 'core:plugin' record.config_name %}">{{ record.title_long }}</a>
"""


class PluginVersionTable(BaseTable):
    version = tables.Column(
        verbose_name=_('Version')
    )
    last_updated = columns.DateTimeColumn(
        accessor=tables.A('date'),
        timespec='minutes',
        verbose_name=_('Last Updated')
    )
    min_version = tables.Column(
        accessor=tables.A('netbox_min_version'),
        verbose_name=_('Minimum NetBox Version')
    )
    max_version = tables.Column(
        accessor=tables.A('netbox_max_version'),
        verbose_name=_('Maximum NetBox Version')
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No plugin data found')
        fields = (
            'version', 'last_updated', 'min_version', 'max_version',
        )
        default_columns = (
            'version', 'last_updated', 'min_version', 'max_version',
        )
        orderable = False


class CatalogPluginTable(BaseTable):
    title_long = columns.TemplateColumn(
        template_code=PLUGIN_NAME_TEMPLATE,
        verbose_name=_('Name')
    )
    author = tables.Column(
        accessor=tables.A('author__name'),
        verbose_name=_('Author')
    )
    is_local = columns.BooleanColumn(
        false_mark=None,
        verbose_name=_('Local')
    )
    is_installed = columns.TemplateColumn(
        verbose_name=_('Active'),
        template_code=PLUGIN_IS_INSTALLED
    )
    is_certified = columns.BooleanColumn(
        false_mark=None,
        verbose_name=_('Certified')
    )
    created_at = columns.DateTimeColumn(
        verbose_name=_('Published')
    )
    updated_at = columns.DateTimeColumn(
        verbose_name=_('Updated')
    )
    installed_version = tables.Column(
        verbose_name=_('Installed Version')
    )
    latest_version = tables.Column(
        accessor=tables.A('release_latest__version'),
        verbose_name=_('Latest Version')
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No plugin data found')
        fields = (
            'title_long', 'author', 'is_local', 'is_installed', 'is_certified', 'created_at', 'updated_at',
            'installed_version', 'latest_version',
        )
        default_columns = (
            'title_long', 'author', 'is_local', 'is_installed', 'is_certified', 'installed_version', 'latest_version',
        )
        # List installed plugins first, then certified plugins, then
        # everything else (with each tranche ordered alphabetically)
        order_by = ('-is_installed', '-is_certified', 'name')

    def render_title_long(self, value, record):
        if record.static:
            return value
        url = reverse('core:plugin', args=[record.config_name])
        return mark_safe(f"<a href='{url}'>{value}</a>")
