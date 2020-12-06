from jinja2 import Template
from pathlib import Path
from libqtile.command_client import CommandClient


MINIMUM_WIDTH = 500
NUMBER_OF_BARS = 2
qtile_client = CommandClient()
template_path = Path('~/.config/picom/picom.conf.template').expanduser()
output_path = Path("~/.config/picom/picom.conf").expanduser()

EDIT_WARNING_MESSAGE = f'''
# THIS FILE WILL BE OVERWRITTEN. FOR PERSISTENT CHANGES, MODIFY {str(template_path)} INSTEAD.
'''


def load_template():
    with open(template_path, 'r') as f:
        file_data = f.read()
    return Template(file_data)


def bar_ids():
    internal_windows = qtile_client.call('internal_windows')()
    internal_windows.sort(key=lambda val: val['y'])

    ids = [window['id'] for window in internal_windows
           if window['width'] > MINIMUM_WIDTH]
    if len(ids) != NUMBER_OF_BARS:
        raise Exception(f'Expected to find {NUMBER_OF_BARS} but got {len(ids)} instead.')
    return {'top_bar_id': hex(ids[0]),
            'bottom_bar_id': hex(ids[1])}


def write(output_str):
    output_str = '{}\n\n{}'.format(EDIT_WARNING_MESSAGE,
                                   output_str)
    with open(output_path, 'w') as f:
        f.write(output_str)


def run():
    ids = bar_ids()
    template = load_template()

    rendered = template.render(**ids)
    write(rendered)


if __name__ == '__main__':
    run()
