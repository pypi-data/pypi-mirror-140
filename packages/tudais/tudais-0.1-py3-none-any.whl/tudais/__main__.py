import os
from pathlib import Path
import tudthemes


def start_jupyter_server():
    pkg_root = Path(os.path.dirname(__file__))
    notebook_dir = str(pkg_root / Path('notebooks'))
    tudthemes.start_notebook(theme_select='bright', notebook_dir=notebook_dir)


if __name__ == '__main__':
    start_jupyter_server()
