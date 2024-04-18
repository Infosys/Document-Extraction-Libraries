# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML


class QnAVisualizer():

    __COUNTS_DEFAULT_VALUE = "char(s): 0 | word(s): 0 | token(s): 0"

    def __init__(self):
        form_label_input = widgets.HTML(
            '<span style="background-color: lightgreen">Question:</span>')
        form_text_area = widgets.Textarea(rows=15, layout={'width': '95%'})
        form_text_area_info = widgets.Label(self.__COUNTS_DEFAULT_VALUE)
        form_submit_button = widgets.Button(description='Submit')
        form_reset_button = widgets.Button(description='Reset')

        form_input_form = widgets.VBox(
            [form_label_input, form_text_area_info, form_text_area,
             widgets.HBox([form_submit_button, form_reset_button])])

        form_grid = widgets.GridspecLayout(1, 10)
        form_grid[0, 0:4] = form_input_form

        form_label_output = widgets.HTML(
            f'\n\n<span style="background-color: lightgreen">Answer:</span>')
#         form_output_rhs_notification = widgets.Output(
#             layout={"border": "0px solid blue"})
        form_output_rhs_info = widgets.Label(self.__COUNTS_DEFAULT_VALUE)
        form_output_rhs = widgets.Output(layout={"border": "1px solid green"})

#         form_output_rhs = widgets.Label(layout={"border": "1px solid red", "padding" : "1px"})

        form_grid[0, 4:] = widgets.VBox(
            [form_label_output, form_output_rhs_info, form_output_rhs])

        # Event handlers
        def on_input_change(change):
            text = form_text_area.value
            char_count = len(text)
            word_count = len(text.split(' '))
            sentence_count = len(text.split('.'))
            if self.__token_counter_fn:
                token_count = self.__token_counter_fn(text)
            else:
                token_count = ''
            form_text_area_info.value = f"char(s): {char_count} | word(s): {word_count} | token(s): {token_count}"

        form_text_area.observe(on_input_change)

        def on_output_change(change):
            text = self.__output_text
            char_count = len(text)
            word_count = len(text.split(' '))
            sentence_count = len(text.split('.'))
            if self.__token_counter_fn:
                token_count = self.__token_counter_fn(text)
            else:
                token_count = ''
            form_output_rhs_info.value = f"char(s): {char_count} | word(s): {word_count} | token(s): {token_count}"

        form_output_rhs.observe(on_output_change)

        def do_reset(_):
            form_text_area.value = ''
            form_output_rhs.clear_output()

        form_reset_button.on_click(do_reset)

        self.__form_grid = form_grid
        self.__form_submit_button = form_submit_button
        self.__form_output_rhs = form_output_rhs
        self.__form_text_area = form_text_area
        self.__output_text = ''
        self.__token_counter_fn = None

    def on_form_submit_callback(self, callback_fn=None):
        form_submit_button = self.__form_submit_button
        form_submit_button.on_click(callback_fn)

    def set_token_counter_fn(self, fn):
        self.__token_counter_fn = fn

    def get_input_text(self):
        form_text_area = self.__form_text_area
        return form_text_area.value

    def set_output_text(self, text):
        # Store text at class level for use in event handler
        self.__output_text = text
        form_output_rhs = self.__form_output_rhs
        form_output_rhs.clear_output()
        with form_output_rhs:
            print(text)

    def get_output_handler(self):
        form_output_rhs = self.__form_output_rhs
        return form_output_rhs

    def show_ui(self):
        form_grid = self.__form_grid
        display(form_grid)
