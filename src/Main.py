from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import (
    LAParams,
    LTContainer,
    LTTextLine,
)
from io import StringIO
import os
from pathlib import Path
from pdf2image import convert_from_path
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import TkFilePath
import TkFolderPath

def get_objs(layout, results):
    if not isinstance(layout, LTContainer):
        return
    for obj in layout:
        if isinstance(obj, LTTextLine):
            results.append({'bbox': obj.bbox, 'text' : obj.get_text(), 'type' : type(obj)})
        get_objs(obj, results)


def start_point_get(event):
    global start_x, start_y  # グローバル変数に書き込みを行なうため宣言
    canvas.delete("rect1")  # すでに"rect1"タグの図形があれば削除
    # グローバル変数に座標を格納
    start_x, start_y = event.x, event.y
    for index, row in enumerate(cordinate):
        if row[0] <= start_x <= row[2] and row[3] <= start_y <= row[1]:
            useTextIndex = index
    msg = results[0][useTextIndex]['text']
    ret = messagebox.askyesno('確認', f'{msg}の箇所をファイル名にしますか？')
    if ret:
        useTextbbox = results[0][useTextIndex]['bbox']
        notOutput = []
        for index, page in enumerate(pages):
            filename = ''
            for row in results[index]:
                if row['bbox'] == useTextbbox:
                    filename = row['text'].replace('\n', '')
            if filename != '':
                image_path = image_dir / f'{filename}.jpeg'
                is_file = os.path.isfile(image_path)
                num = 0
                while is_file:
                    num += 1
                    existfilename = filename + f'_{num}' + '.jpeg'
                    image_path = image_dir / existfilename
                    is_file = os.path.isfile(image_path)
                # JPEGで保存
                page.save(str(image_path), "JPEG")
            else :
                image_dir.append(index)

        errorTextPath = image_dir / 'Error.csv'
        if image_dir != []:
            if (os.path.isfile(errorTextPath)):
                f = open(errorTextPath, 'w')
                f.writelines(notOutput)
            else :
                f = open(errorTextPath, 'x')
                f.writelines(notOutput)
        
        canvas.destroy()
        root.destroy()

def tgr_Button_Func(self):
    iDir = os.path.abspath(os.path.dirname(__file__))
    self.selected_file_path = tk.filedialog.askdirectory(
        initialdir=iDir)
    self.tgr_text.delete(0, tk.END)
    self.tgr_text.insert(tk.END, self.selected_file_path)
    self.tgr_path = self.selected_file_path
if __name__ == "__main__":
    # 標準組込み関数open()でモード指定をbinaryでFileオブジェクトを取得
    root = tk.Tk()
    root.geometry("800x400")
    app = TkFilePath.TkFilePath(root)
    app.mainloop()
    pdfpath = app.tgr_path

    root = tk.Tk()
    root.geometry("800x400")
    appFolder = TkFolderPath.TkFolderPath(root)
    appFolder.mainloop()
    image_dir = Path(appFolder.tgr_directory)
    print(appFolder.tgr_directory)

    fp = open(pdfpath, 'rb')

    # 出力先をPythonコンソールするためにIOストリームを取得
    outfp = StringIO()

    # 各種テキスト抽出に必要なPdfminer.sixのオブジェクトを取得する処理
    rmgr = PDFResourceManager() # PDFResourceManagerオブジェクトの取得
    lprms = LAParams()          # LAParamsオブジェクトの取得
    device = PDFPageAggregator(rmgr, laparams=lprms)
    iprtr = PDFPageInterpreter(rmgr, device) # PDFPageInterpreterオブジェクトの取得

    # PDFファイルから1ページずつ解析(テキスト抽出)処理する
    results = []
    size = []
    for page in PDFPage.get_pages(fp):
        pagetext = []
        if (size == []):
            size = page.mediabox
        iprtr.process_page(page)
        layout = device.get_result()
        get_objs(layout, pagetext)
        results.append(np.array(pagetext))
    print(np.array(results))
    outfp.close()  # I/Oストリームを閉じる
    device.close() # TextConverterオブジェクトの解放
    fp.close()     #  Fileストリームを閉じる

    # PDFを画像変換する。
    poppler_dir = Path(__file__).parent.absolute() / "../poppler/bin"
    os.environ["PATH"] += os.pathsep + str(poppler_dir)

    pages = convert_from_path(pdfpath, 150)

    # canvasに1ページ目のPDFを画像として表示する。
    RESIZE_RETIO = 0.7 # 縮小倍率の規定
    img = pages[0]
    ## 枠線を追加する。
    height_ratio = img.height / size[3]
    width_ratio  = img.width / size[2]

    draw_img = ImageDraw.Draw(img)
    cordinate = []
    for page in results[0]:
        line = page['bbox']
        x0 = line[0] * width_ratio
        y0 = img.height - line[1] * height_ratio
        x1 = line[2] * width_ratio
        y1 = img.height - line[3] * height_ratio
        rect = (x0, y0, x1, y1)
        cordinate.append(rect)
        draw_img.rectangle(rect, outline=(0, 0, 0))
    cordinate = np.array(cordinate)*RESIZE_RETIO
    cordinate = cordinate.tolist()
    img = img.resize(size=(int(img.width * RESIZE_RETIO), int(img.height * RESIZE_RETIO)), resample=Image.BILINEAR)
    root = tk.Tk()
    canvas = tk.Canvas(root, width=img.width, height=img.height)
    canvas.bind("<ButtonPress-1>", start_point_get)
    canvas.pack()

    canvas.Photo = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=canvas.Photo,anchor=tk.NW)

    root.mainloop()
