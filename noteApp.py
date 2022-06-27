import os

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
import yaml


class NoteApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.directory_path = StringProperty("")
        self.focused_md_file = None

    def build_config(self, config):
        config.setdefaults(
            "workingdirectory",
            {
                "current": "/home/ubuntu/PycharmProjects/Bachelor/working_directory"
            }
        )
        config.setdefaults(
            "recent",
            {
                "count": 1,
                "maxvalue": 5
            }
        )

    def get_application_config(self, defaultpath='%(appdir)s/%(appname)s.ini'):

        return super().get_application_config(defaultpath)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        self.sm.add_widget(Builder.load_file(os.path.join(self.directory, "main_screen.kv")))
        self.sm.add_widget(Builder.load_file(os.path.join(self.directory, "setting_screen.kv")))
        self.sm.current = "MainScreen"

        self.config.write()

        self.directory_path = self.config.get("workingdirectory", "current")

        return self.sm

    def read_md_file(self, md_file_name, path):
        if str(md_file_name).endswith(".md"):
            with open(os.path.join(path, md_file_name)) as file:
                content = file.read()
            return content
        else:
            with open(os.path.join(path, md_file_name + ".md")) as file:
                content = file.read()
            return content

    def save_to_md_file(self, md_file_name, path, text):
        if str(md_file_name).endswith(".md"):
            with open(os.path.join(path, str(md_file_name)), "w") as file:
                file.write(text)
        else:
            with open(os.path.join(path, str(md_file_name) + ".md"), "w") as file:
                file.write(text)

    def read_yaml_file(self, file_name, path):
        if str(file_name).endswith(".yaml"):
            with open(os.path.join(path, str(file_name)), "r") as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        else:
            with open(os.path.join(path, str(file_name) + ".yaml"), "r") as file:
                return yaml.load(file, Loader=yaml.Loader)

    def save_to_yaml_file(self, file_name, path, data):
        if str(file_name).endswith(".yaml"):
            with open(os.path.join(path, str(file_name)), "w") as file:
                yaml.dump(data, file)
        else:
            with open(os.path.join(path, str(file_name) + ".yaml"), "w") as file:
                yaml.dump(data, file)

    def switch_to_screen(self, screen_number, direction="left"):
        self.sm.transition.direction = direction
        self.sm.current = self.sm.screens[screen_number].name


NoteApp().run()
