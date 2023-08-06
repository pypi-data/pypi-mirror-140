from kivy.uix.widget import Widget


def widget_wrap(widget: Widget, *args) -> Widget:
    for arg in args:
        widget.add_widget(arg)
        
    return widget
