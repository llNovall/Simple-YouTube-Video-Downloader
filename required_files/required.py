import tkinter as tk
import tkinter.ttk as ttk
from threading import Thread
from pytube import YouTube, request, Playlist
from typing import Callable
from tkinter import filedialog
import regex as re

def clean_yt_title(title: str):
    title = re.sub(r'[-\+!~@#$%^&*()={}\[\]:;<.>?/\'"]', '', title)
    return title

class DownloadThread(Thread):
        def __init__(self, yt_stream, title: str, save_location: str, on_progress_callback: Callable[[int, int], None]):
            super(DownloadThread, self).__init__()

            self.yt_stream = yt_stream
            self.save_location = save_location
            self.is_downloading_stopped = False
            self.on_progress_callback = on_progress_callback
            self.title = title
            
        def run(self) -> None:
            print(f'Downloading...')
            self.download_video()
        
        def stop_downloading(self):
            self.is_downloading_stopped = True
        
        def download_video(self):
            
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


class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works! # https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    
    """
    def __init__(self, parent, *args, **kw):
        super(VerticalScrolledFrame, self).__init__(master=parent, *args, **kw, relief="solid")            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self._interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)
        
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

    @property
    def interior(self):
        return self._interior

class TaskInfo:
    def __init__(self, title: str, save_location: str, yt_stream) -> None:
        self._title = title
        self._save_location = save_location
        self._yt_stream = yt_stream
        
    @property
    def title(self):
        return self._title
    
    @property
    def save_location(self):
        return self._save_location
    
    @property
    def yt_stream(self):
        return self._yt_stream
    
class DownloadProgressFrame(ttk.Frame):
    def __init__(self, master, title:str, save_location:str, yt_stream):
        super(DownloadProgressFrame, self).__init__(master)

        self.columnconfigure(0, weight=3)
        
        self.lbl_download_title = self.create_download_title_widget(title=title)
        self.lbl_save_location = self.create_save_location_widget(save_location=save_location)
        self.pb_download = self.create_pb_download_widget()
        self.btn_cancel_download = self.create_btn_cancel_download_widget()
        self.dl_thread = DownloadThread( yt_stream=yt_stream, title=title, 
                                          save_location=save_location, 
                                          on_progress_callback=self.on_download_progress)
        
        self.pack(fill=tk.X)
        
    def create_download_title_widget(self, title:str):

        lbl_download_title = ttk.Label(self, text=f'Title : {title}', relief="solid")
        
        lbl_download_title.pack(fill=tk.X)
        #lbl_download_title.grid(row=0, column=0, sticky=tk.W)
        
        return lbl_download_title
        
    def create_save_location_widget(self, save_location: str):
        lbl_save_location = ttk.Label(self, text=f'Location : {save_location}', relief="solid")
        lbl_save_location.pack(fill=tk.X)
        #lbl_save_location.grid(row=1, column=0, sticky=tk.W)
        return lbl_save_location
    
    def create_btn_cancel_download_widget(self):
        
        btn_cancel_download = ttk.Button(self, text="Cancel")
        btn_cancel_download.pack(fill=tk.X)
        
        #btn_cancel_download.grid(row=3, column=0, sticky=tk.W)
        return btn_cancel_download
    
    def create_pb_download_widget(self):
        
        pb_download = ttk.Progressbar(self, orient="horizontal")
        pb_download.pack(fill=tk.X)
        #pb_download.grid(row=2, column=0, sticky=tk.W)
        return pb_download

    def on_click_cancel(self):
        
        if isinstance(self.dl_thread, DownloadThread):
            print(f'Stoping Download Thread...')
            self.dl_thread.stop_downloading()
            self.pb_download["value"] = 0
            
    def on_download_progress(self, cur_size, max_size):

        prog_value = (cur_size / max_size) * 100      
        self.pb_download['value'] = prog_value
        print(f'Progress ---> CurSize : {cur_size}, MaxSize : {max_size}, prog_value : {prog_value}')

    def run_task(self):
        self.dl_thread.start()
        
class DownloadListFrame(VerticalScrolledFrame):
    def __init__(self, parent, frame_title:str):
        super(DownloadListFrame, self).__init__(parent)
        
        self.download_tasks = []
        self.frame_title = frame_title
        
        self.create_title_widget()

    def create_title_widget(self):
        
        lbl_frame_title = ttk.Label(self.interior,background="black", foreground="white", text=self.frame_title, width=90)
        lbl_frame_title.pack(fill=tk.X)
    
    def add_download_task(self, task_info: TaskInfo):
        
        download_task = self.create_download_task(task_info)
        self.download_tasks.append(download_task)
        download_task.run_task()

    def create_download_task(self, task_info: TaskInfo):
        task = DownloadProgressFrame(self.interior, title=task_info.title, save_location=task_info.save_location, yt_stream=task_info.yt_stream)
        return task
        

class VideoDownloadFrame(ttk.Frame):
    def __init__(self, master, frame_title: str, download_list: DownloadListFrame):
        super(VideoDownloadFrame, self).__init__(master=master)
        
        assert download_list is not None
        assert frame_title is not None
        
        self.download_list = download_list
        self.frame_title = frame_title
        self.download_link = tk.StringVar()
        self.save_location = tk.StringVar()
        self.create_title_widget()
        self.create_download_widget()
    
    def create_title_widget(self):
        
        lbl_frame_title = ttk.Label(self,background="black", foreground="white", text=self.frame_title)
        lbl_frame_title.pack(fill=tk.X)
        
    def create_download_widget(self):
        
        frm_container = ttk.Frame(self)
        frm_container.columnconfigure(0, weight=1)
        frm_container.columnconfigure(1, weight=2)
        frm_container.columnconfigure(2, weight=2)
        frm_container.columnconfigure(3, weight=1)
        
        lbl_download_link = ttk.Label(master=frm_container, text="DL Link", justify="left")
        ent_downLoad_link = ttk.Entry(master=frm_container, textvariable=self.download_link, width=50)
        
        lbl_save_location = ttk.Label(master=frm_container, text="Save Location", justify="left")
        ent_save_location = ttk.Entry(master=frm_container, textvariable=self.save_location, width=50)
        btn_save_location = ttk.Button(master=frm_container, text="Loc Find", command=self.on_click_save_location)
        
        btn_download = ttk.Button(master=frm_container, text="Download", command=self.on_click_download, width=25)
        
        self.lbl_message = ttk.Label(master=frm_container, text="")
        
        frm_container.pack(fill=tk.X, pady=(10, 0))
        lbl_download_link.grid(row=0, column=0, padx=(10, 10), sticky=tk.W)
        ent_downLoad_link.grid(row=0, column=1, columnspan=2)

        lbl_save_location.grid(row=1, column=0, padx=(10, 10), sticky=tk.W)
        ent_save_location.grid(row=1, column=1, columnspan=2)
        btn_save_location.grid(row=1, column=3, padx=(10,0), sticky=tk.E)
        
        btn_download.grid(row=2, column=2, sticky=tk.E)
        
        self.lbl_message.grid(row=3, column=0, columnspan=3, sticky=tk.E, padx=(10, 10), pady=(10, 0))

    def on_click_save_location(self):
        
        path = filedialog.askdirectory(mustexist=True)
        self.save_location.set(path)
    
    def on_click_download(self):
        
        print(f'DL : {self.download_link.get()}, SL :{self.save_location.get()}')
        
        if (self.download_link.get() == ""):
            self.lbl_message["text"] = "Invalid download link"
            return
        
        if (self.save_location.get() == ""):
            self.lbl_message["text"] = "Invalid save location"
            return

        print(f'Attenpting to download: {self.download_link.get()} and save to {self.save_location.get()}')
        
        yt = YouTube(self.download_link.get())
        yt_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('abr').desc().first()
            
        if yt_stream is None:
            self.lbl_message["text"] = "Failed to find a download stream"
            return
        
        task_info = TaskInfo(title=clean_yt_title(yt_stream.title), save_location=self.save_location.get(), yt_stream=yt_stream)
        self.download_list.add_download_task(task_info)
    
class PlaylistDownloadFrame(ttk.Frame):
    def __init__(self, master, frame_title: str, download_list: DownloadListFrame):
        super(PlaylistDownloadFrame, self).__init__(master=master)
        
        self.download_list = download_list
        self.frame_title = frame_title
        self.download_link = tk.StringVar()
        self.save_location = tk.StringVar()
        
        self.create_title_widget()
        self.create_download_widget()
        
    def create_title_widget(self):
        
        lbl_frame_title = ttk.Label(self,background="black", foreground="white", text=self.frame_title)
        lbl_frame_title.pack(fill=tk.X)
        
        
    def create_download_widget(self):
        
        frm_container = ttk.Frame(self)
        frm_container.columnconfigure(0, weight=1)
        frm_container.columnconfigure(1, weight=2)
        frm_container.columnconfigure(2, weight=2)
        frm_container.columnconfigure(3, weight=1)
        
        lbl_download_link = ttk.Label(master=frm_container, text="DL Link", justify="left")
        ent_downLoad_link = ttk.Entry(master=frm_container, textvariable=self.download_link, width=50)
        
        lbl_save_location = ttk.Label(master=frm_container, text="Save Location", justify="left")
        ent_save_location = ttk.Entry(master=frm_container, textvariable=self.save_location, width=50)
        btn_save_location = ttk.Button(master=frm_container, text="Loc Find", command=self.on_click_save_location)
        
        btn_download = ttk.Button(master=frm_container, text="Download", command=self.on_click_download, width=25)
        
        self.lbl_message = ttk.Label(master=frm_container, text="")
        
        frm_container.pack(fill=tk.X, pady=(10, 0))
        lbl_download_link.grid(row=0, column=0, padx=(10, 10), sticky=tk.W)
        ent_downLoad_link.grid(row=0, column=1, columnspan=2)

        lbl_save_location.grid(row=1, column=0, padx=(10, 10), sticky=tk.W)
        ent_save_location.grid(row=1, column=1, columnspan=2)
        btn_save_location.grid(row=1, column=3, padx=(10,0), sticky=tk.E)
        
        btn_download.grid(row=2, column=2, sticky=tk.E)
        
        self.lbl_message.grid(row=3, column=0, columnspan=3, sticky=tk.E, padx=(10, 10), pady=(10, 0))

    def on_click_save_location(self):
        
        path = filedialog.askdirectory(mustexist=True)
        self.save_location.set(path)
    
    def on_click_download(self):
        
        print(f'DL : {self.download_link.get()}, SL :{self.save_location.get()}')
        
        if (self.download_link.get() == ""):
            self.lbl_message["text"] = "Invalid download link"
            return
        
        if (self.save_location.get() == ""):
            self.lbl_message["text"] = "Invalid save location"
            return

        playlist = Playlist(self.download_link.get())
        
        for url in playlist.video_urls:
            yt = YouTube(url)
            yt_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('abr').desc().first()
                
            if yt_stream is None:
                self.lbl_message["text"] = "Failed to find a download stream"
                return
            
            task_info = TaskInfo(title=clean_yt_title(yt_stream.title), save_location=self.save_location.get(), yt_stream=yt_stream)
            self.download_list.add_download_task(task_info)