# dataset.py
# NDJSON → 이미지 변환 → CNN 학습 → 모델 저장
import os
import ndjson
import numpy as np
from PIL import Image, ImageDraw
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical

DATA_DIR = "data"
MODEL_DIR = "models"
CLASSES = [f[:-7] for f in os.listdir(DATA_DIR) if f.endswith(".ndjson")]

# ndjson 데이터를 이미지로 변환
def load_data(class_name, count=1000, size=28):
    file_path = os.path.join(DATA_DIR, f"{class_name}.ndjson")
    with open(file_path, "r") as f:
        data = ndjson.load(f)

    images = []
    for d in data[:count]:
        img = Image.new("L", (256, 256), 255)
        draw = ImageDraw.Draw(img)
        for stroke in d["drawing"]:
            xy = list(zip(stroke[0], stroke[1]))
            draw.line(xy, fill=0, width=5)
        img = img.resize((size, size))
        images.append(np.array(img))
    return np.array(images)

# 데이터셋 구성
def prepare_dataset():
    X, y = [], []
    for i, cls in enumerate(CLASSES):
        imgs = load_data(cls)
        X.append(imgs)
        y += [i] * len(imgs)

    X = np.concatenate(X, axis=0)
    y = np.array(y)
    X = X / 255.0
    X = X.reshape(-1, 28, 28, 1)
    y = to_categorical(y, num_classes=len(CLASSES))
    return X, y

# 모델 학습 및 저장
def train_model():
    X, y = prepare_dataset()

    model = Sequential([
        Conv2D(16, (3, 3), activation="relu", input_shape=(28, 28, 1)),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(64, activation="relu"),
        Dense(len(CLASSES), activation="softmax")
    ])

    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    model.fit(X, y, epochs=5, batch_size=32)

    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save(os.path.join(MODEL_DIR, "quickdraw_model.h5"))
    print("✅ 모델 저장 완료 → models/quickdraw_model.h5")

if __name__ == "__main__":
    train_model()
