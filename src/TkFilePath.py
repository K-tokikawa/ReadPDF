import os
import sys
import tkinter
import tkinter.filedialog
import tkinter.messagebox
sys.path.append('../')


class TkFilePath(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.tgr_path = ''
        self.tgr_directory = ''

        self.pack()
        self.tgr_Button = tkinter.Button(
            self, bg='#000000', fg='#ffffff', height=20, width=100)
        self.tgr_Button["text"] = "PDFを選択"  # ボタンのテキスト
        self.tgr_Button["command"] = self.tgr_Button_Func  # 割り込み関数
        self.tgr_Button.pack(anchor='center', expand=1)

        self.folder_Button = tkinter.Button(
        self, bg='#000000', fg='#ffffff', height=20, width=100)
        self.folder_Button["text"] = "PDFフォルダを選択"  # ボタンのテキスト
        self.folder_Button["command"] = self.folder_Button_Func  # 割り込み関数
        self.folder_Button.pack(anchor='center', expand=1)

    def tgr_Button_Func(self):
        iDir = os.path.abspath(os.path.dirname(__file__))
        self.selected_file_path = tkinter.filedialog.askopenfile(
            initialdir=iDir)
        self.tgr_path = self.selected_file_path.name
        self.master.destroy()

    def folder_Button_Func(self):
        iDir = os.path.abspath(os.path.dirname(__file__))
        self.selected_file_path = tkinter.filedialog.askdirectory(
            initialdir=iDir)
        self.tgr_directory = self.selected_file_path

        self.master.destroy()
