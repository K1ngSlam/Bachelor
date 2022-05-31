import fnmatch
import os
from datetime import datetime
from logging import Logger

import yaml
from kivy.app import App
from kivy.properties import StringProperty, ListProperty
from kivy.uix.treeview import TreeView, TreeViewNode
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.screen import MDScreen
from mdutils import MdUtils

from setting_screen import SettingScreen


class MainScreen(MDScreen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.first_entered = False

    def on_pre_enter(self,
                     *args):
        self.refresh()

    def create_markdown(self):
        self.ids.tree_views.clear_widgets()
        timestamp_now = str(datetime.now())
        timestamp_now.replace(" ", "_")
        self.create_yaml(timestamp_now)
        open(os.path.join(App.get_running_app().directory_path, timestamp_now + ".md"), 'w')
        self.refresh()

    def create_yaml(self, markdown_timestamp):
        yamlName = markdown_timestamp + '.yaml'
        data = {
            "type": "node",
            "title": markdown_timestamp,
            "importance": 5

        }
        file = open(os.path.join(App.get_running_app().directory_path, yamlName), 'w')
        yaml.dump(data, file)

    def pick_importance_colour(self, content):
        importance = content.get("importance")
        if importance <= 0:
            return 0, 200, 83, 1
        if importance < 3:
            return 0, 250, 120, 1
        if 5 > importance >= 3:
            return 100, 0, 0, 1
        if importance >= 5:
            return 200, 0, 0, 1

    def populate_tree_view(self, tree_view, parent, path):
        app = App.get_running_app()
        for file in os.scandir(path):
            if file.is_file() and file.name.endswith(".yaml"):
                content = app.read_yaml_file(file.name, path)
                color = 255, 1, 1, 1
                if "importance" in content:
                    color = self.pick_importance_colour(content)
                if "type" in content:
                    if content.get("type") == "node":
                        timestamp = file.name.rstrip(".yaml")
                        if not ("title" in content):
                            title = file.name.rstrip(".yaml")
                        else:
                            title = content.get("title")
                        if parent is None:
                            button = TreeViewIconButton(line_color=color, icon="file",
                                                        icon_color=color, text=title, path=file.path.rstrip(file.name),
                                                        timestamp=timestamp, on_touch_down=self.on_pressed)
                            tree_view.add_node(
                                button)
                        else:
                            tree_view.add_node(
                                TreeViewIconButton(line_color=color, icon_color=color, icon="file", text=title,
                                                   path=file.path.rstrip(file.name), timestamp=timestamp,
                                                   on_touch_down=self.on_pressed), parent)
                    if content.get("type") == "project":
                        pass
            if file.is_dir():
                tree_node = tree_view.add_node(TreeViewButton(text=file.name))
                self.populate_tree_view(tree_view, tree_node, file.path)

    def on_pressed(self, instance, touch):
        if touch.button == "right":
            self.delete_node(instance)
        else:
            self.write_text_to_codeinput(instance)

    def delete_node(self, instance):
        os.remove(os.path.join(instance.path, instance.timestamp + ".md"))
        os.remove(os.path.join(instance.path, instance.timestamp + ".yaml"))
        self.refresh()

    def write_text_to_codeinput(self, instance):
        App.get_running_app().focused_md_file = instance
        text = App.get_running_app().read_md_file(instance.timestamp, instance.path)
        self.ids.box_for_codeinput.text = text

    def refresh(self):
        self.ids.tree_views.clear_widgets()
        app = App.get_running_app()
        tv = TreeView(hide_root=True)
        self.populate_tree_view(tv, None, app.config.get("workingdirectory", "current"))
        self.ids.tree_views.add_widget(tv)

    def get_code_input_text(self):
        return self.ids.box_for_codeinput.text


class TreeViewButton(MDFlatButton, TreeViewNode):
    app = App.get_running_app()
    timestamp = StringProperty("")
    path = StringProperty(app.directory_path)


class TreeViewIconButton(MDRectangleFlatIconButton, TreeViewNode):
    app = App.get_running_app()
    timestamp = StringProperty("")
    path = StringProperty(app.directory_path)
