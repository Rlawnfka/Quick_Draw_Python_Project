import numpy as np
import cv2
import customtkinter as ctk
from PIL import Image, ImageDraw

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("퀵, 드뤄우.")
app.geometry("1000x800")
app.configure(fg_color="#d6655a")

# 메인 화면
main_frame = ctk.CTkFrame(app, fg_color="#d6655a")
main_frame.pack(fill="both", expand=True)

title = ctk.CTkLabel(main_frame, text="퀵, 드뤄우.", font=("맑은 고딕", 48, "bold"), text_color="white")
title.place(relx=0.5, rely=0.4, anchor="center")

def go_to_draw():
    main_frame.pack_forget()
    draw_frame.pack(fill="both", expand=True)

start_btn = ctk.CTkButton(main_frame, text="시작하기", width=160, height=60,
                          fg_color="#c45247", hover_color="#b3453a",
                          command=go_to_draw)
start_btn.place(relx=0.5, rely=0.55, anchor="center")
draw_frame = ctk.CTkFrame(app, fg_color="white")

canvas_width, canvas_height = 900, 600
canvas = ctk.CTkCanvas(draw_frame, width=canvas_width, height=canvas_height,
                       bg="white", highlightthickness=2, highlightbackground="#d6655a")
canvas.pack(pady=20)

# 이미지 저장용
image = Image.new("RGB", (canvas_width, canvas_height), "white")
draw = ImageDraw.Draw(image)

# 선 데이터 관리
strokes = []         # 그려진 선들의 리스트
redo_stack = []      # 되돌리기 후 다시 복원할 선들
current_stroke = []  # 현재 그리고 있는 선

def start_draw(event):
    global current_stroke
    current_stroke = [(event.x, event.y)]

def draw_line(event):
    if current_stroke:
        x1, y1 = current_stroke[-1]
        x2, y2 = event.x, event.y
        canvas.create_line(x1, y1, x2, y2, fill="black", width=5)
        current_stroke.append((x2, y2))

def end_draw(event):
    global current_stroke
    if current_stroke:
        strokes.append(current_stroke)
        redo_stack.clear()  # 새로 그리면 redo 초기화
        current_stroke = []

canvas.bind("<Button-1>", start_draw)
canvas.bind("<B1-Motion>", draw_line)
canvas.bind("<ButtonRelease-1>", end_draw)

# 다시 그리기 함수 (전체 갱신용)
def redraw_all():
    canvas.delete("all")
    for stroke in strokes:
        for i in range(len(stroke) - 1):
            x1, y1 = stroke[i]
            x2, y2 = stroke[i + 1]
            canvas.create_line(x1, y1, x2, y2, fill="black", width=5)

# 버튼 기능
def clear_canvas():
    strokes.clear()
    redo_stack.clear()
    canvas.delete("all")

def undo():
    if strokes:
        redo_stack.append(strokes.pop())
        redraw_all()

def redo():
    if redo_stack:
        strokes.append(redo_stack.pop())
        redraw_all()

def save_drawing():
    img = Image.new("RGB", (canvas_width, canvas_height), "white")
    d = ImageDraw.Draw(img)
    for stroke in strokes:
        for i in range(len(stroke) - 1):
            d.line([stroke[i], stroke[i + 1]], fill="black", width=5)

        for i in range(len(stroke[0]) - 1) : 
            x1, y1 = stroke[0][i], stroke[1][i]
            x2, y2 = stroke[0][i+1], stroke[1][i+1]
            cv2.line(img,(x1,y1),(x2,y2),255,1)
        
    img.save("drawing.png")
    print("✅ drawing.png 저장 완료")

# 버튼 배치
btn_frame = ctk.CTkFrame(draw_frame, fg_color="white")
btn_frame.pack(pady=10)

clear_btn = ctk.CTkButton(btn_frame, text="지우기", command=clear_canvas,
                           fg_color="#d6655a", hover_color="#c4544b")
clear_btn.grid(row=0, column=0, padx=10)

undo_btn = ctk.CTkButton(btn_frame, text="↩ 뒤로가기", command=undo,
                          fg_color="#d6655a", hover_color="#c4544b")
undo_btn.grid(row=0, column=1, padx=10)

redo_btn = ctk.CTkButton(btn_frame, text="↪ 다시하기", command=redo,
                          fg_color="#d6655a", hover_color="#c4544b")
redo_btn.grid(row=0, column=2, padx=10)

save_btn = ctk.CTkButton(btn_frame, text="저장", command=save_drawing,
                          fg_color="#d6655a", hover_color="#c4544b")
save_btn.grid(row=0, column=3, padx=10)

back_btn = ctk.CTkButton(btn_frame, text="뒤로", fg_color="#999999", hover_color="#777777",
                          command=lambda: (draw_frame.pack_forget(), main_frame.pack(fill="both", expand=True)))
back_btn.grid(row=0, column=4, padx=10)

app.mainloop()
