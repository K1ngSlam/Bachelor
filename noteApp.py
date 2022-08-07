import os

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
import yaml
from kivymd.uix.label import MDLabel


class NoteApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.directory_path = StringProperty("")
        self.focused_md_file = None

    def build_config(self, config):
        config.setdefaults(
            "workingdirectory",
            {"current": os.getcwd()},
        )
        config.setdefaults("recent", {"count": 0, "maxvalue": 5}),

        config.setdefaults("directories", {"show_empty": False})

    def get_application_config(self, defaultpath="%(appdir)s/%(appname)s.ini"):

        return super().get_application_config(defaultpath)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        self.sm.add_widget(
            Builder.load_file(os.path.join(self.directory, "main_screen.kv"))
        )
        self.sm.add_widget(
            Builder.load_file(os.path.join(self.directory, "setting_screen.kv"))
        )
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
                return yaml.load(file, Loader=yaml.FullLoader)

    def save_to_yaml_file(self, file_name, path, data):
        if type(data) != dict:
            data = yaml.load(data, Loader=yaml.FullLoader)
        if str(file_name).endswith(".yaml"):
            with open(os.path.join(path, str(file_name)), "w") as file:
                yaml.dump(data, file)
        else:
            with open(os.path.join(path, str(file_name) + ".yaml"), "w") as file:
                yaml.dump(data, file)

    def switch_to_screen(self, screen_number, direction="left"):
        self.sm.transition.direction = direction
        self.sm.current = self.sm.screens[screen_number].name

    def invalid_file_error(self):
        Label = MDLabel(
            text="You have not selected a file to safe to or the file doesnt exist anymore!"
        )
        self.sm.get_screen("MainScreen").popup = Popup(
            title="Error Invalid File",
            content=Label,
            auto_dismiss=True,
            size_hint=(None, None),
            size=(400, 100),
        )
        self.sm.get_screen("MainScreen").popup.open()


NoteApp().run()
