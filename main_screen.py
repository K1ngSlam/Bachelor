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
                     *args):  # Sollte nur beim ersten mal die TreeViews populaten oder vorher immer alles löschen?
        if not self.first_entered:
            self.first_entered = True
            self.yaml_list = fnmatch.filter(os.listdir(str(App.get_running_app().directory_path)), '*.yaml')
            for file_name in self.yaml_list:
                self.sortout_md_type(file_name)

            if len(self.tv_list) != 0:
                for tv in self.tv_list:
                    self.ids.tree_views.add_widget(tv)
                    self.populate_tree_view(tv)

            if self.node_list != 0:
                app = App.get_running_app()
                for node in self.node_list:
                    content = app.read_yaml_file(node.timestamp)
                    if not ("directory" in content):
                        self.ids.tree_views.add_widget(node)

    def sortout_md_type(self, file_name):
        app = App.get_running_app()
        content = app.read_yaml_file(file_name)
        if "type" in content:
            if content.get("type") == "directory":
                self.tv_list.append(TreeView(root_options=dict(text=content.get("title"))))
            if content.get("type") == "project":
                self.project_list.append(file_name)
            if content.get("type") == "node":
                self.node_list.append(
                    TreeViewButton(timestamp=file_name.rstrip(".yaml"), text=str(content.get("title")),
                                   on_press=self.write_text_to_codeinput, size_hint=(1, 0.15)))

    def create_markdown(self):
        timestamp_now = datetime.now()
        mdFile = MdUtils(file_name=str(timestamp_now), title='Markdown File Example')
        mdFile.create_md_file()
        self.create_yaml(timestamp_now)
        self.sortout_md_type(timestamp_now)
        self.add_button_widget(timestamp_now)

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

    def add_button_widget(self, markdown_timestamp):
        tvb = TreeViewButton(timestamp=str(markdown_timestamp), size_hint=(1, 0.1), text=str(markdown_timestamp))
        tvb.bind(on_press=self.write_text_to_codeinput)
        self.ids.tree_views.add_widget(tvb)

    def update_tree_view(self):

        pass

    def populate_tree_view(self,
                           tree_view):  # zum Updaten Liste der bereits vorhandenen widges mit der Node_list vergleichen
        app = App.get_running_app()
        for node in self.node_list:
            content = app.read_yaml_file(node.timestamp + ".yaml")
            if content.get("directory") == tree_view.root.text:
                tree_view.add_node(node)

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
