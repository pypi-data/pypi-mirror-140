from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from typing_extensions import Protocol, runtime_checkable

# Type Aliases.
Config = Dict[str, Any]
Answers = Dict[str, Any]
Questions = Iterable[Mapping[str, Any]]
Plugins = Tuple[str, ...]


@runtime_checkable
class GetQuestions(Protocol):
    """
    The get_questions typing definition.
    """

    def __call__(
        self,
        *,
        language: str,
        folder: str,
        config: Config,
        plugins: Plugins,
    ) -> Questions:
        """
        Return a Questionary dictionary-type iterable.

        :param language: Name of the requested language.
        :param folder: Name of the top-level folder.
        :param config: Extra configuration passed to Templateco.
        :param plugins: Tuple containing all of the plugins selected.
        :return Dictionary of answers from the questionnaire.
        """
        pass


@runtime_checkable
class FoldersToTemplate(Protocol):
    """
    The folders_to_template typing definition.
    """

    def __call__(
        self,
        *,
        language: str,
        folder: str,
        config: Config,
        answers: Answers,
        plugins: Plugins,
    ) -> List[str]:
        """
        Take all input and returns a list of folders within the plugin.

        These folders are used to specify which should be templated, and intended to
        support optional configuration.

        :param language: Name of the requested language.
        :param folder: Name of the top-level folder.
        :param config: Extra configuration passed to Templateco.
        :param answers: Dictionary of answers from the questionnaire.
        :param plugins: Tuple containing all of the plugins selected.
        :return List of folders to template.
        """
        pass


@runtime_checkable
class PreTemplateHook(Protocol):
    """
    The pre_template_hook typing definition.
    """

    def __call__(
        self,
        *,
        language: str,
        folder: str,
        config: Config,
        answers: Answers,
        plugins: Plugins,
    ) -> None:
        """
        Run before a plugin creates a language.

        This optional function is intended to be used to modify the data dictionary
        that's passed to Jinja2 for the templating.

        :param language: Name of the requested template.
        :param folder: Name of the top-level folder.
        :param config: Extra configuration passed to Templateco.
        :param answers: Dictionary of answers from the questionnaire.
        :param plugins: Tuple containing all of the plugins selected.
        :return Nothing.
        """
        pass


@runtime_checkable
class PostTemplateHook(Protocol):
    """
    The post_template_hook typing definition.
    """

    def __call__(
        self,
        *,
        language: str,
        folder: str,
        output_folder: Path,
        config: Config,
        answers: Answers,
        plugins: Plugins,
    ) -> None:
        """
        Run after a plugin has successfully templated.

        This optional function is intended to be used to run steps after the templating
        has been run, and passes in the path to the final directory. This can be used
        to run CLI commands, or alter the folder data if wished.

        :param language: Name of the requested language.
        :param folder: Name of the top-level folder.
        :param output_folder: Path to the generated folder.
        :param config: Extra configuration passed to Templateco.
        :param answers: Dictionary of answers from the questionnaire.
        :param plugins: Tuple containing all of the plugins selected.
        :return Nothing.
        """
        pass


def get_questions_decorator(func: GetQuestions) -> GetQuestions:
    """
    Decorate the get_questions plugin function for type checking.
    """
    return func


def folders_to_template_decorator(func: FoldersToTemplate) -> FoldersToTemplate:
    """
    Decorate the folders_to_template plugin function for type checking.
    """
    return func


def pre_template_hook_decorator(func: PreTemplateHook) -> PreTemplateHook:
    """
    Decorate the pre_template_hook plugin function for type checking.
    """
    return func


def post_template_hook_decorator(func: PostTemplateHook) -> PostTemplateHook:
    """
    Decorate the post_template_hook plugin function for type checking.
    """
    return func
