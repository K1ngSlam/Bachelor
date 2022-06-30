import yaml
from kivy.app import App
from kivy.uix.codeinput import CodeInput
from pygments.lexers import MarkdownLexer


class CustomCodeInput(CodeInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blocker = True
        self.lexer = MarkdownLexer()
        self.is_current_lexer_markdown = True

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super().keyboard_on_key_down(window, keycode, text, modifiers)
        if keycode[1] == "s" and "ctrl" in modifiers and self.blocker:
            self.blocker = False


    def keyboard_on_key_up(self, window, keycode):
        super().keyboard_on_key_up(window, keycode)
        if not self.blocker and keycode[1] == "s":
            app = App.get_running_app()
            self.blocker = True
            text = app.sm.current_screen.get_code_input_text()
            if app.focused_md_file is not None and self.is_current_lexer_markdown:
                app.save_to_md_file(app.focused_md_file.timestamp, app.focused_md_file.path, text)
            else:
                parsed_text = yaml.load(text, Loader=yaml.FullLoader)
                app.save_to_yaml_file(app.focused_md_file.timestamp, app.focused_md_file.path, parsed_text)
