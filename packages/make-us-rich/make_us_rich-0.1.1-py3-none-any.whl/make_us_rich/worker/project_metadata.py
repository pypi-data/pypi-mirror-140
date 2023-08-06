"""
This module provides metadata for a Kedro project.

It was developed by Kedro team, but I modified it to make it work with my project.
Here is the original file: https://github.com/kedro-org/kedro/blob/main/kedro/framework/startup.py
"""
import os
import sys
from pathlib import Path, PosixPath
from typing import NamedTuple, Union

import anyconfig

from kedro import __version__ as kedro_version
from kedro.framework.project import configure_project

_PYPROJECT = "kedro_config.toml"


class ProjectMetadata(NamedTuple):
    """Structure holding project metadata derived from `pyproject.toml`"""

    config_file: Path
    package_name: str
    project_name: str
    project_path: Path
    project_version: str
    source_dir: Path


def _version_mismatch_error(project_version) -> str:
    return (
        f"Your Kedro project version {project_version} does not match Kedro package "
        f"version {kedro_version} you are running. Make sure to update your project "
        f"template. See https://github.com/kedro-org/kedro/blob/main/RELEASE.md "
        f"for how to migrate your Kedro project."
    )


def _get_project_metadata(project_path: Union[str, Path]) -> ProjectMetadata:
    """Read project metadata from `<project_path>/pyproject.toml` config file,
    under the `[tool.kedro]` section.
    Args:
        project_path: Local path to project root directory to look up `pyproject.toml` in.
    Raises:
        RuntimeError: `pyproject.toml` was not found or the `[tool.kedro]` section
            is missing, or config file cannot be parsed.
        ValueError: If project version is different from Kedro package version.
            Note: Project version is the Kedro version the project was generated with.
    Returns:
        A named tuple that contains project metadata.
    """
    project_path = Path(project_path).expanduser().resolve()
    pyproject_toml = project_path / _PYPROJECT

    if not pyproject_toml.is_file():
        raise RuntimeError(
            f"Could not find the project configuration file '{_PYPROJECT}' in {project_path}. "
            f"If you have created your project with Kedro "
            f"version <0.17.0, make sure to update your project template. "
            f"See https://github.com/kedro-org/kedro/blob/main/RELEASE.md"
            f"#migration-guide-from-kedro-016-to-kedro-0170 "
            f"for how to migrate your Kedro project."
        )

    try:
        metadata_dict = anyconfig.load(pyproject_toml)
    except Exception as exc:
        raise RuntimeError(f"Failed to parse '{_PYPROJECT}' file.") from exc

    try:
        metadata_dict = metadata_dict["tool"]["kedro"]
    except KeyError as exc:
        raise RuntimeError(
            f"There's no '[tool.kedro]' section in the '{_PYPROJECT}'. "
            f"Please add '[tool.kedro]' section to the file with appropriate "
            f"configuration parameters."
        ) from exc

    mandatory_keys = ["package_name", "project_name", "project_version"]
    missing_keys = [key for key in mandatory_keys if key not in metadata_dict]
    if missing_keys:
        raise RuntimeError(f"Missing required keys {missing_keys} from '{_PYPROJECT}'.")

    # check the match for major and minor version (skip patch version)
    if metadata_dict["project_version"].split(".")[:2] != kedro_version.split(".")[:2]:
        raise ValueError(_version_mismatch_error(metadata_dict["project_version"]))

    source_dir = Path(metadata_dict.get("source_dir")).expanduser()
    source_dir = (project_path / source_dir).resolve()
    metadata_dict["source_dir"] = source_dir
    metadata_dict["config_file"] = pyproject_toml
    metadata_dict["project_path"] = project_path
    metadata_dict.pop("pipeline", {})  # don't include micro-packaging specs

    try:
        return ProjectMetadata(**metadata_dict)
    except TypeError as exc:
        expected_keys = mandatory_keys + ["source_dir"]
        raise RuntimeError(
            f"Found unexpected keys in '{_PYPROJECT}'. Make sure "
            f"it only contains the following keys: {expected_keys}."
        ) from exc


def bootstrap_project(project_path: Path) -> ProjectMetadata:
    """Run setup required at the beginning of the workflow
    when running in project mode, and return project metadata.
    """
    metadata = _get_project_metadata(project_path)
    configure_project(metadata.package_name)
    return metadata


def get_kedro_project_metadata() -> ProjectMetadata:
    """
    Get the metadata of a Kedro project. Wrapper around `bootstrap_project` for mkrich package.
    
    Returns
    -------
    dict
        Metadata of the Kedro project.
    """
    project_path = Path(__file__).parents[1]
    metadata = bootstrap_project(project_path)
    return metadata
