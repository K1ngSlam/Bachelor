
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
import yaml

class NoteApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.directory_path = StringProperty()
        self.directory_path = "/home/ubuntu/PycharmProjects/Bachelor"

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        self.sm.add_widget(Builder.load_file(os.path.join(self.directory, "main_screen.kv")))
        self.sm.add_widget(Builder.load_file(os.path.join(self.directory, "setting_screen.kv")))
        self.sm.current = "MainScreen"
        return self.sm

    def read_md_file(self,md_file_name):
        if str(md_file_name).endswith(".md"):
            with open(os.path.join(self.directory_path, md_file_name)) as file:
                content = file.read()
            return content
        else:
            with open(os.path.join(self.directory_path, md_file_name + ".md")) as file:
                content = file.read()
            return content

    def save_to_md_file(self, md_file_name,text):
        if str(md_file_name).endswith(".md"):
            with open(os.path.join(self.directory_path, str(md_file_name)), "w") as file:
                file.write(text)
        else:
            with open(os.path.join(self.directory_path, str(md_file_name) + ".md"), "w") as file:
                file.write(text)

    def read_yaml_file(self, file_name):
        if str(file_name).endswith(".yaml"):
            with open(os.path.join(self.directory_path, str(file_name)), "r") as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        else:
            with open(os.path.join(self.directory_path, str(file_name) + ".yaml"), "r") as file:
                return yaml.load(file, Loader=yaml.Loader)

    def switch_to_screen(self, screen_number, direction = "left"):
        self.sm.transition.direction = direction
        self.sm.current = self.sm.screens[screen_number].name

NoteApp().run()
