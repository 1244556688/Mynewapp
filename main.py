import os
import pygame
import threading
import time
from tkinter import filedialog
import customtkinter as ctk

# 設定外觀模式與顏色主題
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernMusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 初始化視窗設定
        self.title("Modern Python Music Player")
        self.geometry("900x600")

        # 初始化 Pygame Mixer
        pygame.mixer.init()

        # 變數初始化
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        self.music_folder = ""

        # 建立 UI 配置
        self._setup_ui()

        # 啟動進度條更新執行緒
        self.update_thread_running = True
        self.update_thread = threading.Thread(target=self._update_progress_loop, daemon=True)
        self.update_thread.start()

    def _setup_ui(self):
        """建立現代化的 UI 介面佈局"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 左側面板：播放列表 ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="播放列表", font=ctk.CTkFont(size=20, weight="bold"))
        self.sidebar_label.pack(pady=20, padx=10)

        self.btn_import = ctk.CTkButton(self.sidebar, text="導入音樂資料夾", command=self.load_folder)
        self.btn_import.pack(pady=10, padx=20)

        self.song_listbox = ctk.CTkScrollableFrame(self.sidebar, label_text="曲目")
        self.song_listbox.pack(expand=True, fill="both", padx=10, pady=10)
        self.song_buttons = []

        # --- 右側面板：控制中心 ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 歌曲名稱顯示
        self.track_label = ctk.CTkLabel(self.main_frame, text="尚未選擇歌曲", font=ctk.CTkFont(size=24, weight="bold"))
        self.track_label.grid(row=0, column=0, pady=(60, 20))

        # 進度條
        self.progress_slider = ctk.CTkSlider(self.main_frame, from_=0, to=100, command=self.seek_music)
        self.progress_slider.set(0)
        self.progress_slider.grid(row=2, column=0, padx=40, pady=20, sticky="ew")

        self.time_label = ctk.CTkLabel(self.main_frame, text="00:00 / 00:00")
        self.time_label.grid(row=3, column=0)

        # 控制按鈕區
        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.grid(row=4, column=0, pady=40)

        self.btn_prev = ctk.CTkButton(self.controls_frame, text="⏮", width=60, command=self.prev_track)
        self.btn_prev.grid(row=0, column=0, padx=10)

        self.btn_play = ctk.CTkButton(self.controls_frame, text="▶ 播放", width=100, command=self.toggle_play)
        self.btn_play.grid(row=0, column=1, padx=10)

        self.btn_next = ctk.CTkButton(self.controls_frame, text="⏭", width=60, command=self.next_track)
        self.btn_next.grid(row=0, column=2, padx=10)

        # 音量控制區
        self.volume_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.volume_frame.grid(row=5, column=0, pady=10)
        
        self.volume_label = ctk.CTkLabel(self.volume_frame, text="音量")
        self.volume_label.grid(row=0, column=0, padx=10)
        
        self.volume_slider = ctk.CTkSlider(self.volume_frame, from_=0, to=1, command=self.set_volume, width=150)
        self.volume_slider.set(0.7)
        pygame.mixer.music.set_volume(0.7)
        self.volume_slider.grid(row=0, column=1, padx=10)

    def load_folder(self):
        """開啟資料夾並載入 MP3 檔案"""
        folder = filedialog.askdirectory()
        if folder:
            self.music_folder = folder
            self.playlist = [f for f in os.listdir(folder) if f.endswith(('.mp3', '.wav', '.ogg'))]
            self._refresh_playlist_ui()

    def _refresh_playlist_ui(self):
        """更新側邊欄的歌曲列表按鈕"""
        for btn in self.song_buttons:
            btn.destroy()
        self.song_buttons = []

        for i, song in enumerate(self.playlist):
            btn = ctk.CTkButton(self.song_listbox, text=song, anchor="w", 
                                fg_color="transparent", text_color="white",
                                command=lambda idx=i: self.play_music(idx))
            btn.pack(fill="x", pady=2)
            self.song_buttons.append(btn)

    def play_music(self, index):
        """播放指定索引的歌曲"""
        if 0 <= index < len(self.playlist):
            self.current_index = index
            song_path = os.path.join(self.music_folder, self.playlist[index])
            
            try:
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.btn_play.configure(text="⏸ 暫停")
                self.track_label.configure(text=self.playlist[index])
                
                # 獲取歌曲長度 (秒)
                sound = pygame.mixer.Sound(song_path)
                self.song_length = sound.get_length()
                self.progress_slider.configure(to=self.song_length)
            except Exception as e:
                print(f"播放出錯: {e}")

    def toggle_play(self):
        """切換播放與暫停狀態"""
        if not self.playlist:
            return

        if not self.is_playing:
            self.play_music(0 if self.current_index == -1 else self.current_index)
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.btn_play.configure(text="⏸ 暫停")
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.btn_play.configure(text="▶ 播放")

    def next_track(self):
        """播放下一首"""
        if self.playlist:
            next_idx = (self.current_index + 1) % len(self.playlist)
            self.play_music(next_idx)

    def prev_track(self):
        """播放上一首"""
        if self.playlist:
            prev_idx = (self.current_index - 1) % len(self.playlist)
            self.play_music(prev_idx)

    def set_volume(self, value):
        """設定音量"""
        pygame.mixer.music.set_volume(float(value))

    def seek_music(self, value):
        """跳轉播放進度 (Pygame 的 set_pos 在 MP3 上支援度有限，通常從頭計算)"""
        if self.is_playing:
            # 由於 pygame.mixer.music.set_pos 對於不同格式支援不一
            # 這裡僅更新 UI 邏輯，進階開發可使用更專業的庫如 pydub
            pass

    def _update_progress_loop(self):
        """後台執行緒：每秒更新進度條與時間標籤"""
        while self.update_thread_running:
            if self.is_playing and not self.is_paused:
                # get_pos() 返回毫秒
                current_pos = pygame.mixer.music.get_pos() / 1000
                if current_pos >= 0:
                    self.progress_slider.set(current_pos)
                    
                    # 格式化時間
                    mins, secs = divmod(int(current_pos), 60)
                    total_mins, total_secs = divmod(int(self.song_length), 60)
                    self.time_label.configure(
                        text=f"{mins:02d}:{secs:02d} / {total_mins:02d}:{total_secs:02d}"
                    )
            
            time.sleep(0.5)

    def on_closing(self):
        """關閉程式時釋放資源"""
        self.update_thread_running = False
        pygame.mixer.quit()
        self.destroy()

if __name__ == "__main__":
    app = ModernMusicPlayer()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
