# C:/users/Taro Aizawa/Desktop/mygame
# -*- coding: utf-8 -*-
from numpy.lib.function_base import percentile
import pyxel
from collision_detector import CollisionDetector
import numpy as np
import math
import json

# 場面の定義：ステージ
BEFORE_START: int = 0
START:        int = 1
GAMEOVER:     int = 2
GAMECLEAR:    int = 3
ERROR:        int = 4

# ========== ステージ本体 ==========
class Stage:
    """ステージ画面
    """
    def __init__(self, size_x, size_y, stage_num):
        # ステージ設定読み込み
        with open('assets/stage_setting.json', 'r') as f:
            self.setting_json = json.load(f)
        # ベストレコード読み込み
        with open('assets/best_record.json', 'r') as f:
            self.best_record_json = json.load(f)
        # ステージ番号
        self.stage_num = stage_num
        # 再起動用のステージ初期値
        self.settings = self.setting_json[str(self.stage_num)]
        # 場面
        self.scene = BEFORE_START
        # 直前の場面
        self.scene_last = GAMEOVER
        # エラーメッセージ
        self.error_message = "None"
        # ゲームを動かすか？（終わっていないか？）
        self.activate = True      
        # 渡されたサイズを自身のサイズに設定
        self.size_x = size_x
        self.size_y = size_y
        # ベストレコードが更新されたか
        self.record_update = False
        # 各種オブジェクト生成
        self.pointer = Pointer()
        if type(self.best_record_json[str(self.stage_num)]) == type(1):
            self.best_record = self.best_record_json[str(self.stage_num)]
        else:
            self.scene = ERROR
            self.error_message = "In settings, high-score is must exists!"
        if self.settings["player_args"] != None:
            self.player = Player(self.settings["player_args"][0], self.settings["player_args"][1], self.settings["player_args"][2])
        else:
            self.scene = ERROR
            self.error_message = "In settings, player's args must exist!"
        if self.settings["chasers_args"] != None:
            self.chasers = Chasers(self.settings["chasers_args"])
        if self.settings["capsules_args"] != None:
            self.capsules = Capsules(self.settings["capsules_args"])
        else:
            self.capsules = Capsules([])
        if self.settings["lines_group_args"] != None:
            self.wall = Wall(self.settings["lines_group_args"], [self.player.x, self.player.y])
        if self.settings["goallines_args"] != None:
            self.goallines = GoalLines(self.settings["goallines_args"], [self.player.x, self.player.y])
        else:
            self.scene = ERROR
            self.error_message = "In settings, Goal lines' args must exist!"
        self.flag = Flag()
        self.system_screen = SystemScreen(self.best_record, 8, self.stage_num, 15)
        if self.scene == ERROR:
            self.activate = False
            print(self.error_message)
        pyxel.playm(1, loop=True)
    
    def reset_stage(self):
        """ベストレコード以外の情報を起動時の状態にリセットする"""
        with open('assets/stage_setting.json', 'r') as f:
            self.setting_json = json.load(f)
        # ステージ初期値読み込み
        self.settings = self.setting_json[str(self.stage_num)]
        if self.settings["player_args"] != None:
            self.player = Player(self.settings["player_args"][0], self.settings["player_args"][1], self.settings["player_args"][2])
        if self.settings["chasers_args"] != None:
            self.chasers = Chasers(self.settings["chasers_args"])
        if self.settings["capsules_args"] != None:
            self.capsules = Capsules(self.settings["capsules_args"])
        else:
            self.capsules = Capsules([])
        if self.settings["lines_group_args"] != None:
            self.wall = Wall(self.settings["lines_group_args"], [self.player.x, self.player.y])
        if self.settings["goallines_args"] != None:
            self.goallines = GoalLines(self.settings["goallines_args"], [self.player.x, self.player.y])
        self.system_screen = SystemScreen(self.best_record, 8, self.stage_num, 15)
        self.record_update = False
        self.flag.reset()
        pyxel.playm(1, loop=True)
    
    def set_frame0(self):
        """ステージ開始時に呼び出し、経過フレームの開始点を決める"""
        self.frame0 = pyxel.frame_count
        self.frame = 0
    
    def update_Stage(self):
        """ステージの情報を更新"""
        # ポインターは場面に関わらず更新
        self.pointer.update_pointer(0, 64, self.size_x, self.size_y)
        # ===== スタート前 =====
        if self.scene == BEFORE_START:
            self.player.update_player(self.pointer.x, self.pointer.y)
            # プレイヤーがクリックされてfollowが切り替わったら次フレームからゲーム開始
            if self.player.follow == True:
                self.scene = START
            # 直前の場面を更新
            self.scene_last = BEFORE_START
        # ===== ゲーム開始 =====
        if self.scene == START:
            # 場面切り替え後最初のフレームだけ行うもの
            if self.scene_last == BEFORE_START:
                self.set_frame0()
            # スタートからの経過フレーム更新
            self.frame = pyxel.frame_count - self.frame0
            # 各オブジェクトの更新処理
            self.player.update_player(self.pointer.x, self.pointer.y)
            self.chasers.set_new_vector(self.player.x, self.player.y, pyxel.frame_count)
            self.chasers.set_new_coords()
            self.system_screen.update_system_screen(self.frame)
            # カプセルの判定
            self.capsules.update_capsules(self.player)
            # ヒットチェック
            if hasattr(self, 'chasers'):
                self.chasers.hit_check(self.player.r, self.player.coord_last, self.player.coord_now)
            if hasattr(self, 'wall'):
                self.wall.hit_check(self.player.coord_last, self.player.coord_now, self.player.r)
            self.goallines.hit_check(self.player.coord_last, self.player.coord_now, self.player.r)
            # 判定（ゲームオーバーorクリア）
            self.flag.check_clear(self.goallines.hit)
            if hasattr(self, 'wall'):
                self.flag.check_gameover(self.wall.hit)
            if hasattr(self, 'chasers'):
                self.flag.check_gameover(self.chasers.hit)
            if self.flag.gameover:
                self.scene = GAMEOVER
                pyxel.stop()
                pyxel.playm(0)
            if self.flag.gamecrear:
                self.scene = GAMECLEAR
                pyxel.stop()
                pyxel.playm(0)
                if self.record_update == False and self.best_record > self.frame:
                    with open('assets/best_record.json', 'r') as f:
                        best_records_json = json.load(f)
                    best_records_json[str(self.stage_num)] = self.frame
                    with open('assets/best_record.json', 'w') as f:
                        json.dump(best_records_json, f, indent=4, ensure_ascii=False, sort_keys=True)
                    self.record_update = True
                    self.last_best_record = RecordForResult(27, 80, 80, 100, 15, self.best_record)
                    self.last_best_record.active = False
                    self.best_record = self.frame
            # 直前の場面を更新
            self.scene_last = START
        # ===== ゲームオーバー =====
        elif self.scene == GAMEOVER:
            # 場面切り替え後最初のフレームだけ行うもの
            if self.scene_last == START:
                self.player.show = False
                self.characters = Characters(GAMEOVER, self.size_x/2-70, self.size_y/2-8, 0.2)
                self.bubbles = Bubbles(self.player.x, self.player.y, 10, 10)
                self.wait = WaitCounter(45)
            # ゲームオーバー表示までのウェイトが終わったら
            if hasattr(self, 'wait'):
                if self.wait.end:
                    if not self.wait.end_after_1frame:
                        pyxel.playm(2, loop=True)
                    self.characters.update_characters()
            self.wait.update_count(self.bubbles.update_bubbles)
            # クリック操作
            if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON) and hasattr(self, 'wait'):
                if self.wait.end:
                    pyxel.stop()
                    self.reset_stage()
                    self.set_frame0()
                    del(self.wait)
                    self.scene = BEFORE_START
            elif pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and hasattr(self, 'wait'):
                if self.wait.end:
                    pyxel.stop()
                    self.activate = False
            # 直前の場面を更新
            self.scene_last = GAMEOVER
        # ===== ゲームクリア =====
        elif self.scene == GAMECLEAR:
            # 場面切り替え後最初のフレームだけ行うもの
            if self.scene_last == START:
                self.chasers.set_param("show", False)
                self.characters = Characters(GAMECLEAR, self.size_x/2-87, self.size_y/2-8, -0.5)
                self.bubbles_list = []
                for chaser in self.chasers.chasers:
                    self.bubbles_list.append(Bubbles(chaser.x, chaser.y, 6, 8))
                self.wait = WaitCounter(45)
            # クリア表示までのウェイトが終わったら
            if hasattr(self, 'wait'):
                if self.wait.end:
                    # ベストレコード時
                    if self.record_update:
                        if not self.wait.end_after_1frame:
                            pyxel.playm(4)
                            self.wait_after_clear = WaitCounter(15)
                            self.record_for_result  = RecordForResult(150, 19, 150, 80, 15, self.frame)
                        self.wait_after_clear.update_count(self.record_for_result.update_record_for_result)
                        self.last_best_record.update_record_for_result()
                        # 右クリックされたら再スタート
                        if self.wait_after_clear.end:
                            if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON):
                                pyxel.stop()
                                self.reset_stage()
                                del(self.wait_after_clear)
                                self.set_frame0()
                                del(self.wait)
                                self.scene = BEFORE_START
                            elif pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                                pyxel.stop()
                                self.activate = False
                    # ベストレコードでない時
                    else:
                        if not self.wait.end_after_1frame:
                            pyxel.playm(3)
                        if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON):
                            pyxel.stop()
                            self.reset_stage()
                            self.set_frame0()
                            del(self.wait)
                            self.scene = BEFORE_START
                        elif pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                            pyxel.stop()
                            self.activate = False
                    # "GAME CLEAR!!"
                    self.characters.update_characters()
            if hasattr(self, 'wait'):
                for bubbles in self.bubbles_list:
                    bubbles.update_bubbles()
                self.wait.update_count()
            self.scene_last = GAMECLEAR
    
    def draw_message(self):
        """ゲームオーバー・クリア関係なく表示させるメッセージ
        """
        pyxel.blt(10, 165, 0,  80, 120, 88, 48, 7)
        pyxel.blt(self.size_x-88-10, 165+9, 0, 176, 120, 88, 40, 7)
        pyxel.blt(self.size_x/2-52, self.size_y-80, 1, 16, 32, 104, 80, 7)

    def draw_Stage(self):
        """ステージの描画
        """
        # 画面を色0でクリア
        pyxel.cls(0)
        # 各オブジェクトの描画
        if hasattr(self, 'wall'):
            self.wall.draw_wall()
        self.goallines.draw_lines()
        if hasattr(self, 'capsules'):
            self.capsules.draw_capsules()
        self.player.draw_player()
        if hasattr(self, 'chasers'):
            self.chasers.draw_chasers()
        self.system_screen.draw_system_screen()
        # ゲームオーバー時のみ描画するもの
        if self.scene == GAMEOVER:
            if self.scene_last == START:
                pyxel.rect(0, 0, self.size_x, self.size_y, 7)
            else:
                if not self.wait.end:
                    self.bubbles.draw_bubbles()
                else:
                    # ウェイトが終わった後
                    pyxel.bltm(0, 0, 0, 0, 0, self.size_x, self.size_y, 1)
                    self.system_screen.draw_system_screen()
                    self.characters.draw_characters()
                    self.draw_message()
        # ゲームクリア時のみ描画するもの
        elif self.scene == GAMECLEAR:
            if self.scene_last == START:
                pyxel.rect(0, 0, self.size_x, self.size_y, 7)
            else:
                if not self.wait.end:
                    for bubbles in self.bubbles_list:
                        bubbles.draw_bubbles()
                else:
                    pyxel.bltm(0, 0, 0, 0, 0, self.size_x, self.size_y, 1)
                    self.characters.draw_characters()
                    if self.record_update:
                        if hasattr(self, 'wait_after_clear'):
                            pyxel.blt(120-self.wait_after_clear.count*2, 80, 0, 32, 0, 16, 16, 0)
                            self.record_for_result.draw_record_for_result()
                            self.last_best_record.draw_record_for_result()
                            if self.wait_after_clear.end:
                                self.draw_message()
                    else:
                        self.system_screen.draw_system_screen()
                        self.draw_message()
                        
        self.pointer.draw_pointer()


# ========== マウスポインター ==========
class Pointer:
    def __init__(self):
        self.visible = True
        self.x = pyxel.mouse_x
        self.y = pyxel.mouse_y
        self.on_screen = False

    def update_pointer(self, x1, y1, x2, y2):
        if pyxel.mouse_x < x1:
            self.x = x1
        elif pyxel.mouse_x > x2:
            self.x = x2
        else:
            self.x = pyxel.mouse_x
        if  pyxel.mouse_y < y1:
            self.y = y1
        elif pyxel.mouse_y > y2:
            self.y = y2
        else:
            self.y = pyxel.mouse_y
        
        if x1<=pyxel.mouse_x<x2 and y1<=pyxel.mouse_y<y2:
            pyxel.mouse(False)
            self.on_screen = True
        else:
            pyxel.mouse(True)
            self.on_screen = False

    def draw_pointer(self):
        if self.visible:
            if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON) or pyxel.btn(pyxel.MOUSE_RIGHT_BUTTON):
                pyxel.blt(self.x-2, self.y-2, 0, 8, 0, 5, 5, 0)
            else:
                pyxel.blt(self.x-2, self.y-2, 0, 0, 0, 5, 5, 0)


# ========== プレイヤー ==========
class Player:
    """プレイヤー

    プレイヤーの座標＝pyxel上のマウス座標。
    プレイヤーの座標の管理と描画。    
    """
    def __init__(self, x, y, r):
        """コンストラクタ
        """
        self.r = r
        self.x = x
        self.y = y
        self.coord_now = np.array([self.x, self.y])
        self.last_x = x
        self.last_y = y
        self.coord_last = self.coord_now
        self.follow = False
        self.show = True

    def update_player(self, x, y):
        """自身の座標の更新
        """
        self.coord_last = self.coord_now
        self.x_last = self.x
        self.y_last = self.y
        if self.follow:
            self.x = x
            self.y = y
        self.coord_now = np.array([self.x, self.y])
        # 自分がクリックされたら
        if (np.linalg.norm(np.array([x-self.x, y-self.y]), ord=2)<=self.r and 
            pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON)):
            self.follow = True

    def draw_player(self):
        """自身を円として描画
        """
        if not self.follow:
            if pyxel.frame_count%5 != 0:
                pyxel.rect(self.x-18, self.y-self.r-14, 36, 13, 1)
                pyxel.text(self.x-17, self.y-self.r-13, "CLICK ME\nTO START!", 10)
        if self.show:
            #pyxel.line(self.x, self.y, self.coord_last[0], self.coord_last[1], 8)
            pyxel.circb(self.coord_last[0], self.coord_last[1], self.r, 8)
            pyxel.circb(self.x, self.y, self.r, 10)
        else:
            pass
        



# ========== 追跡者 ==========
class Chaser:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.r_for_draw = r
        self.v = 0
        self.vx = 0
        self.vy = 0
        self.movable = True
        self.color = 8
        self.hit = False
        self.stop = False
        self.show = True
        self.play_sound = False
        self.play_sound_last = False
        self.collision_detector = CollisionDetector()

    def set_new_vector(self, tar_x, tar_y, frame_count):
        """
        対象に向かう角度を算出して
        ｘとｙ方向の速度に反映。
        """
        if self.movable == True:
            self.dy = tar_y-self.y   # 対象との距離：y
            self.dx = tar_x-self.x   # 対象との距離：x
            rad = np.arctan2(self.dy, self.dx)    # 対象との角度
            # x, yどちらの距離も1未満なら動きを止める
            if abs(self.dx) < 1 and abs(self.dy) < 1:
                self.v = 0
            else:
                self.v = 0.8
            self.vx = self.v*math.cos(rad)
            self.vy = self.v*math.sin(rad)
            self.dxy = int(math.sqrt(self.dx*self.dx+self.dy*self.dy))  # 対象との直線距離
            # self.dxyを点滅の速さに使う
            if  70 <= self.dxy < 120:
                change_time = 20
            elif  40 <= self.dxy < 70:
                change_time = 10
            elif self.dxy < 40:
                change_time = 4
            else:
                change_time = 1 
            # 色と大きさを切り替えて自身を点滅させる
            self.play_sound_last = self.play_sound
            if frame_count%change_time/2 < change_time/4:
                self.color = 8
                self.r_for_draw = self.r-1
                self.play_sound = False
            else:
                self.color = 10
                self.r_for_draw = self.r
                self.play_sound = True
            if self.play_sound == True and self.play_sound_last == False:
                pyxel.play(0, 1)

    def set_new_coords(self):
        """
        速度を足して座標更新。
        """
        if not self.stop:
            self.x += self.vx
            self.y += self.vy

    def hit_check(self, tar_r, tar_coord_last, tar_coord_now):
        """当たり判定を行う
        """
        if self.collision_detector.check_c2c(self.x, self.y, self.r, 
                tar_coord_now[0], tar_coord_now[1], tar_r):
            self.hit = True
        elif self.collision_detector.check_c2l(self.x, self.y, self.r,
                tar_coord_last[0], tar_coord_last[1],
                tar_coord_now[0], tar_coord_now[1]): 
            self.hit = True
        else:
            self.hit = False

    def check_over90(self, A, B):
        """hit_check内で使う判定

        ２つのベクトルのなす角が鋭角かどうかをboolで返す。
        内積の正負で判断する。
        """
        if np.dot(A, B) <= 0:
            return True
        else:
            return False

    def draw_chaser(self):
        if self.show:
            if not self.stop:
                pyxel.circ(self.x, self.y, self.r_for_draw, self.color)
                if self.color == 8:
                    pyxel.circb(self.x, self.y, self.r_for_draw, 10)
            else:
                pyxel.circ(self.x, self.y, self.r_for_draw, 5)

    def draw_bubbles(self):
        for chaser in self.chasers:
            pass


# ========== 追跡者の包括管理 ==========
class Chasers:
    def __init__(self, args):
        """args:[[x, y, r] × 個数]
        """
        self.chasers = []
        for one_args in args:
            self.chasers.append(Chaser(one_args[0], one_args[1], one_args[2]))
        self.number = len(self.chasers)
        self.hit = False

    def set_new_vector(self, tar_x, tar_y, frame_count):
        for chaser in self.chasers:
            chaser.set_new_vector(tar_x, tar_y, frame_count)

    def set_new_coords(self):
        for chaser in self.chasers:
            chaser.set_new_coords()

    def hit_check(self, tar_r, tar_coord_last, tar_coord_now):
        for chaser in self.chasers:
            chaser.hit_check(tar_r, tar_coord_last, tar_coord_now)
            if chaser.hit:
                self.hit = True

    def draw_chasers(self):
        for chaser in self.chasers:
            chaser.draw_chaser()
    
    def set_param(self, name, torf):
        for chaser in self.chasers:
            if name == "show":
                chaser.show = torf
            elif name == "stop":
                chaser.stop = torf


# ========== カプセル（赤・青） ==========
class Capsule:
    """カプセル（赤・青）"""
    def __init__(self, x, y, col):
        """初期化"""
        self.x, self.y = x, y
        # 色：　0赤　1青
        self.col = col
        self.collision_detector = CollisionDetector()
        self.hit_points = [
            [self.x-6, self.y+2],
            [self.x+1, self.y-5],
            [self.x+3, self.y-5],
            [self.x+5, self.y-3],
            [self.x+5, self.y-1],
            [self.x-2, self.y+6],
            [self.x-4, self.y+6],
            [self.x-6, self.y+4],
            ] 

    def hit_check(self, tar: Player):
        """ターゲット(プレイヤー)との当たり判定"""
        if (
                self.collision_detector.check_poly2c(
                    self.hit_points,
                    tar.coord_now[0], tar.coord_now[1], tar.r
                ) or
                self.collision_detector.check_poly2l(
                    self.hit_points,
                    tar.coord_last[0], tar.coord_last[1],
                    tar.coord_now[0], tar.coord_now[1]
                )
            ):
            # 当たり判定がTrueのとき
            # 相手（プレイヤー）の半径を操作
            if self.col == 0:
                tar.r *= 2
            elif self.col == 1:
                tar.r /= 2
            # Trueを返す
            return True
        return False

    def draw_capsule(self):
        if self.col == 0:
            pyxel.blt(self.x-6, self.y-5, 0, 34, 234, 12, 12, 0)
        elif self.col == 1:
            pyxel.blt(self.x-6, self.y-5, 0, 50, 234, 12, 12, 0)
        # for i, point in enumerate(self.hit_points):
        #     if i < len(self.hit_points)-1:
        #         pyxel.line(point[0], point[1], self.hit_points[i+1][0], self.hit_points[i+1][1], 10)


# ========== カプセルを包括管理 =========
class Capsules:
    """カプセルを包括管理"""
    def __init__(self, args):
        """初期化"""
        self.capsules = [Capsule(*a) for a in args]

    def update_capsules(self, tar: Player):
        """更新"""
        if len(self.capsules):
            index = 0
            for capsule in self.capsules:
                if not len(self.capsules):
                    # 消去の結果長さが0になっていたら
                    break
                if capsule.hit_check(tar):
                    self.capsules.pop(index)
                    index -= 1
                index += 1

    def draw_capsules(self):
        """描画"""
        for capsule in self.capsules:
            capsule.draw_capsule()


# ========== 壁の線 ==========
class OneLine:
    """当たり判定機能を持った一本の線"""
    def __init__(self, start, end, tar_coord):
        self.start = start  # 始点座標
        self.end = end      # 終点座標
        self.color = 5
        self.hit = False
        # ベクトル：始点->終点
        self.vec_start2end = np.array(self.end-self.start)
        # ベクトル：始点->相手
        self.vec_start2tar = np.array(tar_coord-self.start)
        # ベクトル：終点->相手
        self.vec_end2tar = np.array(tar_coord-self.end)
        # 始点->相手の単位ベクトルと始点->終点ベクトルとの外積
        self.cross_now = np.cross(self.vec_start2end 
            / np.linalg.norm(self.vec_start2end, ord=2), 
            self.vec_start2tar) 
        self.cross_last = self.cross_now
        self.collision_detector = CollisionDetector()

    def hit_check(self, tar_coord_last, tar_coord_now, tar_r):
        """相手を円と見たときの当たり判定"""
        self.hit = False
        if self.collision_detector.check_l2c(
                self.start[0], self.start[1], 
                self.end[0], self.end[1],
                tar_coord_now[0], tar_coord_now[1], tar_r):
            self.hit = True
        elif self.collision_detector.check_l2l(
                self.start[0], self.start[1], 
                self.end[0], self.end[1],
                tar_coord_last[0], tar_coord_last[1],
                tar_coord_now[0], tar_coord_now[1]):
            self.hit = True
        else:
            self.hit = False
    
    def draw_oneline(self):
        """自身の描画"""
        if self.hit == True:
            self.color = 10
        else:
            self.color = 5
        pyxel.line(self.start[0], self.start[1], 
            self.end[0], self.end[1], self.color)


# ========== 壁の線のあつまり ==========
class Lines:
    """線の集まりを包括管理"""
    def __init__(self, args, tar_coord):
        """コンストラクタ

        リストに線オブジェクトがそれぞれ格納される。
        [配列, 終点->始点の線で閉じるかのbool値]が渡される。
        """
        self.close = args[1]
        self.points = np.array(args[0])
        self.lines = []
        self.hit = False
        self.hit_of_lines = np.array([])
        for index, point in enumerate(self.points):
            if index < len(self.points)-1:
                self.lines.append(OneLine(point, 
                    self.points[index+1], tar_coord))
            elif self.close == 1:
                self.lines.append(OneLine(point, 
                    self.points[0], tar_coord))
            self.hit_of_lines = np.append(self.hit_of_lines, False)
        self.collision_ditector = CollisionDetector()

    def hit_check(self, tar_coord_last, tar_coord_now, tar_r):
        """対象との当たり判定を行う

        構成する線オブジェクトの全てで判定し、
        いずれかの判定がTrueなら自身の当たり判定をTrueにする。
        """
        self.hit = False
        for index, line in enumerate(self.lines):
            line.hit_check(tar_coord_last, tar_coord_now, tar_r)
            if line.hit == True:
                self.hit_of_lines[index] = True
            else:
                self.hit_of_lines[index] = False
        if np.any(self.hit_of_lines):
            self.hit = True

    def draw_lines(self):
        """構成する全ての線の描画"""
        for line in self.lines:
            line.draw_oneline()


# ========== 壁の線のあつまりの包括管理 ==========
class Wall:
    """線の集まり　の集まりを包括管理"""
    def __init__(self, args, tar_coord):
        """コンストラクタ

        リストに線の集まりオブジェクトがそれぞれ格納される。
        [任意の数の[配列, 終点->始点の線で閉じるかのbool値]]が渡される。
        """
        self.hit = False
        self.hit_of_lines = np.array([]) 
        self.wall = np.array([])
        for lines in args:
            self.wall = np.append(self.wall, Lines(lines, tar_coord))
            self.hit_of_lines = np.append(self.hit_of_lines, False)
    
    def hit_check(self, tar_coord_last, tar_coord_now, tar_r):
        """対象との当たり判定を行う

        構成する線の集まりオブジェクトの全てで判定し、
        いずれかの判定がTrueなら自身の当たり判定をTrueにする。
        """
        self.hit = False
        for index, lines in enumerate(self.wall):
            lines.hit_check(tar_coord_last, tar_coord_now, tar_r)
            self.hit_of_lines[index] = lines.hit
        if np.any(self.hit_of_lines):
            self.hit = True

    def draw_wall(self):
        """構成する全ての線の集まりの描画"""
        for lines in self.wall:
            lines.draw_lines()


# ========== 各種フラグ ==========
class Flag:
    """ステージ進行上のフラグを管理"""
    def __init__(self):
        """各種フラグの初期化"""
        self.reset()

    def check_gameover(self, *args):
        """ゲームオーバーの判定"""
        if any(args):
            self.gamecrear = False
            self.gameover = True

    def check_clear(self, *args):
        """ゲームクリアの判定"""      
        if any(args):
            self.gameover = False
            self.gamecrear = True

    def reset(self):
        """各種フラグを初期値に戻す"""
        self.gameover = False
        self.gamecrear = False


# ========== 爆発演出の丸１つ ==========
class Bubble:
    """爆発演出の丸１つ"""
    def __init__(self, x, y, r, v, rad, a, col):
        """初期化"""
        self.coord = np.array([x, y])
        self.r = r
        self.v_sca = v
        self.rad = rad
        self.v_init = np.array([math.cos(rad), math.sin(rad)])
        self.a = a
        self.col = col

    def update_bubble(self):
        """更新"""
        pi = np.pi
        v_rad = pi/36
        self.coord = self.coord + self.v_init*self.v_sca
        self.v_sca *= self.a
        self.v_init = np.dot(np.array([[np.cos(v_rad), -np.sin(v_rad)],[np.sin(v_rad), np.cos(v_rad)]]), self.v_init)
        self.r -= 0.2

    def draw_bubble(self):
        """描画"""
        pyxel.circb(self.coord[0], self.coord[1], self.r, self.col)


# ========== 爆発演出 ==========
class Bubbles:
    def __init__(self, tar_x, tar_y, num, col):
        self.bubbles = []
        pi = np.pi
        self.num = num
        self.col = col
        for i in range(self.num):
            self.bubbles.append(Bubble(tar_x, tar_y, 8, 10, pi*2/self.num*i, 0.9, self.col))

    def update_bubbles(self):
        for i in range(self.num):
            self.bubbles[i].update_bubble()

    def draw_bubbles(self):
        for i in range(self.num):
            self.bubbles[i].draw_bubble()


# ========== クリア・ゲームオーバーの文字 ==========
class Characters:
    def __init__(self, result, x, y, v_rad):
        self.x, self.y = x, y
        self.result = result
        self.character_objects = []
        self.v_rad = v_rad
        if result == GAMEOVER:
            self.character_objects = [
                Character(self.x+17*0, self.y, 0, 48, (np.pi/2/8)*0, self.v_rad),    # G
                Character(self.x+17*1, self.y, 16, 48, (np.pi/2/8)*1, self.v_rad),    # A
                Character(self.x*17*2, self.y, 32, 48, (np.pi/2/8)*2, self.v_rad),    # M
                Character(self.x*17*3, self.y, 48, 48, (np.pi/2/8)*3, self.v_rad),    # E
                Character(self.x*17*4+4, self.y, 0, 64,  (np.pi/2/8)*4, self.v_rad),    # O
                Character(self.x*17*5+4, self.y, 16, 64, (np.pi/2/8)*5, self.v_rad),    # V
                Character(self.x*17*6+4, self.y, 48, 48, (np.pi/2/8)*6, self.v_rad),    # E
                Character(self.x*17*7+4, self.y, 32, 64, (np.pi/2/8)*7, self.v_rad)    # R
            ]
        if result == GAMECLEAR:
            self.character_objects = [
                Character(self.x+17*0, self.y, 48, 64, (np.pi/2/10)*0, self.v_rad),    # G
                Character(self.x+17*1, self.y, 32, 32, (np.pi/2/10)*1, self.v_rad),    # A
                Character(self.x*17*2, self.y, 0, 80, (np.pi/2/10)*2, self.v_rad),    # M
                Character(self.x*17*3, self.y, 16, 80, (np.pi/2/10)*3, self.v_rad),    # E
                Character(self.x*17*4+4, self.y, 32, 80,  (np.pi/2/10)*4, self.v_rad),    # C
                Character(self.x*17*5+4, self.y, 16, 32, (np.pi/2/10)*5, self.v_rad),    # L
                Character(self.x*17*6+4, self.y, 16, 80, (np.pi/2/10)*6, self.v_rad),    # E
                Character(self.x*17*7+4, self.y, 32, 32, (np.pi/2/10)*7, self.v_rad),    # A
                Character(self.x*17*8+4, self.y, 48, 80, (np.pi/2/10)*8, self.v_rad),    # R
                Character(self.x*17*9+4, self.y, 0, 96, (np.pi/2/10)*9, self.v_rad)     # !!
            ]

    def update_characters(self):
        if self.result == GAMEOVER:
            for index, character in enumerate(self.character_objects):
                if index < 4:
                    character.update_character(self.x+17*index, self.y)
                else:
                    character.update_character(self.x+17*index+4, self.y)
        if self.result == GAMECLEAR:
            for index, character in enumerate(self.character_objects):
                if index < 4:
                    character.update_character(self.x+17*index, self.y)
                else:
                    character.update_character(self.x+17*index+4, self.y)
    
    def draw_characters(self):
        if self.result == GAMEOVER:
            for character in self.character_objects:
                character.draw_character()
        if self.result == GAMECLEAR:
            for character in self.character_objects:
                character.draw_character()


# ========== 文字１つ ==========
class Character:
    def __init__(self, x, y, u, v, rad, v_rad):
        self.x, self.y, self.u, self.v = x, y, u, v
        self.rad = rad
        self.v_rad = v_rad
        self.y_dis = 0

    def update_character(self, x, y):
        self.x, self.y = x, y
        self.rad += self.v_rad
        self.y_dis = np.sin(self.rad)*5

    def draw_character(self):
        pyxel.blt(self.x, self.y+self.y_dis, 0, self.u, self.v, 16, 16, 0)


class GoalOneLine(OneLine):
    def __init__(self,start, end, tar_coord):
        super().__init__(start, end, tar_coord)
        self.color = 8

    def draw_oneline(self):
        """自身の描画

        色が8固定なるようにオーバーライド。
        """
        pyxel.line(self.start[0], self.start[1], self.end[0], self.end[1], self.color)


# ========== 線のあつまり（ゴール判定版） ==========
class GoalLines(Lines):
    def __init__(self, args, tar_coord):
        super().__init__(args, tar_coord)
        self.lines = []
        self.hit_of_lines = np.array([])
        for index, point in enumerate(self.points):
            if index < len(self.points)-1:
                self.lines.append(GoalOneLine(point, self.points[index+1], tar_coord))
            elif self.close == 1:
                self.lines.append(GoalOneLine(point, self.points[0], tar_coord))
            self.hit_of_lines = np.append(self.hit_of_lines, False)
    
    def hit_check(self, tar_coord_last, tar_coord_now, tar_r):
        super().hit_check(tar_coord_last, tar_coord_now, tar_r)
        if not self.hit:
            self.collision_ditector.check_poly2p(self.points, 
                tar_coord_now[0], 
                tar_coord_now[1])


# ========== ウェイトカウンター ==========
class WaitCounter:
    def __init__(self, count, step=1):
        self.count_init = count
        self.count = count
        self.step = step
        self.end = False
        self.end_after_1frame = False
    
    def update_count(self, func_use=None, args=None):
        self.end_after_1frame = self.end
        if func_use != None:
            if args != None:
                func_use(*args)
            else:
                func_use()
        self.count -= self.step
        if self.count <= 0:
            self.count = 0
            self.end = True
    
    def reset_count(self):
        self.count = self.count_init
        self.end = False


# ========== 上部のシステム画面 ==========
class SystemScreen:
    def __init__(self, best_record, col, num, num_col):
        self.best_record = best_record
        self.best_record_update = False
        self.frame = 0
        self.m, self.s, self.f = "00", "00", "00"
        self.m_b = int((self.best_record/30)/60)
        if self.m_b >= 99:
            self.m_b = 99
        self.s_b = int((((self.best_record/30)/60)-self.m_b)*60)
        self.f_b = int((((((self.best_record/30)/60)-self.m_b)*60)-self.s_b)*100)
        self.m_b = str(self.m_b).rjust(2, '0')
        self.s_b = str(self.s_b).rjust(2, '0')
        self.f_b = str(self.f_b).rjust(2, '0')
        self.col = col
        self.number = Number(25, 36, num, 9, 1, num_col)

    def update_system_screen(self, frame):
        self.frame = frame
        self.m = int((self.frame/30)/60)
        if self.m >= 99:
            self.m = 99
        self.s = int((((self.frame/30)/60)-self.m)*60)
        self.f = int((((((self.frame/30)/60)-self.m)*60)-self.s)*100)
        self.m = str(self.m).rjust(2, '0')
        self.s = str(self.s).rjust(2, '0')
        self.f = str(self.f).rjust(2, '0')

    def compare_frame(self):
        if self.frame < self.best_record:
            self.best_record_update = True

    def draw_system_screen(self):
        # 外枠
        pyxel.bltm(0, 0, 0, 32, 0, 32, 32, 0)
        self.draw_time()
        self.draw_best_record()
        pyxel.rect(13, 13, 86, 38, 0)
        pyxel.text(48, 18, "Avoid", 15)
        pyxel.rectb(69, 16, 9, 9, 5)
        pyxel.text(80, 18, "and", 15)
        pyxel.circ(97, 20, 4, 8)
        pyxel.circb(97, 20, 4, 10)
        pyxel.text(103, 18, ".", 15)
        pyxel.text(48, 18+12, "Aim for", 15)
        pyxel.rectb(77, 16+12, 9, 9, 8)
        pyxel.text(87, 18+12, ".", 15)
        pyxel.text(15, 15, "LEVEL", 15)
        self.number.draw_number()

    def draw_time(self):
        x = 150
        y = 19
        pyxel.text(x-5, y-11, "TIME", 15)
        pyxel.rect(x-5, y-5, 88, 26, 0)
        pyxel.rectb(x-5, y-5, 88, 26, 13)
        pyxel.line(x-5+87, y-5, x-5+87, y-5+25, 15)
        pyxel.line(x-5+87, y-5+25, x-5, y-5+25, 15)
        # m
        pyxel.blt(x, y, 1, int(self.m[0])*16, 0, 16, 16, 0)
        pyxel.blt(x+12*1, y, 1, int(self.m[1])*16, 0, 16, 16, 0)
        # '
        pyxel.blt(x+12*2, y, 1, 16*10, 0, 2, 4, 0)
        # s
        pyxel.blt(x+12*2+4, y, 1, int(self.s[0])*16, 0, 16, 16, 0)
        pyxel.blt(x+12*3+4, y, 1, int(self.s[1])*16, 0, 16, 16, 0)
        # ''
        pyxel.blt(x+12*4+4, y, 1, 16*10, 0, 4, 4, 0)
        # f
        pyxel.blt(x+12*4+8, y, 1, int(self.f[0])*16, 0, 16, 16, 0)
        pyxel.blt(x+12*5+8, y, 1, int(self.f[1])*16, 0, 16, 16, 0)

    def draw_best_record(self):
        x = 195
        y = 46
        pyxel.rect(x-3, y-2, 40, 13, 0)
        pyxel.rectb(x-3, y-2, 40, 13, 13)
        pyxel.line(x-3+39, y-2, x-3+39, y-2+12, 15)
        pyxel.line(x-3+39, y-2+12, x-3, y-2+12, 15)
        # m
        pyxel.blt(x, y, 1, int(self.m_b[0])*8, 16, 8, 8, 0)
        pyxel.blt(x+5*1, y, 1, int(self.m_b[1])*8, 16, 8, 8, 0)
        # '
        #pyxel.blt(x+12*2, y, 1, 16*10, 0, 2, 4, 0)
        # s
        pyxel.blt(x+5*2+2, y, 1, int(self.s_b[0])*8, 16, 8, 8, 0)
        pyxel.blt(x+5*3+2, y, 1, int(self.s_b[1])*8, 16, 8, 8, 0)
        # ''
        #pyxel.blt(x+12*4+4, y, 1, 16*10, 0, 4, 4, 0)
        # f
        pyxel.blt(x+5*4+4, y, 1, int(self.f_b[0])*8, 16, 8, 8, 0)
        pyxel.blt(x+5*5+4, y, 1, int(self.f_b[1])*8, 16, 8, 8, 0)

        pyxel.text(x-20, y, "BEST", 15)


# ========== タイムレコード ==========
class RecordForResult:
    def __init__(self, x, y, x_aim, y_aim, frame_to_use, frame):
        # 各種座標情報
        self.x_init, self.y_init = x, y
        self.x_now, self.y_now = x, y
        self.x_aim, self.y_aim = x_aim, y_aim
        # 移動先へ向かうベクトル
        self.vector_to_aim = [self.x_aim-self.x_init, self.y_aim-self.y_init]
        # 移動先への移動量（移動前0<= 移動量 <=移動先１）
        self.vector_sca_rate = 0
        # 移動先への移動量の、１fごとの増加量(引数f数で移動量１になる)
        self.rate_add_for1frame = 1/frame_to_use
        # 自身の座標を動かすか
        self.active = True
        # 見せるか消すか
        self.visible = True
        # （数字のみ）見えるか消すか
        self.visible_num = True
        # 点滅させるか
        self.blink = False
        # 表示する時間
        self.frame = frame
        self.m = int((self.frame/30)/60)
        if self.m >= 99:
            self.m = 99
        self.s = int((((self.frame/30)/60)-self.m)*60)
        self.f = int((((((self.frame/30)/60)-self.m)*60)-self.s)*100)
        self.m = str(self.m).rjust(2, '0')
        self.s = str(self.s).rjust(2, '0')
        self.f = str(self.f).rjust(2, '0')

    def reset_record_for_result(self):
        self.x_now, self.y_now = self.x_init, self.y_init
        self.vector_sca_rate = 0
        self.active = False

    def update_record_for_result(self):
        if self.active:
            self.x_now = (self.x_init 
                + self.vector_to_aim[0] 
                * self.vector_sca_rate)
            self.y_now = (self.y_init 
                + self.vector_to_aim[1] 
                * self.vector_sca_rate)
            self.vector_sca_rate += self.rate_add_for1frame
            if self.vector_sca_rate >= 1:
                self.blink = True
                self.vector_sca_rate = 1

    def draw_record_for_result(self):
        if self.visible:
            x = self.x_now
            y = self.y_now
            pyxel.rect(x-5, y-5, 88, 26, 0)
            pyxel.rectb(x-5, y-5, 88, 26, 13)
            pyxel.line(x-5+87, y-5, x-5+87, y-5+25, 15)
            pyxel.line(x-5+87, y-5+25, x-5, y-5+25, 15)
            # '
            pyxel.blt(x+12*2, y, 1, 16*10, 0, 2, 4, 0)
            # ''
            pyxel.blt(x+12*4+4, y, 1, 16*10, 0, 4, 4, 0)
            if self.blink:
                if pyxel.frame_count%6 < 3:
                    pyxel.text(x-5, y-11, "BEST RECORD!!", 15)
                if pyxel.frame_count%20 < 10:
                    if pyxel.frame_count%20 == 1:
                        pyxel.play(0, 17)
                    self.visible_num = True
                else:
                    self.visible_num = False
            else:
                self.visible_num = True
            if self.visible_num:
                # m
                pyxel.blt(x, y, 1, int(self.m[0])*16, 0, 16, 16, 0)
                pyxel.blt(x+12*1, y, 1, int(self.m[1])*16, 0, 16, 16, 0)
                # s
                pyxel.blt(x+12*2+4, y, 1, int(self.s[0])*16, 0, 16, 16, 0)
                pyxel.blt(x+12*3+4, y, 1, int(self.s[1])*16, 0, 16, 16, 0)
                # f
                pyxel.blt(x+12*4+8, y, 1, int(self.f[0])*16, 0, 16, 16, 0)
                pyxel.blt(x+12*5+8, y, 1, int(self.f[1])*16, 0, 16, 16, 0)
            else:
                # m
                pyxel.blt(x, y, 1, 11*16, 0, 16, 16, 0)
                pyxel.blt(x+12*1, y, 1, 11*16, 0, 16, 16, 0)
                # s
                pyxel.blt(x+12*2+4, y, 1, 11*16, 0, 16, 16, 0)
                pyxel.blt(x+12*3+4, y, 1, 11*16, 0, 16, 16, 0)
                # f
                pyxel.blt(x+12*4+8, y, 1, 11*16, 0, 16, 16, 0)
                pyxel.blt(x+12*5+8, y, 1, 11*16, 0, 16, 16, 0)


# ========== ステージ番号用 ==========
class Number:
    """[summary]
    """    
    def __init__(self, x, y, num, max, expansion_rate, col):
        """[summary]

        Args:
            x ([type]): [description]
            y ([type]): [description]
            num ([int]): [description]
        """        
        self.count0 = pyxel.frame_count  # カウントの0位置
        self.coords = np.array([x, y])  # 中心座標
        self.rad = 0  # 傾ける角度
        self.expansion_rate = expansion_rate  # 中心座標からの拡大率
        self.expansion_rate_max = expansion_rate  # 拡大率の最大値
        self.v_expansion_rate = 1  # 拡大
        self.v_rad = np.pi/90

        # 数字の中心座標を原点とした位置ベクトル
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
        self.num = num  # 選択されているステージ番号
        self.num_min = 1  # ステージ番号の最小値
        self.num_max = max  # ステージ番号の最大値
        self.selected_setting = self.settings[self.num]  # 番号のステージ設定
        self.col = col  # 数字の描画色
        self.prev_next = 1  # -1:prev, 1:next 数字を倒す角度に利用

    def update_number(self, next, prev):
        """[summary]
        """       
        if prev:
            # 戻るボタンが押された場合
            self.count0 = pyxel.frame_count
            self.prev_next = -1
            self.num -= 1
        elif next:
            # 進むボタンが押された場合
            self.count0 = pyxel.frame_count
            self.prev_next = 1
            self.num += 1
        if self.num < self.num_min:
            # 結果の数字が最小値未満なら、最小値と同じにする
            self.num = self.num_min
        elif self.num > self.num_max:
            # 結果の数字が最大値より大きいとき、最大値と同じにする
            self.num = self.num_max
        # 選択されたステージ番号に該当するステージ設定
        self.selected_setting = self.settings[self.num]
        # 数字を傾ける処理
        self.expansion_rate *= self.v_expansion_rate
        self.rad_sca = np.pi / 8 / ((pyxel.frame_count-self.count0) + 1 / 50)
        if self.rad_sca <= 0.03:
            self.rad_sca = 0
        self.rad = (self.rad_sca 
                    * (self.prev_next)
                    * np.cos(np.pi / 2 * (pyxel.frame_count-self.count0)))

    def draw_number(self):
        """[summary]
        """        
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
        return (self.coords 
            + np.dot(np.array([[np.cos(self.rad), -np.sin(self.rad)], 
                    [np.sin(self.rad), np.cos(self.rad)]]), point)
            * self.expansion_rate)