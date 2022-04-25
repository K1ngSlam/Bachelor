import fnmatch
import os
from datetime import datetime
from logging import Logger
from kivy.app import App
from kivy.properties import StringProperty
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
        self.focused_md_file = StringProperty("")

    def on_pre_enter(self, *args):
        # TODO suche in den Yaml datein nach den root directorys/Namen um trees zu erstellen
        # self.tv_list.append(TreeView(root_options=dict(text="Hausaufgaben")))
        self.tv_list.append(TreeView(root_options=dict(text="Hausarbeiten")))
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
        tvb = TreeViewButton(size_hint=(1, 0.1), text=str(markdown_timestamp))
        tvb.bind(on_press=lambda *args: self.write_text_to_codeinput(markdown_timestamp))
        self.ids.tree_views.add_widget(tvb)

    def update_tree_view(
            self):  # TODO sollte async sein falls sich im repo etwas ändert das es sofort aktualisiert wird
        pass

    def populate_tree_view(self, tree_view):
        app = App.get_running_app()
        yaml_files = fnmatch.filter(os.listdir(str(app.directory_path)), '*.yaml')
        for x in range(
                len(yaml_files)):  # Alle nodes in dem Tree danach abfrage ob node Notiz oder nochmal directory ist
            timestamp = yaml_files[x].rstrip(".yaml")
            tree_view.add_node(TreeViewButton(text=timestamp, size_hint=(1, 0.01),
                                              on_press=lambda *args: self.write_text_to_codeinput(timestamp))) #Wird hier auch wirklich bei den verschiedenen Buttons zur laufzeit das richtige übergeben?

    def write_text_to_codeinput(self, markdown_timestamp):
        self.focused_md_file = markdown_timestamp  # Aus der Yaml datei lesen
        text = App.get_running_app().read_md_file(str(markdown_timestamp))
        self.ids.box_for_codeinput.text = text

    def on_focus(self, instance, value): #Sollte mit Tastenkombination funktionieren also z.B. Strg + s
        if not value and self.focused_md_file != "":
            App.get_running_app().save_to_md_file(self.focused_md_file, instance.text)


class TreeViewButton(MDFlatButton, TreeViewNode):
    pass

# class TreeViewOneLineListItem(OneLineListItem, TreeViewNode):
#    pass
