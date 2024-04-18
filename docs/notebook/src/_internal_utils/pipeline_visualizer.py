# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import io
import base64
import math
import networkx as nx
import matplotlib.pyplot as plt
from IPython.display import display, HTML


class PipelineVisualizer():

    def __init__(self, nodes: list):
        self.__nodes = nodes
        self.__generate_graph()

    def get_img_html(self):
        img_html = self.__img_html
        return img_html

    # --------------- Private methods -------------- #
    def __generate_graph(self) -> None:
        nodes = self.__nodes
        # Create a directed graph
        G = nx.DiGraph()
        color_dict = {'Scheduled': 'whitesmoke', 'Running': 'yellow', 'Completed': 'springgreen',
                      'Cancelled': 'orange', 'Failed': 'red',
                      'Disabled': 'darkgray', 'Enabled': 'lightgray'}

        color_list = []
        pos_dict = {}
        row = 0
        col = 0

        node_count = len(nodes)
        # To control the number of nodes per row, change below
        COL_COUNT = 4
        ROW_COUNT = math.ceil(node_count/COL_COUNT)
        # print("ROW_COUNT =", ROW_COUNT)
        grid_cells = self.__create_flow_grid_cells(node_count, COL_COUNT)
        # print(grid_cells)

        for idx, node in enumerate(nodes):
            step_name = node['name']
            if node['nodes']:
                G.add_edge(step_name, node['nodes'][0])
            color_list.append(color_dict[node['status']])
        #     pos_dict[step_name] = [col, row]
            col += 1
            pos_dict[step_name] = grid_cells[idx]

        # print("pos_dict =", pos_dict)
        # print("color_list =", color_list)
        canvas_height = 1 + (ROW_COUNT-1)*1.5

        # print("canvas_height =", canvas_height)
        plt.figure(figsize=(10, canvas_height))

        nx.draw(G, pos_dict, with_labels=True, node_size=3000, node_color=color_list,
                node_shape='s', edge_color='gray', arrowstyle='->', arrowsize=20)

        # Add a margin around the plot E.g. 0.2 means 20%
        if ROW_COUNT <= 1:
            margin_y = 0.3
        elif ROW_COUNT == 2:
            margin_y = 0.2
        elif ROW_COUNT == 3:
            margin_y = 0.1
        elif ROW_COUNT == 4:
            margin_y = 0.05
        elif ROW_COUNT == 5:
            margin_y = 0.025
        else:
            margin_y = 0.0125
        # print('ROW_COUNT=', ROW_COUNT, 'margin_y=', margin_y)
        plt.margins(y=margin_y)

        # Save image to in-memory file object
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='png')
        # Close the figure window to prevent it from being displayed
        plt.close()
        my_stringIObytes.seek(0)
        encoded_string = base64.b64encode(
            my_stringIObytes.read()).decode('utf-8')

        prefix_string = "data:image/png;base64, "
        # encoded_string = encoded_string.decode('utf-8')
        style = "display: block;margin-left: auto;margin-right: auto;width: 96%; border:1px dotted black;"
        img = f'<div><img style="{style}" src="{prefix_string}{encoded_string}" /></div>'
        self.__img_html = img

    def __create_flow_grid_cells(self, node_count, items_per_row=5):
        grid_cells = []
        row, col = 0, -1
        offset = 1
        for i in range(node_count):
            row = -(i//items_per_row)
            col = col + offset
            # print(row, col)
            grid_cells.append([col, row])
            if col+offset == items_per_row:
                col += offset
                offset = -1
                # print("offset =", offset)
            elif col+offset == -1:
                col += offset
                offset = 1
        return grid_cells
