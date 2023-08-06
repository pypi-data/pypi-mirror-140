from noteapp.games.game2048.core import Game2048App


class NoteApp(Game2048App):
    def __init__(self, *args, **kwargs):
        super(NoteApp, self).__init__(**kwargs)


def main_screen():
    NoteApp().run()
