import customtkinter as ctk
import subprocess

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("퀵, 드뤄우.")
app.geometry("800x600")

# 붉은 배경
app.configure(fg_color="#d6655a")

# 제목
title = ctk.CTkLabel(app, text="퀵, 드뤄우.", font=("맑은 고딕", 42, "bold"), text_color="white")
title.place(relx=0.5, rely=0.4, anchor="center")

# 시작 버튼
def start_game():
    subprocess.Popen(["python", "draw_app.py"])

start_btn = ctk.CTkButton(app, text="시작하기", width=160, height=60, fg_color="#c45247", hover_color="#b3453a")
start_btn.place(relx=0.5, rely=0.55, anchor="center")

app.mainloop()
