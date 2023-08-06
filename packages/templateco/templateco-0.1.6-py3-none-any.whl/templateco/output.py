import logging
from pathlib import Path
from typing import List

from jinja2 import StrictUndefined, Template

from templateco.typing import Answers

logger = logging.getLogger(__name__)


def _template_file(
    input_file: Path,
    template_directory: Path,
    output_directory: Path,
    answers: Answers,
) -> None:
    """
    Take an input file, and generate a fully templated output file to the filesystem.
    """
    relative_path = input_file.relative_to(template_directory)

    logger.debug(f"[{relative_path}] Iterating over file.")
    stripped_path = str(relative_path).rstrip(".jinja2")

    rendered_path = (
        Template(stripped_path, undefined=StrictUndefined).render(**answers).split(";")
    )
    logger.debug(f"[{relative_path}] Rendered path: {rendered_path}")

    for templated_path in rendered_path:
        if len(templated_path) > 0:
            output_path = output_directory / Path(templated_path.lstrip("/"))
            logger.debug(f"[{relative_path}] Output name: [{output_path}].")

            # Make the parent directory if it doesn't exist.
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Additional metadata to add as _metadata.
            metadata = {"_file_name": templated_path.lstrip("/")}

            with open(input_file.absolute(), "r") as file:
                logger.debug(f"[{relative_path}] Outputting templated file.")
                Template(file.read(), undefined=StrictUndefined).stream(
                    {**answers, "_metadata": metadata}
                ).dump(str(output_path))


def generate_output(
    input_directory: Path,
    output_directory: Path,
    folders_to_template: List[str],
    answers: Answers,
) -> None:
    """
    Output a templated folder structure.

    :param input_directory: Path to input folder structure.
    :param output_directory: Path to output templated files to.
    :param folders_to_template: List of template folders.
    :param answers: Dictionary of data.
    :return None.
    """
    files_to_template = (
        (input_file, input_directory / folder)
        for folder in folders_to_template
        for input_file in (input_directory / folder).rglob("*.jinja2")
    )

    # Iterate over the files to template, and generate them.
    for (input_file, template_directory) in files_to_template:
        _template_file(input_file, template_directory, output_directory, answers)
