from pathlib import Path
import base64


def create_common_stylesheet(common_path, output_path):
    """
    The TU Dresden Logo in folder 'common_path' gets converted into a
    css string and saved in the respective custom folder 'output_path'.
    """
    with open(common_path / 'Logo_TU_Dresden.svg', 'rb') as svg:
        encoded_string = base64.b64encode(svg.read())
    stylesheet = '#ipython_notebook img{ display:block; ' \
                 'background: url("data:image/svg+xml;base64,' \
                 f'{encoded_string.decode("utf-8")}");' '}'
    with open(output_path / 'common.css', 'w') as f:
        print(stylesheet, file=f)
