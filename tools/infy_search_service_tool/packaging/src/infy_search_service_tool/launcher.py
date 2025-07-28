# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import argparse
import http.server
import socketserver
import os

HTML_ROOT_PATH = os.path.dirname(__file__) + "\\www"
BASE_HREF = "searchserviceui"
input_data_dict = {}


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler that serves files from the root_dir"""

    def translate_path(self, path):
        """Override the translate_path method to serve files from the root_dir"""
        _path = super().translate_path(path).replace('/', '')
        relpath = os.path.relpath(_path, os.getcwd())
        relpath = '' if relpath == '.' else relpath
        base_href_stripped = BASE_HREF.strip('/')
        if relpath.startswith(base_href_stripped):
            relpath = relpath[len(base_href_stripped):]
        local_path = HTML_ROOT_PATH + relpath
        if input_data_dict['verbose']:
            print(f"Requested URL: {path}")
            print(f"Relative Path: {relpath}")
            print(f"Local Path: {local_path}")
        return local_path


def __parse_input():
    global input_data_dict
    input_data_dict = INPUT_DATA_DICT.copy()
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, choices=["start"])
    parser.add_argument("--http_port", type=int, default=8000, required=False)
    parser.add_argument("--verbose", default=False, required=False)
    args = parser.parse_args()
    input_data_dict['action'] = args.action
    input_data_dict['http_port'] = args.http_port
    input_data_dict['verbose'] = args.verbose
    return input_data_dict


def start_server():
    """Main function to start the server"""
    global input_data_dict
    input_data_dict = __parse_input()
    if input_data_dict['verbose']:
        print("Input parameters received:")
        for key, value in input_data_dict.items():
            print(f"{key}: {value}")

    handler = CustomHTTPRequestHandler
    http_port = input_data_dict['http_port']
    with socketserver.TCPServer(("", http_port), handler) as httpd:
        print("---------------------------------------")
        print(f"Serve Folder: {HTML_ROOT_PATH}")
        print(f"Serve URL: http://localhost:{http_port}")
        print("---------------------------------------")
        httpd.serve_forever()


INPUT_DATA_DICT = {
    "action": None,
    "http_port": None,
    "verbose": None
}

if __name__ == '__main__':
    # For unit testing
    import sys
    sys.argv = ['<leave blank>',
                "start",
                '--http_port',
                '8989',
                '--verbose',
                'True']
    start_server()
