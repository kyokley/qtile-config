import functools
from libqtile import hook, widget, layout
from custom.default import extension_defaults


class ScreenLayout(widget.CurrentLayout):
    def setup_hooks(self):
        def hook_layout_change(layout, group):
            self.text = layout.name
            self.bar.draw()
        hook.subscribe.layout_change(hook_layout_change)

        hook_screen_change = functools.partial(
                hook_layout_change,
                layout=None,
                group=None)
        hook.subscribe.current_screen_change(hook_screen_change)


LAYOUTS = [
    layout.MonadTall(name='GapsTall',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     margin=extension_defaults.layout_margin,
                     border_normal=extension_defaults.border_normal,
                     border_focus=extension_defaults.border_focus,
                     ),
    layout.MonadWide(name='GapsWide',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     margin=extension_defaults.layout_margin,
                     border_normal=extension_defaults.border_normal,
                     border_focus=extension_defaults.border_focus,
                     ),
    layout.TreeTab(name='Max'),
    layout.MonadTall(name='Tall',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     border_normal=extension_defaults.border_normal,
                     border_focus=extension_defaults.border_focus,
                     ),
    layout.MonadWide(name='Wide',
                     new_at_current=True,
                     border_width=6,
                     single_border_width=2,
                     border_normal=extension_defaults.border_normal,
                     border_focus=extension_defaults.border_focus,
                     ),
]
