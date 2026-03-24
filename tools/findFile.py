import os,subprocess
from langchain_core.tools import tool
from rapidfuzz import fuzz
from dotenv import load_dotenv
load_dotenv()

def search_files(search_query, search_path="D:\\"):
    print(f"Searching for '{search_query}' in {search_path}...")
    scored_matches = []

    for root, dirs, files in os.walk(search_path):
        for filename in files:
            score = fuzz.partial_ratio(search_query.lower(), filename.lower())
            if score >= 80:
                full_path = os.path.join(root, filename)
                scored_matches.append((full_path, score))
                print(f"  Match ({score}%): {full_path}")

    if not scored_matches:
        print("No matches found above 80% threshold.")
        return None

    scored_matches.sort(key=lambda x: x[1], reverse=True)
    best_path, best_score = scored_matches[0]
    print(f"\nBest match ({best_score}%): {best_path}")
    return best_path

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
    basePath1=os.getenv("BASE_PATH1")
    basePath2=os.getenv("BASE_PATH2")
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
                    return f"VS Code opened in: {full_path}"
                except Exception as e:
                    return f"Failed to open VS Code: {str(e)}"
                
    return "Could not find the project you were looking for"

# openFile("conservation economics.pdf")