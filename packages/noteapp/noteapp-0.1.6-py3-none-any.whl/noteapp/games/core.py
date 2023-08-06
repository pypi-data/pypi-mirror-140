from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager

from .game2048 import Game2048


class GameList(Screen):
    """the menu screen"""

    def __init__(self, **kwargs):
        super(GameList, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        title = Label(text='GameList', font_size=48)

        self.layout.add_widget(title)
        self.layout.add_widget(Button(text='2048', on_press=self.start_game('2048-1'), font_size=48))
        self.layout.add_widget(Button(text='2048', on_press=self.start_game('2048-2'), font_size=48))
        self.add_widget(self.layout)

    def start_game(self, name):
        def on_press(instance):
            """slide to game screen and start game"""
            self.manager.transition.direction = 'left'
            self.manager.current = name

        return on_press


class GameManage(ScreenManager):
    def __init__(self, *args, **kwargs):
        super(GameManage, self).__init__(**kwargs)
        self.add_widget(GameList(name='menu'))
        self.add_widget(Game2048(name='2048-1'))
        self.add_widget(Game2048(name='2048-2'))
        self.current = 'menu'


class GameManageScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(GameManageScreen, self).__init__(**kwargs)
        self.add_widget(GameManage(size=Window.size))
