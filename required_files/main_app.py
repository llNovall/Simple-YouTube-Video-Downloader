import tkinter as tk
import tkinter.ttk as ttk
from turtle import title
from required_files.required import PlaylistDownloadFrame, VideoDownloadFrame, VerticalScrolledFrame, DownloadListFrame

class App(tk.Tk):
    def __init__(self):
        super(App, self).__init__()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        self.container_left = ttk.Frame(self)
        self.container_right = DownloadListFrame(parent=self, frame_title="Download List")
        
        self.container_left.pack(side="left", anchor=tk.N)
        self.container_right.pack(side="right", anchor=tk.N, fill=tk.BOTH)

        self.video_download_frame = VideoDownloadFrame(self.container_left, frame_title="Download Video", download_list=self.container_right)
        self.video_download_frame.pack(fill=tk.X)
        self.playlist_download_frame = PlaylistDownloadFrame(self.container_left, frame_title="Download Playlist", download_list=self.container_right)
        self.playlist_download_frame.pack(fill=tk.X)

def run_gui():
    
    app = App()
    app.geometry('1080x300')
    app.resizable(width=False, height=False)
    app.mainloop()
