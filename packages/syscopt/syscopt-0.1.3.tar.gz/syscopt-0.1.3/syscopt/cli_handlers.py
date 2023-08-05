import datetime
import os


def delete_files(folder_path: str):
    file_list = os.listdir(folder_path)
    if file_list:
        for file_index, file in enumerate(file_list):
            filepath = os.path.join(folder_path, file)
            os.remove(filepath)
        print(f" {folder_path.split('/')[-1]} cleaned.")
    else:
        print(f"{folder_path.split('/')[-1]} is empty")


def get_current_time_stamp():
    return str(datetime.datetime.now()).split('.')[0].replace(' ', '_')
