# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import glob
import subprocess


class NotebookUtil():

    @classmethod
    def clear_output(cls, nb_root_folder_path: str, exclude_nb_file_list: list,
                     recursive: bool = True, dry_run_mode: bool = True):
        """Clears the output of all the notebook files."""
        joiner = "/"
        if recursive:
            joiner = "/**/"
        nb_files = glob.glob(nb_root_folder_path + joiner +
                             "*.ipynb", recursive=recursive)
        task_list = []
        for nb_file in nb_files:
            matches = [x for x in exclude_nb_file_list if nb_file.endswith(x)]
            if len(matches) > 0:
                continue
            cmd_str = f"jupyter nbconvert --clear-output --ClearMetadataPreprocessor.enabled=True {nb_file}"
            task_list.append([nb_file, cmd_str])

        if dry_run_mode:
            print('Running in dry run mode. No command will be executed.')
            print('To disable dry run, set dry_run_mode = False\n')
        else:
            print('Processing started. Please wait for completed message...')

        for idx, task in enumerate(task_list):
            if dry_run_mode:
                print(task[1])
                continue
            subprocess.run(task[1])
            print(f"Completed {idx+1} of {len(task_list)}: {task[0]}  ")

        if not dry_run_mode:
            print('Processing completed.')
