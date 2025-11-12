# draw_app.py
# 퀵드로우 게임형 (획 단위 예측, 45초 타이머, 색상 전환/되돌리기 기능 포함)

import os
import random
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageDraw
from tensorflow.keras.models import load_model

# ---------------- 모델 및 클래스 ----------------
model = load_model("models/quickdraw_model.h5")
CLASSES = sorted([f[:-7] for f in os.listdir("data") if f.endswith(".ndjson")])
print(f"AI 인식 클래스 {len(CLASSES)}개:", CLASSES)

# ---------------- UI 설정 ----------------
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("퀵, 드뤄우.")
app.geometry("1000x800")
app.configure(fg_color="#d6655a")

# ---------------- 메인 화면 ----------------
main_frame = ctk.CTkFrame(app, fg_color="#d6655a")
main_frame.pack(fill="both", expand=True)

title = ctk.CTkLabel(main_frame, text="퀵, 드뤄우.", font=("맑은 고딕", 48, "bold"), text_color="white")
title.place(relx=0.5, rely=0.35, anchor="center")

info = ctk.CTkLabel(main_frame, text="AI가 제시어를 내면 45초 안에 그려서 맞혀보세요!",
                    font=("맑은 고딕", 20), text_color="white")
info.place(relx=0.5, rely=0.45, anchor="center")

# ---------------- 전역 변수 ----------------
strokes = []
redo_stack = []
current_stroke = []
current_color = "black"
target_word = ""
time_left = 45
timer_job = None

# ---------------- 드로잉 프레임 ----------------
draw_frame = ctk.CTkFrame(app, fg_color="white")
canvas_width, canvas_height = 900, 600
canvas = ctk.CTkCanvas(draw_frame, width=canvas_width, height=canvas_height,
                       bg="white", highlightthickness=2, highlightbackground="#d6655a")
canvas.pack(pady=20)

# ---------------- 드로잉 함수 ----------------
def start_draw(event):
    global current_stroke
    current_stroke = [(event.x, event.y)]

def draw_line(event):
    if current_stroke:
        x1, y1 = current_stroke[-1]
        x2, y2 = event.x, event.y
        canvas.create_line(x1, y1, x2, y2, fill=current_color, width=5)
        current_stroke.append((x2, y2))

def end_draw(event):
    global current_stroke
    if current_stroke:
        strokes.append((current_stroke, current_color))
        redo_stack.clear()
        current_stroke = []
        predict_after_stroke()  # 획 그릴 때마다 즉시 예측

canvas.bind("<Button-1>", start_draw)
canvas.bind("<B1-Motion>", draw_line)
canvas.bind("<ButtonRelease-1>", end_draw)

# ---------------- AI 예측 ----------------
def get_prediction():
    img = Image.new("L", (canvas_width, canvas_height), 255)
    d = ImageDraw.Draw(img)
    for stroke, color in strokes:
        for i in range(len(stroke) - 1):
            d.line([stroke[i], stroke[i + 1]], fill=0, width=5)
    img = img.resize((28, 28))
    arr = np.array(img) / 255.0
    arr = arr.reshape(1, 28, 28, 1)
    pred = model.predict(arr, verbose=0)
    idx = int(np.argmax(pred))
    label = CLASSES[idx]
    prob = float(pred[0][idx]) * 100
    return label, prob

def predict_after_stroke():
    label, prob = get_prediction()
    if label == target_word and prob > 70:
        result_label.configure(text=f"✅ 정답! ({label}, {prob:.1f}%)", text_color="#008000")
        app.after_cancel(timer_job)
    else:
        result_label.configure(text=f"🤔 이건 {label} ({prob:.1f}%) 인가요?", text_color="#333333")

# ---------------- 타이머 ----------------
def update_timer():
    global time_left, timer_job
    if time_left > 0:
        time_left -= 1
        timer_label.configure(text=f"남은 시간: {time_left}초")
        timer_job = app.after(1000, update_timer)
    else:
        result_label.configure(text=f"⏰ 시간 초과! 정답은 {target_word}", text_color="#b00000")

# ---------------- 제시어 시작 ----------------
def start_game():
    global target_word, time_left, strokes, redo_stack, current_color
    strokes.clear()
    redo_stack.clear()
    canvas.delete("all")
    current_color = "black"
    target_word = random.choice(CLASSES)
    time_left = 45
    main_frame.pack_forget()
    draw_frame.pack(fill="both", expand=True)
    word_label.configure(text=f"제시어: {target_word}")
    timer_label.configure(text=f"남은 시간: {time_left}초")
    result_label.configure(text="")
    update_timer()

# ---------------- 편집 기능 ----------------
def redraw_all():
    canvas.delete("all")
    for stroke, color in strokes:
        for i in range(len(stroke) - 1):
            x1, y1 = stroke[i]
            x2, y2 = stroke[i + 1]
            canvas.create_line(x1, y1, x2, y2, fill=color, width=5)

def undo():
    if strokes:
        redo_stack.append(strokes.pop())
        redraw_all()

def redo():
    if redo_stack:
        strokes.append(redo_stack.pop())
        redraw_all()

def clear_canvas():
    strokes.clear()
    redo_stack.clear()
    canvas.delete("all")
    result_label.configure(text="")

def toggle_color():
    global current_color
    current_color = "red" if current_color == "black" else "black"
    color_label.configure(text=f"색상: {'빨강' if current_color == 'red' else '검정'}")

# ---------------- 버튼 영역 ----------------
btn_frame = ctk.CTkFrame(draw_frame, fg_color="white")
btn_frame.pack(pady=10)

undo_btn = ctk.CTkButton(btn_frame, text="↩ 한 획 뒤로", command=undo,
                          fg_color="#d6655a", hover_color="#c4544b")
undo_btn.grid(row=0, column=0, padx=10)

redo_btn = ctk.CTkButton(btn_frame, text="↪ 한 획 앞으로", command=redo,
                          fg_color="#d6655a", hover_color="#c4544b")
redo_btn.grid(row=0, column=1, padx=10)

clear_btn = ctk.CTkButton(btn_frame, text="전체 지우기", command=clear_canvas,
                           fg_color="#d6655a", hover_color="#c4544b")
clear_btn.grid(row=0, column=2, padx=10)

color_btn = ctk.CTkButton(btn_frame, text="색상 바꾸기", command=toggle_color,
                           fg_color="#3c9d5e", hover_color="#348a52")
color_btn.grid(row=0, column=3, padx=10)

back_btn = ctk.CTkButton(btn_frame, text="메인으로",
                          fg_color="#999999", hover_color="#777777",
                          command=lambda: (draw_frame.pack_forget(), main_frame.pack(fill="both", expand=True)))
back_btn.grid(row=0, column=4, padx=10)

# ---------------- 상태 라벨 ----------------
word_label = ctk.CTkLabel(draw_frame, text="제시어:", font=("맑은 고딕", 28, "bold"), text_color="#222")
word_label.pack(pady=10)

timer_label = ctk.CTkLabel(draw_frame, text="남은 시간:", font=("맑은 고딕", 24), text_color="#222")
timer_label.pack(pady=5)

color_label = ctk.CTkLabel(draw_frame, text="색상: 검정", font=("맑은 고딕", 20), text_color="#222")
color_label.pack(pady=5)

result_label = ctk.CTkLabel(draw_frame, text="", font=("맑은 고딕", 22, "bold"))
result_label.pack(pady=10)

# ---------------- 메인 시작 버튼 ----------------
start_btn = ctk.CTkButton(main_frame, text="시작하기", width=200, height=60,
                          fg_color="#c45247", hover_color="#b3453a",
                          command=start_game)
start_btn.place(relx=0.5, rely=0.6, anchor="center")

app.mainloop()
