import logging
from pathlib import Path
from typing import List, Tuple

from colorama import Fore, Style, init
from questionary import Choice, checkbox, unsafe_prompt

from templateco.exceptions import NoPluginsFoundException, PluginOperationException
from templateco.output import generate_output
from templateco.plugin import TemplatecoPlugin, list_compatible_plugins
from templateco.typing import Config

logger = logging.getLogger(__name__)


def _execute_plugin(
    language: str,
    folder: Path,
    plugin: TemplatecoPlugin,
    config: Config,
    plugins: Tuple[str, ...],
) -> None:
    """
    Execute a single Templateco plugin.

    This function prompts for the plugin's questions, runs the hooks and generates
    the template files.

    :param language:
    :param folder: Folder to output to.
    :param plugin: Plugin to execute.
    :param config: Extra configuration passed to Templateco.
    :return None.
    """
    logger.debug(f"[{plugin.friendly_name}] Running plugin.")
    try:
        top_level_folder_name = folder.name
        logger.debug(f"[{plugin.friendly_name}] Prompting for interaction.")

        answers = unsafe_prompt(
            plugin.get_questions(
                language=language,
                folder=top_level_folder_name,
                config=config,
                plugins=plugins,
            )
        )

        if plugin.pre_template_hook:
            logger.debug(f"[{plugin.friendly_name}] Running pre-template hook.")
            plugin.pre_template_hook(
                language=language,
                folder=top_level_folder_name,
                config=config,
                answers=answers,
                plugins=plugins,
            )

        logger.debug(f"[{plugin.friendly_name}] Determining template from answers.")
        folders = plugin.folders_to_template(
            language=language,
            folder=top_level_folder_name,
            config=config,
            answers=answers,
            plugins=plugins,
        )

        logger.debug(f"[{plugin.friendly_name}] Templating folder structure.")
        generate_output(plugin.path_to_module, folder, folders, answers)
        logger.debug(f"[{plugin.friendly_name}] Successfully templated.")

        if plugin.post_template_hook:
            logger.debug(f"[{plugin.friendly_name}] Running post-template hook.")
            plugin.post_template_hook(
                language=language,
                folder=top_level_folder_name,
                output_folder=folder,
                config=config,
                answers=answers,
                plugins=plugins,
            )
    except PluginOperationException:
        logger.error(f"[{plugin.friendly_name}] Plugin raised an operation exception:")
        logger.debug(
            f"[{plugin.friendly_name}] These exceptions should be raised to the user."
        )
        raise
    except Exception as err:
        logger.error(f"[{plugin.friendly_name}] Plugin raised an unhandled exception.")
        logger.error(err)


def templateco(
    *,
    language: str,
    folder: Path,
    config: Config = {},
    namespaces: List[str] = ["templateco"],
) -> None:
    """
    Execute Templateco, and produce a templated folder.

    Supports only kwargs, so invoke with language="foo" rather than positional
    arguments.

    :param language: Name of template to load plugins for.
    :param folder: Folder to generate e.g. $(PWD)/output_folder.
    :param config: Extra configuration passed to Templateco.
    :param namespaces: List of Templateco plugin namespaces to accept.
    :return None.
    """
    # Initialise Colorama for terminal output.
    init(autoreset=True)
    print(
        Fore.GREEN
        + Style.BRIGHT
        + "[ Templateco ]"
        + Style.RESET_ALL
        + " - A Templating Ecosystem"
    )

    logger.debug("Instantiating Templateco.")

    # Get a complete list of all compatible Templateco plugins.
    plugins = [
        plugin
        for plugin in list_compatible_plugins(namespaces)
        if language in plugin.compatible_languages
    ]

    logger.debug(f"Found {len(plugins)} plugin(s).")

    if len(plugins) == 0:
        logger.debug("Query resulted in zero plugins, raising NoPlugins exception.")
        raise NoPluginsFoundException()
    elif len(plugins) > 1:
        logger.debug("Multiple plugins found, asking user for choices.")
        # Ask the user which plugins should be executed.
        plugins = checkbox(
            "Select plugins to use",
            choices=[
                Choice(
                    plugin.friendly_name,
                    checked=plugin.selected_by_default,
                    value=plugin,
                )
                for plugin in plugins
            ],
        ).unsafe_ask()

    name_of_plugins = tuple(plugin.package_name for plugin in plugins)

    for plugin in plugins:
        print("\nConfiguring " + Fore.GREEN + Style.BRIGHT + f"{plugin.friendly_name}")
        _execute_plugin(language, folder, plugin, config, name_of_plugins)

    print("\nSuccessfully templated " + Style.BRIGHT + Fore.GREEN + str(folder))
