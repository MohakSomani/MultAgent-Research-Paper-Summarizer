import os
from huggingface_hub import hf_hub_download
from pathlib import Path

def download_model():
    model_dir = Path("./models")
    model_dir.mkdir(exist_ok=True)
    
    model_id = os.getenv("HUGGINGFACE_MODEL_ID", "TheBloke/Llama-2-7B-GGUF")
    filename = os.getenv("HUGGINGFACE_FILENAME", "llama-2-7b.Q4_K_M.gguf")
    model_path = model_dir / filename
    
    if not model_path.exists():
        print(f"Downloading {model_id}/{filename}...")
        model_path = hf_hub_download(
            repo_id=model_id,
            filename=filename,
            local_dir=model_dir
        )
        print(f"Model downloaded to {model_path}")
    else:
        print(f"Model already exists at {model_path}")
    
    return model_path

if __name__ == "__main__":
    download_model()
