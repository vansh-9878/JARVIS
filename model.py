import requests
import os

def download_gguf(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    existing_size = os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
    headers = {
        "Range": f"bytes={existing_size}-",
        "User-Agent": "Mozilla/5.0",  # ← HuggingFace blocks non-browser requests without this
    }

    response = requests.get(url, headers=headers, stream=True, timeout=60)

    # ── Validate we got the actual file, not an error page ──
    content_type = response.headers.get("content-type", "")
    if "text/html" in content_type:
        print("✗ Got an HTML page instead of the file.")
        print("  This usually means the URL is wrong or HuggingFace needs a token.")
        print(f"  Content-Type: {content_type}")
        print(f"  URL tried: {url}")
        return None

    total_size = int(response.headers.get("content-length", 0)) + existing_size
    downloaded = existing_size
    mode = "ab" if existing_size else "wb"

    print(f"File size     : {total_size / 1e9:.2f} GB")
    print(f"Already have  : {existing_size / 1e6:.1f} MB")
    print(f"Downloading to: {dest_path}\n")

    with open(dest_path, mode) as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    done_mb  = downloaded / 1e6
                    total_mb = total_size / 1e6
                    filled   = int(40 * downloaded / total_size)
                    bar      = "█" * filled + "░" * (40 - filled)
                    print(f"\r[{bar}] {percent:.1f}%  {done_mb:.0f}/{total_mb:.0f} MB",
                          end="", flush=True)

    print("\n\nDownload complete!")

    # ── Verify file starts with GGUF magic bytes ──
    with open(dest_path, "rb") as f:
        magic = f.read(4)
    if magic == b"GGUF":
        print("✓ File verified as valid GGUF format.")
    else:
        print(f"✗ File is NOT a valid GGUF (got: {magic}). Deleting corrupt file.")
        os.remove(dest_path)
        return None

    return dest_path


def create_modelfile(gguf_path, modelfile_path):
    with open(modelfile_path, "w") as f:
        f.write(f"FROM {gguf_path}\n")
        f.write('SYSTEM "You are a helpful assistant."\n')
    print(f"Modelfile created at: {modelfile_path}")


def import_to_ollama(modelfile_path, model_name="qwen2.5"):
    print(f"\nImporting into Ollama as '{model_name}'...")
    ret = os.system(f'ollama create {model_name} -f "{modelfile_path}"')
    if ret == 0:
        print(f"✓ Model '{model_name}' imported successfully!")
    else:
        print("✗ Import failed. Make sure Ollama is running.")


def verify_model():
    print("\nInstalled models:")
    os.system("ollama list")


if __name__ == "__main__":
    # ── Direct blob URL (more reliable than /resolve/main/) ──
    URL = (
    "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF"
    "/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    "?download=true"
    )
    DEST       = r"C:\Users\Vansh\models\Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    MODELFILE  = r"C:\Users\Vansh\models\Modelfile"
    MODEL_NAME = "qwen2.5"

    path = download_gguf(URL, DEST)
    if path:
        create_modelfile(path, MODELFILE)
        import_to_ollama(MODELFILE, MODEL_NAME)
        verify_model()
    else:
        print("\nDownload failed. Try the manual link below in your browser:")
        print("https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf?download=true")