"""Patch cell 4 (model load) and cell 2 (dependencies) for Gemma 3n E2B."""
import json
from pathlib import Path

NB_PATH = Path(__file__).parent / "nalama-gemma4-tamil-fixed-hosted.ipynb"

NEW_CELL_2 = '''# Cell 2 — Install dependencies (pinned for Gemma 3n)
# Force-reinstall Pillow first: Kaggle's pre-installed torchvision/PIL
# combination has a known _Ink import mismatch that breaks transformers.
!pip install -q -U --force-reinstall "pillow>=11.0,<12.0"
!pip install -q -U "transformers>=4.53.0" "accelerate>=0.34" "timm"
!pip install -q torch librosa soundfile
!apt-get install -q ffmpeg
print("Dependencies installed — RESTART KERNEL NOW")
'''

NEW_CELL_4 = '''# Cell 4 — Load Gemma 3n E2B (multimodal: text + audio + image)
# Class: AutoModelForImageTextToText is the right loader for Gemma 3n.
# We load straight to GPU; bfloat16 fits comfortably on a T4 with E2B (~6 GB).

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

MODEL_ID = "google/gemma-3n-E2B-it"

print(f"Loading processor for {MODEL_ID}...")
processor = AutoProcessor.from_pretrained(MODEL_ID)

print("Loading model (this takes ~60s on first run, model is ~6 GB)...")
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="cuda",
    low_cpu_mem_usage=True,
)
model.eval()

print(f"Model device: {next(model.parameters()).device}")
print(f"Gemma 3n loaded successfully: {MODEL_ID}")
'''


def main():
    nb = json.loads(NB_PATH.read_text())
    cells = nb["cells"]

    patched = []
    for i, c in enumerate(cells):
        if c["cell_type"] != "code":
            continue
        src = "".join(c.get("source", []))
        if i == 2 or ("pip install" in src and "transformers" in src and "Cell 2" in src):
            cells[i] = {
                "cell_type": "code", "metadata": {}, "execution_count": None,
                "outputs": [], "source": NEW_CELL_2.splitlines(keepends=True),
            }
            patched.append(("cell 2 (deps)", i))
        elif "from_pretrained" in src and ("gemma" in src.lower() or "AutoModelForMultimodalLM" in src):
            cells[i] = {
                "cell_type": "code", "metadata": {}, "execution_count": None,
                "outputs": [], "source": NEW_CELL_4.splitlines(keepends=True),
            }
            patched.append(("cell 4 (model load)", i))

    NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n")
    for name, idx in patched:
        print(f"Patched {name} at index {idx}")
    if not patched:
        print("WARNING: no cells matched. Notebook unchanged.")


if __name__ == "__main__":
    main()
