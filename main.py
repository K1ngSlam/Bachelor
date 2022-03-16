from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from mdutils.mdutils import MdUtils
from datetime import datetime

class CreateButtonWidget(GridLayout):
    def create_markdown(self):
        print("Button clicked")
        now = datetime.now()
        MdUtils(file_name=now, title='Markdown File Example')
        self.create_yaml(now)

    def create_yaml(self,markdowntimestamp):
        yamlname = str(markdowntimestamp) + '.yaml'
        print(yamlname)
        open(yamlname, 'x')

class MainWidget(Widget):
    pass

class MainApp(App):
    pass




MainApp().run()
