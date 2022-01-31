# C:/users/Taro Aizawa/Desktop/mygame
# -*- coding: utf-8 -*-
from numpy.lib.function_base import percentile
import pyxel
from collision_detector import CollisionDetector
import numpy as np
import math
import json

# 場面の定義：ステージ
STANDBY: int = 0
GAMEPLAY: int = 1
GAMEOVER: int = 2
GAMECLEAR: int = 3
ERROR: int = 4

# 入力モード
MODE_MOUSE: int = 5
MODE_GAMEPAD: int = 6

# pyxel上のキー定義
APP_W: int = 256
APP_H: int = 256



class Stage:
    """ ステージ本体 """
    def __init__(self) -> None:
        # ポインターオブジェクト所持
        self.pointer = Pointer(speed_rate=0.0001)
        # pyxel初期化
        pyxel.init(APP_W, APP_H, title="IRA IRA CHASE", 
            fps=30, quit_key=pyxel.KEY_ESCAPE, capture_scale=5)
        # リソースファイル読込
        pyxel.load("assets/for_mygame.pyxres")
        # フルスクリーン表示
        pyxel.fullscreen(True)
        # pyxel起動
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        """ ステージの更新 """
        # ポインター更新
        self.pointer.update()

    def draw(self) -> None:
        """ ステージの描画 """
        # 画面消去
        pyxel.cls(0)
        # ポインター描画
        self.pointer.draw()


class Pointer:
    """ ポインター """
    def __init__(self, speed_rate: float) -> None:
        """ コンストラクタ """
        # 座標
        self.x = 0
        self.y = 0
        # ゲームパッド入力を速度に適用する割合
        self.speed_rate = speed_rate
        # 入力モード識別用
        self.input_mode = MODE_MOUSE

    def update(self) -> None:
        # 入力モードに沿った座標更新処理
        if self.input_mode == MODE_MOUSE:
            # マウスカーソル入力のとき
            self.x = pyxel.mouse_x
            self.y = pyxel.mouse_y
            if (pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)):
                # ゲームパッドのAボタン入力でモード切替
                self.input_mode = MODE_GAMEPAD
        elif self. input_mode == MODE_GAMEPAD:
            # ゲームパッド入力のとき
            input_x = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)
            input_y = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)
            # しきい値2000を超えたら入力
            if abs(input_x) > 2000:
                addition_x = input_x * self.speed_rate
                if pyxel.btn(pyxel.GAMEPAD1_BUTTON_X):
                    # ゲームパッドのX入力があれば倍速
                    addition_x *= 2
                self.x += addition_x
            if abs(input_y) > 2000:
                addition_y = input_y * self.speed_rate
                if pyxel.btn(pyxel.GAMEPAD1_BUTTON_X):
                    # ゲームパッドのX入力があれば倍速
                    addition_y *= 2
                self.y += addition_y
            if (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or
                pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT)):
                # マウスボタンの左右入力でモード切替。
                # 同時にマウスカーソルをポインター座標にセット
                pyxel.set_mouse_pos(self.x, self.y)
                self.input_mode = MODE_MOUSE
        # 自身を画面内に収める処理
        if self.x < 0:
            self.x = 0
        elif self.x >= APP_W:
            self.x = APP_W - 1
        if  self.y < 0:
            self.y = 0
        elif self.y >= APP_H:
            self.y = APP_H - 1

    def draw(self) -> None:
        if (pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) or
            pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)):
            pyxel.blt(self.x-2, self.y-2, 0, 8, 0, 5, 5, 0)
        else:
            pyxel.blt(self.x-2, self.y-2, 0, 0, 0, 5, 5, 0)
        pyxel. text(
            10, 10,
            f"GAMEPAD1_AXIS_LEFTX: {pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)}\n"
            f"GAMEPAD1_AXIS_LEFTY: {pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)}\n",
            10
        )



if __name__ == "__main__":
    Stage()
