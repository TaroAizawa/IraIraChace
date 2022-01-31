# C:/users/Taro Aizawa/Desktop/mygame
# -*- coding: utf-8 -*-
from numpy.lib.shape_base import expand_dims
from numpy.lib.utils import info
import pyxel
import numpy as np
import json
from collision_detector import CollisionDetector

# =======================================================
# =======================================================
# ==================== 定数扱いの変数 ====================
# =======================================================
# =======================================================

# 以下a, bで共通して使用
NOTHING:      int = 0  # "無し"の意

# a. 場面（または選択フィールド）に関係
DRAW:         int = 1  # "DRAW"フィールド選択
ERASE:        int = 2  # "ERASE"フィールド選択
LOAD_OR_SAVE: int = 3  # ステージのロード・セーブフィールド選択
WARN:         int = 4  # 警告画面表示

# b. ボタンの選択に関係
PLAYER:       int = 5   # プレイヤー
CHASER:       int = 6   # 追跡者
CAPSULE_RED:  int = 7   # 赤カプセル
CAPSULE_BLUE: int = 8   # 青カプセル
LINE_OPEN:    int = 9   # 開いた線
LINE_CLOSE:   int = 10  # 閉じた線
LINE_RECT:    int = 11  # 四角の線
GOAL:         int = 12  # ゴール

ERASER_0:     int = 13  # 消しゴム小
ERASER_1:     int = 14  # 消しゴム中
ERASER_2:     int = 15  # 消しゴム大
ERASE_ALL:    int = 16  # 全消去

STAGE_LOAD:   int = 17  # 選択ステージを描画面に読込
STAGE_SAVE:   int = 18  # 現在の描画面を選択ステージに保存

# 警告画面で使用
YES:          int = 19
NO:           int = 20
OK:           int = 21

# c.画面のサイズ設定に関係
SCREEN_W:     int = 256
SCREEN_H:     int = 256
SYSTEM_H:     int = 64









# =======================================================
# =======================================================
# ======================== メイン =======================
# =======================================================
# =======================================================

# =======================================
# ========== エディタアプリ本体 ==========
# =======================================  
class Editor:
    def __init__(self):
        """各部品の初期化"""
        self.pointer = Pointer()    # マウスポインタ―
        self.canvas = Canvas()      # 描画面
        self.system = System()      # システム画面
        self.scene = NOTHING
        self.selected_button_this_frame = NOTHING
        self.selected_button = NOTHING
        self.selected_button_last = NOTHING
        self.selected_stage = NOTHING

    def update_editor(self):
        """エディタの情報更新(システム画面、描画面、場面管理)"""
        # マウスポインタ―の更新
        self.pointer.update_pointer(SCREEN_W, SCREEN_H, SYSTEM_H, 
            self.selected_button)
        # システム画面から、現フレームの選択ボタン取得（NOTHING含む）
        self.selected_button_this_frame, self.selected_stage = (
            self.system.update_system(self.pointer.x, 
                self.pointer.y, 
                self.scene, self.canvas.savable)
            ) 
        # 選択ボタンの名称が存在すれば最後の選択ボタンとして記憶
        # （＝NOTHINGでは更新しない）
        if self.selected_button_this_frame != NOTHING:
                self.selected_button = self.selected_button_this_frame
        if (self.selected_button_last == ERASE_ALL or
            self.selected_button_last == STAGE_LOAD or
            self.selected_button_last == STAGE_SAVE):
            # 指定のボタンはその1フレームだけ押されたことにする
            self.selected_button = NOTHING
        # 場面の判別
        if PLAYER <= self.selected_button <= GOAL:
            self.scene = DRAW
        elif ERASER_0 <= self.selected_button <= ERASE_ALL:
            self.scene = ERASE
        elif STAGE_LOAD <= self.selected_button <= STAGE_SAVE:
            self.scene = LOAD_OR_SAVE
        else:
            self.scene = NOTHING
        # 描画面の更新
        self.canvas.update_canvas(self.scene, 
            self.selected_button, 
            self.pointer, 
            self.selected_stage)
        self.selected_button_last = self.selected_button

    def draw_editor(self):
        """エディタの描画"""
        pyxel.cls(0)                 # 全画面を黒でクリア
        draw_bg()                    # システム画面背景の描画
        self.system.draw_system(self.scene, self.canvas.savable)
        self.canvas.draw_canvas(self.pointer)
        self.pointer.draw_pointer()  # マウスポインタ―の描画


# =====================================
# ========== マウスポインター ==========
# =====================================
class Pointer:
    def __init__(self):
        """初期化"""
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y
        self.last_x = 0
        self.last_y = 0
        self.r = 0
        self.right_x = 0
        self.right_y = 0
        self.right_last_x = 0
        self.right_last_y = 0
        self.left_x = 0
        self.left_y = 0
        self.left_last_x = 0
        self.left_last_y = 0
        self.on_system = False
        self.on_canvas = False
        self.is_eraser = False
        self.rect = [[self.left_x, self.left_y], 
            [self.right_x, self.right_y], 
            [self.right_last_x, self.right_last_y], 
            [self.left_last_x, self.last_y]]

    def update_pointer(self, size_x, size_y, system_height, selected_button):
        """更新"""
        self.last_x = self.x
        self.last_y = self.y
        if self.is_eraser:
            self.right_last_x = self.right_x
            self.right_last_y = self.right_y
            self.left_last_x = self.left_x
            self.left_last_y = self.left_y
        self.size_x = size_x
        self.size_y = size_y
        self.system_height = system_height
        self.is_eraser = False
        # 消しゴムとして機能させる
        if selected_button == ERASER_0:
            self.is_eraser = True
            self.r = 1
        elif selected_button == ERASER_1:
            self.is_eraser = True
            self.r = 5
        elif selected_button == ERASER_2:
            self.is_eraser = True
            self.r = 15
        else:
            self.r = 0
        # 自身をはみ出させないための処理
        if pyxel.mouse_x < 0:
            self.x = 0
        elif pyxel.mouse_x >= size_x:
            self.x = size_x - 1
        else:
            self.x = pyxel.mouse_x
        if  pyxel.mouse_y < system_height:
            self.y = system_height
        elif pyxel.mouse_y >= size_y:
            self.y = size_y - 1
        else:
            self.y = pyxel.mouse_y
        # 自身がどの領域にいるか判定
        if 0 <= pyxel.mouse_x < size_x:
            if 0 <= pyxel.mouse_y < system_height:
                self.on_system = True
                self.on_canvas = False
            elif system_height <= pyxel.mouse_y < size_y:
                self.on_system = False
                self.on_canvas = True
            else:
                self.on_system = False
                self.on_canvas = False
        else:
            self.on_system = False
            self.on_canvas = False
        # pyxel上にマウスカーソルを表示するか
        if (pyxel.mouse_x < 0 or size_x <= pyxel.mouse_x or
            pyxel.mouse_y < system_height or size_y <= pyxel.mouse_y):
            pyxel.mouse(True)
        else:
            pyxel.mouse(False)
        if (pyxel.btn(pyxel.KEY_SHIFT)):
            # オプション機能（グリッド）使用時
            # 8pxごとにスナップ
            self.x -= self.x % 8
            self.y -= self.y % 8
        # ベクトルとベクトル長さ算出
        vec = np.array([self.x - self.last_x, self.y - self.last_y])
        vec_sca = np.linalg.norm(vec, ord=2)
        # 選択ボタンが消しゴム かつ移動中のみ機能指せる
        if self.is_eraser and vec_sca > 0:
            vec_to_right = np.dot(
                np.array([[0, -1], [1, 0]]), 
                vec / vec_sca * self.r)
            vec_to_left = np.dot(
                np.array([[0, 1], [-1, 0]]), 
                vec / vec_sca * self.r)
            self.right_x = self.x + vec_to_right[0]
            self.right_y = self.y + vec_to_right[1]
            self.left_x = self.x + vec_to_left[0]
            self.left_y = self.y + vec_to_left[1]
        # 軌道上の当たり判定用(未実装)
        self.rect_points = [[self.left_x, self.left_y], 
            [self.right_x, self.right_y], 
            [self.right_last_x, self.right_last_y], 
            [self.left_last_x, self.last_y]]

    def draw_pointer(self):
        """描画"""
        # テキストの文字数
        text_len = len(f"({self.x},{self.y-self.system_height}")
        # テキストの表示幅・高さ
        text_w = text_len * 3 + text_len - 1
        text_h = 5
        # 自身の位置でテキストの表示位置を変える
        if self.x >= self.size_x / 2:
            self.text_x = self.x - 3 - text_w
        else:
            self.text_x = self.x + 3
        if self.y < (self.size_y-self.system_height) / 2 + self.system_height:
            self.text_y = self.y + 6
        else:
            self.text_y = self.y - 6 - text_h
        # テキスト描画
        pyxel.text(self.text_x, self.text_y, 
            f"({self.x},{self.y-self.system_height})", 5)
        # 消しゴムとしての処理
        if self.is_eraser and self.on_canvas:
            # 自身が消しゴムでキャンバス上にいる場合
            if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
                col = 2
            else:
                col = 8
            pyxel.circb(self.x, self.y, self.r, col)
            pyxel.line(self.right_last_x, self.right_last_y, 
                self.right_x, self.right_y, col)
            pyxel.line(self.left_last_x, self.left_last_y, 
                self.left_x, self.left_y, col)
            pyxel.circb(self.last_x, self.last_y, self.r, col)
        else:
            # そうでない場合
            if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
                pyxel.blt(self.x-2, self.y-2, 0, 8, 0, 5, 5, 0)
            else:
                pyxel.blt(self.x-2, self.y-2, 0, 0, 0, 5, 5, 0)







# ==================================================================
# ==================================================================
# ==================== システム画面に関係するもの ====================
# ==================================================================
# ==================================================================


# =================================================
# ========== システム画面本体（画面上部） ==========
# =================================================
class System:
    """選択された項目と、読込・書き込み対象のステージ番号を管理
    """
    def __init__(self):
        # 各部品の初期化
        self.buttons = Buttons()
        self.button_eraseall = EraseAll()
        self.stageselect = StageSelect()
        self.button_load = Load()
        self.button_save = Save()

    def update_system(self, pointer_x, pointer_y, scene, savable):
        pointer_x = pyxel.mouse_x
        pointer_y = pyxel.mouse_y
        if scene != WARN:
            self.selected_button = NOTHING
            # 継続選択ボタン（DRAW / ERASE）
            self.selected_button = self.buttons.update_buttons(
                pointer_x, pointer_y)
            # 全消去ボタン
            if self.button_eraseall.update_eraseall(pointer_x, pointer_y):
                self.buttons.reset_buttons()
                self.selected_button = ERASE_ALL
            # ステージ選択
            self.selected_stage = self.stageselect.update_stageselect(
                pointer_x, pointer_y)
            # ステージ読込ボタン
            if self.button_load.update_load(pointer_x, pointer_y):
                self.buttons.reset_buttons()
                self.selected_button = STAGE_LOAD
            # ステージ保存ボタン
            if self.button_save.update_save(pointer_x, pointer_y, savable):
                self.buttons.reset_buttons()
                self.selected_button = STAGE_SAVE
            # 選択されたボタンと現在のステージ番号を返す
        else:
            self.selected_button = NOTHING
        # 選択情報を本体に返す
        return self.selected_button, self.selected_stage

    def draw_system(self, scene, savable):
        # 各部品の描画
        self.buttons.draw_buttons()
        self.button_eraseall.draw_eraseall()
        self.stageselect.draw_stageselect()
        self.button_load.draw_load()
        self.button_save.draw_save(savable)
        # 選択フィールド強調（DRAW / ERASE）
        if scene == DRAW:
            pyxel.blt(4, 4, 0, 88, 220, 38, 12, 0)
        elif scene == ERASE:
            pyxel.blt(80, 4, 0, 126, 220, 45, 12, 0)
        # "PRESS Q KEY TO BACK TO TITLE"
        pyxel.text(139, 11, 
            "Q KEY : QUIT,\n"
            "SHIFT : OPTION", 6)


# ====================================
# ========== 継続選択ボタン ==========
# ====================================
class Button:
    def __init__(self, name, x, y, w, h):
        """初期化"""
        # 座標, 幅, 高さ
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        # 選択ボタン識別用
        self.name = name
        # hoverしているか
        self.hover = False
        # hoverした状態でクリックされたか
        self.click_after_hover = False
        # 自身が選択されているか
        self.selected = False

    def reset(self):
        """選択状態解除"""
        self.selected = False

    def update_button(self, pointer_x, pointer_y):
        """更新"""
        if (self.x <= pointer_x < self.x + self.w and
            self.y <= pointer_y < self.y + self.h):
            self.hover = True
        else:
            self.hover = False
        if self.hover and pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            self.click_after_hover = True
        if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
            if self.click_after_hover and self.hover:
                self.selected = True
            self.click_after_hover = False

    def set_selected(self, selected):
        self.selected = selected

    def draw_button(self):
        """描画"""
        if self.selected:
            pyxel.rectb(self.x - 1, self.y - 1, 
                        self.w + 2, self.h + 2, 10)
            pyxel.rectb(self.x, self.y, 
                        self.w, self.h, 10)            
        if self.click_after_hover and not self.selected:
            pyxel.rectb(self.x, self.y, 
                        self.w, self.h, 2)
        elif self.hover:
            pyxel.rectb(self.x, self.y, 
                        self.w, self.h, 10)


# =============================================
# ========== 継続選択ボタンの包括管理 ==========
# =============================================
class Buttons:
    def __init__(self):
        """初期化"""
        
        # （フル機能のとき）
        settings = [[PLAYER, 3, 23, 16, 16],[CHASER, 21, 23, 16, 16],
                    [CAPSULE_RED, 39, 23, 16, 16],
                    [CAPSULE_BLUE, 57, 23, 16, 16],
                    [LINE_OPEN, 3, 41, 16, 16],[LINE_CLOSE, 21, 41, 16, 16],
                    [LINE_RECT, 39, 41, 16, 16],
                    [GOAL, 57, 41, 16, 16],[ERASER_0, 80, 23, 17, 17],
                    [ERASER_1, 96, 23, 17, 17],[ERASER_2, 112, 23, 17, 17],]
        # ボタンのオブジェクトが入る
        self.buttons = [Button(s[0], s[1], s[2], s[3], s[4]) 
            for s in settings]
        # 現在選択されているボタン
        self.selected_now: int = NOTHING

    def update_buttons(self, pointer_x, pointer_y):
        """更新"""
        for b in self.buttons:
            b.update_button(pointer_x, pointer_y)
            if b.selected:
                self.reset_buttons()
                b.set_selected(True)
                self.selected_now = b.name
        return self.selected_now

    def reset_buttons(self):
        """全ボタンの選択状態リセット"""
        for b in self.buttons:
            b.reset()
        self.selected_now = NOTHING

    def draw_buttons(self):
        """描画"""
        for b in self.buttons:
            b.draw_button()


# =====================================================================
# ========== 以下３つの継承元（選択されたそのフレームのみオン） ==========
# =====================================================================
class ButtonOneFrame:
    """選択されたフレームのみオンになるボタン"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.name = NOTHING
        self.hover = False
        self.click_after_hover = False
        self.selected = False

    def update_buttononeframe(self, pointer_x, pointer_y):
        """更新"""
        self.selected = False
        self.hover = (self.x <= pointer_x < self.x+self.w and 
                        self.y <= pointer_y < self.y+self.h)
        if self.hover and pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            self.click_after_hover = True
        if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
            if self.click_after_hover and self.hover:
                self.selected = True
            self.click_after_hover = False
        if self.selected:
            return self.name
        else:
            return NOTHING

    def before_draw(self):
        """描画に際して行う処理"""
        self.col_button = 8
        self.col_button_behind = 2
        self.col_lines_first = 1
        self.col_lines_second = 1
        self.uv_first = [168, 232]
        self.uv_second = [168, 232]
        if self.hover:
            self.col_button = 10
            if self.click_after_hover:
                self.col_lines_first = 6
                self.uv_first = [168, 240]
                self.col_button = 2
        if self.selected:
            self.uv_first = [168, 232]
            self.col_lines_second = 6
            self.col_button_behind = 6
            self.uv_second = [168, 240]


# =================================
# ========== 全消去ボタン ==========
# =================================
class EraseAll(ButtonOneFrame):
    """全消去ボタン"""
    def __init__(self):
        """初期化"""
        super().__init__()
        self.x = 86
        self.y = 43
        self.w = 37
        self.h = 13
        self.name = ERASE_ALL

    def update_eraseall(self, pointer_x, pointer_y):
        """更新"""
        return super().update_buttononeframe(pointer_x, pointer_y)

    def draw_eraseall(self):
        """描画"""
        # 事前計算
        super().before_draw()
        if self.hover and self.click_after_hover:
            # 自身がクリックされた後ホバーしているとき
            pyxel.rectb(0, 63, 256, 256-63, 6)
        # 矢印線 描画面 -> ボタン
        pyxel.line(79, 62, 79, 49, self.col_lines_first)   
        pyxel.blt(83, 47, 0, self.uv_first[0], self.uv_first[1], 3, 5, 0)
        pyxel.line(79, 49, 85, 49, self.col_lines_first)
        # ボタン
        pyxel.rectb(86, 43, 38, 13, self.col_button)             
        pyxel.text(88, 47, "ERASE", self.col_button)
        pyxel.text(111, 47, "ALL", self.col_button)
        pyxel.line(108, 49, 109, 49, self.col_button_behind)
        pyxel.pset(117, 49, self.col_button_behind)
        pyxel.pset(121, 49, self.col_button_behind)
        # 矢印線 ボタン -> 描画面
        pyxel.line(124, 49, 129, 49, self.col_lines_second)  
        pyxel.line(129, 49, 129, 62, self.col_lines_second)
        pyxel.blt(127, 60, 0, self.uv_second[0], self.uv_second[1], 5, 3, 0)
        if self.selected:
            # 自身が選択されているとき
            pyxel.rectb(0, 63, 256, 256-63, 6)


# =================================
# ========== ロードボタン ==========
# =================================
class Load(ButtonOneFrame):
    """ロードボタン"""
    def __init__(self):
        """初期化"""
        super().__init__()
        self.x = 208
        self.y = 32
        self.w = 37
        self.h = 13
        self.name = STAGE_SAVE

    def update_load(self, pointer_x, pointer_y):
        """更新"""
        return super().update_buttononeframe(pointer_x, pointer_y)

    def draw_load(self):
        """描画"""
        # 事前計算
        super().before_draw()
        if self.hover and self.click_after_hover:
            # 自身がクリックされた後ホバーしているとき
            pyxel.rectb(208, 9, 37, 21, self.col_lines_first)
        # 矢印線 ステージ選択 -> ボタン
        pyxel.line(207, 19, 201, 19, self.col_lines_first)  
        pyxel.line(201, 19, 201, 38, self.col_lines_first)
        pyxel.blt(205, 36, 0, self.uv_first[0], self.uv_first[1], 3, 5, 0)
        pyxel.line(201, 38, 207, 38, self.col_lines_first)  
        # ボタン
        pyxel.rectb(208, 32, 37, 13, self.col_button)  
        pyxel.text(219, 36, "LOAD", self.col_button)
        pyxel.line(210, 38, 217, 38, self.col_button_behind)
        pyxel.line(235, 38, 242, 38, self.col_button_behind)
        pyxel.pset(221, 38, self.col_button_behind)
        # 矢印線 ボタン -> 描画面
        pyxel.line(245, 38, 248, 38, self.col_lines_second)  
        pyxel.line(248, 38, 248, 62, self.col_lines_second)
        pyxel.blt(246, 60, 0, self.uv_second[0], self.uv_second[1], 5, 3, 0)
        if self.selected:
            # 自身が選択されているとき
            pyxel.rectb(0, 63, 256, 256-63, 6)


# =================================
# ========== セーブボタン ==========
# =================================
class Save(ButtonOneFrame):
    """セーブボタン"""
    def __init__(self):
        """初期化"""
        super().__init__()
        self.x = 208
        self.y = 48
        self.w = 37
        self.h = 13
        self.name = STAGE_SAVE

    def update_save(self, pointer_x, pointer_y, savable):
        """更新"""
        if not pyxel.btn(pyxel.KEY_SHIFT) and savable:
            # シフトキーが押されていない時のみ機能させる
            return super().update_buttononeframe(pointer_x, pointer_y)
        else:
            return NOTHING

    def draw_save(self, savable):
        """描画"""
        # 事前計算
        super().before_draw()
        if not pyxel.btn(pyxel.KEY_SHIFT) and savable:
            # シフトキーが押されていないとき
            if self.hover and self.click_after_hover:
                # 自身がクリックされた後ホバーしているとき
                pyxel.rectb(0, 63, 256, 256-63, 6)
            # 矢印線 描画面 -> ボタン
            pyxel.line(201, 62, 201, 54, self.col_lines_first)  
            pyxel.blt(205, 52, 0, self.uv_first[0], self.uv_first[1], 3, 5, 0)
            pyxel.line(201, 54, 207, 54, self.col_lines_first)
            # ボタン
            pyxel.rectb(208, 48, 37, 13, self.col_button)  
            pyxel.text(219, 52, "SAVE", self.col_button)
            pyxel.line(210, 54, 217, 54, self.col_button_behind)
            pyxel.line(235, 54, 242, 54, self.col_button_behind)
            # 矢印線 ボタン -> ステージ選択
            pyxel.line(245, 54, 251, 54, self.col_lines_second)  
            pyxel.line(251, 54, 251, 19, self.col_lines_second)
            pyxel.line(251, 19, 245, 19, self.col_lines_second)
            pyxel.blt(245, 17, 0, self.uv_second[0]+2, self.uv_second[1], 
                3, 5, 0)
            if self.selected:
                # 自身が選択されているとき
                pyxel.rectb(208, 9, 37, 21, self.col_lines_second)
        else:
            # シフトキーが押されているとき
            # 矢印線 描画面 -> ボタン
            pyxel.line(201, 62, 201, 54, self.col_lines_first)  
            pyxel.blt(205, 52, 0, self.uv_first[0], self.uv_first[1], 3, 5, 0)
            pyxel.line(201, 54, 207, 54, self.col_lines_first)
            # ボタン
            pyxel.rectb(208, 48, 37, 13, 1)  
            pyxel.text(219, 52, "SAVE", 1)
            pyxel.line(210, 54, 217, 54, 1)
            pyxel.line(235, 54, 242, 54, 1)
            # 矢印線 ボタン -> ステージ選択
            pyxel.line(245, 54, 251, 54, self.col_lines_second)  
            pyxel.line(251, 54, 251, 19, self.col_lines_second)
            pyxel.line(251, 19, 245, 19, self.col_lines_second)
            pyxel.blt(245, 17, 0, self.uv_second[0]+2, self.uv_second[1], 
                3, 5, 0)
            if self.selected:
                # 自身が選択されているとき
                pyxel.rectb(208, 9, 37, 21, self.col_lines_second)


# =================================
# ========== ステージ番号 ==========
# =================================
class StageNumber:
    """ステージ番号"""
    def __init__(self, x, y, num, max, expansion_rate, col):
        """初期化"""
        self.count0 = pyxel.frame_count
        self.coords = np.array([x, y])
        self.coords_init = np.array([x, y])
        self.rad = 0
        self.expansion_rate = expansion_rate
        self.expansion_rate_max = expansion_rate
        self.v_expansion_rate = 1
        self.v_rad = np.pi/90
        # 中心座標を原点とした位置ベクトル
        self.settings = [
            [
                [[-3, -13], [2, -13], [7, -8], [7, 7], 
                    [2, 12], [-3, 12], [-8, 7], [-8, -8]],
                [[-3, -8], [2, -8], [2, 7], [-3, 7]]
            ],
            [
                [[-3, -13], [2, -13], [2, 12], 
                    [-3, 12], [-3, -8], [-8, -3], [-8, -8]]
            ],
            [
                [[-3, -13], [2, -13], [7, -8], [7, -3], [-3, 7], [7, 7], 
                    [7, 12], [-8, 12], [-8, 7], [2, -3], [2, -8], [-8, -8]]
            ],
            [
                [[-3, -13], [2, -13], [7, -8], [7, 7], 
                    [2, 12], [-3, 12], [-8, 7], [2, 7], [2, 2], 
                    [-3, 2], [-3, -3], [2, -3], [2, -8], [-8, -8]]
            ], 
            [
                [[-8, -13], [-3, -13], [-3, -3], [2, -3], 
                    [2, -13], [7, -13], [7, 12], [2, 12], [2, 2], [-8, 2]]
            ],
            [
                [[-8, -13], [7, -13], [7, -8], [-3, -8], 
                    [-3, -3], [2, -3], [7, 2], [7, 7], [2, 12], 
                    [-3, 12], [-8, 7], [2, 7], [2, 2], [-3, 2], [-8, -3]]
            ],
            [
                [[-3, -13], [2, -13], [7, -8], 
                    [-3, -8], [-3, -3], [2, -3], [7, 2], 
                    [7, 7], [2, 12], [-3, 12], [-8, 7], [-8, -8]],
                [[-3, 2], [2, 2], [2, 7], [-3, 7]]
            ],
            [
                [[-8, -13], [7, -13], [7, -3], [-3, 12], 
                    [-8, 12], [2, -3], [2, -8], [-8, -8]]
            ],
            [
                [[-3, -13], [2, -13], [7, -8], [7, 7], 
                    [2, 12], [-3, 12], [-8, 7], [-8, -8]],
                [[-3, -8], [2, -8], [2, -3], [-3, -3]],
                [[-3, 2], [2, 2], [2, 7], [-3, 7]]
            ],
            [
                [[-3, -13], [2, -13], [7, -8], 
                    [7, 7], [2, 12], [-3, 12], [-8, 7], 
                    [2, 7], [2, 2], [-3, 2], [-8, -3], [-8, -8]],
                [[-3, -8], [2, -8], [2, -3], [-3, -3]],
            ],
        ]
        self.num = num
        self.num_min = 1
        self.num_max = max
        self.selected_setting = self.settings[self.num]
        self.col = col
        self.prev_next = 1

    def update_stagenumber(self, prev, next):
        """更新"""     
        if self.coords[0] != self.coords_init[0]:
            self.coords[0] = self.coords_init[0]  
        if prev:
            self.count0 = pyxel.frame_count
            self.prev_next = -1
            self.num -= 1
        elif next:
            self.count0 = pyxel.frame_count
            self.prev_next = 1
            self.num += 1
        if self.num < self.num_min:
            self.coords[0] -= 1
            self.num = self.num_min
        elif self.num > self.num_max:
            self.coords[0] += 1
            self.num = self.num_max
        self.selected_setting = self.settings[self.num]
        

    def draw_stagenumber(self):
        """描画"""        
        for index, points in enumerate(self.selected_setting):
            for index, point in enumerate(points):
                if index < len(points)-1:
                    pyxel.line(self.set_point_coord(point)[0], 
                        self.set_point_coord(point)[1], 
                        self.set_point_coord(points[index+1])[0], 
                        self.set_point_coord(points[index+1])[1], 
                        self.col)
                else:
                    pyxel.line(self.set_point_coord(point)[0],
                        self.set_point_coord(point)[1], 
                        self.set_point_coord(points[0])[0], 
                        self.set_point_coord(points[0])[1], 
                        self.col)

    def set_point_coord(self, point):
        """点の座標をセット"""
        return (self.coords + 
            np.dot(
                np.array(
                    [
                        [np.cos(self.rad), -np.sin(self.rad)], 
                        [np.sin(self.rad), np.cos(self.rad)]
                    ]
                    ), 
                point) *
            self.expansion_rate)


# =================================
# ========== ステージ選択 ==========
# =================================
class StageSelect:
    """ステージ選択の機能"""
    def __init__(self):
        """初期化"""
        self.stagenumber = StageNumber(226, 20, 1, 9, 0.6, 6)

    def update_stageselect(self, pointer_x, pointer_y):
        """更新"""
        # 初期状態：全部False
        self.hover_p = False
        self.selected_p = False
        self.hover_n = False
        self.selected_n = False
        # ホバーしているかのチェック
        if 11-1 <= pointer_y < 28+1:
            if 210-1 <= pointer_x < 215+5:
                self.hover_p = True
            else:
                self.hover_p = False
            if 238-5 <= pointer_x < 243+1:
                self.hover_n = True
            else:
                self.hover_n = False
        if (pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON, 15, 3) and 
            (self.hover_p or self.hover_n)):
            # いずれかがホバーの状態でクリックしたとき選択状態に
            if self.hover_p:
                self.selected_p = True
            elif self.hover_n:
                self.selected_n = True
        # ステージ番号の更新
        self.stagenumber.update_stagenumber(self.selected_p, self.selected_n)
        # 選択されているステージ番号を返す
        return self.stagenumber.num           

    def draw_stageselect(self):
        """描画"""
        self.stagenumber.draw_stagenumber()
        if self.hover_p and not self.selected_p:
            pyxel.blt(210, 11, 0, 192, 232, 5, 17, 0)
        else:
            pyxel.blt(210, 11, 0, 176, 232, 5, 17, 0)
        if self.hover_n and not self.selected_n:
            pyxel.blt(238, 11, 0, 200, 232, 5, 17, 0)
        else:
            pyxel.blt(238, 11, 0, 184, 232, 5, 17, 0)
        if pyxel.btn(pyxel.KEY_SHIFT):
            pyxel.text(208, 3, "STAGE", 1)
            pyxel.text(208, 3, "PRESET", 6)
        else:
            pyxel.text(208, 3, "PRESET", 1)
            pyxel.text(208, 3, "STAGE", 6)            
        pyxel.rectb(208, 9, 37, 21, 5)             










# =============================================================
# =============================================================
# ==================== 描画面に関係するもの ====================
# =============================================================
# =============================================================


# ================================================
# ========== 描画面本体（システム画面外） ==========
# ================================================
class Canvas:
    """ボタンで選択された動作を実行する＋各アクタの管理"""
    def __init__(self):
        self.player = Player()
        self.chasers = Chasers()
        self.capsules = Capsules()
        self.lines_group = LinesGroup()
        self.rectlines = RectLines()
        self.goallines = GoalLines()
        self.selected_button_last = NOTHING
        # キャンバス上の設定
        self.settings = {
            "player_args":None,
            "chasers_args":None,
            "capsules_args":None,
            "lines_group_args":None,
            "goallines_args":None
        }
        self.best_record = BestRecord(1800)
        self.savable = False

    def update_canvas(self, 
            scene: int, 
            selected_button: int, 
            pointer: Pointer,  
            stage_number: int):
        """描画面の更新処理"""
        # セーブ可能か判定
        if (self.settings["player_args"] != None and
            self.settings["chasers_args"] != None and
            self.settings["goallines_args"] != None):
            # 最低限必要なアクタが描画されているとき
            self.savable = True
        else:
            self.savable = False
        # 各アクタが選択されている場合の追加処理
        if scene == DRAW:
            # 場面が DRAW のとき                           
            if selected_button == PLAYER:               
                # === PLAYER ===
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and pointer.on_canvas:
                    self.player.init_player(pointer)
                if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
                    self.player.determine_player()
            elif selected_button == CHASER:             
                # === CHASER ===
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and pointer.on_canvas:
                    self.chasers.append_chaser()
                    self.chasers.chasers[-1].init_chaser(pointer)
                if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
                    if len(self.chasers.chasers):
                        self.chasers.chasers[-1].determine_chaser()
            elif selected_button == CAPSULE_RED:        
                # === CAPSULE_RED ===
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and pointer.on_canvas:
                    self.capsules.add_capsures(0, pointer)
            elif selected_button == CAPSULE_BLUE:       
                # === CAPSULE_BLUE ===
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and pointer.on_canvas:
                    self.capsules.add_capsures(1, pointer)
            elif selected_button == LINE_OPEN:          
                # === LINE_OPEN ===
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and pointer.on_canvas:
                    self.lines_group.operation_continue(0, pointer)
                if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON):
                    self.lines_group.operation_determine(True, 0)
            elif selected_button == LINE_CLOSE:         
                # === LINE_CLOSE ===
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and pointer.on_canvas:
                    self.lines_group.operation_continue(1, pointer)
                if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON):
                    self.lines_group.operation_determine(True, 1)
            elif selected_button == LINE_RECT:
                # === LINE_RECT ===
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and pointer.on_canvas:
                    self.rectlines.init_rectlines(pointer)
                if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
                    self.rectlines.determine_rectlines(pointer, 
                        self.lines_group)
            elif selected_button == GOAL:
                # === GOAL ===
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and pointer.on_canvas:
                    self.goallines.init_goallines(pointer)
                if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
                    self.goallines.determine_goallines()  
        elif scene == ERASE:                        
            # 場面が ERASE のとき
            if selected_button == ERASER_0:             
                # === ERASER_0 ===
                pass  # （マウスポインタ―側で処理）
            elif selected_button == ERASER_1:           
                # === ERASER_1 ===
                pass  # （マウスポインタ―側で処理）
            elif selected_button == ERASER_2:           
                # === ERASER_2 ===
                pass  # （マウスポインタ―側で処理）
            elif selected_button == ERASE_ALL:          
                # === ERASE_ALL ===
                # 全てのアクタの消去処理
                self.player.erase_player()
                self.chasers.clear()
                self.capsules.clear()
                self.lines_group.clear_lines_group()
                self.goallines.erase_goallines()
                # 設定も初期化
                self.settings = {
                    "player_args":None,
                    "chasers_args":None,
                    "capsules_args":None,
                    "lines_group_args":None,
                    "goallines_args":None
                }
        elif scene == LOAD_OR_SAVE:                 
            # 場面が LOAD_OR_SAVE のとき
            if selected_button == STAGE_LOAD:           
                # === STAGE_LOAD のとき ===
                # ステージ設定読込 
                if pyxel.btn(pyxel.KEY_SHIFT):
                    with open('assets/stage_setting_preset.json', 'r') as f:
                        settings_preset = json.load(f)
                    with open('assets/best_record_preset.json', 'r') as f:
                        best_record_preset_json = json.load(f)
                    # 各種設定をセット
                    self.player.set(
                        settings_preset[str(stage_number)]["player_args"], 
                        pointer
                        )
                    self.chasers.set(
                        settings_preset[str(stage_number)]["chasers_args"], 
                        pointer
                        )
                    self.capsules.set(
                        settings_preset[str(stage_number)]["capsules_args"]
                        )
                    self.lines_group.set(
                        settings_preset[str(stage_number)]["lines_group_args"]
                        )
                    self.goallines.set(
                        settings_preset[str(stage_number)]["goallines_args"]
                        )
                    self.best_record.set(
                        best_record_preset_json[str(stage_number)]
                    )
                else:
                    with open('assets/stage_setting.json', 'r') as f:
                        all_settings = json.load(f)
                    with open('assets/best_record.json', 'r') as f:
                        self.best_records_json = json.load(f)
                    # 各種設定をセット
                    self.player.set(
                        all_settings[str(stage_number)]["player_args"], 
                        pointer
                        )
                    self.chasers.set(
                        all_settings[str(stage_number)]["chasers_args"], 
                        pointer
                        )
                    self.capsules.set(
                        all_settings[str(stage_number)]["capsules_args"]
                        )
                    self.lines_group.set(
                        all_settings[str(stage_number)]["lines_group_args"]
                        )
                    self.goallines.set(
                        all_settings[str(stage_number)]["goallines_args"]
                        )
                    self.best_record.set(
                        self.best_records_json[str(stage_number)]
                        )
            elif selected_button == STAGE_SAVE:         
                # === STAGE_SAVE のとき ===
                if self.savable:
                    # 必要最低限のものが全て描画されていた時のみjsonに保存
                    with open('assets/stage_setting.json', 'r') as f:
                        all_settings = json.load(f)
                    all_settings[str(stage_number)] = self.settings
                    with open('assets/stage_setting.json', 'w') as f:
                        json.dump(all_settings, f, indent=4)
                    with open('assets/best_record.json', 'r') as f:
                        self.best_records_json = json.load(f)
                    self.best_records_json[str(stage_number)] = (
                        self.best_record.best_record
                    )
                    with open('assets/best_record.json', 'w') as f:
                        json.dump(self.best_records_json, f, indent=4)
        elif scene == WARN: 
            # 場面がWARNのとき（未実装）                        
            pass        
        elif scene == NOTHING:
            # 場面が NOTHING のとき
            pass  # 何もしない
        # ===== 各アクタの更新処理 =====
        if scene != WARN:
            # 場面がWARNでなければ行う
            self.player.update_player(self.settings, pointer)
            self.chasers.update_chasers(self.settings, pointer)
            self.rectlines.update_rectlines(pointer)
            self.capsules.update_capsules(pointer, selected_button,
                self.settings)
            self.lines_group.update_lines_group(pointer, self.settings, 
                selected_button, self.selected_button_last)
            self.goallines.update_goallines(pointer, self.settings) 
            self.best_record.update_bestrecord()
        # ===== １フレーム前の選択ボタンとして保存 =====
        self.selected_button_last = selected_button

    def draw_canvas(self, pointer: Pointer):
        """描画"""
        # グリッド線描画
        if pyxel.btn(pyxel.KEY_SHIFT):
            for i in range(int(192/16)):
                pyxel.blt(0, 64+i*16, 1, 0, 240, 256, 16, 0)
            for i in range(int(256/16)):
                pyxel.blt(i*16, 64, 1, 192, 0, 16, 192, 0)
        # 各アクタの描画
        self.player.draw_player()
        self.chasers.draw_chasers()
        self.capsules.draw_capsules(pointer)
        self.rectlines.draw_rectlines()
        self.lines_group.draw_lines_group()
        self.goallines.draw_goallines()
        self.best_record.draw_bestrecord()

# ===============================
# ========== プレイヤー ==========
# ===============================
class Player:
    """プレイヤー"""
    def __init__(self):
        """初期化"""
        # 座標と半径
        self.x, self.y = 0, 0
        self.r = 0
        # 自身が存在しているか
        self.exist = False
        # 自身の描画が確定していないか
        self.active = False
        # 当たり判定機能
        self.collision_detector = CollisionDetector()

    def init_player(self, pointer: Pointer):
        """描画を始めるための初期化"""
        self.x = pointer.x
        self.y = pointer.y
        self.r = 0
        self.exist = True
        self.active = True
        self.pointer_x_last = pointer.x
        self.pointer_y_last = pointer.y

    def determine_player(self):
        """描画を確定"""
        if self.active:
            self.active = False

    def erase_player(self):
        """自身を消去"""
        self.active = False
        self.exist = False
        self.x = 0
        self.y = 0
        self.r = 0

    def set(self, args: list, pointer: Pointer):
        """読み込まれた設定の反映"""
        self.erase_player()
        self.x = args[0]
        self.y = args[1]
        self.r = args[2]
        self.exist = True
        self.pointer_x_last = pointer.x
        self.pointer_y_last = pointer.y

    def update_player(self, settings, pointer: Pointer):
        """更新"""
        if self.active:
            # 確定されていない状態のとき
            tar_coord_x = pyxel.mouse_x
            tar_coord_y = pyxel.mouse_y
            if pointer.on_canvas:
                tar_coord_x = pointer.x
                tar_coord_y = pointer.y
            tar_coord = np.array([tar_coord_x, tar_coord_y])
            coord = np.array([self.x, self.y])
            self.dis = np.linalg.norm(tar_coord - coord, ord=2)
            self.r = self.dis/5
        if self.x == 0 and self.y == 0 and self.r == 0:
            settings["player_args"] = None
        else:
            # 自身の状態がオール0でなければ
            settings["player_args"] = [self.x, self.y, self.r]
        if ((pointer.is_eraser and
            (self.collision_detector.check_c2c(self.x, self.y, self.r,
                pointer.x, pointer.y, pointer.r) or
            self.collision_detector.check_c2poly(self.x, self.y, self.r,
                pointer.rect_points))) and
            pyxel.btn(pyxel.MOUSE_LEFT_BUTTON)):
            # 消しゴム状態のポインターに当たったとき
            self.erase_player()
            settings["Player_args"] = None
        # 前フレームの座標として保存
        self.pointer_x_last = pointer.x
        self.pointer_y_last = pointer.y

    def draw_player(self):
        """描画"""
        if self.exist:
            pyxel.circb(self.x, self.y, self.r, 10)


# ===============================
# ========== 追跡者１つ ==========
# ===============================
class Chaser(Player):
    """追跡者"""
    def __init__(self):
        """初期化"""
        super().__init__()

    def init_chaser(self, pointer: Pointer):
        """描画を始めるための初期化"""
        super().init_player(pointer)

    def determine_chaser(self):
        """描画を確定"""
        super().determine_player()

    def erase_chaser(self):
        """自身を消去"""
        super().erase_player()

    def set(self, args: list, pointer: Pointer):
        """読み込まれた設定の反映"""
        super().set(args, pointer)

    def update_chaser(self, pointer: Pointer):
        """更新"""
        self.erase = False
        if self.active:
            tar_coord_x = pyxel.mouse_x
            tar_coord_y = pyxel.mouse_y
            if pointer.on_canvas:
                tar_coord_x = pointer.x
                tar_coord_y = pointer.y
            tar_coord = np.array([tar_coord_x, tar_coord_y])
            coord = np.array([self.x, self.y])
            self.dis = np.linalg.norm(tar_coord - coord, ord=2)
            self.r = self.dis/5
        if ((pointer.is_eraser and
            (self.collision_detector.check_c2c(self.x, self.y, self.r,
                pointer.x, pointer.y, pointer.r) or
            self.collision_detector.check_c2poly(self.x, self.y, self.r,
                pointer.rect_points))) and
            pyxel.btn(pyxel.MOUSE_LEFT_BUTTON)):
            # 消しゴム状態のポインターに当たったとき
            self.erase = True
        self.pointer_x_last = pointer.x
        self.pointer_y_last = pointer.y

    def draw_chaser(self):
        """描画"""
        if self.exist:
            pyxel.circ(self.x, self.y, self.r, 8)
            pyxel.circb(self.x, self.y, self.r, 10)


# =====================================
# ========== 追跡者を包括管理 ==========
# =====================================
class Chasers:
    """追跡者を包括管理"""
    def __init__(self):
        """初期化"""
        self.chasers = []
        self.for_erase = []

    def append_chaser(self):
        """追跡者を１つ加える"""
        self.chasers.append(Chaser())

    def update_chasers(self, settings, pointer: Pointer):
        """更新"""
        if self.chasers != []:
            for chaser in self.chasers:
                chaser.update_chaser(pointer)
            self.for_erase.clear()
            index = 0
            for _ in range(len(self.chasers)):
                if self.chasers[index].erase:
                    self.chasers.pop(index)
                    index -= 1
                index += 1
            settings["chasers_args"] = [[c.x, c.y, c.r] for c in self.chasers]
        else:
            settings["chasers_args"] = None

    def clear(self):
        """消去"""
        self.chasers.clear()

    def set(self, args, pointer: Pointer):
        """読み込まれた設定の反映"""
        self.clear()
        for a in args:
            chaser = Chaser()
            chaser.set(a, pointer)
            chaser.determine_chaser()
            self.chasers.append(chaser)

    def draw_chasers(self):
        """描画"""
        for chaser in self.chasers:
            chaser.draw_chaser()


# =======================================
# ========== カプセル（赤・青） ==========
# =======================================
class Capsule:
    """カプセル（赤・青）"""
    def __init__(self, x, y, col):
        """初期化"""
        self.x, self.y = x, y
        self.col = col
        self.hit_points = [
            [self.x-6, self.y+2],
            [self.x+1, self.y-5],
            [self.x+3, self.y-5],
            [self.x+5, self.y-3],
            [self.x+5, self.y-1],
            [self.x-2, self.y+6],
            [self.x-4, self.y+6],
            [self.x-6, self.y+4],
            [self.x-6, self.y+2],
            ] 
        self.collision_detector = CollisionDetector()

    def hit_check(self, pointer: Pointer):
        """消しゴムとの当たり判定をboolで返す"""
        for index, point in enumerate(self.hit_points):
            if index < len(self.hit_points) - 1:
                if (self.collision_detector.check_l2c(
                        point[0], point[1],
                        self.hit_points[index+1][0], 
                        self.hit_points[index+1][1],
                        pointer.x, pointer.y, pointer.r) or
                    self.collision_detector.check_l2poly(
                        point[0], point[1],
                        self.hit_points[index+1][0], 
                        self.hit_points[index+1][1],
                        pointer.rect_points
                    )):
                    # 当たり判定がTrueのときにTrueを返す
                    return True
        return False

    def draw_capsule(self):
        """描画"""
        if self.col == 0:
            pyxel.blt(self.x-6, self.y-5, 0, 34, 234, 12, 12, 0)
        elif self.col == 1:
            pyxel.blt(self.x-6, self.y-5, 0, 50, 234, 12, 12, 0)


# ================================================
# ========== カプセル（赤・青）を包括管理 ==========
# ================================================
class Capsules:
    """カプセルを包括管理"""
    def __init__(self):
        """初期化"""
        self.capsules = []

    def add_capsures(self, col: int, pointer: Pointer):
        """カプセルを追加"""
        # col 0:赤, 1:青
        self.capsules.append(Capsule(pointer.x, pointer.y, col))
    
    def clear(self):
        """消去"""
        self.capsules.clear()

    def update_capsules(self,pointer: Pointer, 
        selected_button: int, settings: dict):
        """更新"""
        self.selected_button = selected_button
        if (len(self.capsules) and 
            pointer.is_eraser and 
            pyxel.btn(pyxel.MOUSE_LEFT_BUTTON)):
            # ポインターが消しゴム　かつクリックしていたら
            index = 0
            for _ in range(len(self.capsules)):
                if not len(self.capsules):
                    # 消去の結果長さが0になったら
                    break
                if self.capsules[index].hit_check(pointer):
                    self.capsules.pop(index)
                    index -= 1
                index += 1
        if len(self.capsules):
            settings["capsules_args"] = ([[c.x, c.y, c.col] for c 
                in self.capsules])
        else:
            settings["capsules_args"] = None
    
    def set(self, args: list):
        """読み込まれた設定の反映"""
        self.clear()
        if args != None:
            for arg in args:
                self.capsules.append(Capsule(arg[0], arg[1], arg[2]))

    def draw_capsules(self, pointer: Pointer):
        """描画"""
        if pointer.on_canvas:
            if self.selected_button == CAPSULE_RED:
                pyxel.blt(pointer.x-6, pointer.y-5, 0, 106, 194, 12, 12, 0)
            elif self.selected_button == CAPSULE_BLUE:
                pyxel.blt(pointer.x-6, pointer.y-5, 0, 122, 194, 12, 12, 0)
        for capsule in self.capsules:
            capsule.draw_capsule()


# =========================================
# ========== 線の集まりを包括管理 ==========
# =========================================
class LinesGroup:
    """線の集まりを包括管理"""
    def __init__(self):
        """初期化"""
        self.lines_group = []
        self.exist = False
        self.determined = True

    def operation_continue(self, close: int, pointer: Pointer):
        """次ステップの操作（線の集まりを生成＆点を追加）"""
        if self.determined:
            self.determined = False
            self.lines_now = Lines(close, 6, 5)
            self.lines_now.update_lines(pointer)
        self.lines_now.add_point()

    def operation_determine(self, generate_next: bool, close: int):
        """線の集まりを確定させて次を生成する"""
        if not self.determined:
            self.determined = True
            if self.lines_now.check():
                self.lines_now.determine_lines()
                self.lines_group.append(self.lines_now)
            if generate_next:
                self.lines_now = Lines(close, 6, 5)

    def update_lines_group(self, pointer: Pointer, settings, 
        selected_button, selected_button_last):
        """更新"""
        if not self.determined:
            self.lines_now.update_lines(pointer)
        else:
            for index, lines in enumerate(self.lines_group):
                if lines.erase_check(pointer, self) == True:
                    self.lines_group.pop(index)
        if len(self.lines_group):
            self.exist = True
            settings["lines_group_args"] = [[ls.points, ls.close] 
                for ls in self.lines_group]
        else:
            self.exist = False
            settings["lines_group_args"] = None
        if selected_button_last != selected_button:
            if not self.determined:
                # 描画が確定されないままボタン切替が起こったら消去
                self.operation_determine(False, 0)

    def clear_lines_group(self):
        """線の集まりを全消去"""
        if self.exist:
            self.lines_now.clear_lines()
            self.lines_group.clear()
            self.determined = True
            self.exist = False

    def set(self, args: list):
        """読み込まれた設定の反映"""
        self.clear_lines_group()
        if args != None:
            for a in args:
                self.lines_now = Lines(a[1], 6, 5)
                self.lines_now.set(a[0])
                self.lines_now.determine_lines()
                self.lines_group.append(self.lines_now)

    def draw_lines_group(self):
        """描画"""
        if not self.determined:
            self.lines_now.draw_lines()
        for lines in self.lines_group:
            lines.draw_lines()


# ===================================
# ========== 線の集まり１つ ==========
# ===================================
class Lines:
    """線の集まり"""
    def __init__(self, close: int, col_active: int, col_inactive: int):
        """初期化"""
        self.active = True
        # 点群の座標を格納
        self.points = []
        # 各線の当たり判定結果
        self.hit = []
        # 0：開いている 1:閉じている
        self.close = close
        self.col_active = col_active
        self.col_inactive = col_inactive
        self.corrision_detector = CollisionDetector()

    def add_point(self):
        """点の追加"""
        # 点の座標を末尾に追加
        self.points.append([self.pointer_x, self.pointer_y])

    def update_lines(self, pointer: Pointer):
        """更新"""
        self.pointer_x = pointer.x
        self.pointer_y = pointer.y

    def clear_lines(self):
        """消去"""
        self.active = False
        self.points.clear()

    def erase_check(self, pointer: Pointer, lines_group: LinesGroup):
        """消しゴムとの当たり判定, その後の処理"""
        self.hit.clear()
        if len(self.points) > 1:
            # 点群のリスト長さが存在すれば
            for i, point in enumerate(self.points):
                if (pointer.is_eraser and
                    pyxel.btn(pyxel.MOUSE_LEFT_BUTTON)):
                    # ポインターが消しゴム化していてマウス左が押されていたら
                    # ポインターとの当たり判定＝消しゴムに消された判定
                    # indexの位置によって次の
                    if i < len(self.points) - 1:
                        point_next = self.points[i+1]
                    elif self.close:
                        point_next = self.points[0]
                    else:
                        break
                    if (self.corrision_detector.check_l2c(
                                point[0], point[1], 
                                point_next[0], point_next[1], 
                                pointer.x, pointer.y, pointer.r) or
                        self.corrision_detector.check_l2poly(
                                point[0], point[1], 
                                point_next[0], point_next[1],  
                                pointer.rect_points)):
                        self.hit.append(True)
                    else:
                        # 消される条件が無ければ
                        self.hit.append(False)
            if any(self.hit):
                i = 0
                if self.close:
                    lines_number = len(self.points)
                else:
                    lines_number = len(self.points) - 1
                if len(self.points) <= 2:
                    self.clear_lines()
                for h in self.hit:
                    if h and lines_number > 1:
                        if self.close:
                            self.close = 0
                            if i == 0:
                                # これまでの先頭要素を取り出して末尾に移動
                                start2end = self.points.pop(0)
                                self.points.append(start2end)
                                i -= 1
                                lines_number -= 1
                            elif i == lines_number - 1:
                                # 末尾は最後の点->最初の点
                                # closeを0にした時点で消去完了
                                lines_number -= 1
                            else:
                                # 当たった線の終点以降を前半に、
                                # 当たった線の始点以前を後半に入れ替える
                                # ->当たった線の終点は始点に、
                                # 当たった線の始点は終点になる
                                before2after = self.points[:i+1]
                                after2before = self.points[i+1:]
                                self.points = after2before + before2after
                                # indexを直前部分の移動距離に合わせて戻す
                                i -= len(before2after)
                                lines_number -= 1
                        else:
                            if i == 0:
                                self.points.pop(0)
                                i -= 1
                                lines_number -= 1
                            elif i == lines_number - 1:
                                self.points.pop(-1)
                                lines_number -= 1
                            else:
                                before = self.points[:i+1]
                                after = self.points[i+1:]
                                # after部分を新たな線としてLineGroupに追加
                                # そちらに以降のhitを引き継いで
                                # 同様の消去処理を行う
                                self.points = before
                                splited_lines = Lines(0, 6, 5)
                                if not splited_lines.after_split(after, 
                                    self.hit[i+1:], lines_group):
                                    # 分割した先の点が2つより多ければ
                                    splited_lines.determine_lines()
                                    lines_group.lines_group.append(
                                        splited_lines
                                        )
                                break
                    i += 1

    def check(self):
        """線が１本以上あるかどうか"""
        return len(self.points) > 1

    def determine_lines(self):
        """線の集まりを確定させる"""
        self.active = False

    def after_split(self, points: list, hit: list, lines_group: LinesGroup):
        """自身が元の線の集まりから分割された場合の処理
        
        erase_checkの当たり判定後の処理を同様に行う
        """
        self.points = points
        self.hit = hit
        if any(self.hit):
            i = 0
            if self.close:
                lines_number = len(self.points)
            else:
                # 閉じる線の分引く
                lines_number = len(self.points) - 1
            if len(self.points) <= 2:
                self.clear_lines()
                return True
            for h in self.hit:
                if h and lines_number > 1:
                    if self.close:
                        self.close = 0
                        if i == 0:
                            # これまでの先頭要素を取り出して末尾に移動
                            start2end = self.points.pop(0)
                            self.points.append(start2end)
                            i -= 1
                            lines_number -= 1
                        elif i == lines_number:
                            # 末尾は最後の点->最初の点
                            # closeを0にした時点で消去完了
                            lines_number -= 1
                        else:
                            # 当たった線の終点以降を前半に、
                            # 当たった線の始点以前を後半に入れ替える
                            # ->当たった線の終点は始点に、
                            # 当たった線の始点は終点になる
                            before2after = self.points[:i+1]
                            after2before = self.points[i+1:]
                            self.points = after2before + before2after
                            # indexを直前部分の移動距離に合わせて戻す
                            i -= len(before2after)
                            lines_number -= 1
                    else:
                        if i == 0:
                            self.points.pop(0)
                            i -= 1
                            lines_number -= 1
                        elif i == lines_number:
                            self.points.pop(-1)
                            lines_number -= 1
                        else:
                            before = self.points[:i+1]
                            after = self.points[i+1:]
                            # after部分を新たな線としてLineGroupに追加
                            # そちらに以降のhitを引き継いで同様の消去処理を行う
                            self.points = before
                            splited_lines = Lines(0, 6, 5)
                            if not splited_lines.after_split(after, 
                                self.hit[i+1:], lines_group):
                                # 分割した先の点が2つより多ければ
                                splited_lines.determine_lines()
                                lines_group.lines_group.append(splited_lines)
                            break
                i += 1

    def set(self, args):
        """読み込まれた設定の反映"""
        self.points = args
        self.determine_lines()
        

    def draw_lines(self):
        """描画"""
        for index,  point in enumerate(self.points):
            if index < len(self.points) - 1:
                point_next = self.points[index+1]
            else:
                if self.close:
                    point_next = self.points[0]
                    if self.active:
                        pyxel.line(point[0], point[1], 
                            self.pointer_x, self.pointer_y, self.col_active)
                        pyxel.line(self.pointer_x, self.pointer_y,
                            self.points[0][0], self.points[0][1], 
                            self.col_active)
                    else:
                        point_next = self.points[0]
                else:
                    if self.active:
                        pyxel.line(point[0], point[1], 
                            self.pointer_x, self.pointer_y, self.col_active)
                    return
            pyxel.line(point[0], point[1], 
                    point_next[0], point_next[1], self.col_inactive)


# ===============================
# ========== 長方形の線 ==========
# ===============================
class RectLines:
    """ゴールの長方形"""
    def __init__(self):
        """初期化"""
        self.exist = False
        self.active = False
        self.x_init, self.y_init = 0, 0
        self.x, self.y = 0, 0
        self.w, self.h = 0, 0
        self.corrision_detector = CollisionDetector()

    def init_rectlines(self, pointer: Pointer):
        """描画を始めるための初期化"""
        self.x_init, self.y_init = pointer.x, pointer.y
        self.x, self.y = pointer.x, pointer.y
        self.w, self.h = 0, 0
        self.exist = True
        self.active = True

    def determine_rectlines(self, pointer: Pointer, lines_group: LinesGroup):
        """描画を確定させる"""
        if abs(self.w) < 1 or abs(self.h) < 1:
            self.erase_rectlines()
        elif abs(self.w) == 1:
            lines_group.operation_continue(0, pointer)
            lines_group.lines_now.points = [
                [self.x, self.y], 
                [self.x, self.y+self.h-1]
            ]
            lines_group.operation_determine(False, 0)
            self.erase_rectlines()
        elif abs(self.h) == 1:
            lines_group.operation_continue(0, pointer)
            lines_group.lines_now.points = [
                [self.x, self.y], 
                [self.x+self.w-1, self.y]
            ]
            lines_group.operation_determine(False, 0)
            self.erase_rectlines()
        else:
            lines_group.operation_continue(1, pointer)
            lines_group.lines_now.points = [
                [self.x, self.y], 
                [self.x+self.w-1, self.y], 
                [self.x+self.w-1, self.y+self.h-1], 
                [self.x, self.y+self.h-1]
            ]
            lines_group.operation_determine(False, 1)
            self.erase_rectlines()

    def erase_rectlines(self):
        """消去"""
        self.active = False
        self.exist = False
        self.x, self.y = 0, 0
        self.w, self.h = 0, 0

    def update_rectlines(self, pointer: Pointer):
        """更新"""
        if self.active:
            self.w = pointer.x - self.x_init + 1
            self.h = pointer.y - self.y_init + 1
            if self.w < 0:
                self.x = pointer.x
                self.w = self.w * (-1) + 2
            else:
                self.x = self.x_init
            if self.h < 0:
                self.y = pointer.y
                self.h = self.h * (-1) + 2
            else:
                self.y = self.y_init

    def draw_rectlines(self):
        if self.exist:
            pyxel.rectb(self.x, self.y, self.w, self.h, 6)


# ===================================
# ========== ゴールの長方形 ==========
# ===================================
class GoalLines:
    """ゴールの長方形"""
    def __init__(self):
        """初期化"""
        self.exist = False
        self.active = False
        self.x_init, self.y_init = 0, 0
        self.x, self.y = 0, 0
        self.w, self.h = 0, 0
        self.corrision_detector = CollisionDetector()

    def init_goallines(self, pointer: Pointer):
        """描画を始めるための初期化"""
        self.x_init, self.y_init = pointer.x, pointer.y
        self.x, self.y = pointer.x, pointer.y
        self.w, self.h = 0, 0
        self.exist = True
        self.active = True

    def determine_goallines(self):
        """描画を確定させる"""
        if abs(self.w) < 7 or abs(self.h) < 9:
            self.erase_goallines()
        else:
            self.active = False

    def erase_goallines(self):
        """消去"""
        self.active = False
        self.exist = False
        self.x, self.y = 0, 0
        self.w, self.h = 0, 0

    def erase_check(self, pointer: Pointer):
        """消しゴムとの当たり判定"""
        if pointer.is_eraser and pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
            points = [
                        [self.x, self.y], 
                        [self.x+self.w-1, self.y], 
                        [self.x+self.w-1, self.y+self.h-1], 
                        [self.x, self.y+self.h-1]
                    ]
            for index, point in enumerate(points):
                if index < len(points)-1:
                    point_next = points[index+1]
                else:
                    point_next = points[0]
                if (self.corrision_detector.check_l2c(point[0], point[1],
                        point_next[0], point_next[1], 
                        pointer.x, pointer.y, pointer.r) or
                    self.corrision_detector.check_l2poly(point[0], point[1],
                        point_next[0], point_next[1],
                        pointer.rect_points)):
                    self.erase_goallines()

    def update_goallines(self, pointer: Pointer, settings):
        """更新"""
        if self.active:
            self.w = pointer.x - self.x_init + 1
            self.h = pointer.y - self.y_init + 1
            if self.w < 0:
                self.x = pointer.x
                self.w = self.w * (-1) + 2
            else:
                self.x = self.x_init
            if self.h < 0:
                self.y = pointer.y
                self.h = self.h * (-1) + 2
            else:
                self.y = self.y_init
        else:
            self.erase_check(pointer)
        if self.x == 0 and self.y == 0 and self.w == 0 and self.h == 0:
            settings["goallines_args"] = None
        else:
            settings["goallines_args"] = [
                [
                    [self.x, self.y], 
                    [self.x+self.w-1, self.y], 
                    [self.x+self.w-1, self.y+self.h-1], 
                    [self.x, self.y+self.h-1]
                ], 
                1
            ]

    def set(self, args):
        self.erase_goallines()
        self.exist = True
        self.x = args[0][0][0]
        self.y = args[0][0][1]
        self.w = args[0][1][0] - self.x + 1
        self.h = args[0][2][1] - self.y + 1

    def draw_goallines(self):
        if self.exist:
            pyxel.rectb(self.x, self.y, self.w, self.h, 8)
            pyxel.blt(self.x+(self.w/2)-2, self.y+(self.h/2)-2, 
                0, 102, 238, 4, 6, 0)


# ===================================
# ========== ベストレコード ==========
# ===================================
class BestRecord:
    """ベストレコード設定の機能"""
    def __init__(self, best_record):
        self.best_record = best_record
        # h = (総フレーム数 ÷ fps) ÷ 3600 の小数点以下切り捨て
        # m = hの小数部 × 60 の小数点以下切り捨て
        # s = mの小数部 × 60 の小数点以下切り捨て
        # f = sの小数部 × 100 の小数点以下切り捨て
        self.f_b: int = (self.best_record % 1800) % 30
        self.s_b: int = int((self.best_record % 1800) / 30)
        self.m_b: int = int(self.best_record / 1800)
        self.m_b = str(self.m_b).rjust(2, '0')
        self.s_b = str(self.s_b).rjust(2, '0')
        self.f_b = str(self.f_b).rjust(2, '0')
        self.x = 150
        self.y = 42
        self.w = 19
        self.h = 8
        self.coord_list = [
            [self.x-14, self.y-10],
            [self.x-14+21, self.y-10],
            [self.x-14+21*2, self.y-10],
            [self.x-14, self.y+11],
            [self.x-14+21, self.y+11],
            [self.x-14+21*2, self.y+11],
            ]
        self.hover_list = [False for _ in range(6)]
        self.push_list = [False for _ in range(6)]
    
    def set(self, best_record):
        self.best_record = best_record
        # h = (総フレーム数 ÷ fps) ÷ 3600 の小数点以下切り捨て
        # m = hの小数部 × 60 の小数点以下切り捨て
        # s = mの小数部 × 60 の小数点以下切り捨て
        # f = sの小数部 × 100 の小数点以下切り捨て
        self.f_b: int = (self.best_record % 1800) % 30
        self.s_b: int = int((self.best_record % 1800) / 30)
        self.m_b: int = int(self.best_record / 1800) 
        self.m_b = str(self.m_b).rjust(2, '0')
        self.s_b = str(self.s_b).rjust(2, '0')
        self.f_b = str(self.f_b).rjust(2, '0')

    def update_bestrecord(self):
        """更新"""
        for i in range(6):
            # ホバーと押されている判定の処理
            if (self.coord_list[i][0] <= pyxel.mouse_x and
                pyxel.mouse_x < self.coord_list[i][0]+self.w and
                self.coord_list[i][1] <= pyxel.mouse_y and
                pyxel.mouse_y < self.coord_list[i][1]+self.h):
                # ホバーしているとき
                self.hover_list[i] = True
            else:
                # ホバーしていないとき
                self.hover_list[i] = False
            if (pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON, 15, 2) and 
                self.hover_list[i]):
                self.push_list[i] = True
            else:
                self.push_list[i] = False
        # ベストレコードの値の増減
        if self.push_list[0] or self.push_list[3]:
            if self.push_list[0]:
                # m, increase
                self.m_b = str(int(self.m_b)+1).rjust(2, '0')
            elif self.push_list[3]:
                # m, decrease
                self.m_b = str(int(self.m_b)-1).rjust(2, '0')
            if int(self.m_b) < 0:
                self.m_b = "99"
            elif int(self.m_b) > 99:
                self.m_b = "00"
        elif self.push_list[1] or self.push_list[4]:
            if self.push_list[1]:
                # s, increase
                self.s_b = str(int(self.s_b)+1).rjust(2, '0')
            elif self.push_list[4]:
                # s, decrease
                self.s_b = str(int(self.s_b)-1).rjust(2, '0')
            if int(self.s_b) < 0:
                self.s_b = "59"
            elif int(self.s_b) > 59:
                self.s_b = "00"
        elif self.push_list[2] or self.push_list[5]:
            if self.push_list[2]:
                # f, increase
                self.f_b = str(int(self.f_b)+1).rjust(2, '0')
            elif self.push_list[5]:
                # f, decrease
                self.f_b = str(int(self.f_b)-1).rjust(2, '0')
            if int(self.f_b) < 0:
                self.f_b = "29"
            elif int(self.f_b) > 29:
                self.f_b = "00"
        # ベストレコードの反映
        self.best_record = (int(self.m_b)*60*30
            + int(self.s_b)*30
            + int(int(self.f_b)))

    def draw_bestrecord(self):
        """描画"""
        x = self.x
        y = self.y
        pyxel.rect(x-3, y-2, 40, 13, 0)
        pyxel.rectb(x-3, y-2, 40, 13, 13)
        pyxel.line(x-3+39, y-2, x-3+39, y-2+12, 15)
        pyxel.line(x-3+39, y-2+12, x-3, y-2+12, 15)
        # m
        pyxel.blt(x, y, 1, int(self.m_b[0])*8, 16, 8, 8, 0)
        pyxel.blt(x+5*1, y, 1, int(self.m_b[1])*8, 16, 8, 8, 0)
        # '
        pyxel.pset(x+22, y, 10)
        pyxel.pset(x+24, y, 10)
        # s
        pyxel.blt(x+5*2+2, y, 1, int(self.s_b[0])*8, 16, 8, 8, 0)
        pyxel.blt(x+5*3+2, y, 1, int(self.s_b[1])*8, 16, 8, 8, 0)
        # ''
        pyxel.pset(x+11, y, 10)
        # f
        f_display = str(int(int(self.f_b)*3.33)).rjust(2, '0')
        pyxel.blt(x+5*4+4, y, 1, int(f_display[0])*8, 16, 8, 8, 0)
        pyxel.blt(x+5*5+4, y, 1, int(f_display[1])*8, 16, 8, 8, 0)
        pyxel.text(x-13, y-16, "BEST RECORD", 6)
        u_init = 208
        v = 232
        w = self.w
        h = self.h
        # 左上
        if self.hover_list[0]:
            pyxel.rect(self.coord_list[0][0],
                self.coord_list[0][1],
                w, h, 1)
            if not self.push_list[0]:
                u = u_init + 24
            else:
                u = u_init
        else:
            u = u_init
        pyxel.blt(
            self.coord_list[0][0], 
            self.coord_list[0][1], 
            0, u, v, w, (-1)*h, 0
            )
        # 中央上
        if self.hover_list[1]:
            pyxel.rect(self.coord_list[1][0],
                self.coord_list[1][1],
                w, h, 1)
            if not self.push_list[1]:
                u = u_init + 24
            else:
                u = u_init
        else:
            u = u_init
        pyxel.blt(
            self.coord_list[1][0], 
            self.coord_list[1][1], 
            0, u, v+8, w, (-1)*h, 0
            )
        # 右上
        if self.hover_list[2]:
            pyxel.rect(self.coord_list[2][0],
                self.coord_list[2][1],
                w, h, 1)
            if not self.push_list[2]:
                u = u_init + 24
            else:
                u = u_init
        else:
            u = u_init
        pyxel.blt(
            self.coord_list[2][0], 
            self.coord_list[2][1], 
            0, u, v, -1*w, (-1)*h, 0
            )
        # 左下
        if self.hover_list[3]:
            pyxel.rect(self.coord_list[3][0],
                self.coord_list[3][1],
                w, h, 1)
            if not self.push_list[3]:
                u = u_init + 24
            else:
                u = u_init
        else:
            u = u_init
        pyxel.blt(
            self.coord_list[3][0], 
            self.coord_list[3][1], 
            0, u, v, w, h, 0
            )
        # 中央下
        if self.hover_list[4]:
            pyxel.rect(self.coord_list[4][0],
                self.coord_list[4][1],
                w, h, 1)
            if not self.push_list[4]:
                u = u_init + 24
            else:
                u = u_init
        else:
            u = u_init
        pyxel.blt(
            self.coord_list[4][0], 
            self.coord_list[4][1], 
            0, u, v+8, w, h, 0
            )
        # 右下
        if self.hover_list[5]:
            pyxel.rect(self.coord_list[5][0],
                self.coord_list[5][1],
                w, h, 1)
            if not self.push_list[5]:
                u = u_init + 24
            else:
                u = u_init
        else:
            u = u_init
        pyxel.blt(
            self.coord_list[5][0], 
            self.coord_list[5][1], 
            0, u, v, -1*w, h, 0
            )


# ===============================================
# ==================== その他 ====================
# ===============================================


# ========== システム画面背景の描画 ==========
def draw_bg():
    """システム画面背景の描画"""
    # === 外枠 ===
    pyxel.rectb(0, 0, 256, 64, 5)
    # === 区切り線 ===
    pyxel.line(75, 3, 75, 60, 5)
    pyxel.line(134, 3, 134, 60, 5)
    pyxel.line(198, 3, 198, 60, 5)
    # === DRAW ===
    pyxel.blt(4, 4, 0, 0, 220, 38, 12, 0)     # "DRAW"
    pyxel.blt(3, 23, 0, 0, 232, 16, 16, 0)    # player
    pyxel.blt(21, 23, 0, 16, 232, 16, 16, 0)  # chaser
    pyxel.blt(39, 23, 0, 32, 232, 16, 16, 0)  # capsule(red)
    pyxel.blt(57, 23, 0, 48, 232, 16, 16, 0)  # capsule(blue)
    pyxel.blt(3, 41, 0, 64, 232, 16, 16, 0)   # lines(open)
    pyxel.blt(21, 41, 0, 80, 232, 16, 16, 0)  # lines(close)
    pyxel.blt(39, 41, 0, 88, 192, 16, 16, 0)  # lines(rect)
    pyxel.blt(57, 41, 0, 96, 232, 16, 16, 0)  # goal
    # === ERASE ===
    pyxel.blt(80, 4, 0, 38, 220, 45, 12, 0)    # "ERASE"
    pyxel.blt(80, 23, 0, 112, 232, 49, 17, 0)  # eraser
    # === EXPLANATION ===
    #pyxel.text(137, 3, "EXPLANATION", 6)       # "EXPLANATION"
    pyxel.text(137, 3, "KEYSTROKE", 6)
    pyxel.rectb(137, 9, 59, 15, 5)             # 枠