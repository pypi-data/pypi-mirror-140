import logging
from dataclasses import MISSING, dataclass, fields
from functools import lru_cache
from importlib import import_module
from pathlib import Path
from typing import Any, Generator, Iterable, List, Optional

from importlib_metadata import Distribution, distributions
from typeguard import check_type

from templateco.exceptions import IncompatiblePluginException
from templateco.typing import (
    FoldersToTemplate,
    GetQuestions,
    PostTemplateHook,
    PreTemplateHook,
)

logger = logging.getLogger(__name__)


@dataclass(init=False)
class TemplatecoPlugin:
    """
    Templateco Plugin.
    """

    package_name: str
    friendly_name: str
    path_to_module: Path
    compatible_languages: List[str]
    get_questions: GetQuestions
    folders_to_template: FoldersToTemplate
    selected_by_default: bool = False
    pre_template_hook: Optional[PreTemplateHook] = None
    post_template_hook: Optional[PostTemplateHook] = None

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialise the plugin by discarding all kwargs that aren't specified as args.
        """
        for field in fields(self):
            value = kwargs.get(field.name, MISSING)

            if value is MISSING and field.default is not MISSING:
                value = field.default

            check_type(field.name, value, field.type)
            setattr(self, field.name, value)


@lru_cache(maxsize=None)
def _import_templateco_plugin(name: str) -> TemplatecoPlugin:
    """
    Import a compatible Templateco package, and return a TemplatecoPlugin.

    :param name: Name of Python package.
    :raises IncompatiblePluginException
    :return Templateco Plugin.
    """
    module = import_module(name.replace("-", "_"))

    try:
        return TemplatecoPlugin(
            **module.__dict__,
            package_name=name,
            path_to_module=Path(str(module.__file__)).parent,
        )
    except (KeyError, TypeError) as err:
        logger.debug(f"[{name}] Failed to parse plugin information.")
        logger.debug(err)
        raise IncompatiblePluginException(err)


def list_compatible_plugins(
    namespaces: List[str],
) -> Generator[TemplatecoPlugin, None, None]:
    """
    Return a list of compatible Templateco plugins.

    :param namespaces: List of Templateco plugin namespaces to accept.
    :return Iterable containing Templateco plugins.
    """
    logger.debug("Getting list of Python distributions.")

    installed_distributions: Iterable[Distribution] = distributions()  # type: ignore

    for distribution in installed_distributions:
        if "-" in distribution.name:
            split_package = distribution.name.split("-")
            if split_package[0] in namespaces and distribution.name[-6:] == "plugin":
                logger.debug(f"[{distribution.name}] Found potential plugin.")
                try:
                    yield _import_templateco_plugin(distribution.name)
                    logger.debug(f"[{distribution.name}] Successfully loaded plugin.")
                except IncompatiblePluginException:
                    logger.debug(f"[{distribution.name}] Plugin incompatible.")
