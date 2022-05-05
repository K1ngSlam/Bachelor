import fnmatch
import os
from datetime import datetime
from logging import Logger

import yaml
from kivy.app import App
from kivy.properties import StringProperty, ListProperty
from kivy.uix.treeview import TreeView, TreeViewNode
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen
from mdutils import MdUtils

from setting_screen import SettingScreen


class MainScreen(MDScreen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.tv_list = []
        self.node_list = []
        self.project_list = []
        self.yaml_list = ListProperty()
        self.focused_md_file = StringProperty("")
        self.first_entered = False

    def on_pre_enter(self,
                     *args):
        if not self.first_entered:
            self.first_entered = True
            self.refresh()

    def sortout_md_type(self, file_name):
        app = App.get_running_app()
        content = app.read_yaml_file(file_name)
        if "type" in content:
            if content.get("type") == "directory":
                tv = TreeView(root_options=dict(text=content.get("title")), timestamp=file_name.rstrip(".yaml"))
                if content.get("directory") is None:
                    self.tv_list.append(tv)
                else:  # Zum TreeView an TreeView adden
                    pass
                    self.tv_list.append(tv)
                    self.node_list.append(tv)
            if content.get("type") == "project":
                self.project_list.append(file_name)
            if content.get("type") == "node":
                tvb = TreeViewButton(timestamp=file_name.rstrip(".yaml"), text=str(content.get("title")),
                                     on_touch_down=self.on_pressed, size_hint=(1, 0.15))
                self.node_list.append(tvb)

    def create_markdown(self):
        self.ids.tree_views.clear_widgets()
        timestamp_now = datetime.now()
        mdFile = MdUtils(file_name=str(timestamp_now), title='Markdown File Example')
        mdFile.create_md_file()
        self.create_yaml(str(timestamp_now))
        self.sortout_md_type(str(timestamp_now))
        if len(self.tv_list) != 0:
            for tv in self.tv_list:
                self.populate_tree_view(tv)
        self.populate_nodes()

    def create_yaml(self, markdown_timestamp):
        yamlName = str(markdown_timestamp) + '.yaml'
        print("Yaml name:", yamlName)
        data = {
            "type": "node",
            "directory": "Hausaufgaben",
            "title": markdown_timestamp
        }
        file = open(os.path.join(App.get_running_app().directory_path, yamlName), 'w')
        yaml.dump(data, file)

    def populate_tree_view(self, tree_view):
        app = App.get_running_app()
        for node in self.node_list.copy():
            content = app.read_yaml_file(node.timestamp + ".yaml")
            if "directory" in content:
                if content.get("directory") == tree_view.root.text:
                    if content.get("type") == "directory":
                        tree_view.add_node(node, parent=tree_view)
                        self.node_list.remove(node)
                    else:
                        tree_view.add_node(node)
                        self.node_list.remove(node)
        self.ids.tree_views.add_widget(tree_view)

    def populate_nodes(self):
        app = App.get_running_app()
        for node in self.node_list.copy():
            content = app.read_yaml_file(node.timestamp + ".yaml")
            if not ("directory" in content):
                self.ids.tree_views.add_widget(node)

    def on_pressed(self, instance, touch):
        if touch.button == "right":
            self.delete_node(instance)
        else:
            self.write_text_to_codeinput(instance)

    def delete_node(self,instance):
        app = App.get_running_app()
        content = app.read_yaml_file(instance.timestamp)
        os.remove(os.path.join(app.directory_path, instance.timestamp + ".md"))
        os.remove(os.path.join(app.directory_path, instance.timestamp + ".yaml"))
        if "directory" in content:
            for tv in self.tv_list:
                if content.get("directory") == tv.root.text:
                    tv.remove_node(instance)
        else:
            self.ids.tree_views.remove_widget(instance)

    def write_text_to_codeinput(self,instance):
        self.focused_md_file = instance.timestamp
        text = App.get_running_app().read_md_file(instance.timestamp)
        self.ids.box_for_codeinput.text = text

    def on_focus(self, instance, value):  # Keyboard_on_key_down textinput zum speichern
        if not value and self.focused_md_file != "":
            App.get_running_app().save_to_md_file(self.focused_md_file, instance.text)

    def refresh(self):
        self.node_list = []
        self.tv_list = []
        self.project_list = []
        self.ids.tree_views.clear_widgets()
        self.yaml_list = fnmatch.filter(os.listdir(str(App.get_running_app().directory_path)), '*.yaml')
        for file_name in self.yaml_list:
            self.sortout_md_type(file_name)

        if len(self.tv_list) != 0:
            for tv in self.tv_list:
                self.populate_tree_view(tv)
        self.populate_nodes()


class TreeViewButton(MDFlatButton, TreeViewNode):
    timestamp = StringProperty("")


class TreeView(TreeView, TreeViewNode):
    timestamp = StringProperty()
# class TreeViewOneLineListItem(OneLineListItem, TreeViewNode):
#    pass
