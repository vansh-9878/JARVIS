import os,subprocess
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
    """Searches for a file on the local machine and opens it and """
    result=search_files(fileName)
    os.startfile(result)
    
def normalize(name):
    return ''.join(name.split()).lower()


@tool
def openProject(folderName):
    """Opens a folder/project on VS code and assume the folder is in a predefined base directory."""
    basePath1="C://Users/Vansh/Machine Learning"
    basePath2="C://Users/Vansh/Web Developement"
    for root, dirs, _ in os.walk(basePath1):
        for folder in dirs:
            if normalize(folder) == normalize(folderName):
                full_path = os.path.join(root, folder)
                try:
                    subprocess.Popen(["code", full_path], shell=True)
                    return f"VS Code opened in: {full_path}"
                except Exception as e:
                    return f"Failed to open VS Code: {str(e)}"
    for root, dirs, _ in os.walk(basePath2):
        for folder in dirs:
            if folder.lower() == folderName.lower():
                full_path = os.path.join(root, folder)
                try:
                    subprocess.Popen(["code", full_path], shell=True)
                    return f"✅ VS Code opened in: {full_path}"
                except Exception as e:
                    return f"❌ Failed to open VS Code: {str(e)}"
                
    return "Could not find the project you were looking for"