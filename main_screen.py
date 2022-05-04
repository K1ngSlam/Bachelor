import fnmatch
import os
from datetime import datetime
from logging import Logger

import yaml
from kivy.app import App
from kivy.properties import StringProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.treeview import TreeView, TreeViewNode
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen
from mdutils import MdUtils


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
        # Sollte nur beim ersten mal die TreeViews populaten oder vorher immer alles löschen?
        if not self.first_entered:
            self.first_entered = True
            self.yaml_list = fnmatch.filter(os.listdir(str(App.get_running_app().directory_path)), '*.yaml')
            for file_name in self.yaml_list:
                self.sortout_md_type(file_name)

            if len(self.tv_list) != 0:
                for tv in self.tv_list:
                    self.populate_tree_view(tv)
            self.populate_nodes()

    def sortout_md_type(self, file_name):
        app = App.get_running_app()
        content = app.read_yaml_file(file_name)
        if "type" in content:
            if content.get("type") == "directory":
                tv = TreeView(root_options=dict(text=content.get("title")))
                self.tv_list.append(tv)
            if content.get("type") == "project":
                self.project_list.append(file_name)
            if content.get("type") == "node":
                tvb = TreeViewButton(timestamp=file_name.rstrip(".yaml"), text=str(content.get("title")),
                                   on_press=self.write_text_to_codeinput, size_hint=(1, 0.15))
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

    def populate_tree_view(self,tree_view):
        app = App.get_running_app()
        for node in self.node_list.copy():
            content = app.read_yaml_file(node.timestamp + ".yaml")
            if "directory" in content:
                if content.get("directory") == tree_view.root.text:
                    tree_view.add_node(node)
                    self.node_list.remove(node)
        self.ids.tree_views.add_widget(tree_view)

    def populate_nodes(self):
        app = App.get_running_app()
        for node in self.node_list.copy():
            content = app.read_yaml_file(node.timestamp + ".yaml")
            if not ("directory" in content):
                self.ids.tree_views.add_widget(node)



    def write_text_to_codeinput(self, instance):
        self.focused_md_file = instance.timestamp
        text = App.get_running_app().read_md_file(instance.timestamp)
        self.ids.box_for_codeinput.text = text

    def on_focus(self, instance, value):  # Keyboard_on_key_down textinput zum speichern
        if not value and self.focused_md_file != "":
            App.get_running_app().save_to_md_file(self.focused_md_file, instance.text)


class TreeViewButton(MDFlatButton, TreeViewNode):
    timestamp = StringProperty("")


# class TreeViewOneLineListItem(OneLineListItem, TreeViewNode):
#    pass
