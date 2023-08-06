import os
from pathlib import Path


def get_address(theme=None):
    """
    Lists all embedded themes, checks if requested 'theme' exists and returns
    the path of the respective theme.
    If no 'theme' is forwarded, the path to the custom theme is returned.
    """

    # list available themes in 'themes_avail'
    pkg_root = Path(os.path.dirname(__file__))
    theme_path = Path("themes")
    themes_avail = [folder_name for folder_name in os.listdir(pkg_root / theme_path)
                    if os.path.isdir(os.path.join(pkg_root / theme_path, folder_name))]
    if "common" in themes_avail:
        themes_avail.remove("common")

    # check if 'theme' exists in 'themes_avail'
    if theme is not None:
        assert (theme in themes_avail), "The theme does not exist."
    else:
        theme = "default"

    return pkg_root / theme_path / Path(theme)
