from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label

Builder.load_string('''
<SimpleLabel>:
    text: 'Hello World'
''')


class SimpleLabel(Label):
    pass


class SampleApp(App):
    def build(self):
        return SimpleLabel()
