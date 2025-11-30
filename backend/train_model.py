import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.utils import to_categorical
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
NAV_DATA_PATH = BASE_DIR / "navigation_data.csv"
MODEL_PATH = BASE_DIR / "model.h5"
MAPPING_PATH = BASE_DIR / "label_mapping.json"
MAX_SEQUENCE_LEN = 4
EMBEDDING_DIM = 8
LSTM_UNITS = 16

def load_navigation_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, comment="#")
    required_cols = {"session_id", "step", "page"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"navigation_data.csv must contain {required_cols}")
    return df

def build_sequences(df: pd.DataFrame, label_encoder: LabelEncoder):
    df = df.sort_values(["session_id", "step"])
    df["page_id"] = label_encoder.fit_transform(df["page"])

    sequences = []
    targets = []

    for session_id, group in df.groupby("session_id"):
        pages = group["page_id"].tolist()
        # build (history -> next_page) pairs
        for i in range(1, len(pages)):
            history = pages[:i]
            nxt = pages[i]
            sequences.append(history)
            targets.append(nxt)

    if not sequences:
        raise ValueError("Not enough data")

    X = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LEN, padding="pre")
    y = to_categorical(targets, num_classes=len(label_encoder.classes_))
    return X, y

def build_model(num_classes: int):
    model = Sequential([
        Embedding(input_dim=num_classes,
                  output_dim=EMBEDDING_DIM,
                  input_length=MAX_SEQUENCE_LEN),
        LSTM(LSTM_UNITS),
        Dense(num_classes, activation="softmax")
    ])
    model.compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"]
    )
    return model

def main():
    df = load_navigation_data(NAV_DATA_PATH)

    # Encoding pages
    le = LabelEncoder()
    X, y = build_sequences(df, le)

    num_classes = len(le.classes_)
    print(f"Detected {num_classes} unique pages:", list(le.classes_))

    # Model building
    model = build_model(num_classes)

    print("Training model")
    model.fit(
        X,
        y,
        epochs=10,
        batch_size=8,
        verbose=1,
        validation_split=0.2
    )

    print(f"Saving model to {MODEL_PATH}")
    model.save(MODEL_PATH)

    print(f"Saving label mapping to {MAPPING_PATH}")
    mapping = {"classes": le.classes_.tolist(),
               "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    with open(MAPPING_PATH, "w") as f:
        json.dump(mapping, f, indent=2)

    print("Done.")

if __name__ == "__main__":
    main()