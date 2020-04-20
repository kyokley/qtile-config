import functools
from libqtile import hook, widget


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
