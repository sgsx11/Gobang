# -*- coding: utf-8 -*-
#主窗口
import sys
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from AI import AI
from gobang_ui import Ui_MainWindow
from copy import deepcopy

#ai线程
class AIThread(QThread):
    _signal = pyqtSignal(list)
    def __init__(self):
        super(AIThread, self).__init__()

    def set_chessboard(self,chessboard):
        self.chessboard = chessboard

    def run(self):
        ai = AI(self.chessboard)
        values = -100000000
        record = [-1, -1, 2]
        # 记录values最大的那步棋下的位置
        for i in range(15):
            for j in range(15):
                # 如果该点为空，假设下在该点，修改棋盘状态
                if self.chessboard[i][j][2] == 0:
                    # 如果该点周围米字方向上两格都为空，就跳过该点(缩小落子范围,跳过离棋盘上其他棋子较远的点)
                    if ai.judge_empty(i, j):
                        continue
                    self.chessboard[i][j][2] = 2
                    # 评估
                    evaluate = ai.ai(1,1,values)
                    # # 如果当前白子下法能完成五连，则将evaluate设一个较大的值
                    # if ai.judge(i, j):
                    #     evaluate = 10000000
                    #取评估值的最大值
                    if evaluate >= values:
                        values = evaluate
                        record = [i, j, 2]
                    # 回溯
                    self.chessboard[i][j][2] = 0
        #print("{}:{}".format(0, values))
        #print("剪枝次数：{}".format(ai.count))
        self._signal.emit(record)

#对局时间线程
class GameTime(QThread):
    _signal = pyqtSignal(str)

    def __init__(self,label):
        self.label = label
        super(GameTime, self).__init__()

    def set_status(self,status):
        self.status = status

    def run(self):
        start = time.time()
        while self.status:
            time.sleep(1)
            end = time.time()
            second = int(end-start)
            display_time = str(int(second/60))+":"+str(second%60)
            #print(display_time)
            self._signal.emit(display_time)


# 重新定义Label类
class LaBel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)

    def enterEvent(self, e):
        e.ignore()

class MyMainForm(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.setCursor(Qt.PointingHandCursor)  # 鼠标变成手指形状
        self.black = QPixmap('./designer/image/black.png')
        self.white = QPixmap('./designer/image/white.png')
        self.mouse_point = LaBel(self)  # 将鼠标图片改为棋子
        self.mouse_point.setScaledContents(True)
        self.mouse_point.setPixmap(self.black)  # 加载黑棋
        self.mouse_point.setGeometry(1100, 750, 64, 64)
        self.pieces = [LaBel(self) for i in range(225)]  # 新建225个棋子标签，准备在棋盘上绘制棋子
        for piece in self.pieces:
            piece.setVisible(True)  # 图片可视
            piece.setScaledContents(True)  # 图片大小根据标签大小可变
        self.mouse_point.raise_()  # 鼠标始终在最上层
        #实例化计时线程
        self.game_time = GameTime(self.label_3)
        self.game_time._signal.connect(self.set_time)
        self.game_time.set_status(1)
        self.game_time.start()
        #实例化ai线程
        self.ai = AIThread()
        self.ai._signal.connect(self.ai_draw)
        #要想鼠标不按下时的移动也能捕捉到，需要setMouseTracking(true)。
        self.setMouseTracking(True)
        #棋局状态，1为开始对局，0为停止
        self.status = 1
        #设置已下步数
        self.step = 0
        # 棋盘大小
        self.size = 15
        #棋盘点坐标,前两个元素是坐标x,坐标y,第三个元素是棋盘状态，未落子为0，黑子为1，白子为2
        self.chessboard_position = []
        pos = [40,40,0]
        for i in range(self.size):
            temp = []
            for j in range(self.size):
                temp.append(deepcopy(pos))
                pos[0] += 64
            self.chessboard_position.append(deepcopy(temp))
            pos[1] += 64
            pos[0] = 40
        #print(self.chessboard_position)

    def set_time(self,time):
        self.label_3.setText("时间：{}".format(time))

    def mouseMoveEvent(self, e):  # 黑色棋子随鼠标移动
        # self.lb1.setText(str(e.x()) + ' ' + str(e.y()))
        self.mouse_point.move(e.x() - 16 , e.y() - 16)
    #玩家下棋
    def mousePressEvent(self, e):
        #判断棋局状态
        if self.status == 0:
            return
        x, y = e.x(), e.y()
        #print(x,y)
        if e.button() == Qt.LeftButton:
            #校验落在位置是否在棋盘内，棋盘范围（40，40）~（960，960）
            if x >= 40 and x <= 960 and y >= 40 and y<= 960:
                #确定棋子精确位置,x,y为将要放置棋子的坐标，a为该坐标的状态值，m,n是该棋子坐标在棋盘点矩阵chessboard_position中的行和列
                x,y,a,m,n = self.position(x,y)
                #如果未能确定棋子精确位置(x == -1)，就不允许落子,如果该位置已有棋子(a!=0)，也不允许落子
                if x == -1 or a != 0:
                    return
                #print(x, y)
                #画出棋子
                self.draw(x,y,1)
                # 更改棋盘点状态
                self.chessboard_position[m][n][2] = 1
                #判断输赢,根据结果决定是否继续棋局
                if self.judge(m,n):
                    # 锁定棋局状态，待ai下完后再放开
                    self.status = 0
                    self.label_7.setText("让我想一下......")
                    #ai下棋
                    self.ai.set_chessboard(self.chessboard_position)
                    self.ai.start()
            else:
                print("请在棋盘内落子!")
                return

    #ai落子
    def ai_draw(self,result):
        i,j,a = result
        #如果棋盘下满，则停止
        if i == j == -1:
            self.status = 0
        self.draw(self.chessboard_position[i][j][0] - 16, self.chessboard_position[i][j][1] - 16, a)
        # 更改棋盘点状态
        self.chessboard_position[i][j][2] = a
        self.status = 1
        self.label_7.setText("轮到你了！")
        # 判断输赢
        self.judge(i, j)

    #在每次落子后判断输赢,x,y为落子的棋盘点矩阵行列
    def judge(self,m,n):
        #print(m,n)
        #print(self.chessboard_position[m][n])
        #判断chessboard_position[m][n]在米字方向上是否有五个连续的棋子
        directions = [(-1,0),(1,0),(-1,1),(1,-1),(0,1),(0,-1),(1,1),(-1,-1)]
        #上下方向,统计向上和向下连续的棋子个数，大于等于五则胜利
        j = 0
        while j < len(directions):
            count = 1
            a = 0
            #循环两次，分别判断两个相对的方向
            while a <= 1:
                x, y = m, n
                a += 1
                for i in range(4):
                    if x + directions[j][0] < 0 or x + directions[j][0] > self.size - 1 or y + directions[j][1] < 0 or y + directions[j][1] > self.size - 1:
                        break
                    x += directions[j][0]
                    y += directions[j][1]
                    if self.chessboard_position[x][y][2] == self.chessboard_position[m][n][2]:
                        count += 1
                    else:
                        #若当前方向上出现另一颜色棋子，中止该方向的判断
                        break
                j += 1

            if count >= 5:
                result_label = LaBel(self)
                result_label.setVisible(True)  # 图片可视
                result_label.setScaledContents(True)  # 图片大小根据标签大小可变
                if self.chessboard_position[m][n][2] == 1:
                    print("黑子胜出")
                    #计时停止
                    self.game_time.set_status(0)
                    #设置棋局状态为0
                    self.status = 0
                    #显示相关信息
                    #self.winner = LaBel(self)
                    win = QPixmap('./designer/image/win-removebg-preview.png')
                    result_label.setPixmap(win)
                    result_label.setGeometry(140, 232, 700, 150)
                    #结束棋局
                    return 0
                else:
                    print("白子胜出")
                    # 计时停止
                    self.game_time.set_status(0)
                    # 设置棋局状态为0
                    self.status = 0
                    win = QPixmap('./designer/image/lost-removebg-preview.png')
                    result_label.setPixmap(win)
                    result_label.setGeometry(140, 232, 700, 150)
                    # 结束棋局
                    return 0
        #继续棋局
        return 1


    # 确定棋子精确位置,遍历225个棋盘点坐标，
    # 若落子位置坐标和某棋盘点坐标距离小于32，就返回该棋盘点坐标和状态值
    def position(self,i,j):
        for m in range(self.size):
            for n in range(self.size):
                pos = self.chessboard_position[m][n]
                dist = self.distance(i,j,pos[0],pos[1])
                if dist <= 32:
                    # 减16是为了保证棋子处于棋盘十字线中心位置
                    return pos[0]-16,pos[1]-16,pos[2],m,n
        #默认返回
        return -1,-1,-1,-1,-1
    #求两点距离
    def distance(self,x1,y1,x2,y2):
        return ((x1-x2)**2 + (y1-y2)**2)**0.5
    #放置棋子
    def draw(self,i,j,a):
        if a == 1:
            self.pieces[self.step].setPixmap(self.black)  # 放置黑色棋子
        elif a == 2:
            self.pieces[self.step].setPixmap(self.white)  # 放置白色棋子
        self.pieces[self.step].setGeometry(i,j,64,64) # 设置位置，大小
        self.step += 1
        self.label_2.setText("步数：{}".format(self.step))


if __name__ == "__main__":
    # 固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    # 初始化
    myWin = MyMainForm()
    #设置标题图标
    myWin.setWindowIcon(QIcon('./favicon.ico'))
    #设置标题
    myWin.setWindowTitle('五子棋(人机博弈)')
    # 将窗口控件显示在屏幕上
    myWin.show()
    # 程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())