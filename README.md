# Python+PyQt5实现五子棋游戏（人机博弈+深搜+α-β剪枝）
### 一、问题描述

#### 1、五子棋

五子棋是[全国智力运动会](https://baike.baidu.com/item/全国智力运动会/2832395)竞技项目之一，是一种两人对弈的纯策略型棋类游戏。

五子棋的棋具与[围棋](https://baike.baidu.com/item/围棋/111288)通用，是一种传统的棋种，有两种玩法。

一种是双方分别使用黑白两色的棋子，下在棋盘直线与横线的交叉点上，先形成五子连线者获胜。还有一种是自己形成五子连线就替换对方任意一枚棋子。被替换的棋子可以和对方交换棋子。最后以先出完所有棋子的一方为胜。

#### 2、什么是Agent？

Agent的概念——1977年Carl Hewitt “Viewing Control Structures as Patterns of Passing Messages”

Agent一词最早见于M.Minsky于1986年出版的《Society of Mind》

广义的Agent包括人类、物理世界的机器人和信息世界的软件机器人。

**狭义的Agent**专指信息世界中的软件机器人或称**软件****Agent**。

Wooldrige 《Intelligent Agents: Theory and Practice》：

##### 2.1弱定义

Agent用来最一般地说明一个软硬件系统，具有四个特性：

（1）**自治性**。在无人或其他系统的直接干预下可自主操作，并能控制其行为和内部状态。

（2）**社会性**。能够通过某种通信语言与其他Agent（也可能是人）进行交互。

（3）**反应性**。感知所处的环境，对环境的变化做出实时的反应，并可通过行为改变环境。

（4）**能动性**。不仅仅简单地对环境做出反应，而且可以主动地表现出目标驱动的行为。

##### 2.2强定义

Agent除具备弱定义中所有特性外，还应具备一些人类才具有的特性，如知识、信念、义务、意图等。

#### 3、实验内容

2、参照象棋游戏案例，设计一个五子棋人机游戏

（1）使用 python 编写

（2）不要求智能体的棋力

### 二、建立模型

#### 1、游戏规则

1、对局双方各执一色棋子。

2、空棋盘开局。

3、黑先、白后，交替下子，每次只能下一子。

4、棋子下在棋盘的空白点上，棋子下定后，不得向其它点移动，不得从棋盘上拿掉或拿起另落别处。

5、黑方的第一枚棋子必须下在天元点上，即中心交叉点

#### 2、游戏实现

##### 2.1 玩家下棋

```python
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
```



##### 2.2 AI下棋

###### 2.2.1 AI线程

```python
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
```

###### 2.2.2 AI推演

```python
#color表示下棋的那一方，deep表示推演深度,pre_evaluate表示上一层的评估值
    def ai(self,color,deep,pre_evaluate):
        #递归边界
        if deep >= 2:
            temp = self.evaluateBoard(2,self.chessboard) - self.evaluateBoard(1,self.chessboard)
            #print("{}:{}".format(deep, temp))
            return temp
        #values初始值
        if color == 2:
            values = -100000000
        else:
            values = 100000000
        #记录values最大的那步棋下的位置
        for i in range(15):
            for j in range(15):

                #如果该点为空，假设下在该点，修改棋盘状态
                if self.chessboard[i][j][2] == 0:
                    #如果该点周围米字方向上两格都为空，就跳过该点
                    if self.judge_empty(i,j):
                        continue
                    self.chessboard[i][j][2] = color
                    #递归评估
                    evaluate = self.ai(3-color,deep+1,values)
                    if color == 2:
                        # 剪枝，如果当前的评估值比最小的pre_evaluate要大就跳过该情况，注意要回溯
                        if evaluate > pre_evaluate:
                            # 回溯
                            self.chessboard[i][j][2] = 0
                            self.count += 1
                            return 100000000
                    else:
                        # 剪枝，如果当前的评估值比最大的pre_evaluate要小就跳过该分支，注意要回溯
                        if evaluate < pre_evaluate:
                            # 回溯
                            self.chessboard[i][j][2] = 0
                            self.count += 1
                            return -100000000
                    #如果是白子回合，应当取评估值的最大值
                    if color == 2:
                        # #如果当前白子下法能完成五连，则将evaluate设一个较大的值
                        # if self.judge(i,j):
                        #     evaluate = 10000000
                        if evaluate >= values:
                            values = evaluate
                    # 如果是黑子回合，应当取评估值的最小值
                    else:
                        if evaluate <= values:
                            values = evaluate
                    #回溯
                    self.chessboard[i][j][2] = 0
        #print("{}:{}".format(deep,values))
        return values
```

##### 2.5 画出棋子

```python
#放置棋子
    def draw(self,i,j,a):
        if a == 1:
            self.pieces[self.step].setPixmap(self.black)  # 放置黑色棋子
        elif a == 2:
            self.pieces[self.step].setPixmap(self.white)  # 放置白色棋子
        self.pieces[self.step].setGeometry(i,j,64,64) # 设置位置，大小
        self.step += 1
        self.label_2.setText("步数：{}".format(self.step))
```



##### 2.4 评估函数

```python
# 这个函数是评价当前棋盘上仅考虑某一种颜色的得分
    # 想要得到考虑双方棋子的得分，就是自己得分减去对方得分即可evaluateBoard(1) - evaluateBoard(2)
    # color 1-black 2-white
    def evaluateBoard(self,color,chessboard):
        values = 0
        directions = [(-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1), (1, 1), (-1, -1)]
        directions_2 = [(1, 0), (1, -1), (0, 1), (1, 1)]
        for row in range(self.size):
            for col in range(self.size):
                #如果当前棋子不是color对应的棋子就跳过
                if chessboard[row][col][2] != color:
                    continue
                #五个棋子，每一个都会被计算一次，所以如果出现五连，那么最后的values相当于加上5*200000
                j = 0
                while j < len(directions):
                    count = 1
                    a = 0
                    #记录中止原因
                    record = []
                    # 循环两次，分别判断两个相对的方向
                    while a <= 1:
                        x, y = row, col
                        a += 1
                        for i in range(4):
                            if x + directions[j][0] < 0 or x + directions[j][0] > self.size - 1 or y + directions[j][1] < 0 or y + directions[j][1] > self.size - 1:
                                #超过边界相当于被另一棋子堵住
                                record.append(3-color)
                                break
                            x += directions[j][0]
                            y += directions[j][1]
                            if chessboard[x][y][2] == chessboard[row][col][2]:
                                count += 1
                            else:
                                # 若当前方向上出现另一颜色棋子或者没有棋子，中止该方向的判断
                                #记录该次中止原因
                                record.append(chessboard[x][y][2])
                                break
                        j += 1
                    # 如果在米子方向上有连续5个子，则
                    # values += 200000;
                    if count >= 5:
                        values += 200000
                    elif count == 4:
                        #print("4中止原因：{}".format(record))
                        # 如果有连续4个子并且两边都没有堵住，则
                        # values += 70000;
                        if record[0] == record[1] == 0:
                            values += 70000
                        # 如果同一个方向有连续4个子并且仅有一边被堵住，则
                        # values += 4000;
                        elif (record[0] == 0 and record[1] == (3-color)) or (record[0] == (3-color) and record[1] == 0):
                            values += 1000
                    elif count == 3:
                        #print("3中止原因：{}".format(record))
                        # 如果是“活三”的情况，则values += 3000
                        if record[0] == record[1] == 0:
                            values += 1000
                        # 如果是“活三”被堵住了一边，则values += 500;
                        elif (record[0] == 0 and record[1] == (3-color)) or (record[0] == (3-color) and record[1] == 0):
                            values += 150
                    elif count == 2:
                        #print("2中止原因：{}".format(record))
                        #如果连续两个子且两边没有被堵住，values += 2000;
                        if record[0] == record[1] == 0:
                            values += 1000
                        # 如果连续两个子被堵住一边，values += 300;
                        elif (record[0] == 0 and record[1] == (3-color)) or (record[0] == (3-color) and record[1]== 0):
                            values += 150
                    # 如果是 ** * 0 * 的情况，则values += 3000;
                    # 如果是 ** 0 ** 的情况，则values += 2600;

                    k = 0
                    while k < len(directions_2):
                        x,y = row,col
                        record = []
                        record.append(chessboard[x][y][2])
                        #向下，右，左下，右下，四个方向搜索4个格子
                        for i in range(4):
                            # 搜索一个格子，如果白棋和黑棋相邻，values += 10确保白棋第一棋下在黑棋旁边
                            if i == 1 and len(record) == 2:
                                if record[0] != record[1] and record[0] and record[1]:
                                    values += 10
                            if x + directions_2[k][0] < 0 or x + directions_2[k][0] > self.size - 1 or y + directions_2[k][
                                1] < 0 or y + directions_2[k][1] > self.size - 1:
                                break
                            x += directions_2[k][0]
                            y += directions_2[k][1]
                            record.append(chessboard[x][y][2])
                        if len(record) == 5:
                            count = record.count(0)
                            # 如果是 *** 0 * 或* 0 * **的情况，则values += 3000;
                            # 即record中0的个数为1，且record[1]或record[3]是0,record.count(color) == 4
                            if (count == 1 and record[1] == 0 and record.count(color) == 4) or (count == 1 and record[3] == 0 and record.count(color) == 4):
                                values += 3000
                                #print("*** 0 * 或* 0 * **:{}".format(record))
                            # 如果是 ** 0 ** 的情况，则values += 2600;
                            if count == 1 and record[2] == 0 and record.count(color) == 4:
                                values += 2600
                                #print("** 0 **:{}".format(record))
                        k += 1
        return values
```

##### 2.5 判断输赢

```python
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
```



### 二、模型实现

#### 1、图形界面

![QQ截图20211201132728](https://user-images.githubusercontent.com/93324578/144184764-95b1039f-3d40-412c-bd79-2550896b9712.png)

#### 2、完整代码：

##### 2.1 Github

该项目使用Pycharm 2021.2.3 + Python3.8编写

完整项目已上传github：https://github.com/sgsx11/Gobang

##### 2.2 start.py

![carbon (6)](https://user-images.githubusercontent.com/93324578/144185116-0cb3e737-1882-4017-aa77-2545d5571fa0.png)

##### 2.3 AI.py

![carbon (7)](https://user-images.githubusercontent.com/93324578/144184793-6d7ae629-40ab-404b-8c43-351e73a5c81c.png)

##### 2.4 gobang_ui.py

![carbon (8)](https://user-images.githubusercontent.com/93324578/144185133-7281ae6a-387d-423f-b59a-11678cfb4aee.png)


### 三、总结

该五子棋游戏棋盘大小n = 15*15=255，假设搜索深度为d，使用深度优先搜索进行推演的时间复杂度为
$$
O(n^d)
$$
在未使用剪枝前，当d = 2时，ai思考的时间为9~10s，使用剪枝后时间缩短到3~4s，当d = 3时，ai思考的时间为3~4分钟，d = 4时，ai思考时间已经不能忍受，使得游戏体验大大下降

在后续可以通过启发式搜索来优化ai，或者改用人工神经网络来训练ai

### 四、参考文章

[五子棋AI算法（一）](https://blog.csdn.net/qq_44732921/article/details/102620510)https://blog.csdn.net/qq_44732921/article/details/102620510

[五子棋AI算法（二）](https://blog.csdn.net/qq_44732921/article/details/102648408)https://blog.csdn.net/qq_44732921/article/details/102648408

[五子棋AI算法（三）](https://blog.csdn.net/qq_44732921/article/details/104068832)https://blog.csdn.net/qq_44732921/article/details/104068832

[PyQt5实现五子棋游戏（人机对弈）](https://www.jb51.net/article/155340.htm)https://www.jb51.net/article/155340.htm


