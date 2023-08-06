import os
import json
import dropbox
import requests
from datetime import datetime

class Manager(object):
    def __init__(self, token) -> None:
        self.__dbx = dropbox.Dropbox(token)
        self.download_paths: str

    def get_folders(self):
        result = self.__dbx.files_list_folder('', recursive=True)
        
        folders = {}
        
        for entry in result.entries:
            if not isinstance(entry, dropbox.files.FileMetadata):
                folders.update({entry.path_lower: entry.id})
            
        return folders

    def download_dropbox(self, cloud_path: str, local_path: str, file_type: str = ''):
        folders = self.get_folders()[cloud_path]
        result = self.__dbx.files_list_folder(folders, recursive=True)
        files_paths = []
        folders_paths = []
        
        for entry in result.entries:
            txt = entry.path_display
            if isinstance(entry, dropbox.files.FileMetadata):
                files_paths.append(txt)
            else:
                folders_paths.append(txt)

        for folder in folders_paths:
            if not(os.path.isdir(local_path + folder)):
                os.mkdir(local_path + folder)

        for file in files_paths:
            if file_type in file:
                self.__dbx.files_download_to_file(local_path + file, file, None)

        self.download_paths = files_paths
        return files_paths

    def upload_dropbox(self, cloud_path: str, file_name: str, payload: bin) -> None:
        """
        Uploads some binary to dropbox using the specified token to the specified path (in dropbox).
        """
        self.__dbx.files_upload(payload, os.path.join(cloud_path, file_name), mode = dropbox.files.WriteMode("overwrite"))