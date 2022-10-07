import tkinter as tk
import tkinter.ttk as ttk
from tkinter import DISABLED, NORMAL, filedialog
from typing import Callable
from pytube import YouTube, request
from threading import Thread
import regex as re
    
class App(tk.Tk):
    
    class DownloadThread(Thread):
        def __init__(self, yt_stream, title: str, save_location: str, enable_btn_download: Callable[[bool], None], show_btn_cancel: Callable[[bool], None], on_progress_callback: Callable[[int, int], None]):
            super(App.DownloadThread, self).__init__()

            self.yt_stream = yt_stream
            self.save_location = save_location
            self.is_downloading_stopped = False
            self.enable_btn_download = enable_btn_download
            self.show_btn_cancel = show_btn_cancel
            self.on_progress_callback = on_progress_callback
            self.title = title
            
        def run(self) -> None:
            print(f'Downloading...')
            self.download_video()
        
        def stop_downloading(self):
            self.is_downloading_stopped = True
        
        def download_video(self):
            
            self.show_btn_cancel(True)
            self.enable_btn_download(False)
            
            try:
                
                with open(f'{self.save_location}/{self.title}.mp4','xb') as f:
                    
                    stream = request.stream(self.yt_stream.url)
                    file_size = self.yt_stream.filesize
                    downloaded_size = 0
                    
                    while True:
                        if self.is_downloading_stopped:
                            print("Downloading stopped...")
                            break
                        
                        chunck = next(stream, None)
                        
                        if chunck:
                            f.write(chunck)
                            downloaded_size += len(chunck)
                            self.on_progress_callback(downloaded_size, file_size)
                            
                        else:
                            print(f"Download Complete")
                            break
                            
                print(f'Closing...')
                            
            except Exception as e:
                print(e)                  
            
            self.show_btn_cancel(False)
            self.enable_btn_download(True)

    def __init__(self):
        super().__init__()
        
        self.initialize(title="Youtube Video Downloader", width=650, height=200)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 2)
        self.columnconfigure(3, weight = 1)
        
        self.download_link = tk.StringVar()
        self.save_location = tk.StringVar()
        self.dl_thread = None
        
        self.create_download_link_widget()
        self.create_save_location_widget()
        self.btn_download = self.create_download_button_widget()
        self.btn_cancel = self.create_cancel_button_widget()
        self.pb_download = self.create_progress_bar()
        
    def initialize(self, title, width, height):
        self.title(title)
        self.resizable(width=False, height=False)
        # TODO: Add an icon for the app
        self.iconbitmap()
        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(screen_width/2 - width / 2)
        center_y = int(screen_height/2 - height / 2)
        
        self.geometry(f"{width}x{height}+{center_x}+{center_y}")

    def create_download_link_widget(self):
        
        lbl_download_link = ttk.Label(self, text="Url", justify="left", width=20)
        ent_downLoad_link = ttk.Entry(master=self, width=75, textvariable=self.download_link)
        ent_downLoad_link.focus()
        
        lbl_download_link.grid(column=0, row=0, padx=10, pady=(30,10))
        ent_downLoad_link.grid(column=1, columnspan=2, row=0, padx=10, pady=(30,10))
        
    def create_save_location_widget(self):
        
        lbl_save_location = ttk.Label(self, text="Save Location", justify="left", width=20)
        ent_save_location = ttk.Entry(master=self, width=75, textvariable=self.save_location)
        btn_save_location = ttk.Button(self, text="Loc Find", command=self.on_click_save_location)
        
        lbl_save_location.grid(column=0, row=1, padx=10, pady=10)
        ent_save_location.grid(column=1, columnspan=2, row=1, padx=10, pady=10)
        btn_save_location.grid(column=3, row=1, padx=10, pady=10)
        
    def create_download_button_widget(self) -> ttk.Button:
        
        btn_download = ttk.Button(self, text="Download", width=35, command=self.on_click_download)
        btn_download.grid(column=2, row=2, padx=10, pady=10, sticky=tk.E)
        
        return btn_download
        
    def create_progress_bar(self) -> ttk.Progressbar:
        
        pb_download = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=600) 
        pb_download.grid(column=0, columnspan=3, row=3, sticky=tk.W, padx=10, pady=10)
        
        return pb_download
    
    def create_cancel_button_widget(self) -> ttk.Button:
        
        btn_cancel = ttk.Button(self, text="Cancel", width=35, command=self.on_click_cancel)
        
        return btn_cancel    
    
    def on_click_download(self):
        print(f'DL : {self.download_link.get()}, SL :{self.save_location.get()}')
        
        if (self.download_link.get() != "") and (self.save_location.get() != ""):
            print(f'Attenpting to download: {self.download_link.get()} and save to {self.save_location.get()}')
            
            yt = YouTube(self.download_link.get())
            yt_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('abr').desc().first()
            
            if yt_stream is not None:
                
                self.dl_thread = self.DownloadThread(yt_stream=yt_stream, title=self.clean_yt_title(yt_stream.title),
                                                     save_location=self.save_location.get(), 
                                                     enable_btn_download=self.enable_btn_download, show_btn_cancel=self.show_btn_cancel, 
                                                     on_progress_callback=self.on_download_progress)
                
                self.dl_thread.start()
                
    def show_btn_cancel(self, enable: bool):
        if enable:
            print(f'Enabling Cancel Button...')
            self.btn_cancel.grid(column=1, row=2, padx=10, pady=10, sticky=tk.W)
        else:
            print(f'Disabling Cancel Button...')
            self.btn_cancel.grid_forget()
            
    def on_click_cancel(self):
        
        if isinstance(self.dl_thread, self.DownloadThread):
            print(f'Stoping Download Thread...')
            self.dl_thread.stop_downloading()
            self.pb_download["value"] = 0
            
    def enable_btn_download(self, enable:bool):

        if enable == True:
            print(f'Enabling Download Button...')
            self.btn_download["state"] = tk.NORMAL
        else:
            print(f'Disabling Download Button...')
            self.btn_download["state"] = tk.DISABLED
    
    @staticmethod
    def clean_yt_title(title: str):
        title = re.sub(r'[-\+!~@#$%^&*()={}\[\]:;<.>?/\'"]', '', title)
        return title
    
    def on_click_save_location(self):
        
        path = filedialog.askdirectory(mustexist=True)
        self.save_location.set(path)
        
    def on_download_progress(self, cur_size, max_size):

        prog_value = (cur_size / max_size) * 100      
        self.pb_download['value'] = prog_value
        print(f'Progress ---> CurSize : {cur_size}, MaxSize : {max_size}, prog_value : {prog_value}')
        
def run_gui():
    
    app = App()
    app.mainloop()

