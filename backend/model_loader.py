import json
from pathlib import Path

import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "model.h5"
MAPPING_PATH = BASE_DIR / "label_mapping.json"
MAX_SEQUENCE_LEN = 4

# Wraps the trained LSTM model and exposes a simple predict_top_k() interface
class NextPagePredictor:
    def __init__(self,
                 model_path: Path = MODEL_PATH,
                 mapping_path: Path = MAPPING_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {model_path}. "
                f"Run train_model.py locally to generate model.h5."
            )

        if not mapping_path.exists():
            raise FileNotFoundError(
                f"Label mapping not found at {mapping_path}. "
                f"Run train_model.py locally to generate label_mapping.json."
            )

        self.model = load_model(model_path)

        with open(mapping_path, "r") as f:
            mapping = json.load(f)

        classes = mapping.get("classes")
        if not classes:
            raise ValueError("Invalid label_mapping.json")

        self.classes = classes
        self.page_to_id = {page: idx for idx, page in enumerate(self.classes)}
        self.id_to_page = {idx: page for idx, page in enumerate(self.classes)}

    def _encode_history(self, history_pages):
        ids = [self.page_to_id[p] for p in history_pages if p in self.page_to_id]
        if not ids:
            return None
        seq = pad_sequences([ids], maxlen=MAX_SEQUENCE_LEN, padding="pre")
        return seq

    def predict_top_k(self, history_pages, k: int = 2):
        seq = self._encode_history(history_pages)
        if seq is None:
            return []

        probs = self.model.predict(seq, verbose=0)[0]
        k = max(1, min(k, len(probs)))
        top_indices = np.argsort(probs)[-k:][::-1]
        return [self.id_to_page[i] for i in top_indices]
