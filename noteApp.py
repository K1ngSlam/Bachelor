
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp


class NoteApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.directory_path = StringProperty()
        self.directory_path = "/home/ubuntu/PycharmProjects/Bachelor"

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.sm.add_widget(Builder.load_file(os.path.join(self.directory, "main_screen.kv")))
        self.sm.add_widget(Builder.load_file(os.path.join(self.directory, "setting_screen.kv")))
        self.sm.current = "MainScreen"
        return self.sm

    def read_md_file(self,md_file_name):
        with open(os.path.join(self.directory_path, md_file_name + ".md")) as file:
            content = file.read()
        return content

    def save_to_md_file(self, md_file_name,text):
        with open(os.path.join(self.directory_path, str(md_file_name) + ".md"), "w") as file:
            file.write(text)

NoteApp().run()
