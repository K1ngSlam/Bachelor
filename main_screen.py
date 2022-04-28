import fnmatch
import os
from datetime import datetime
from logging import Logger
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

    def on_pre_enter(self, *args):  #Sollte nur beim ersten mal die TreeViews populaten oder vorher immer alles löschen?
        app = App.get_running_app()
        self.yaml_list = fnmatch.filter(os.listdir(str(App.get_running_app().directory_path)), '*.yaml')
        for file_name in self.yaml_list:
            content = app.read_yaml_file(file_name)
            if "type" in content:
                if content.get("type") == "directory":
                    self.tv_list.append(TreeView(root_options=dict(text=content.get("title"))))
                if content.get("type") == "project":
                    self.project_list.append(file_name)
                if content.get("type") == "node":
                    self.node_list.append(TreeViewButton(timestamp= file_name.rstrip(".yaml"), text=content.get("title"), on_press=self.write_text_to_codeinput,size_hint=(1, 0.01)))

        if len(self.tv_list) != 0:
            for tv in self.tv_list:
                self.ids.tree_views.add_widget(tv)
                self.populate_tree_view(tv)

    def create_markdown(self):
        now = datetime.now()
        mdFile = MdUtils(file_name=str(now), title='Markdown File Example')
        mdFile.create_md_file()
        self.create_yaml(now)
        self.add_button_widget(now)

    def create_yaml(self, markdown_timestamp):
        yamlName = str(markdown_timestamp) + '.yaml'
        print("Yaml name:", yamlName)
        open(os.path.join(App.get_running_app().directory_path, yamlName), 'x')

    def add_button_widget(self, markdown_timestamp):
        tvb = TreeViewButton(timestamp=str(markdown_timestamp), size_hint=(1, 0.1), text=str(markdown_timestamp))
        tvb.bind(on_press=self.write_text_to_codeinput)
        self.ids.tree_views.add_widget(tvb)

    def update_tree_view(
            self):
        pass

    def populate_tree_view(self, tree_view):
        app = App.get_running_app()
        for node in self.node_list:# Alle nodes in dem Tree danach abfrage ob node Notiz oder nochmal directory ist
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
