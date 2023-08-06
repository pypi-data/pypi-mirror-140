import os
from pathlib import Path

from .get_address import get_address
from .create_common_stylesheet import create_common_stylesheet


def start_notebook(theme_select='bright', notebook_dir=None):
    """
    A jupyter notebook server at the folder 'notebook_dir' with one of the
    embedded themes (controllable with 'theme_select') gets started.
    """

    pkg_root = Path(os.path.dirname(__file__))
    if not notebook_dir:
        notebook_dir = os.path.expanduser('~')

    custom_style_dir = get_address(theme_select)
    common_dir = pkg_root / 'themes' / 'common'
    create_common_stylesheet(common_dir,
                             custom_style_dir / 'custom')
    os.environ["JUPYTER_CONFIG_DIR"] = str(custom_style_dir)
    os.system('jupyter notebook --notebook-dir="' + notebook_dir + '"')
