import fnmatch
import os
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from mdutils.mdutils import MdUtils


class MainPageWidget(BoxLayout):
    def __init__(self,**kwargs): # Wie update ich was displayed wird und pack in ein bestimmtes Layout neue widgets?
        super().__init__(**kwargs)
        side_bar = self.ids.md_files
        side_bar.add_widget(Button(text='test'))
        number_of_files = len(fnmatch.filter(os.listdir(self.directory_path), '*.yaml'))
        for x in range(number_of_files):
            b = Button(text = 'Button in code')


    def create_markdown(self):
        print("Button clicked")
        now = datetime.now()
        mdFile = MdUtils(file_name=str(now), title='Markdown File Example')
        mdFile.create_md_file()
        self.create_yaml(now)
        print(len(fnmatch.filter(os.listdir(self.directory_path), '*.yaml')))

    def create_yaml(self,markDownTimeStamp):
        yamlName = str(markDownTimeStamp) + '.yaml'
        print(yamlName)
        open(yamlName, 'x')

    def add_button_widget(self,markDownTimeStamp):
        root = MainPageWidget()
        root.add_widget(Button(text="Test Button A"))

class MainWidget(Widget): #Hier build(self) benutzen? Aber warum und wie?
    pass

class MainApp(App):
    pass



MainApp().run()
