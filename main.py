"""
①フロントサイドに渡す関数を定義
②eelの起動
"""

import eel
import desktop
from translate import Tran


app_name="html"
end_point="index.html"
size=(800,600)

translator = Tran()

@ eel.expose
def translate(text, dest, src):
    return translator.translate_text(text, dest, src)

@ eel.expose
def get_lang_master():
    return translator.get_language_master()

desktop.start(app_name,end_point,size)