import os
from datetime import datetime

import yaml
import webbrowser
import markdown
from kivy.app import App
from kivy.effects.scroll import ScrollEffect
from kivy.properties import StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.treeview import TreeView, TreeViewNode
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.chip import MDChip
from kivymd.uix.label import MDLabel
from kivymd.uix.list import ThreeLineAvatarListItem
from kivymd.uix.screen import MDScreen
from pygments.lexers import MarkdownLexer
from pygments.lexers import YamlLexer


class MainScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.first_entered = False
        self.popup = None

    def on_pre_enter(self, *args):
        self.refresh()

    def create_markdown(self):
        timestamp_now = str(datetime.now())
        timestamp_now = timestamp_now.replace(" ", "_")
        if os.name == "nt":
            timestamp_now = timestamp_now.replace(":", "-")
        self.create_yaml(timestamp_now)
        open(
            os.path.join(App.get_running_app().directory_path, timestamp_now + ".md"),
            "w",
        )
        self.refresh()

    def create_yaml(self, markdown_timestamp):
        yamlName = markdown_timestamp + ".yaml"
        app = App.get_running_app()
        data = {
            "type": "node",
            "title": markdown_timestamp,
            "timestamp": markdown_timestamp,
            "importance": 1,
        }
        app.save_to_yaml_file(yamlName, app.directory_path, data)

    def pick_importance_colour(self, importance):
        if importance <= 0:
            return 1, 1, 1, 1
        if 0 < importance < 3:
            return "#57FF54"
        if 5 > importance >= 3:
            return "#EBB221"
        if importance >= 5:
            return "#FF2E4D"

    def populate_tree_view(self, tree_view, parent, path, search):
        app = App.get_running_app()
        show_empty = app.config.getboolean("directories", "show_empty")
        for file in os.scandir(path):
            if file.is_dir():
                tree_node = tree_view.add_node(
                    TreeViewButton(text=file.name, line_color=(1, 1, 1, 1)), parent
                )
                tree_view.toggle_node(tree_node)
                self.populate_tree_view(tree_view, tree_node, file.path, search)
                if search is not None and not show_empty and len(tree_node.nodes) == 0:
                    tree_view.remove_node(tree_node)

            if not (file.is_file() and file.name.endswith(".yaml")):
                continue
            content = app.read_yaml_file(file.name, path)
            title = content.get("title", file.name.removesuffix(".yaml"))
            file_name = file.name.removesuffix(".yaml")
            tags = content.get("tags", [])
            importance = content.get("importance", 0)
            color = self.pick_importance_colour(importance)

            if "type" in content and content.get("type") == "node":
                if parent is not None and parent.text not in tags:
                    content["tags"] = tags
                    tags.append(parent.text)
                    app.save_to_yaml_file(file.name, path, content)
                tags = self.get_formatted_node_tags(content)
                is_in_search = search is not None and (
                    search in title or search in tags
                )
                if not is_in_search:
                    continue

                button = TreeViewThreeLineAvatarListItem(
                    text=title,
                    secondary_text=tags,
                    tertiary_text=" ",
                    icon="file",
                    path=file.path.removesuffix(file.name),
                    timestamp=file_name,
                    on_touch_down=self.on_pressed,
                )
                self.set_default_values_treeviewbutton(button)
                button.set_button_icon_color(color)

                if parent:
                    parent.importance.append(importance)
                    self.calc_dir_importance(parent)

                tree_view.add_node(button, parent)

    def on_pressed(self, instance, touch):
        App.get_running_app().focused_md_file = instance
        if touch.button == "right":
            self.write_yaml_to_codeinput()
        else:
            self.write_md_to_codeinput()
        self.display_title()
        self.display_tags()

    def delete_node(self, instance):
        App.get_running_app().focused_md_file = None
        codeinput = self.ids.box_for_codeinput
        codeinput.text = ""
        tag_boxlayout = self.ids.chip_tags
        tag_boxlayout.clear_widgets()
        self.ids.md_header_label.text = ""
        os.remove(os.path.join(instance.path, instance.timestamp + ".md"))
        os.remove(os.path.join(instance.path, instance.timestamp + ".yaml"))

        self.refresh()

    def write_md_to_codeinput(self):
        app = App.get_running_app()
        codeinput = self.ids.box_for_codeinput
        instance = app.focused_md_file
        text = app.read_md_file(instance.timestamp, instance.path)
        codeinput.lexer = MarkdownLexer()
        codeinput.is_current_lexer_markdown = True
        codeinput.text = text

    def write_yaml_to_codeinput(self):
        app = App.get_running_app()
        instance = app.focused_md_file
        codeinput = self.ids.box_for_codeinput
        codeinput.cursor = (0, 0)
        content = app.read_yaml_file(instance.timestamp, instance.path)
        codeinput.lexer = YamlLexer()
        codeinput.is_current_lexer_markdown = False
        codeinput.text = yaml.dump(content)

    def display_tags(self):
        app = App.get_running_app()
        instance = app.focused_md_file
        tag_boxlayout = self.ids.chip_tags
        tag_boxlayout.clear_widgets()
        icon_button = MDIconButton(icon="plus-circle-outline")
        icon_button.bind(on_press=lambda x: self.open_add_tag_popup())
        tag_boxlayout.add_widget(icon_button)
        content = App.get_running_app().read_yaml_file(
            instance.timestamp, instance.path
        )

        for tag in content.get("tags", []):
            chip = MDChip(text=tag, icon="close-circle-outline", pos_hint={"y": 0.25})
            chip.bind(on_release=self.remove_tag)
            tag_boxlayout.add_widget(chip)

    def display_title(self):
        app = App.get_running_app()
        instance = app.focused_md_file
        content = app.read_yaml_file(instance.timestamp, instance.path)
        self.ids.md_header_label.text = content.get("title")

    def refresh(self):
        search = self.ids.search_field.text
        self.ids.tree_views.clear_widgets()
        app = App.get_running_app()
        tv = TreeView(hide_root=True, indent_level=9)
        tv.size_hint = (1, None)
        tv.bind(minimum_height=tv.setter("height"))
        scroll_view = ScrollView(pos=(0, 0), effect_cls=ScrollEffect)
        self.populate_tree_view(
            tv, None, app.config.get("workingdirectory", "current"), search
        )
        self.ids.tree_views.add_widget(scroll_view)

        scroll_view.add_widget(tv)

    def get_code_input_text(self):
        return self.ids.box_for_codeinput.text

    def open_add_tag_popup(self):
        tag_input = TextInput(multiline=False, size_hint=(1, None))
        tag_input.bind(minimum_height=tag_input.setter("height"))
        self.popup = Popup(
            title="Add Tag", content=tag_input, auto_dismiss=True, size_hint=(0.3, None)
        )
        tag_input.bind(on_text_validate=lambda x: self.add_tag(tag_input.text))

        self.popup.open()

    def add_tag(self, tag_name):
        app = App.get_running_app()
        instance = app.focused_md_file
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
        if not self.ids.box_for_codeinput.is_current_lexer_markdown:
            self.write_yaml_to_codeinput()

        self.popup.dismiss()
        self.refresh()

    def remove_tag(self, instance):
        app = App.get_running_app()
        tag_boxlayout = self.ids.chip_tags
        tag_boxlayout.remove_widget(instance)
        content = app.read_yaml_file(
            app.focused_md_file.timestamp, app.focused_md_file.path
        )
        content["tags"].remove(instance.text)
        app.save_to_yaml_file(
            app.focused_md_file.timestamp, app.focused_md_file.path, content
        )
        if not self.ids.box_for_codeinput.is_current_lexer_markdown:
            self.write_yaml_to_codeinput()

        self.refresh()

    def get_formatted_node_tags(self, content):
        tags = ""
        for tag in content.get("tags", []):
            tags += "[color=#ff0000]#[/color]" + tag + " "

        return tags

    def header_change(self):
        app = App.get_running_app()
        md_header_input = self.ids.md_header_input
        md_header_label = self.ids.md_header_label

        md_header_input.disabled = True
        md_header_input.opacity = 0
        if app.focused_md_file is None:
            app.invalid_file_error()
            return
        new_header = md_header_input.text
        md_header_label.text = new_header
        content = app.read_yaml_file(
            app.focused_md_file.timestamp, app.focused_md_file.path
        )
        content["title"] = new_header
        app.save_to_yaml_file(
            app.focused_md_file.timestamp, app.focused_md_file.path, content
        )

        self.refresh()

    def activate_header_change(self):
        app = App.get_running_app()
        if app.focused_md_file is None:
            app.invalid_file_error()
            return
        md_header_input = self.ids.md_header_input
        md_header_input.disabled = False
        md_header_input.opacity = 1

    def set_default_values_treeviewbutton(self, button):
        left_container = button.ids._left_container

        left_container.orientation = "vertical"
        left_container.clear_widgets()
        left_container.add_widget(
            MDIconButton(icon="delete", on_release=lambda x: self.delete_node(button))
        )
        # left_container.remove_widget(left_container.children[1])
        left_container.add_widget(
            MDIconButton(
                icon="file", on_release=lambda x: self.open_md_file_in_browser(button)
            )
        )
        left_container.pos_hint = {"y": -0.05}
        left_container.children[0].pos_hint = {"right": 0.6}
        left_container.children[1].pos_hint = {"right": 0.6}

        text_container = button.ids._text_container
        text_container.pos_hint = {"right": 0.92}

        for label in text_container.children:
            label.size_hint_x = 1.3

    def calc_dir_importance(self, dir_node):
        result = 0
        for number in dir_node.importance:
            result = result + number
        color = self.pick_importance_colour(result / len(dir_node.importance))
        dir_node.line_color = color

    def open_md_file_in_browser(self, button):
        app = App.get_running_app()
        text = app.read_md_file(button.timestamp, button.path)
        html_text = markdown.markdown(text, extensions=["extra"])
        html_file = button.timestamp.removesuffix(".md") + ".html"
        html_file_path = os.path.join(button.path, html_file)
        with open(html_file_path, "w") as file:
            file.write(html_text)

        webbrowser.open(html_file_path)
        if not os.name == "nt":
            os.remove(html_file_path)


class TreeViewButton(MDFlatButton, TreeViewNode):
    importance = ListProperty()


class TreeViewThreeLineAvatarListItem(ThreeLineAvatarListItem, TreeViewNode):
    app = App.get_running_app()
    timestamp = StringProperty("")
    path = StringProperty(app.directory_path)
    icon = StringProperty()

    def set_button_icon_color(self, color):
        self.ids._left_container.children[0].children[0].color = color
        self.ids._left_container.children[1].children[0].color = color
        pass


class MDButtonLabel(ButtonBehavior, MDLabel):
    pass
