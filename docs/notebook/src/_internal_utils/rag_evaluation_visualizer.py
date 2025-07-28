# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import ipywidgets as widgets
from IPython.display import display
from IPython.display import display, clear_output, HTML
import matplotlib.pyplot as plt

class RagEvaluationVisualizer():

    CONTEXT_DELIMITER = '{{EOC}}'
    __SAMPLE_IDX_NONE = -1
    
    def __init__(self, samples=None):
        # Begin LHS Elements
        control_list = []
        form_lhs_title = widgets.HTML(
                            f'<span style="font-size:1.5em"><b>INPUT</b></span>')
        control_list.append(form_lhs_title)
        name_idx_pairs = [(x['name'], idx) for idx, x in enumerate(samples)] if samples else []
        name_idx_pairs.append(('None', self.__SAMPLE_IDX_NONE))
        form_lst_samples = widgets.Dropdown(
            options=name_idx_pairs,
            value=-1,
            description='Select sample:',
            layout={'width': '95%'},
            style={'description_width': 'initial'}
        )
        control_list.append(form_lst_samples)

        html_code='<span><b>1. Contexts: (For multiple items, use '
        html_code+=f'<span style="color:red">{self.CONTEXT_DELIMITER}</span> as delimiter) </b></span>'
        form_lbl_context = widgets.HTML(html_code)
        self.__form_txa_context = widgets.Textarea(rows=5, layout={'width': '95%'})
        form_lbl_question = widgets.HTML(f'<span><b>2. Question:</b></span>')
        self.__form_txa_question = widgets.Textarea(rows=2, layout={'width': '95%'})
        form_lbl_ground_truth = widgets.HTML(f'<span><b>3. Ground Truth:</b> (correct answer - human-written)</span>')
        self.__form_txa_ground_truth = widgets.Textarea(rows=2, layout={'width': '95%'})
        form_lbl_answer = widgets.HTML(f'<span><b>4. Answer:</b> (generated answer - AI)</span>')
        self.__form_txa_answer = widgets.Textarea(rows=2, layout={'width': '95%'})

        control_list.extend([form_lbl_context, self.__form_txa_context, 
                      form_lbl_question, self.__form_txa_question,
                      form_lbl_ground_truth, self.__form_txa_ground_truth,
                      form_lbl_answer, self.__form_txa_answer])

        self.__form_submit_button = widgets.Button(description='Submit For Evaluation',
            display='flex', style={'description_width': 'initial'})
        form_reset_button = widgets.Button(description='Clear Form')
        # control_list.append(widgets.HBox([self.__form_submit_button, form_reset_button]))

        # Create a GridspecLayout with 1 row and 10 columns for fine-tuning the layout
        grid_for_buttons = widgets.GridspecLayout(1, 10)
        grid_for_buttons[0, 0:5] = self.__form_submit_button
        grid_for_buttons[0, 6:] = widgets.HBox([form_reset_button])  # Wrap the right_widget in an HBox for alignment
        control_list.append(grid_for_buttons)
        form_lhs = widgets.VBox(control_list)

        # RHS Elements
        form_rhs_title = widgets.HTML(
                            f'<span style="font-size:1.5em"><b>METRICS</b></span>')
        self.__form_gra_output = widgets.Output()
        control_list = [form_rhs_title, self.__form_gra_output]
        form_rhs = widgets.VBox(control_list)

        self.__form_grid = widgets.GridspecLayout(1, 10)
        self.__form_grid[0, 0:5] = form_lhs
        self.__form_grid[0, 5:] = form_rhs

        # Event handlers        
        def do_reset(_):
            self.__form_txa_context.value = ''
            self.__form_txa_question.value = ''
            self.__form_txa_ground_truth.value = ''
            self.__form_txa_answer.value = ''
            self.__form_gra_output.clear_output()
        
        form_reset_button.on_click(do_reset)

        def do_populate_sample(change):
            if change['type'] == 'change' and change['name'] == 'value':
                # print("changed to %s" % change['new'])
                idx = change['new']
                if idx == self.__SAMPLE_IDX_NONE:
                    self.__form_txa_context.value = ''
                    self.__form_txa_question.value = ''
                    self.__form_txa_ground_truth.value = ''
                    self.__form_txa_answer.value = ''
                else:
                    record = samples[idx]['dataset']
                    # print('record:', record)
                    delimiter = "\n" + self.CONTEXT_DELIMITER + "\n"
                    self.__form_txa_context.value =   delimiter.join(record['contexts'][0])
                    self.__form_txa_question.value = record['question'][0]
                    self.__form_txa_ground_truth.value = record['ground_truth'][0]
                    self.__form_txa_answer.value = record['answer'][0]

        form_lst_samples.observe(do_populate_sample)

    
        
    def get_input_form_data(self):        
        return {
            'contexts': self.__form_txa_context.value,
            'question': self.__form_txa_question.value,
            'ground_truth': self.__form_txa_ground_truth.value,
            'answer': self.__form_txa_answer.value
        }
    
    def set_output_graph(self, data_dict):
        form_gra_output = self.__form_gra_output
        form_gra_output.clear_output()
        with form_gra_output:
            self.__plot_graph(data_dict) 

    def get_output_handler(self):
        form_gra_output = self.__form_gra_output
        return form_gra_output

    def on_form_submit_callback(self, callback_fn=None):
        self.__form_submit_button.on_click(callback_fn)
        
    def show_ui(self):
        form_grid = self.__form_grid
        display(form_grid)

    def plot_graph(self, data_dict):
        self.__plot_graph(data_dict)

    ### ------------- Private methods ----------------
    def __plot_graph(self, data_dict):
        # print(data_dict)
        labels, values, labels_with_none = [] , [], []
        sorted_key_list = sorted(list(data_dict.keys()), reverse=True)
        # print('sorted_key_list = ', sorted_key_list)
        for key in sorted_key_list:
            value = data_dict[key]
            if value is None:
                labels_with_none.append(key)                
            else:
                labels.append(key)
                values.append(value)
                
        
        # Create figure with reduced height
        height = 0.3 * len(labels)
        plt.figure(figsize=(4, height))  # Adjust figsize: (width, height) in inches


        # Plotting
        # plt.barh(categories, values, color=['blue', 'green'])
        bars = plt.barh(labels, values, height=0.5)  # Adjust the height parameter as needed
        plt.xlabel('Scores')
        plt.title('Performance Metrics')
        plt.xlim(0, 1)  # Assuming scores are between 0 and 1
        
        # Annotating each bar with its value
        for bar in bars:
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height() / 2, f'{width:.2f}', 
                    va='center', ha='left')
        
        plt.show()

        if labels_with_none:
            html_code = '<span style="color:red">NOTE: Metrics with value "None" are not plotted: '
            html_code += f'<b>{labels_with_none}</b></span>'
            display(HTML(html_code))