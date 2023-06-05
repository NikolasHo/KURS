### Helpers

import os

def get_subfolders(directory):
    subfolders = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            subfolders.append(dir)
    return subfolders