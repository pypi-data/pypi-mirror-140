from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.screenmanager import FadeTransition, ScreenManager
from kivymd.app import MDApp
from kivymd.font_definitions import theme_font_styles
from noteapp.apps.tiktok.screen import Home

# os.environ['KIVY_VIDEO'] = 'ffpyplayer'
# os.environ['KIVY_VIDEO'] = 'ffmpeg'


class WindowManager(ScreenManager):
    pass


Window.size = (310, 600)


class TikTokApp(MDApp):
    def __init__(self, *args, **kwargs):
        super(TikTokApp, self).__init__(**kwargs)
        self.wm = WindowManager(transition=FadeTransition())
        self.theme_cls.theme_style = 'Dark'

    def build(self):
        LabelBase.register(name="TikTokIcons", fn_regular="TikTokIcons.ttf")
        theme_font_styles.append('TikTokIcons')
        self.theme_cls.font_styles["TikTokIcons"] = ["TikTokIcons", 16, False, 0.15]

        screens = [Home(name='home')]

        for screen in screens:
            self.wm.add_widget(screen)

        return self.wm
