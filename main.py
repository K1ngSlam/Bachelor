import fnmatch
import os
from datetime import datetime

from kivy import app
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from mdutils.mdutils import MdUtils


class MainWindow(Screen):
    # def __init__(self,**kwargs): # Wie update ich was displayed wird und packe es in ein bestimmtes Layout neue widgets?
    # super().__init__(**kwargs)
    # self.directory_path = "/home/ubuntu/PycharmProjects/Bachelor"
    # side_bar = self.ids.md_files
    # side_bar.add_widget(Button(text='test'))
    # number_of_files = len(fnmatch.filter(os.listdir(self.directory_path), '*.yaml'))
    # for x in range(number_of_files):
    #   b = Button(text = 'Button created in code')

    def create_markdown(self):
        print("Button clicked")
        now = datetime.now()
        mdFile = MdUtils(file_name=str(now), title='Markdown File Example')
        mdFile.create_md_file()
        self.create_yaml(now)
        print(len(fnmatch.filter(os.listdir(WindowManager.directory_path), '*.yaml')))

    def create_yaml(self, markDownTimeStamp):
        yamlName = str(markDownTimeStamp) + '.yaml'
        print(yamlName)
        open(yamlName, 'x')

    def add_button_widget(self, markDownTimeStamp):
        root = MainWindow()
        root.add_widget(Button(text="Test Button A"))


class SettingsWindow(Screen):

    def change_md_directory_path(self):
        WindowManager.directory_path = self.ids.set_md_directory.text
        print(WindowManager.directory_path)

class WindowManager(ScreenManager):
    directory_path = "/home/ubuntu/PycharmProjects/Bachelor"


class MainApp(App):  # Hier build(self) benutzen? Aber warum? Wo tu ich Daten rein die nicht von Widgets gehalten werden sollten?
    pass


MainApp().run()
