import os
import nltk
import time
import pandas
import hashlib
import tempfile

class CrackDict(object):
    def __init__(self, complex: bool = False) -> None:
        tmp_dir = tempfile.gettempdir()
        now = str(time.time())
        download_path = os.path.join(tmp_dir, hashlib.sha256(bytes(now, 'utf-8')).hexdigest())
        nltk.download('words', download_dir=download_path)

        self.folder_path = os.path.join(download_path, 'corpora', 'words')

        if complex:
            with open(os.path.join(self.folder_path, 'en'), 'r+') as file:
                self.words = file.read().split('\n')
        
        else:
            with open(os.path.join(self.folder_path, 'en-basic'), 'r+') as file:
                self.words = file.read().split('\n')

def sha256(key: bin):
    return hashlib.sha256(b'tttt').hexdigest()

