# %% ../../nbs/Utils.ipynb 1
import os
from typing import *
from urllib.parse import urlparse
from contextlib import contextmanager
from pathlib import Path

import nbdev
from configparser import ConfigParser

# %% ../../nbs/Utils.ipynb 3
@contextmanager
def set_cwd(cwd_path: Union[Path, str]):

    cwd_path = Path(cwd_path)
    original_cwd = os.getcwd()
    os.chdir(cwd_path)

    try:
        nbdev.config.get_config.cache_clear()
        yield
    finally:
        os.chdir(original_cwd)

# %% ../../nbs/Utils.ipynb 5
def get_value_from_config(root_path: str, config_name: str) -> str:
    """Get the value from settings.ini file"""

    settings_path = Path(root_path) / "settings.ini"
    config = ConfigParser()
    config.read(settings_path)
    if not config.has_option("DEFAULT", config_name):
        return ""
    return config["DEFAULT"][config_name]

# %% ../../nbs/Utils.ipynb 7
def is_local_path(path):
    # Check if the path is an absolute path
    if os.path.isabs(path):
        return True

    # Check if the path is a URL with a scheme (e.g. http, https, ftp)
    parsed_url = urlparse(path)
    if parsed_url.scheme:
        return False

    # If the path is not an absolute path and does not have a URL scheme,
    # it is assumed to be a local path
    return True

# %% ../../nbs/Utils.ipynb 9
def add_counter_suffix_to_filename(src_path: Path):
    """Add a counter suffix to the given file
    Args:
        src_path: The path to the file to rename.
    """
    parent_dir = src_path.parent
    counter_suffix = (
        max(
            [
                int(f.stem.split(".")[1])
                for f in parent_dir.glob(f"{src_path.stem}.*.*")
            ],
            default=0,
        )
        + 1
    )
    dst_path = parent_dir / f"{src_path.stem}.{counter_suffix}{src_path.suffix}"
    os.rename(src_path, dst_path)
