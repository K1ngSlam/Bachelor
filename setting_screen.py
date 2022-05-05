
from kivy.app import App
from kivymd.uix.screen import MDScreen


class SettingScreen(MDScreen):

    def change_md_directory_path(self):
        App.get_running_app().directory_path = self.ids.set_md_directory.text
        print(App.get_running_app().directory_path)
