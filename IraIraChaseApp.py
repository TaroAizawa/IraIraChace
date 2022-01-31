# C:/users/Taro Aizawa/Desktop/mygame
# -*- coding: utf-8 -*-
import pyxel
import json
from title import Title
from stage_select import StageSelect
from stage import Stage
from stageeditor import Editor


# 場面の定義：アプリ
TITLE: int = 0
STAGE_SELECT: int = 1
STAGE: int = 2
STAGE_EDIT: int = 3
STAGE_ENDLESS: int = 4

# アプリの幅と高さ
APP_W: int = 256
APP_H: int = 256

class App():
    """アプリ本体"""
    def __init__(self):
        # アプリの初期設定
        self.scene = TITLE
        self.scene_last = STAGE_SELECT
        # fps指定   
        self.fps = 30
        # ステージ設定の読み込み       
        self.stage_settings_json = json.load(open('assets/stage_setting.json', 'r'))
        # 選択ステージ番号
        self.selected_stage_num = None
        # pyxel初期化
        pyxel.init(APP_W, APP_H, caption="IRA IRA CHASE", 
                    scale=5, fps=self.fps, quit_key=pyxel.KEY_ESCAPE, fullscreen=True)
        # リソースファイル読込
        pyxel.load("assets/for_mygame.pyxres")
        # pyxel起動
        pyxel.run(self.update, self.draw)

    def update(self):
        """内部情報の更新"""
        # ===== タイトル画面 =====
        if self.scene == TITLE:
            if self.scene_last != TITLE:
                pyxel.play(0, 5, loop=True)
                self.title = Title(APP_W, APP_H)
            self.title.update_title()
            if not self.title.active:
                pyxel.stop()
                self.scene = self.title.selected_mode
            self.scene_last = TITLE
        # ===== ステージセレクト画面 =====
        elif self.scene == STAGE_SELECT:
            if self.scene_last != STAGE_SELECT:
                pyxel.playm(1, loop=True)
                pyxel.stop(2)
                pyxel.stop(3)
                if not hasattr(self, 'stage_select') or self.scene_last == TITLE:
                    self.stage_select = StageSelect(APP_W, APP_H, 
                                                    self.stage_settings_json)
                else:
                    self.stage_select.activate = True 
            self.selected_stage_num = self.stage_select.update_stage_select()
            if not self.stage_select.activate:
                pyxel.stop()
                if self.stage_select.back_button.back:
                    self.scene = TITLE
                else:
                    self.scene = STAGE
            self.scene_last = STAGE_SELECT
        # ===== ステージ =====
        elif self.scene == STAGE:
            if self.scene_last == STAGE_SELECT:
                self.stage = Stage(APP_W, APP_H, self.selected_stage_num)
                self.stage.set_frame0()
            self.stage.update_Stage()
            if not self.stage.activate:
                del(self.stage)
                self.scene = STAGE_SELECT
            self.scene_last = STAGE
        # ===== ステージエディタ =====
        elif self.scene == STAGE_EDIT:
            if self.scene_last != STAGE_EDIT:
                pyxel.stop()
                self.editor = Editor()
            self.editor.update_editor()
            # 終了条件
            if pyxel.btnp(pyxel.KEY_Q):
                del(self.editor)
                self.scene = TITLE
            self.scene_last = STAGE_EDIT
        # ===== エンドレス（工事中） =====
        elif self.scene == STAGE_ENDLESS:
            pass

    def draw(self):
        """主に描画を行う"""
        # 画面を黒で初期化
        pyxel.cls(0)
        # ===== タイトル画面 =====
        if self.scene == TITLE:
            if self.scene_last == TITLE:
                self.title.draw_title()
        # ===== ステージセレクト画面 =====
        elif self.scene == STAGE_SELECT:
            if self.scene_last == STAGE_SELECT:
                self.stage_select.draw_stage_select()
        # ===== ステージ =====          
        elif self.scene == STAGE:
            if self.scene_last == STAGE:        
                self.stage.draw_Stage()
        # ===== ステージエディタ =====
        elif self.scene == STAGE_EDIT:
            if self.scene_last == STAGE_EDIT:
                self.editor.draw_editor()
        # ===== エンドレス（工事中） =====
        elif self.scene == STAGE_ENDLESS:
            pass


if __name__ == "__main__":
    App()