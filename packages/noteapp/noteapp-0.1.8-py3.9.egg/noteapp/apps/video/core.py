from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout

Window.size = (310, 600)


class VideoScroll(ScrollView):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'size_hint': kwargs.get('size_hint', (1, 0.8)),
            'pos_hint': kwargs.get('pos_hint', {'center_x': 0.5, 'top': 1}),
        })
        super(VideoScroll, self).__init__(**kwargs)
        self.inside = GridLayout(pos_hint={'center_x': 0.5, 'top': 1}, cols=1, size_hint_y=None, spacing=10)
        self.inside.bind(minimum_height=self.inside.setter('height'))
        self.button_on_press(num=10)
        self.add_widget(self.inside)

    def button_on_press(self, instance=None, num=1):
        for i in range(num):
            self.inside.add_widget(Button(text=f'something{len(self.inside.children)}',
                                          size_hint_y=None, height=40,
                                          on_press=self.button_on_press))


class VideoLayout(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        kwargs.update({'size_hint': kwargs.get('size_hint', (None, None)), })
        super(VideoLayout, self).__init__(orientation='vertical', **kwargs)
        # name = f'{self.name}-t',
        self.add_widget(Button(text="Video", size_hint_y=None, height=40, size_hint=(1, 0.05)))
        # name=f'{self.name}-scroll',
        self.add_widget(VideoScroll(size_hint=(1, 0.9)))


class VideoScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(VideoScreen, self).__init__(**kwargs)
        self.add_widget(VideoLayout(size=Window.size))
