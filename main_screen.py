import fnmatch
import os
from datetime import datetime
from logging import Logger
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.treeview import TreeView, TreeViewNode
from mdutils import MdUtils


class MainScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.tv_list = []

    def on_pre_enter(self, *args):
        # TODO suche in den Yaml datein nach den root directorys/Namen um trees zu erstellen
        # self.tv_list.append(TreeView(root_options=dict(text="Hausaufgaben")))
        self.tv_list.append(TreeView(root_options=dict(text="Hauarbeiten")))
        for x in range(len(self.tv_list)):
            self.ids.tree_views.add_widget(self.tv_list[x])
            self.populate_tree_view(self.tv_list[x])

    def create_markdown(self):
        print("Main Window: Button clicked")
        now = datetime.now()
        mdFile = MdUtils(file_name=str(now), title='Markdown File Example')
        mdFile.create_md_file()
        self.create_yaml(now)
        self.add_button_widget(now)
        print(len(fnmatch.filter(os.listdir(str(App.get_running_app().directory_path)), '*.yaml')))

    def create_yaml(self, markdown_timestamp):
        yamlName = str(markdown_timestamp) + '.yaml'
        print("Yaml name:", yamlName)
        open(yamlName, 'x')

    def add_button_widget(self, markdown_timestamp):
        self.ids.tree_views.add_widget(TreeViewButton(text=markdown_timestamp))

    def update_tree_view(self): #TODO
        pass

    def populate_tree_view(self, tree_view):
        app = App.get_running_app()
        yaml_files = fnmatch.filter(os.listdir(str(app.directory_path)), '*.yaml')
        for x in range(len(yaml_files)):# Alle nodes in dem Tree danach abfrage ob node Notiz oder nochmal directory ist
            tree_view.add_node(TreeViewButton(text = yaml_files[x].title(), size_hint= (1,0.01)))# self.write_text_to_codeinput(app.read_md_file(yaml_files[x]))))

    def write_text_to_codeinput(self, text):
        self.ids.box_for_codeinput.text = text


class TreeViewButton(Button, TreeViewNode):
    pass

# class TreeViewOneLineListItem(OneLineListItem, TreeViewNode):
#    pass
