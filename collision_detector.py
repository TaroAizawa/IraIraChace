# C:/users/Taro Aizawa/Desktop/mygame
# -*- coding: utf-8 -*-
import math
import numpy as np

class CollisionDetector:
    """ 当たり判定の関数を提供 """
    def __init__(self):
        """ コンストラクタ """
        # メソッドの再帰識別変数
        # 判定基準が自身なら0, 相手なら1
        self.perspective: int = 0

    # ベクトル同士の角度の鋭角・鈍角判定(自身の内部で使用)
    def check_over90(self, A: np.ndarray, B: np.ndarray) -> bool:
        """ベクトルAとBのなす角が鋭角ならTrueを返す"""
        if np.dot(A, B) <= 0:
            # 鋭角：Trueを返す
            return True
        else:
            # 鈍角：Falseを返す
            return False

    # ================================
    # ========== 点 -> 相手 ==========
    # ================================
    def check_p2p(self,
        x: int, y: int,
        tar_x: int, tar_y: int) -> bool:
        """ 点 -> 点 の当たり判定 """
        # ===== 当たり判定 =====
        # 条件：
        # 自身と相手の座標(int)が一致
        if [x, y] == [tar_x, tar_y]:
            # 当たった判定：Trueを返す
            return True
        else:
            # そうでない場合：Falseを返す
            return False

    def check_p2c(self,
        x: int, y: int,
        tar_x: int , tar_y: int, tar_r: int) -> bool:
        """ 点 -> 円 の当たり判定 """
        # ===== 事前の計算 =====
        # x方向の距離
        dx = x - tar_x
        # y方向の距離
        dy = y - tar_y
        # -> ２点間の距離
        dir: float = math.sqrt(dx*dx+dy*dy)
        # ===== 当たり判定 =====
        # 条件：
        # 自身と相手の中心との距離が相手の半径未満
        if dir < tar_r:
            # 当たった判定：Trueを返す
            return True
        else:
            # そうでない場合：Falseを返す
            return False

    def check_p2l(self,
        x: int, y: int,
        tar_x1: int, tar_y1: int,
        tar_x2: int, tar_y2: int) -> bool:
        """ 点 -> 線 の当たり判定 """
        # ===== 事前の計算 =====
        # 各種座標（0：自身 1：線分の始点 2：線分の終点）
        coord_0 = np.array([x, y])
        tar_coord_1 = np.array([tar_x1, tar_y1])
        tar_coord_2 = np.array([tar_x2, tar_y2])
        # ベクトル：始点->終点
        self.vec_2to1 = np.array(tar_coord_1-tar_coord_2
            + np.array([0.01, 0.01]))    
        # ベクトル：始点->自身 
        self.vec_1to0 = np.array(coord_0-tar_coord_1) 
        # ベクトル：終点->自身                      
        self.vec_2to0 = np.array(coord_0-tar_coord_2)
        # 線分と円の中心との外積（＝最短距離）         
        self.cross = np.cross(self.vec_2to1  
            / np.linalg.norm(self.vec_2to1, ord=2), 
            self.vec_2to0)             
        # ===== 当たり判定 =====
        # 条件：
        # 線分と自身の最短距離(intにキャストで小数点以下切り捨て) が0に近い かつ
        # （自身が線分と並行の区間内にない もしくは
        # 　線分の始点・終点のいずれかとの距離が0）
        if (int(abs(self.cross) < 0.45 and
            self.check_over90(self.vec_2to1, self.vec_2to0) 
            != self.check_over90(self.vec_2to1, self.vec_1to0)) or
            (np.linalg.norm(self.vec_2to0, ord=2) == 0 or
            np.linalg.norm(self.vec_1to0, ord=2) == 0)):
            # 当たった判定：Trueを返す
            return True
        else:
            # そうでない場合：Falseを返す
            return False

    def check_p2poly(self,
        x: int, y: int,
        tar_points: list) -> bool:
        """ 点 -> 多角形 の当たり判定 """
        tar_points = np.array(tar_points)
        # 判定処理前のチェック
        if len(tar_points) < 3:
            # 渡された点群が３個未満＝多角形でないとき
            if len(tar_points) == 0:
                additional = ''
            elif len(tar_points) == 1:
                additional = 'You must use method "check_p2p" instead.'
            elif len(tar_points) == 2:
                additional = 'You must use method "check_p2l" instead.'
            # エラー文吐かせる -> 代わりのメソッド勧める
            raise ValueError('Method "check_p2poly" needs more than 3 points\n'
                + f'but passed {len(tar_points)} points.\n{additional}')
        if True:
            # 多角形が凸のとき（三角形は必ず凸）
            # ===== 当たり判定 =====
            # 条件：
            # 相手の点群を 点０->点１, ..., 終点->点０ の順に
            # 隣同士で結ぶ各ベクトルの全てについて、
            # そのベクトルの始点->自身を結ぶベクトルとの外積の符号が等しい
            # （＝左右判定が等しい）
            for i, p in enumerate(tar_points):
                vec_s2t = np.array([x, y]) - p
                if i < len(tar_points) - 1:
                    # ～ 終点１個前の点->終点のベクトル
                    vec_s2e = tar_points[i+1] - p
                    cross = np.cross(vec_s2e, vec_s2t)
                    if i == 0:
                        # 点０->点１の最初のベクトルの場合
                        # 単独では判定できないのでpassする
                        pass
                    elif cross * cross_last <= 0:
                        # そうでない判定：Falseを返す
                        return False
                    # 今の外積を次の判定用に保持して次へ
                    cross_last = cross
                else:
                    # 終点->点０のベクトル（最後）
                    vec_s2e = tar_points[0] - p
                    cross = np.cross(vec_s2e, vec_s2t)
                    if cross * cross_last < 0:
                        # そうでない判定：Falseを返す
                        return False
                    else:
                        # 最後まで「そうでない判定」がない
                        # ＝当たった判定：Trueを返す
                        return True
        else:
            # 多角形が凹のとき
            pass
        return False

    # ================================
    # ========== 円 -> 相手 ==========
    # ================================
    def check_c2p(self,
        x: int , y: int, r: int,
        tar_x: int, tar_y: int) -> bool:
        """ 円 -> 点 の当たり判定 """
        # 点 -> 円 に視点を変えて判定
        return self.check_p2c(tar_x, tar_y, x, y, r)

    def check_c2c(self, 
        x: int, y: int, r: float, 
        tar_x: int, tar_y: int, tar_r: float) -> bool:
        """ 円 -> 円 の当たり判定 """
        # ===== 事前の計算 =====
        # x方向の距離
        dx = x - tar_x
        # y方向の距離
        dy = y - tar_y
        # ２点間の距離
        dir: float = math.sqrt(dx*dx+dy*dy)
        # ===== 当たり判定 =====
        # 条件：
        # 自身の中心と相手の中心との距離が互いの半径の合計未満
        if dir < r + tar_r:
            # 当たった判定：Trueを返す
            return True
        else:
            # そうでない場合：Falseを返す
            return False

    def check_c2l(self, 
            x: int, y: int, r: float, 
            tar_x1: int, tar_y1: int, 
            tar_x2: int, tar_y2: int) -> bool:
        """ 円 -> 線 の当たり判定 """
        # ===== 事前の計算 =====
        # 各種座標（0：自身の中心 1：線分の始点 2：線分の終点）
        coord_0 = np.array([x, y])
        tar_coord_1 = np.array([tar_x1, tar_y1])
        tar_coord_2 = np.array([tar_x2, tar_y2])
        # ベクトル：始点->終点
        self.vec_2to1 = np.array(tar_coord_1-tar_coord_2
            + np.array([0.01, 0.01]))    
        # ベクトル：始点->自身 
        self.vec_1to0 = np.array(coord_0-tar_coord_1) 
        # ベクトル：終点->自身                      
        self.vec_2to0 = np.array(coord_0-tar_coord_2)
        # 線分と円の中心との外積（＝最短距離）         
        self.cross = np.cross(self.vec_2to1  
            / np.linalg.norm(self.vec_2to1, ord=2), 
            self.vec_2to0)             
        # ===== 当たり判定 =====
        # 条件：
        # 線分と中心の最短距離が半径以下 かつ
        # （中心が線分と並行の区間内にない もしくは
        # 線分の始点・終点のいずれかが自身の半径内にある）
        if (abs(self.cross) <= r and
            (self.check_over90(self.vec_2to1, self.vec_2to0) 
            != self.check_over90(self.vec_2to1, self.vec_1to0) or
            (np.linalg.norm(self.vec_2to0, ord=2) <= r or
            np.linalg.norm(self.vec_1to0, ord=2) <= r))):
            # 当たった判定：Trueを返す
            return True
        else:
            # そうでない場合：Falseを返す
            return False

    def check_c2poly(self,
        x: int, y: int, r: float,
        tar_points: list) -> bool:
        """ 円 -> 多角形 の当たり判定 """
        # 判定処理前のチェック
        if len(tar_points) < 3:
            # 渡された点群が３個未満＝多角形でないとき
            if len(tar_points) == 0:
                additional = ''
            elif len(tar_points) == 1:
                additional = 'You must use method "check_c2p" instead.'
            elif len(tar_points) == 2:
                additional = 'You must use method "check_c2l" instead.'
            # エラー文吐かせる -> 代わりのメソッド勧める
            raise ValueError('Method "check_p2poly" needs more than 3 points\n'
                + f'but passed {len(tar_points)} points.\n{additional}')
        if True:
            # 多角形が凸のとき（三角形は必ず凸）
            # ===== 当たり判定 =====
            # 条件：下記の判定１か判定２のいずれかがTrue
            if self.check_poly2p(tar_points, x, y):
                # 判定１：自身の中心点が多角形の内部にある
                return True
            else:
                # 判定２：自身が多角形を構成する線のいずれかに当たっている
                for index, point in enumerate(tar_points):
                    if index < len(tar_points)-1:
                        point_next = tar_points[index + 1]
                    else:
                        point_next = tar_points[0]
                    if self.check_l2c(point[0], point[1], 
                            point_next[0], point_next[1],
                            x, y, r):
                            # 当たった判定：Trueを返す
                            return True
            # いずれも該当しない場合：Falseを返す
            return False
        else:
            # 多角形が凹のとき
            pass
        return False

    # ================================
    # ========== 線 -> 相手 ==========
    # ================================
    def check_l2p(self,
        x1: int, y1: int,
        x2: int, y2: int,
        tar_x: int, tar_y: int) -> bool:
        """ 線 -> 点 の当たり判定 """
        # 点 -> 線 に視点を変えて判定
        return self.check_p2l(tar_x, tar_y, x1, y1, x2, y2)

    def check_l2c(self,
        x1: int, y1: int,
        x2: int, y2: int,
        tar_x: int, tar_y: int, tar_r: float) -> bool:
        """ 線 -> 円 の当たり判定 """
        # 円 -> 線 に視点を変えて判定
        return self.check_c2l(tar_x, tar_y, tar_r, x1, y1, x2, y2)

    def check_l2l(self,
        x1: int, y1: int, 
        x2: int, y2: int,
        tar_x1: int, tar_y1: int, 
        tar_x2: int, tar_y2: int) -> bool:
        """ 線 -> 線 の当たり判定 """
        # ===== 事前の計算 =====
        # 各種座標（1：始点 2：終点, 
        coord_1 = np.array([x1, y1])
        coord_2 = np.array([x2, y2])
        coord_tar1 = np.array([tar_x1, tar_y1])
        coord_tar2 = np.array([tar_x2, tar_y2])
        # ベクトル：始点->終点
        vec_1to2 = np.array(coord_2 - coord_1 + np.array([0.01, 0.01]))
        # ベクトル：始点->相手の始点 
        vec_1totar1 = np.array(coord_tar1 - coord_1) 
        # ベクトル：始点->相手の終点                      
        vec_1totar2 = np.array(coord_tar2 - coord_1)
        # 自身と相手の始点との外積（＝自身より上にいるか下にいるか）         
        cross1 = np.cross(vec_1to2 
            / np.linalg.norm(vec_1to2, ord=2), 
            vec_1totar1) 
        # 自身と相手の終点との外積（＝自身より上にいるか下にいるか）         
        cross2 = np.cross(vec_1to2  
            / np.linalg.norm(vec_1to2, ord=2), 
            vec_1totar2)
        # ===== 当たり判定 =====
        # 条件：
        # 自身の始点->相手の始点/終点２つのベクトルの外積の符号が異なる かつ
        # （再帰により）相手の始点->自身の始点/終点でも同様に異なる
        # （＝互いに「始点と終点が相手の線分をまたぐ」）
        if ((cross1 * cross2) < 0):
            # 当たった判定：
            if self.perspective == 0:
                # これが再帰でない場合：視点は相手
                self.perspective = 1
                # 互いの立場を入れ替えて、再帰による最終判定を返す
                return self.check_l2l(
                    tar_x1, tar_y1, 
                    tar_x2, tar_y2, 
                    x1, y1, 
                    x2, y2)
            elif self.perspective == 1:
                # これが再帰の場合：視点を自身に戻す
                self.perspective = 0
                # 最終的な当たった判定：Trueを返す
                return True
        else:
            # そうでない場合：
            if self.perspective == 1:
                # これが再帰の場合：視点を自身に戻す
                self.perspective = 0
            # Falseを返す
            return False

    def check_l2poly(self,
        x1: int, y1: int, x2: int, y2: int,
        tar_points: list) -> bool:
        """ 線 -> 多角形 の当たり判定 """
        # 判定処理前のチェック
        if len(tar_points) < 3:
            # 渡された点群が３個未満＝多角形でないとき
            if len(tar_points) == 0:
                additional = ''
            elif len(tar_points) == 1:
                additional = 'You must use method "check_l2p" instead.'
            elif len(tar_points) == 2:
                additional = 'You must use method "check_l2l" instead.'
            # エラー文吐かせる -> 代わりのメソッド勧める
            raise ValueError('Method "check_p2poly" needs more than 3 points\n'
                + f'but passed {len(tar_points)} points.\n{additional}')
        if True:
            # 多角形が凸のとき（三角形は必ず凸）
            if (self.check_poly2p(tar_points, x1, y1) and
                    self.check_poly2p(tar_points, x2, y2)):
                return True
            else:
                for index, point in enumerate(tar_points):
                    if index < len(tar_points)-1:
                        point_next = tar_points[index + 1]
                    else:
                        point_next = tar_points[0]
                    if self.check_l2l(point[0], point[1], 
                            point_next[0], point_next[1],
                            x1, y1, 
                            x2, y2):
                            return True
                return False
        else:
            # 多角形が凹のとき
            pass
        return False

    # ===================================
    # ========== 多角形 -> 相手 ==========
    # ===================================
    def check_poly2p(self,
        points: list,
        tar_x: int, tar_y: int) -> bool:
        """ 多角形 -> 点 の当たり判定 """
        # 判定処理前のチェック
        if len(points) < 3:
            # 渡された点群が３個未満＝多角形でないとき
            if len(points) == 0:
                additional = ''
            elif len(points) == 1:
                additional = 'You must use method "check_p2p" instead.'
            elif len(points) == 2:
                additional = 'You must use method "check_l2p" instead.'
            # エラー文吐かせる -> 代わりのメソッド勧める
            raise ValueError('Method "check_p2poly" needs more than 3 points\n'
                + f'but passed {len(points)} points.\n{additional}')
        # 点 -> 多角形 に視点を変えて判定
        return self.check_p2poly(tar_x, tar_y, points)

    def check_poly2c(self,
        points: list,
        tar_x: int, tar_y: int, tar_r: float) -> bool:
        """ 多角形 -> 円 の当たり判定 """
        # 判定処理前のチェック
        if len(points) < 3:
            # 渡された点群が３個未満＝多角形でないとき
            if len(points) == 0:
                additional = ''
            elif len(points) == 1:
                additional = 'You must use method "check_p2c" instead.'
            elif len(points) == 2:
                additional = 'You must use method "check_l2c" instead.'
            # エラー文吐かせる -> 代わりのメソッド勧める
            raise ValueError('Method "check_p2poly" needs more than 3 points\n'
                + f'but passed {len(points)} points.\n{additional}')
        # 円 -> 多角形 に視点を変えて判定
        return self.check_c2poly(tar_x, tar_y, tar_r, points)

    def check_poly2l(self,
        points: list,
        tar_x1: int, tar_y1: int,
        tar_x2: int, tar_y2: int) -> bool:
        """ 多角形 -> 線 の当たり判定 """
        # 判定処理前のチェック
        if len(points) < 3:
            # 渡された点群が３個未満＝多角形でないとき
            if len(points) == 0:
                additional = ''
            elif len(points) == 1:
                additional = 'You must use method "check_p2l" instead.'
            elif len(points) == 2:
                additional = 'You must use method "check_l2l" instead.'
            # エラー文吐かせる -> 代わりのメソッド勧める
            raise ValueError('Method "check_p2poly" needs more than 3 points\n'
                + f'but passed {len(points)} points.\n{additional}')
        # 線 -> 多角形 に視点を変えて判定
        return self.check_l2poly(tar_x1, tar_y1, tar_x2, tar_y2, points)

    def check_poly2poly(self,
        points: list,
        tar_points: list) -> bool:
        """ 多角形 -> 多角形 の当たり判定 """
        # 判定処理前のチェック
        if len(points) < 3 or len(tar_points) < 3:
            # 渡された点群が３個未満＝多角形でないとき
            # 自身の場合分け
            if len(points) == 1:
                this = 'p'
            elif len(points) == 2:
                this = 'l'
            elif len(points) > 2:
                this = 'poly'
            # 相手の場合分け
            if len(tar_points) == 1:
                tar = 'p'
            elif len(tar_points) == 2:
                tar = 'l'
            elif len(tar_points) > 2:
                tar = 'poly'
            if len(points) == 0 or len(tar_points) == 0:
                # いずれかが空のリストであれば何も勧めない
                additional = ''
            else:
                # 代わりのメソッドがあるので勧める
                additional = (f'You must use method "check_{this}2{tar}"' 
                    'instead.')
            if len(tar_points) < len(points):
                length = len(tar_points)
            else:
                length = len(points)
            # エラー文吐かせる -> 代わりのメソッド勧める
            raise ValueError('Method "check_p2poly" needs more than 3 points\n'
                + f'but passed {length} points.\n{additional}')
        if True:
            # 自身が凸のとき（三角形は必ず凸）
            if True:
                # 相手の多角形が凸のとき
                for i, tar_point in enumerate(tar_points):
                    if self.check_p2poly(
                        tar_point[0], tar_point[1],
                        points):
                        # 相手の点が１個でも自身の中にあればTrue
                        return True
                    if i < len(tar_points) - 1:
                        next_point = tar_points[i+1]
                    else:
                        next_point = tar_points[0]
                    if self.check_l2poly(
                        tar_point[0], tar_point[1],
                        next_point[0], next_point[1],
                        points
                        ):
                        # 相手の線が１本でも自身に当たっていればTrue
                        return True
                # 自身と相手の立場を入れ替えてもう一度
                for i, point in enumerate(points):
                    if self.check_p2poly(
                        point[0], point[1],
                        tar_points):
                        # 相手の点が１個でも自身の中にあればTrue
                        return True
                    if i < len(points) - 1:
                        next_point = points[i+1]
                    else:
                        next_point = points[0]
                    if self.check_l2poly(
                        point[0], point[1],
                        next_point[0], next_point[1],
                        tar_points
                        ):
                        # 相手の線が１本でも自身に当たっていればTrue
                        return True
                # 全ての過程でTrueとならなければFalse
                return False
            else:
                # 相手の多角形が凹のとき
                pass
        else:
            # 自身が凹のとき
            if True:
                # 相手の多角形が凸のとき
                pass
            else:
                # 相手の多角形が凹のとき
                pass
        return False