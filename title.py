import pyxel
import numpy as np
from stage import Pointer

# モード選択に関する定数扱い変数
STAGE_SELECT: int = 1
EDIT:         int = 3
ENDLESS:      int = 4


class Title:
    """タイトル画面"""
    def __init__(self, size_x, size_y):
        self.active = True
        self.size_x = size_x
        self.size_y = size_y
        self.pointer = Pointer()
        self.select = ModeSelect(self.size_x, self.size_y)
        self.selected_mode = None

    def update_title(self):
        """情報の更新"""
        self.active = True
        self.pointer.update_pointer(0, 0, self.size_x, self.size_y)
        self.active, self.selected_mode = self.select.update_modeselect(self.pointer)

    def draw_title(self):
        """タイトル画面の描画"""
        pyxel.blt(0, 8, 2, 0, 0, self.size_x, 193, 0)
        pyxel.text(self.size_x-50, 2, "Ver.Alpha", 7)
        self.select.draw_modeselect()
        pyxel.blt(self.size_x/2-51, self.size_y-52, 2, 111, 219, 103, 10, 1)
        if pyxel.frame_count%16 < 8:
            pyxel.blt(self.size_x/2-50, self.size_y-51, 2, 0, 216, 101, 8, 0)
        else:
            pyxel.blt(self.size_x/2-50, self.size_y-51, 2, 0, 224, 101, 8, 0)
        if pyxel.frame_count%30 < 15:  
            pyxel.circ(143, 167, 8, 8)
        else:
            pyxel.circ(143, 167, 8, 10)
        pyxel.circb(143, 167, 8, 10)
        self.pointer.draw_pointer()

class ModeArrow:
    """モード選択のための矢印"""
    def __init__(self, size_x, size_y):
        """コンストラクタ"""
        self.size_x = size_x
        self.size_y = size_y
        self.x_l = -2
        self.y_l = self.size_y-52
        self.x_r = self.size_x-22
        self.y_r = self.y_l
        self.w = 23
        self.h = 48
        self.hover_l, self.hover_r = False, False
        self.push_l, self.push_r = False, False

    def update_modearrow(self, pointer: Pointer):
        """更新"""
        self.hover_l, self.hover_r = False, False
        self.push_l, self.push_r = False, False
        if pointer.on_screen:
            if (self.x_l <= pointer.x < self.x_l+self.w and 
                self.y_l <= pointer.y < self.y_l+self.h):
                self.hover_l = True
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                    pyxel.play(3, 1)
                    self.push_l = True
            elif (self.x_r <= pointer.x < self.x_r+self.w and 
                self.y_r <= pointer.y < self.y_r+self.h):
                self.hover_r = True
                if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                    pyxel.play(3, 1)
                    self.push_r = True

    def draw_modearrow(self):
        """描画"""
        # ホバーしているときの背景
        if self.hover_l:
            pyxel.bltm(self.x_l, self.y_l, 0, 0, 0, 3, 6)
            pyxel.line(self.x_l+self.w, self.y_l, 
                self.x_l+self.w, self.y_l+self.h, 0)
        if self.hover_r:
            pyxel.bltm(self.x_r, self.y_r, 0, 0, 0, 3, 6)
        # 元の赤
        if self.hover_l and not self.push_l:
            pyxel.blt(1, self.size_y-38, 2, 198, 232, 18, 18, 1)
        elif self.hover_r and not self.push_r:
            pyxel.blt(self.size_x-16-4, self.size_y-38, 2, 162, 232, 18, 18, 1)
        pyxel.blt(1, self.size_y-37, 2, 180, 232, 18, 18, 1)
        pyxel.blt(self.size_x-16-4, self.size_y-37, 2, 144, 232, 18, 18, 1)
        pyxel.blt(2, self.size_y-36, 0, 0, 128, 16, 16, 0)
        pyxel.blt(self.size_x-16-3, self.size_y-36, 0, 0, 112, 16, 16, 0)
        # ホバーしていて押されていないときの浮いている黄色
        if self.hover_l and not self.push_l:
            pyxel.blt(2, self.size_y-37, 0, 16, 128, 16, 16, 0)
        if self.hover_r and not self.push_r:
            pyxel.blt(self.size_x-16-3, self.size_y-37, 0, 16, 112, 16, 16, 0)


class ModeSelect:
    """モード選択部分"""
    def __init__(self, size_x, size_y):
        """コンストラクタ"""
        # 矢印
        self.arrow = ModeArrow(size_x, size_y)
        self.size_x, self.size_y = size_x, size_y
        self.mode_list = [STAGE_SELECT, EDIT]
        # 非選択モード管理用
        self.selected_mode: int = self.mode_list[0]
        # 文字表示位置用
        self.for_STAGESELECT = [[0, 200], [16, 200], [32, 200], [48, 200],
            [64, 200], 0, [0, 200], [64, 200], [80, 200], [64, 200],
            [96, 200], [16, 200]]
        self.for_EDIT = [[64, 200], [112, 200], [128, 200], [16, 200]]
        self.move = False
        self.selected_index = 0
        self.hover = False
        self.push = False
        self.click_after_hover = False

    def update_modeselect(self, pointer: Pointer):
        """更新"""
        # 矢印の更新
        self.arrow.update_modearrow(pointer)
        # 矢印の情報から非選択モードの表示
        if self.move:
            self.start_coord = ([self.size_x/2 
                - (len(self.selected_list)*16+(len(self.selected_list)-1))/2, 
                self.size_y-36])
            self.move = False
        if self.selected_mode == STAGE_SELECT:
            self.selected_list = self.for_STAGESELECT
        elif self.selected_mode == EDIT:
            self.selected_list = self.for_EDIT    
        self.start_coord = ([self.size_x/2 
            - (len(self.selected_list)*16+(len(self.selected_list)-1))/2, 
            self.size_y-36])
        if self.arrow.push_l:
            self.selected_index -= 1
            if self.selected_index == -1:
                self.selected_index = len(self.mode_list)-1
            self.start_coord[0] -= 1
            self.move = True
        elif self.arrow.push_r:
            self.selected_index += 1
            if self.selected_index == len(self.mode_list):
                self.selected_index = 0
            self.start_coord[0] += 1
            self.move = True
        self.selected_mode = self.mode_list[self.selected_index]
        # ボタンの処理
        self.hover = False
        self.push = False
        if pointer.on_screen:
            if (22 <= pointer.x < self.size_x-23 and 
                self.size_y-52 <= pointer.y < self.size_y-52+48):
                self.hover = True
            if self.hover and pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                self.click_after_hover = True
            if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
                if self.click_after_hover and self.hover:
                    self.push = True
                self.click_after_hover = False
        return not self.push, self.selected_mode  

    def draw_modeselect(self):
        """描画"""
        if self.hover:
            #pyxel.rect(22, self.size_y-52, self.size_x-45, 48, 1)
            pyxel.bltm(22, self.size_y-52, 0, 0, 0, 27, 6, 0)
            pyxel.rect(self.arrow.x_r-1, self.size_y-52, 16, 48, 0)
            # ホバーしているとき
            if self.click_after_hover:
                pyxel.rect(self.start_coord[0]-5, self.start_coord[1]-5, 
                    (len(self.selected_list)*16+(len(self.selected_list)-1))+10,
                    16+10, 0)
                # and 一回自身の上で押していて離す前の状態
                pyxel.rectb(self.start_coord[0]-4, self.start_coord[1]-4, 
                    (len(self.selected_list)*16+(len(self.selected_list)-1))+8,
                    16+8, 5)
                for index, coord in enumerate(self.selected_list):
                    if coord != 0:
                        pyxel.blt(self.start_coord[0]+16*index+index, self.start_coord[1], 2, 
                            coord[0], coord[1]+32, 16, 16, 0)
                    else:
                        pass
            else:
                # and 自身が押されておらずただホバーしているとき
                # ホバーしていないとき
                pyxel.rect(self.start_coord[0]-5, self.start_coord[1]-6, 
                    (len(self.selected_list)*16+(len(self.selected_list)-1))+10,
                    16+11, 0)
                pyxel.rectb(self.start_coord[0]-4, self.start_coord[1]-4, 
                    (len(self.selected_list)*16+(len(self.selected_list)-1))+8,
                    16+8, 5)
                for index, coord in enumerate(self.selected_list):
                    if coord != 0:
                        pyxel.blt(self.start_coord[0]+16*index+index, self.start_coord[1], 2, 
                            coord[0], coord[1]+32, 16, 16, 0)
                    else:
                        pass
                pyxel.rectb(self.start_coord[0]-4, self.start_coord[1]-5, 
                    (len(self.selected_list)*16+(len(self.selected_list)-1))+8,
                    16+8, 6)
                for index, coord in enumerate(self.selected_list):
                    if coord != 0:
                        pyxel.blt(self.start_coord[0]+16*index+index, self.start_coord[1]-1, 2, 
                            coord[0], coord[1], 16, 16, 0)
                    else:
                        pass
        else:
            # ホバーしていないとき
            pyxel.rect(self.start_coord[0]-5, self.start_coord[1]-5, 
                    (len(self.selected_list)*16+(len(self.selected_list)-1))+10,
                    16+10, 0)
            pyxel.rectb(self.start_coord[0]-4, self.start_coord[1]-4, 
                (len(self.selected_list)*16+(len(self.selected_list)-1))+8,
                16+8, 6)
            for index, coord in enumerate(self.selected_list):
                if coord != 0:
                    pyxel.blt(self.start_coord[0]+16*index+index, self.start_coord[1], 2, 
                        coord[0], coord[1], 16, 16, 0)
                else:
                    pass
        # 矢印の描画
        self.arrow.draw_modearrow()