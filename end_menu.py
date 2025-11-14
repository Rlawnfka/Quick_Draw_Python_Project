import customtkinter as ctk
from tkinter import messagebox

class DrawConfirmApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 윈도우 설정
        self.title("드로우 종료 확인")
        self.geometry("800x600")
        
        # 배경색 설정 
        self._set_appearance_mode("light")
        self.configure(fg_color="#d6655a")
        
        # 메인 프레임
        main_frame = ctk.CTkFrame(self, fg_color="#d6655a")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # 제목
        title_label = ctk.CTkLabel(
            main_frame,
            text="드로우 종료! 결과를 확인해보세요.",
            font=("Malgun Gothic", 28, "bold"),
            text_color="white"
        )
        title_label.pack(pady=(20, 30))
        
        # AI가 맞춘 그림 정보
        info_frame = ctk.CTkFrame(main_frame, fg_color="#d6655a")
        info_frame.pack(pady=20)
        
        ai_label = ctk.CTkLabel(
            info_frame,
            text="AI가 맞춘 그림 : n개",
            font=("Malgun Gothic", 18),
            text_color="white"
        )
        ai_label.pack()
        
        wrong_label = ctk.CTkLabel(
            info_frame,
            text="맞추지 못한 그림 : (클래스 이름)",
            font=("Malgun Gothic", 18),
            text_color="white"
        )
        wrong_label.pack(pady=5)
        
        instruction_label = ctk.CTkLabel(
            info_frame,
            text="그림을 클릭해서 다른 사람의 그림을 확인해보세요!",
            font=("Malgun Gothic", 16),
            text_color="white"
        )
        instruction_label.pack(pady=5)
        
        # 그림 그리드 (2x3)
        grid_frame = ctk.CTkFrame(main_frame, fg_color="#d6655a")
        grid_frame.pack(pady=40, expand=True)
        
        # 그리드 설정
        for i in range(2):
            grid_frame.grid_rowconfigure(i, weight=1)
        for j in range(3):
            grid_frame.grid_columnconfigure(j, weight=1)
        
        # 6개의 그림 버튼 생성
        self.buttons = []
        for row in range(2):
            for col in range(3):
                btn = ctk.CTkButton(
                    grid_frame,
                    text="(사용자가 그린 그림)",
                    font=("Malgun Gothic", 16, "bold"),
                    width=200,
                    height=120,
                    fg_color="white",
                    text_color="black",
                    hover_color="#F0F0F0",
                    corner_radius=10,
                    command=lambda r=row, c=col: self.on_button_click(r, c)
                )
                btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
                self.buttons.append(btn)
    
    def on_button_click(self, row, col):
        """버튼 클릭 시 실행되는 함수"""
        button_num = row * 3 + col + 1
        messagebox.showinfo("그림 확인", f"{button_num}번 그림을 선택했습니다!")

if __name__ == "__main__":
    # CustomTkinter 테마 설정
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    app = DrawConfirmApp()
    app.mainloop()