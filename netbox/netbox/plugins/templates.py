from django.template.loader import get_template
from django.utils.translation import gettext as _

__all__ = (
    'PluginTemplateExtension',
)


class PluginTemplateExtension:
    """
    This class is used to register plugin content to be injected into core NetBox templates. It contains methods
    that are overridden by plugin authors to return template content.

    The `models` attribute on the class defines the which specific model detail pages this class renders content
    for. It should be defined as a list of strings in the following form:

        models = ['<app_label>.<model_name>', '<app_label>.<model_name>']

    If `models` is left as None, the extension will render for _all_ models.

    The `render()` method provides the following context data:

    * object - The object being viewed (object views only)
    * model - The type of object being viewed (list views only)
    * request - The current request
    * settings - Global NetBox settings
    * config - Plugin-specific configuration parameters
    """
    models = None

    def __init__(self, context):
        self.context = context

    def render(self, template_name, extra_context=None):
        """
        Convenience method for rendering the specified Django template using the default context data. An additional
        context dictionary may be passed as `extra_context`.
        """
        if extra_context is None:
            extra_context = {}
        elif not isinstance(extra_context, dict):
            raise TypeError(_("extra_context must be a dictionary"))

        return get_template(template_name).render({**self.context, **extra_context})

    #
    # Global methods
    #

    def head(self):
        """
        HTML returned by this method will be inserted in the page's `<head>` block. This may be useful e.g. for
        including additional Javascript or CSS resources.
        """
        raise NotImplementedError

    def navbar(self):
        """
        Content that will be rendered inside the top navigation menu. Content should be returned as an HTML
        string. Note that content does not need to be marked as safe because this is automatically handled.
        """
        raise NotImplementedError

    #
    # Object list views
    #

    def list_buttons(self):
        """
        Buttons that will be rendered and added to the existing list of buttons on the list view. Content
        should be returned as an HTML string. Note that content does not need to be marked as safe because this is
        automatically handled.
        """
        raise NotImplementedError

    #
    # Object detail views
    #

    def buttons(self):
        """
        Buttons that will be rendered and added to the existing list of buttons on the detail page view. Content
        should be returned as an HTML string. Note that content does not need to be marked as safe because this is
        automatically handled.
        """
        raise NotImplementedError

    def alerts(self):
        """
        Arbitrary content to be inserted at the top of an object's detail view. Content should be returned as an
        HTML string. Note that content does not need to be marked as safe because this is automatically handled.
        """
        raise NotImplementedError

    def left_page(self):
        """
        Content that will be rendered on the left of the detail page view. Content should be returned as an
        HTML string. Note that content does not need to be marked as safe because this is automatically handled.
        """
        raise NotImplementedError

    def right_page(self):
        """
        Content that will be rendered on the right of the detail page view. Content should be returned as an
        HTML string. Note that content does not need to be marked as safe because this is automatically handled.
        """
        raise NotImplementedError

    def full_width_page(self):
        """
        Content that will be rendered within the full width of the detail page view. Content should be returned as an
        HTML string. Note that content does not need to be marked as safe because this is automatically handled.
        """
        raise NotImplementedError
