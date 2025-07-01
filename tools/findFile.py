import os
import fnmatch
import difflib
from langchain_core.tools import tool

def search_files(search_query, search_path="D:\\"):
    matches = []
    for root, dirs, files in os.walk(search_path):
        for filename in files:
            if fnmatch.fnmatch(filename.lower(), f"*{search_query.lower()}*"):
                full_path = os.path.join(root, filename)
                matches.append(full_path)

    if not matches:
        return None

    filenames = [os.path.basename(path) for path in matches]
    best_match = difflib.get_close_matches(search_query, filenames, n=1, cutoff=0.4)
    
    if best_match:
        for path in matches:
            if best_match[0] == os.path.basename(path):
                return path
    else:
        return matches[0]  

    return None

@tool
def openFile(fileName):
    """Searches for a file on the local machine and opens it"""
    result=search_files(fileName)
    os.startfile(result)
