import pyxel
import numpy as np
from stage import Pointer, Number

class StageSelect:
    """ステージセレクト画面
    """
    def __init__(self, size_x, size_y, json_load):
        self.size_x = size_x
        self.size_y = size_y
        self.stages = json_load
        self.number = Number(size_x/2, size_y/2, 1, len(json_load), 5, 10)
        self.pointer = Pointer()
        self.array_button_right = ArrayButton(self.size_x-40, 128, 20, 40, 0)
        self.array_button_left = ArrayButton(40, 128, 20, 40, 1)
        self.play_button = PlayButton(40, 200, self.size_x-40-40, self.size_y-200-20)
        self.back_button = BackButton(10, 10, 40, 30)
        self.activate = True

    def update_stage_select(self):
        """情報の更新

        Returns:
            int: 選択されたステージ番号
        """
        if self.activate:
            self.pointer.update_pointer(0, 0, self.size_x, self.size_y)
            self.array_button_right.update_array_button(self.pointer.x, self.pointer.y)
            self.array_button_left.update_array_button(self.pointer.x, self.pointer.y)
            self.play_button.update_playbutton(self.pointer.x, self.pointer.y)
            self.back_button.update_backbutton(self.pointer.x, self.pointer.y)
            self.number.update_number(self.array_button_right.push, self.array_button_left.push)
            if self.play_button.push or self.back_button.push:
                pyxel.play(0, 1)
                self.activate = False
                return self.number.num
            else:
                return None, None
    
    def draw_blue_lines(self):
        """外の青い枠線の描画
        """
        pyxel.line(0, 200, 30, 200, 5)
        pyxel.line(30, 200, 30, 245, 5)
        pyxel.line(30, 245, 225, 245, 5)
        pyxel.line(225, 245, 225, 200, 5)
        pyxel.line(225, 200, self.size_x, 200, 5)

        pyxel.line(0, 190, 40, 190, 5)
        pyxel.line(40, 190, 40, 158, 5)
        pyxel.line(40, 158, 20, 158, 5)
        pyxel.line(20, 158, 20, 88, 5)
        pyxel.line(20, 88, 40, 88, 5)
        pyxel.line(40, 88, 40, 49, 5)
        pyxel.line(40, 49, 0, 49, 5)

        pyxel.line(self.size_x, 190, self.size_x-40, 190, 5)
        pyxel.line(self.size_x-40, 190, self.size_x-40, 158, 5)
        pyxel.line(self.size_x-40, 158, self.size_x-20, 158, 5)
        pyxel.line(self.size_x-20, 158, self.size_x-20, 88, 5)
        pyxel.line(self.size_x-20, 88, self.size_x-40, 88, 5)
        pyxel.line(self.size_x-40, 88, self.size_x-40, 49, 5)
        pyxel.line(self.size_x-40, 49, self.size_x, 49, 5)

        pyxel.line(59, 0, 59, 29, 5)
        pyxel.line(59, 29, 59, 49, 5)
        pyxel.line(59, 49, 74, 49, 5)
        pyxel.line(74, 49, 74, 29, 5)
        pyxel.line(74, 29, self.size_x-75, 29, 5)
        pyxel.line(self.size_x-75, 29, self.size_x-75, 49, 5)
        pyxel.line(self.size_x-75, 49, self.size_x-59, 49, 5)
        pyxel.line(self.size_x-59, 49, self.size_x-59, 0, 5)

        pyxel.rectb(self.size_x-40-10, 10, 40, 30, 5)

    def draw_stage_select(self):
        """ステージセレクト画面の描画
        """
        if self.activate:
            self.number.draw_number()
            self.array_button_right.draw_array_button()
            self.array_button_left.draw_array_button()
            self.play_button.draw_playbutton()
            self.back_button.draw_backbutton()
            self.pointer.draw_pointer()
            pyxel.blt(self.size_x/2-88/2, self.size_y/2/2-25, 0, 0, 192, 88, 16, 0)
            self.draw_blue_lines()


class ArrayButton:
    """ステージ番号を増減させるためのボタン
    """
    def __init__(self, x, y, w, h, l_or_r):
        self.x, self.y = x, y
        self.w, self.h = w, h       
        self.hover = False
        self.click_after_hover = False
        self.push = False
        self.l_or_r = l_or_r
        self.col = 8

    def update_array_button(self, tar_x, tar_y):
        """情報の更新

        Args:
            tar_x (int): 相手のｘ座標
            tar_y (int): 相手のｙ座標
        """
        self.hover = False
        self.push = False
        if (self.x-self.w/2 <= tar_x < self.x+self.w/2 and 
            self.y-self.h/2 <= tar_y < self.y+self.h/2):
            self.hover = True
            if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                pyxel.play(0, 1)
                self.push = True

    def draw_array_button(self):
        """自身の描画
        """
        if self.hover:
            if not self.push:
                self.col = 10
            else:
                self.col = 8
        else:
            self.col = 8
        # 右=0
        if self.l_or_r == 0:
            points = np.array([
                [self.x-self.w/2, self.y-self.h/2], 
                [self.x-self.w/2, self.y+self.h/2], 
                [self.x+self.w/2, self.y],
                ])
            text = "NEXT"
        else:
            points = np.array([
                [self.x+self.w/2, self.y-self.h/2], 
                [self.x+self.w/2, self.y+self.h/2],
                [self.x-self.w/2, self.y],
                ])
            text = "PREV"
        for index, point in enumerate(points):
            if index < len(points)-1:
                pyxel.line(point[0], point[1], points[index+1][0], points[index+1][1], self.col)
            else:
                pyxel.line(point[0], point[1], points[0][0], points[0][1], self.col)
        pyxel.text(self.x-self.w/2*0.75, self.y-self.h*0.75, text, self.col)


class PlayButton:
    """ステージ開始ボタン
    """
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.hover = False
        self.push = False
        self.click_after_hover = False

    def update_playbutton(self, tar_x, tar_y):
        """情報の更新

        Args:
            tar_x (int): 相手のｘ座標
            tar_y (int): 相手のｙ座標
        """
        self.hover = False
        self.push = False
        if (self.x <= tar_x < self.x+self.w and 
            self.y <= tar_y < self.y+self.h):
            self.hover = True
        if self.hover and pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            self.click_after_hover = True
        if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
            if self.click_after_hover and self.hover:
                self.push = True
            self.click_after_hover = False
        
    def draw_playbutton(self):
        """自身の描画
        """
        if self.hover:
            if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON) and self.click_after_hover:
                pyxel.rectb(self.x, self.y, self.w, self.h, 8)
                pyxel.blt(self.x+self.w/2-32, self.y+self.h/2-8, 0, 0, 32, 64, 16, 0) # "PLAY"
            else:
                pyxel.rectb(self.x, self.y, self.w, self.h, 10)
                pyxel.rectb(self.x, self.y-1, self.w, self.h, 8)
                pyxel.blt(self.x+self.w/2-32, self.y+self.h/2-8, 0, 0, 16, 64, 16, 0) # "PLAY"
                pyxel.blt(self.x+self.w/2-32, self.y+self.h/2-9, 0, 0, 32, 64, 16, 0) # "PLAY"
        else:
            pyxel.rectb(self.x, self.y, self.w, self.h, 10)
            pyxel.blt(self.x+self.w/2-32, self.y+self.h/2-8, 0, 0, 16, 64, 16, 0) # "PLAY"


class BackButton(PlayButton):
    """タイトルに戻るボタン

    Args:
        PlayButton (Class): ステージ開始ボタンのクラス。
                            ボタンとしての挙動が同じであるため
    """
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.back = False

    def update_backbutton(self, tar_x, tar_y):
        super().update_playbutton(tar_x, tar_y)
        if self.push:
            self.back = True    # 選択画面本体で判定に使う
    
    def draw_backbutton(self):
        """自身の描画
        """
        if self.hover:
            # 相手が自身の上にあって押されている
            if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON) and self.click_after_hover:
                pyxel.rectb(self.x, self.y, self.w, self.h, 8)
                pyxel.text(self.x+self.w/2, self.y+self.h/2, "BACK TO\n TITLE", 8) 
                pyxel.blt(self.x+self.w/2-16, self.y+self.h/2, 0, 56, 0, 8, 12, 0)
            # 相手が自身の上にあるが押されていない、強調表示
            else:
                pyxel.rectb(self.x, self.y, self.w, self.h, 10)
                pyxel.rectb(self.x, self.y-1, self.w, self.h, 8)
                pyxel.text(self.x+self.w/2, self.y+self.h/2-1, "BACK TO\n TITLE", 8) 
                pyxel.blt(self.x+self.w/2-16, self.y+self.h/2, 0, 48, 0, 8, 12, 0)
                pyxel.blt(self.x+self.w/2-16, self.y+self.h/2-1, 0, 56, 0, 8, 12, 0)
        # 相手が自身の上におらず、待機
        else:
            pyxel.rectb(self.x, self.y, self.w, self.h, 10)
            pyxel.text(self.x+self.w/2, self.y+self.h/2, "BACK TO\n TITLE", 10)
            pyxel.blt(self.x+self.w/2-10, self.y+self.h/2, 0, 48, 0, 8, 12, 0) 