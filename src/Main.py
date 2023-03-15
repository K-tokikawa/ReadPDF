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
from PIL import Image, ImageTk, ImageDraw
import numpy as np

def get_objs(layout, results):
    if not isinstance(layout, LTContainer):
        return
    for obj in layout:
        if isinstance(obj, LTTextLine):
            results.append({'bbox': obj.bbox, 'text' : obj.get_text(), 'type' : type(obj)})
        get_objs(obj, results)

if __name__ == "__main__":
    # 標準組込み関数open()でモード指定をbinaryでFileオブジェクトを取得
    pdfpath = "F:\\TsuhanTests\DirectAce\\trunk\\06_PF\\14_PF出荷GMO用納品書追加\\比較テスト\\テスト結果\\GMO\\出力納品書\\データ③\\1.pdf"

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
        if (size == []):
            size = page.mediabox
        iprtr.process_page(page)
        layout = device.get_result()
        get_objs(layout, results)
    print(size)
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
    draw_img = ImageDraw.Draw(img)
    height_ratio = img.height / size[3]
    width_ratio  = img.width / size[2]
    for row in results:
        line = np.array(row['bbox'])
        # line[0] = 左下からの横軸の距離
        # line[1] = 左下からの縦軸の距離
        # line[2] = 横幅
        # line[3] = 縦幅

        # x0 = 左上のx座標
        # y0 = 左上のy座標
        # x1 = 右下のx座標
        # y1 = 右下のy座標
        x0 = line[0] * width_ratio
        y0 = img.height - line[1] * height_ratio
        x1 = line[2] * width_ratio
        y1 = img.height - line[3] * height_ratio

        rect = (x0, y0, x1, y1)

        line = line.tolist()
        draw_img.rectangle(rect, outline=(0, 0, 0))

    img = img.resize(size=(int(img.width * RESIZE_RETIO), int(img.height * RESIZE_RETIO)), resample=Image.BILINEAR)
    root = tk.Tk()
    canvas = tk.Canvas(root, width=img.width, height=img.height)
    canvas.pack()

    canvas.Photo = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=canvas.Photo,anchor=tk.NW)

    root.mainloop()
