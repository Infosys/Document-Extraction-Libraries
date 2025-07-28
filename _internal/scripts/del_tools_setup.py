# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import shutil
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INFY_SEARCH_SERVICE_TOOL_DIR = os.path.join(BASE_DIR, "../../tools/infy_search_service_tool")

def list_tools():
    """List available DEL tools."""
    apps = [
        "infy_search_service_tool"
    ]
    return apps

def setup_tool(service_name):
    """Move the required files for respective folder."""
    if service_name == "infy_search_service_tool":
        vectordb_data = os.path.abspath(os.path.join(BASE_DIR, "../../_internal/samples/input/semantic_search_data/vectordb"))
        sparsedb_data = os.path.abspath(os.path.join(BASE_DIR, "../../_internal/samples/input/semantic_search_data/sparsedb"))
        file_path = os.path.abspath(os.path.join(BASE_DIR, "../../_internal/samples/input/AR_2022-23_page-14-17.pdf"))
        vectordb_dest_dir = "C:/del/fs/services/dbsvc/STORAGE/data/vectordb/encoded/sentence_transformer-all-MiniLM-L6-v2/documents"
        sparsedb_dest_dir = "C:/del/fs/services/dbsvc/STORAGE/data/db/sparseindex/bm25s/documents"
        file_path_dest_dir = "C:/del/fs/services/resourcesvc/STORAGE/data/vectordb/resources"
        dummy_file_name = "6f158336-e28a-4fa2-b42e-805cd53c6feb.pdf"
        dummy_file_path = os.path.join(file_path_dest_dir, dummy_file_name)

        if not os.path.exists(vectordb_dest_dir):
            os.makedirs(vectordb_dest_dir)
            print(f"Created directory: {vectordb_dest_dir}")
        if not os.path.exists(sparsedb_dest_dir):
            os.makedirs(sparsedb_dest_dir)
            print(f"Created directory: {sparsedb_dest_dir}")
        if not os.path.exists(file_path_dest_dir):
            os.makedirs(file_path_dest_dir)
            print(f"Created directory: {file_path_dest_dir}")

        if os.path.exists(vectordb_data):
            for item in os.listdir(vectordb_data):
                s = os.path.join(vectordb_data, item)
                d = os.path.join(vectordb_dest_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            print(f"Copied files from {vectordb_data} to {vectordb_dest_dir}")
            
        if os.path.exists(sparsedb_data):
            for item in os.listdir(sparsedb_data):
                s = os.path.join(sparsedb_data, item)
                d = os.path.join(sparsedb_dest_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            print(f"Copied files from {sparsedb_data} to {sparsedb_dest_dir}")

        if os.path.exists(file_path):
            shutil.copy2(file_path, dummy_file_path)
            print(f"Copied file from {file_path} to {dummy_file_path}")

def main():
    """Main function to launch applications."""
    print("DEL Tools Setup\n")    
    apps = list_tools()
    print("Select tool to setup:")
    for i, app in enumerate(apps, start=1):
        print(f"{i}. {app}")

    while True:
        try:
            choice = int(input("\nEnter the number of the tool you want to setup (or 0 to exit): "))
            if choice == 0:
                break
            if 1 <= choice <= len(apps):
                selected_app = apps[choice - 1]
                setup_tool(selected_app)
            else:
                print("Invalid choice. Please select a valid service number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()