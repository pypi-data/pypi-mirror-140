from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
#from noteapp.apps.video import VideoScreen
from noteapp.games import GameManageScreen
from noteapp.utils.widget import widget_wrap


class AppLayout(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        kwargs.update({'size_hint': kwargs.get('size_hint', (None, None)), })
        super(AppLayout, self).__init__(orientation='vertical', **kwargs)
        self.screen_manager = ScreenManager()

        # self.screen_manager.add_widget(VideoScreen(name='screen1'))
        self.screen_manager.add_widget(GameManageScreen(name='screen1'))
        self.screen_manager.add_widget(GameManageScreen(name='screen2'))
        self.screen_manager.add_widget(GameManageScreen(name='screen3'))

        self.add_widget(Button(text="Video", size_hint_y=None, height=40, size_hint=(1, 0.05)))
        self.add_widget(self.screen_manager)
        self.add_widget(widget_wrap(
            MDBoxLayout(orientation='horizontal', size_hint=(1, 0.05), pos_hint={'center_x': 0.5, 'button': 1}),

            Button(text="推荐", font_name='STHeiti Medium.ttc', on_press=self.change_screen('screen1')),
            Button(text="游戏", font_name='STHeiti Medium.ttc', on_press=self.change_screen('screen2')),
            Button(text="视频", font_name='STHeiti Medium.ttc', on_press=self.change_screen('screen3')),
            Button(text="我的", font_name='STHeiti Medium.ttc')))

    def change_screen(self, name):
        def on_press(instance=None):
            self.screen_manager.current = name

        return on_press


class MyApp(App):
    def __init__(self, *args, **kwargs):
        super(MyApp, self).__init__(**kwargs)


class NoteApp(App):
    def __init__(self, *args, **kwargs):
        super(NoteApp, self).__init__(**kwargs)

    def build(self):
        return AppLayout(size=Window.size)


def main_screen():
    NoteApp().run()
