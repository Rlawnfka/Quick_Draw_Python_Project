# draw_app.py
import os
import random
import numpy as np
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image, ImageDraw
from tensorflow.keras.models import load_model

# 모델 로드
model = load_model("models/quickdraw_model.h5")
CLASSES = sorted([f.replace(".ndjson", "") for f in os.listdir("data") if f.endswith(".ndjson")])

# 색상/변수들
RED = "#d6655a"
WHITE = "#ffffff"

strokes = []
redo_stack = []
current_stroke = []
current_color = "black"

# 라운드 관련
round_index = 0
round_total = 5
round_words = []
correct_count = 0
wrong_list = []
time_left = 20
round_timer_id = None
target_word = ""

# 캔버스 크기
CANVAS_W = 1100
CANVAS_H = 420
SQUARE_SIZE = 420

# CTk 기본 설정
ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("퀵, 드뤄우.")
app.geometry("1280x720")
app.resizable(False, False)

# 바깥 붉은 테두리
outer = ctk.CTkFrame(app, fg_color=RED, corner_radius=30)
outer.pack(fill="both", expand=True, padx=15, pady=15)

inner = ctk.CTkFrame(outer, fg_color=WHITE, corner_radius=25)
inner.pack(fill="both", expand=True, padx=18, pady=18)

inner.grid_rowconfigure(0, weight=12)
inner.grid_rowconfigure(1, weight=70)
inner.grid_rowconfigure(2, weight=18)
inner.grid_columnconfigure(0, weight=1)

# 제시어+시작 버튼+타이머
header = ctk.CTkFrame(inner, fg_color=WHITE)
header.grid(row=0, column=0, sticky="nsew", pady=(5, 5), padx=5)
header.grid_columnconfigure(0, weight=1)
header.grid_columnconfigure(1, weight=1)
header.grid_columnconfigure(2, weight=1)

# 제시어 박스
word_frame = ctk.CTkFrame(header, fg_color=RED, corner_radius=12, width=260, height=60)
word_frame.grid(row=0, column=0, sticky="w", padx=(40,0), pady=(5,0))
word_frame.grid_propagate(False)
word_label = ctk.CTkLabel(word_frame, text="제시어:", font=("맑은 고딕", 24, "bold"), text_color=WHITE)
word_label.place(relx=0.5, rely=0.5, anchor="center")

# 게임시작 버튼
start_btn = ctk.CTkButton(header, text="게임 시작", width=160, height=60,
                          fg_color=RED, hover_color="#c4544b",
                          font=("맑은 고딕", 22, "bold"))
start_btn.grid(row=0, column=1, sticky="e", padx=(0,40), pady=(5,0))

# 타이머 Label
timer_label = ctk.CTkLabel(header, text="남은 시간: 20", font=("맑은 고딕", 20, "bold"), text_color=RED)
timer_label.grid(row=0, column=2, sticky="e", padx=(0,40), pady=(5,0))

# 캔버스 + 그림도구들
center = ctk.CTkFrame(inner, fg_color=WHITE)
center.grid(row=1, column=0, sticky="nsew", pady=(5,5), padx=5)
center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(0, weight=1)

# 캔버스 전체 테두리
board = ctk.CTkFrame(center, fg_color=WHITE, border_width=4, border_color=RED, corner_radius=12)
board.grid(row=0, column=0, sticky="nsew", padx=40, pady=5)
board.grid_rowconfigure(0, weight=1)
board.grid_columnconfigure(0, weight=1)
board.grid_columnconfigure(1, weight=0)

# 실제 캔버스
canvas = ctk.CTkCanvas(board, width=CANVAS_W, height=CANVAS_H, bg="white", highlightthickness=0)
canvas.grid(row=0, column=0, sticky="nsew", padx=(15,0), pady=15)

# 오른쪽 도구 버튼
tools = ctk.CTkFrame(board, fg_color=WHITE)
tools.grid(row=0, column=1, sticky="ns", padx=(10,15), pady=15)

def make_tool_btn(text, cmd):
    btn = ctk.CTkButton(tools, text=text, width=70, height=50, fg_color=RED,
                        hover_color="#c4544b", font=("맑은 고딕",18), command=cmd)
    return btn

undo_btn = make_tool_btn("↩", lambda: undo())
redo_btn = make_tool_btn("↪", lambda: redo())
clear_btn = make_tool_btn("지우기", lambda: clear_canvas())

undo_btn.pack(pady=10)
redo_btn.pack(pady=10)
clear_btn.pack(pady=10)

# 하단 말풍선
bottom = ctk.CTkFrame(inner, fg_color=WHITE)
bottom.grid(row=2, column=0, sticky="nsew", pady=(5,5), padx=5)

bubble = ctk.CTkFrame(bottom, fg_color=WHITE, border_width=4, border_color=RED, corner_radius=15)
bubble.pack(fill="both", expand=True, padx=40, pady=(0,5))

try:
    img = Image.open("assets/gadi.png").resize((70,70))
    gadi_img = CTkImage(light_image=img, size=(70,70))
    gadi_label = ctk.CTkLabel(bubble, image=gadi_img, text="")
    gadi_label.place(x=20, rely=0.5, anchor="w")
except Exception:
    gadi_label = ctk.CTkLabel(bubble, text="[가디]", font=("맑은 고딕",16))
    gadi_label.place(x=20, rely=0.5, anchor="w")

ai_label = ctk.CTkLabel(bubble, text="그림을 그리면 제가 맞춰볼게요!",
                        font=("맑은 고딕",20), text_color="#333")
ai_label.place(relx=0.5, rely=0.5, anchor="center")

# 드로잉 로직
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
        predict_after_stroke()

canvas.bind("<Button-1>", start_draw)
canvas.bind("<B1-Motion>", draw_line)
canvas.bind("<ButtonRelease-1>", end_draw)

# AI 예측 
from PIL import ImageOps

def get_prediction():
    if not strokes:
        return None  # 그림 없으면 None

    # 캔버스를 정사각형 이미지로 변환
    img = Image.new("L", (SQUARE_SIZE, SQUARE_SIZE), 255)
    draw = ImageDraw.Draw(img)
    offset_y = (SQUARE_SIZE - CANVAS_H)//2

    for stroke, color in strokes:
        for i in range(len(stroke)-1):
            x1, y1 = stroke[i]
            x2, y2 = stroke[i+1]
            draw.line([x1, y1+offset_y, x2, y2+offset_y], fill=0, width=5)

    # 비율 유지하면서 정사각형
    img_square = ImageOps.fit(img, (28,28), method=Image.LANCZOS)
    arr = np.array(img_square)/255.0

    input_shape = model.input_shape 
    if len(input_shape) == 4:
        arr = arr.reshape(1, input_shape[1], input_shape[2], input_shape[3])
    elif len(input_shape) == 3:
        arr = arr.reshape(1, input_shape[1], input_shape[2])
    else:
        raise ValueError("모델 입력 형태를 확인하세요")

    # 예측
    pred = model.predict(arr, verbose=0)
    idx = int(np.argmax(pred))
    label = CLASSES[idx]
    prob = pred[0][idx]*100

    return label, prob


def predict_after_stroke():
    if target_word == "" or not strokes:
        ai_label.configure(text="그림을 그려주세요!")
        return

    label, prob = get_prediction()
    if label is None:
        ai_label.configure(text="그림을 그려주세요!")
        return

    if label == target_word:
        ai_label.configure(text=f"이제 알겠어요! 정답은 {label}에요.")
    else:
        ai_label.configure(text=f"음.. 이건 {label} 인가요?")

# 캔버스/도구 기능
def redraw_all():
    canvas.delete("all")
    for stroke, color in strokes:
        for i in range(len(stroke)-1):
            x1, y1 = stroke[i]
            x2, y2 = stroke[i+1]
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
    ai_label.configure(text="")

app.bind_all("<Control-z>", lambda event: undo())
app.bind_all("<Control-Z>", lambda event: undo())
app.bind_all("<Control-y>", lambda evnet: redo())
app.bind_all("<Control-Y>", lambda event: redo())

# 라운드/타이머
def prepare_rounds():
    global round_words, round_index, correct_count, wrong_list
    round_index = 0
    correct_count = 0
    wrong_list = []
    round_words = random.sample(CLASSES, round_total)

def start_round():
    global target_word, time_left, round_timer_id
    if round_index >= round_total:
        return finish_game()
    target_word = round_words[round_index]
    word_label.configure(text=f"제시어: {target_word}")
    ai_label.configure(text="그림을 그려주세요!")
    clear_canvas()
    time_left = 20
    timer_label.configure(text=f"남은 시간: {time_left}")
    # 이전 타이머 취소
    if round_timer_id:
        app.after_cancel(round_timer_id)
    update_timer()

def update_timer():
    global time_left, round_timer_id
    if time_left > 0:
        timer_label.configure(text=f"남은 시간: {time_left}")
        time_left -= 1
        round_timer_id = app.after(1000, update_timer)
    else:
        end_round()

def end_round():
    global correct_count, wrong_list, round_index
    label, prob = get_prediction()
    if label == target_word :
        correct_count += 1
    else:
        wrong_list.append(target_word)
    round_index += 1
    if round_index >= round_total : 
        finish_game()
        return
    
    start_round()

# 게임 종료 
def finish_game():
    global round_timer_id
    if round_timer_id:
        app.after_cancel(round_timer_id)
    inner.destroy()
    end_screen = ctk.CTkFrame(outer, fg_color=WHITE, corner_radius=25)
    end_screen.pack(fill="both", expand=True, padx=18, pady=18)

    title = ctk.CTkLabel(end_screen, text="게임 종료!", font=("맑은 고딕",40,"bold"), text_color=RED)
    title.pack(pady=30)

    score = ctk.CTkLabel(end_screen, text=f"맞춘 문제: {correct_count}/{round_total}",
                         font=("맑은 고딕",30), text_color="#333")
    score.pack(pady=20)

    wrong_text = "\n".join(wrong_list) if wrong_list else "없음"
    wrong_label = ctk.CTkLabel(end_screen, text=f"틀린 문제:\n{wrong_text}",
                               font=("맑은 고딕",24), text_color="#333")
    wrong_label.pack(pady=20)

# 게임 전체 시작
def start_game():
    start_btn.configure(state="disabled")
    prepare_rounds()
    start_round()

start_btn.configure(command=start_game)
app.mainloop()