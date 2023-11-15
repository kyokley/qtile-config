from collections import namedtuple

ExtensionDefault = namedtuple(
    'ExtensionDefault',
    ['font',
     'fontsize',
     'padding',
     'foreground',
     'background',
     'inactive_foreground',
     'border_focus',
     'border_normal',
     'layout_margin',
     'bar_margin',
     'bar_thickness',
     ])
extension_defaults = ExtensionDefault(
    font='sans',
    fontsize=18,
    padding=3,
    foreground='AE4CFF',
    background=None,
    inactive_foreground='404040',
    border_focus='FF0000',
    border_normal='030303',
    layout_margin=40,
    bar_margin=10,
    bar_thickness=40,
)
