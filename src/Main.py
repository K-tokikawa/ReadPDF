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
        for index, page in enumerate(pages):
            filename = ''
            for row in results[index]:
                if row['bbox'] == useTextbbox:
                    filename = row['text'].replace('\n', '') + '.jpeg'
            image_dir = Path("./")
            image_path = image_dir / filename
            # JPEGで保存
            page.save(str(image_path), "JPEG")

if __name__ == "__main__":
    # 標準組込み関数open()でモード指定をbinaryでFileオブジェクトを取得
    pdfpath = "F:\\TsuhanTests\DirectAce\\trunk\\06_PF\\14_PF出荷GMO用納品書追加\\比較テスト\\テスト結果\\GMO\\出力納品書\\データ①\\1.pdf"

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
