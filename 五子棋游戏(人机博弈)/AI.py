# -*- coding: utf-8 -*-
class AI:
    def __init__(self,chessboard):
        self.chessboard = chessboard
        self.size = len(chessboard)
        self.count = 0
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
    #如果该点周围米字方向上两格都为空，就跳过该点
    def judge_empty(self,m,n):
        directions = [(-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1), (1, 1), (-1, -1)]
        j = 0
        count = 1
        while j < len(directions):
            a = 0
            # 循环两次，分别判断两个相对的方向
            while a <= 1:
                x, y = m, n
                a += 1
                for i in range(2):
                    #判断边界
                    if x + directions[j][0] < 0 or x + directions[j][0] > self.size - 1 or y + directions[j][
                        1] < 0 or y + directions[j][1] > self.size - 1:
                        break
                    x += directions[j][0]
                    y += directions[j][1]
                    if self.chessboard[x][y][2] == 0:
                        count += 1
                    else:
                        #若当前方向上出现另一颜色棋子，中止该方向的判断
                        break
                j += 1
        if count == 17:
            return 1
        return 0
    #判断白子是否赢
    def judge(self,m,n):
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
                    if self.chessboard[x][y][2] == self.chessboard[m][n][2]:
                        count += 1
                    else:
                        #若当前方向上出现另一颜色棋子，中止该方向的判断
                        break
                j += 1
            if count >= 5:
                if self.chessboard[m][n][2] == 2:
                    # 赢
                    return 1
        #输
        return 0
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



