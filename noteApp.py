import fnmatch
import os
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen


class NoteApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.directory_path = StringProperty()
        self.directory_path = "/home/ubuntu/PycharmProjects/Bachelor"

    def build(self):
        self.sm.add_widget(Builder.load_file(os.path.join(self.directory, "main_screen.kv")))
        self.sm.add_widget(Builder.load_file(os.path.join(self.directory, "setting_screen.kv")))
        self.sm.current = "MainScreen"
        return self.sm

    def read_md_file(self,md_file_name):
        with open(os.path.join(self.directory_path, md_file_name)) as file:
            content = file.read()
        return content

NoteApp().run()
