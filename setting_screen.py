from kivy.app import App
from kivymd.material_resources import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar


class SettingScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu = None
        self.update_menu()

    def update_menu(self):
        app = App.get_running_app()
        recent_count = app.config.getint("recent", "count")
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": app.config.get("recent", str(i)),
                "height": dp(56),
                "on_release": lambda x=app.config.get(
                    "recent", str(i)
                ): self.menu_callback(x),
            }
            for i in range(1, recent_count + 1)
        ]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=12)

    def on_pre_enter(self, *args):
        self.ids.set_md_directory.text = App.get_running_app().directory_path

    def menu_callback(self, path):
        app = App.get_running_app()
        self.menu.dismiss()
        self.ids.set_md_directory.text = str(path)
        recent_count = app.config.getint("recent", "count")
        for i in range(1, recent_count + 1):  # find new dir path in the recent dict
            if path == app.config.get("recent", str(i)):
                self.change_to_path_from_history(str(path), str(i))

    def callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def set_cur_and_working_dir_path(self, new_dir_path):
        app = App.get_running_app()
        app.directory_path = new_dir_path
        app.config["workingdirectory"]["current"] = new_dir_path
        app.config.write()

    def change_to_path_from_history(self, new_dir_path, number):
        app = App.get_running_app()
        new_dir_path = app.config["recent"][number]
        app.config["recent"][number] = app.directory_path
        app.config["workingdirectory"]["current"] = new_dir_path
        app.directory_path = new_dir_path

        app.config.write()
        self.update_menu()

        Snackbar(text="[color=#ddbb34]" + new_dir_path + "[/color]").open()

    def change_directory_path(self):
        app = App.get_running_app()
        new_dir_path = self.ids.set_md_directory.text
        max_value = app.config.getint("recent", "maxvalue")
        recent_count = app.config.getint("recent", "count")
        if new_dir_path == app.directory_path:
            return
        for i in range(1, recent_count + 1):  # find new dir path in the recent dict
            if new_dir_path == app.config.get("recent", str(i)):
                self.change_to_path_from_history(new_dir_path, str(i))
                return
        if recent_count + 1 <= max_value:
            app.config["recent"][str(recent_count + 1)] = app.directory_path
            app.directory_path = new_dir_path
            app.config["workingdirectory"]["current"] = new_dir_path
            app.config["recent"]["count"] = str(recent_count + 1)
            app.config.write()
            self.update_menu()
        else:
            for i in range(1, recent_count):
                app.config["recent"][str(i)] = app.config["recent"][str(i + 1)]
            app.config["recent"][str(max_value)] = app.directory_path
            self.set_cur_and_working_dir_path(new_dir_path)
            self.update_menu()
