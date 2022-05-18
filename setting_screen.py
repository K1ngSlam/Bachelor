from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.material_resources import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar


class SettingScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        dirs_len = len(app.config["recent"])
        menu_items = [

            {
                "viewclass": "OneLineListItem",
                "text": app.config.get("recent", str(i+1)),
                "height": dp(56),
                "on_release": lambda x=app.config.get("recent", str(i+1), y=i+1): self.menu_callback(x,y),
            } for i in range(dirs_len)
        ]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=8
        )

    def on_pre_enter(self, *args):
        self.ids.set_md_directory.text = App.get_running_app().directory_path

    def menu_callback(self, text_item, number):
        app = App.get_running_app()
        self.menu.dismiss()
        self.ids.set_md_directory.text = text_item.text
        app.config["recent"][number] =
        Snackbar(text=text_item).open()

    def callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def change_md_directory_path(self):
        app = App.get_running_app()
        app.config["recent"][str(len(app.config["recent"])+ 1)] = app.directory_path
        app.directory_path = self.ids.set_md_directory.text
        app.config["workingdirectory"]["current"] = self.ids.set_md_directory.text
        app.config.write()
        print(app.config.get("workingdirectory", "current"))
        print(app.config.get("recent", "1"))
        print(App.get_running_app().directory_path)
