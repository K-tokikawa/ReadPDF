import os
import sys
import tkinter
import tkinter.filedialog
import tkinter.messagebox
sys.path.append('../')


class TkFolderPath(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.pack()
        self.tgr_Button = tkinter.Button(
            self, bg='#000000', fg='#ffffff', height=20, width=100)
        self.tgr_Button["text"] = "フォルダーを選択"  # ボタンのテキスト
        self.tgr_Button["command"] = self.tgr_Button_Func  # 割り込み関数
        self.tgr_Button.pack(anchor='center', expand=1)

    def tgr_Button_Func(self):
        iDir = os.path.abspath(os.path.dirname(__file__))
        self.selected_file_path = tkinter.filedialog.askdirectory(initialdir=iDir)
        self.tgr_directory = self.selected_file_path
        print(self.tgr_directory)

        self.master.destroy()


