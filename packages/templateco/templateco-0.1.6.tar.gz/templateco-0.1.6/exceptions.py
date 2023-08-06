class TemplatecoException(BaseException):
    """
    Generic Templateco exception.
    """

    pass


class IncompatiblePluginException(TemplatecoException):
    """
    Indicates that a Templateco plugin has been loaded, but it is not compatible.
    """

    pass


class NoPluginsFoundException(TemplatecoException):
    """
    Called when Templateco has been invoked, but no plugins are specified.
    """

    pass


class UnknownOperatingModeException(TemplatecoException):
    """
    Called when Templateco is missing the operating mode e.g. prefixes or plugins.
    """

    pass


class PluginOperationException(TemplatecoException):
    """
    Called during a Templateco plugin's operation to be echoed back to the user.

    This should be called by Plugin authors when they wish to pass a clear message back
    up to the user that _something_ they have selected isn't correct.
    """

    pass
