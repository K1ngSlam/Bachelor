import os
from datetime import datetime
from logging import Logger

import yaml
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.treeview import TreeView, TreeViewNode
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton, MDIconButton
from kivymd.uix.chip import MDChip
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.list import ThreeLineAvatarListItem, IconLeftWidget
from kivymd.uix.screen import MDScreen
from pygments.lexers import YamlLexer
from pygments.lexers import MarkdownLexer


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
        timestamp_now = timestamp_now.replace(" ", "_")
        self.create_yaml(timestamp_now)
        open(os.path.join(App.get_running_app().directory_path, timestamp_now + ".md"), 'w')
        self.refresh()

    def create_yaml(self, markdown_timestamp):
        yamlName = markdown_timestamp + '.yaml'
        app = App.get_running_app()
        data = {
            "type": "node",
            "title": markdown_timestamp,
            "importance": 5
        }
        app.save_to_yaml_file(yamlName, app.directory_path, data)

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

    def populate_tree_view(self, tree_view, parent, path, search):
        app = App.get_running_app()
        for file in os.scandir(path):
            if file.is_dir() and parent is None:
                tree_node = tree_view.add_node(TreeViewButton(text=file.name, line_color=(1, 1, 1, 1)))
                self.populate_tree_view(tree_view, tree_node, file.path, search)
            if file.is_dir() and parent is not None:
                tree_node = tree_view.add_node(TreeViewButton(text=file.name), parent)
                self.populate_tree_view(tree_view, tree_node, file.path, search)
            if not (file.is_file() and file.name.endswith(".yaml")):
                continue
            content = app.read_yaml_file(file.name, path)
            color = 255, 1, 1, 1
            tags = " "
            if "importance" in content:
                color = self.pick_importance_colour(content)
            if "type" in content:
                if content.get("type") == "node":
                    timestamp = file.name.rstrip(".yaml")
                    title = self.get_node_title(content, file)
                    if "tags" in content:
                        if parent is not None and parent.text not in content.get("tags"):
                            content["tags"].append(parent.text)
                            app.save_to_yaml_file(file.name, path, content)
                        tags = self.get_formatted_node_tags(content)
                    if parent is None:
                        if search is not None and (search in title or search in tags):
                            button = TreeViewThreeLineAvatarListItem(text=title,
                                                                     secondary_text=tags,
                                                                     tertiary_text=" ",
                                                                     icon="file",
                                                                     path=file.path.rstrip(file.name),
                                                                     timestamp=timestamp, on_touch_down=self.on_pressed)
                            self.set_default_values_treeviewbutton(button)
                            button.set_button_icon_color(color)

                            tree_view.add_node(
                                button)
                    else:
                        if search is not None and (search in title or search in tags):
                            button = TreeViewThreeLineAvatarListItem(icon="file", text=title,
                                                                     secondary_text=tags,
                                                                     tertiary_text=" ",
                                                                     path=file.path.rstrip(file.name),
                                                                     timestamp=timestamp,
                                                                     on_touch_down=self.on_pressed)
                            self.set_default_values_treeviewbutton(button)
                            button.set_button_icon_color(color)

                            tree_view.add_node(button,
                                               parent)

    def on_pressed(self, instance, touch):
        if touch.button == "right":
            self.edit_yaml_file(instance)
            self.display_title(instance)
        else:
            self.write_text_to_codeinput(instance)
            self.display_title(instance)
            self.display_tags(instance)

    def delete_node(self, instance):
        os.remove(os.path.join(instance.path, instance.timestamp + ".md"))
        os.remove(os.path.join(instance.path, instance.timestamp + ".yaml"))

        self.refresh()

    def write_text_to_codeinput(self, instance):
        App.get_running_app().focused_md_file = instance
        codeinput = self.ids.box_for_codeinput
        text = App.get_running_app().read_md_file(instance.timestamp, instance.path)
        codeinput.lexer = MarkdownLexer()
        codeinput.is_current_lexer_markdown = True
        codeinput.text = text

    def edit_yaml_file(self,instance):
        app = App.get_running_app()
        app.focused_md_file = instance
        codeinput = self.ids.box_for_codeinput
        content= app.read_yaml_file(instance.timestamp, instance.path)
        codeinput.lexer = YamlLexer()
        codeinput.is_current_lexer_markdown = False
        codeinput.text = yaml.dump(content)

    def display_tags(self, instance):
        tag_boxlayout = self.ids.chip_tags
        tag_boxlayout.clear_widgets()
        icon_button = MDIconButton(icon="plus-circle-outline")
        icon_button.bind(on_press=lambda x: self.open_add_tag_popup(instance))
        tag_boxlayout.add_widget(icon_button)
        content = App.get_running_app().read_yaml_file(instance.timestamp, instance.path)

        if "tags" in content:
            for tag in content.get("tags"):
                chip = MDChip(text=tag, icon="close-circle-outline", pos_hint={"y": 0.25})
                chip.bind(on_release=self.remove_tag)
                tag_boxlayout.add_widget(chip)

    def display_title(self, instance):
        app = App.get_running_app()
        content = app.read_yaml_file(instance.timestamp, instance.path)
        self.ids.md_header_label.text = content.get("title")

    def refresh(self):
        search = self.ids.search_field.text
        self.ids.tree_views.clear_widgets()
        app = App.get_running_app()
        tv = TreeView(hide_root=True)
        tv.size_hint = (1, None)
        tv.bind(minimum_height=tv.setter("height"))
        scroll_view = ScrollView(pos=(0, 0))
        self.populate_tree_view(tv, None, app.config.get("workingdirectory", "current"), search)
        self.ids.tree_views.add_widget(scroll_view)

        scroll_view.add_widget(tv)

    def get_code_input_text(self):
        return self.ids.box_for_codeinput.text

    def open_add_tag_popup(self, instance):
        tag_input = TextInput(multiline=False, size_hint=(1, None))
        tag_input.bind(minimum_height=tag_input.setter("height"))
        popup = Popup(title="Add Tag", content=tag_input, auto_dismiss=True, size_hint=(0.3, None))
        tag_input.bind(on_text_validate=lambda x: self.add_tag(tag_input.text, popup, instance))

        popup.open()

    def add_tag(self, tag_name, popup, instance):
        app = App.get_running_app()
        tag_boxlayout = self.ids.chip_tags
        chip = MDChip(text=tag_name, icon="close-circle-outline", pos_hint={"y": 0.25})
        chip.bind(on_release=self.remove_tag)
        tag_boxlayout.add_widget(chip)
        content = app.read_yaml_file(instance.timestamp, instance.path)
        if "tags" not in content:
            tag_list = []
            content["tags"] = tag_list
        content["tags"].append(tag_name)
        app.save_to_yaml_file(instance.timestamp, instance.path, content)

        popup.dismiss()

    def remove_tag(self, instance):
        app = App.get_running_app()
        tag_boxlayout = self.ids.chip_tags
        tag_boxlayout.remove_widget(instance)
        content = app.read_yaml_file(app.focused_md_file.timestamp, app.focused_md_file.path)
        content["tags"].remove(instance.text)
        app.save_to_yaml_file(app.focused_md_file.timestamp, app.focused_md_file.path, content)

    def get_node_title(self, content, file):
        if not ("title" in content):
            title = file.name.rstrip(".yaml")
            return title
        else:
            title = content.get("title")
            return title

    def get_formatted_node_tags(self, content):
        tags = ''
        for tag in content.get("tags"):
            tags += "[color=#ff0000]#[/color]" + tag + " "

        return tags

    def header_change(self):
        app = App.get_running_app()
        md_header_input = self.ids.md_header_input
        md_header_label = self.ids.md_header_label
        new_header = md_header_input.text
        md_header_input.disabled = True
        md_header_input.opacity = 0
        md_header_label.text = new_header
        content = app.read_yaml_file(app.focused_md_file.timestamp, app.focused_md_file.path)
        content["title"] = new_header
        app.save_to_yaml_file(app.focused_md_file.timestamp, app.focused_md_file.path, content)

        self.refresh()

    def activate_header_change(self):
        md_header_input = self.ids.md_header_input
        md_header_input.disabled = False
        md_header_input.opacity = 1

    def set_default_values_treeviewbutton(self, button):
        left_container = button.ids._left_container

        left_container.orientation = "vertical"
        left_container.add_widget(MDIconButton(icon="file"))
        left_container.pos_hint = {"y": -0.05}
        left_container.children[0].pos_hint = {"x": -0.5}
        left_container.children[2].pos_hint = {"x": -0.5}

        text_container = button.ids._text_container

        for label in text_container.children:
            label.size_hint_x = 1.3
            label.pos_hint = {"x": -0.1}


class TreeViewButton(MDFlatButton, TreeViewNode):
    app = App.get_running_app()
    timestamp = StringProperty("")
    path = StringProperty(app.directory_path)


class TreeViewIconButton(MDRectangleFlatIconButton, TreeViewNode):
    app = App.get_running_app()
    timestamp = StringProperty("")
    path = StringProperty(app.directory_path)


class TreeViewThreeLineAvatarListItem(ThreeLineAvatarListItem, TreeViewNode):
    app = App.get_running_app()
    timestamp = StringProperty("")
    path = StringProperty(app.directory_path)
    source = StringProperty()
    icon = StringProperty()

    def set_button_icon_color(self, color):
        self.ids._left_container.children[0].children[0].color = color
        self.ids._left_container.children[2].children[0].color = color


class MDButtonLabel(ButtonBehavior, MDLabel):
    pass
