# 数独求解 v1.2
# z.yf@pku.edu.cn
# 最后更新：2021-02-03


import copy

MATRIX = [    # 在此输入要解的数独，空单元格用0表示
    [0,0,5, 3,0,0, 0,0,0,],
    [8,0,0, 0,0,0, 0,2,0,],
    [0,7,0, 0,1,0, 5,0,0,],

    [4,0,0, 0,0,5, 3,0,0,],
    [0,1,0, 0,7,0, 0,0,6,],
    [0,0,3, 2,0,0, 0,8,0,],

    [0,6,0, 5,0,0, 0,0,9,],
    [0,0,4, 0,0,0, 0,3,0,],
    [0,0,0, 0,0,9, 7,0,0,],
]    # 这个数独是Arto Inkala博士设计的一款难度较大的数独，相关报道见https://www.mirror.co.uk/news/weird-news/worlds-hardest-sudoku-can-you-242294

MATRIX_2 = [    # 在此输入要解的数独，空单元格用0表示
    [8,0,0, 0,0,0, 0,0,0,],
    [0,0,3, 6,0,0, 0,0,0,],
    [0,7,0, 0,9,0, 2,0,0,],

    [0,5,0, 0,0,7, 0,0,0,],
    [0,0,0, 0,4,5, 7,0,0,],
    [0,0,0, 1,0,0, 0,3,0,],

    [0,0,1, 0,0,0, 0,6,8,],
    [0,0,8, 5,0,0, 0,1,0,],
    [0,9,0, 0,0,0, 4,0,0,],
]    # 这个数独是百度百科上宣称由Arto Inkala博士设计的“最难数独”，但和前一个并不一样。单就本程序解这两个数独的猜测次数而言，倒是百度百科上这款的难度要更大一些

# 第一部分：准备阶段（后面要反复调用的一些函数）
 
# 判断当前的矩阵（数独）是否已经填满
def is_filled(matrix):
    for row in range(9):
        for col in range(9):
            if matrix[row][col] == 0:
                return False
    return True

# 返回矩阵中某单元格所处的行、列、宫
# 例如，get_areas(matrix, 0, 3)返回的就是三个列表：分别是数独的第1行、第4列和中上部的宫
def get_areas(matrix, row, col):
    the_row = matrix[row]
    the_col = [each_row[col] for each_row in matrix]
    the_block = [matrix[i][j] for i in range(3 * (row // 3), 3 * (row // 3 + 1)) for j in range(3 * (col // 3), 3 * (col // 3 + 1))]
    return [the_row, the_col, the_block]

# 以九元列表area（area可以是行/列/宫）为分析单位，排除得出该行/列/宫剩下的单元格的所有可行填法，返回一个集合
# 例如，该行已经有了1、3、5、7、9五个数，那么就返回一个集合{2, 4 ,6 ,8}
def get_available_answers(area):
    return set(range(1, 10)) - set(area)    # 求差集即可

# 排除法确定单个单元格可填的数
# 例如，某个单元格所处的行已经有了1、3、5.所处的列已经有了1、2、4、5、6，所处的宫有2、4、5、7，那么就返回双元素集合{8, 9}
def get_availble_cell_values(matrix, row, col):
    available_cell_values = set(range(1, 10))
    for area in get_areas(matrix, row, col):    # 排除法确定可填的数
        available_cell_values = available_cell_values & get_available_answers(area)
    return available_cell_values


# 第二部分：等价变换（把那些没有任何争议的单元格填满）

# 对矩阵“优化”一次（等价变换），会改变变量指针指向的矩阵
def optimize(matrix):
    for row in range(9):
        for col in range(9):
            if matrix[row][col] == 0:    # 如果该单元格待填写
                available_cell_values = get_availble_cell_values(matrix, row, col)
                if len(available_cell_values) == 0:    # 无解
                    return 'ERROR'    # 返回错误提示
                elif len(available_cell_values) == 1:
                    matrix[row][col] = list(available_cell_values)[0]    # 填入唯一解
                    return matrix    # 立即返回优化后的矩阵
    return 'END'    # 这表明矩阵中已经没有值为0的单元格，或者有值为0的单元格但len(available_cell_values) >= 2，说明矩阵已经无法继续等价变换，或者是已经填满了

# 反复等价变换，直至无法优化为止，会改变变量指针指向的矩阵（很多数独可以用这个方法一次解完） 
def optimize_to_end(matrix):
    while True:
        new_matrix = optimize(matrix)
        if new_matrix == 'ERROR':
            return 'ERROR'    # 返回错误提示
        elif new_matrix == 'END':
            return matrix    # 返回当前矩阵
        else:
            matrix = new_matrix


# 第三部分：猜测

# 判断：最好情况下，一格至少要猜几次。比如，还有20个单元格没有填，其中有的有3种可能的填法，有的有4种可能的填法，有的有7种可能的填法，其中情况最好的一个格子有3种可能的填法，那么就返回3
def min_guess_num(matrix):
    num = 9
    for row in range(9):
        for col in range(9):
            if matrix[row][col] == 0:    # 如果该单元格待填写
                available_cell_values = get_availble_cell_values(matrix, row, col)
                num = min(len(available_cell_values), num)
    return num

# 对无法再等价变换的矩阵，进行n选1（一般是2选1）猜测，尝试，直至解出唯一解
def guess(input_matrix):
    # 找一个单元格用来猜
    row = -1
    col = -1
    possible_values = []
    num = min_guess_num(input_matrix)    # 一般num=2，除非每格都有至少3种可能的填法
    for i in range(9):    # 找到首个有num个可能解的单元格
        for j in range(9):
            if input_matrix[i][j] == 0:    # 如果该单元格待填写
                available_cell_values = get_availble_cell_values(input_matrix, i, j)
                if len(available_cell_values) == num:
                    row = i
                    col = j
                    possible_values = list(available_cell_values)
                    break
        if row != -1:    # 找到就撤，就用这个单元格来猜测。比如，现在有6个单元格都有2种可能填法，那么第一个这样的单元格就被我们用来进行猜测，其余的暂且不管
            break
    # 开始猜测
    print('猜测的单元格：(%d, %d)，可能的值：%s' % (row, col, possible_values))
    results = []
    for value in possible_values:
        matrix = copy.deepcopy(input_matrix)    # 保留原始矩阵，必须用deepcopy，因为如果这种可能填法被否定，还得回到原始矩阵尝试另一种填法
        matrix[row][col] = value    # 用其中一个值填进去
        result = optimize_to_end(matrix)    # 每填一个数，都要等价变换到底，再继续
        if result != 'ERROR':    # 只要不是错误信息，就一定是matrix
            if is_filled(result):    # 说明result是一个最终解；可继续验证解是否唯一
                results.append(result)
            else:    # 如果还是得不到最终解，那就再猜一次
                new_result = guess(result)    # guess()函数引用自己
                if new_result == 'MORE_THAN_ONE_ANSWER':
                    return 'MORE_THAN_ONE_ANSWER'
                elif new_result == 'ERROR':
                    pass
                else:
                    results.append(new_result)
    # 判断结果
    if results == []:
        return 'ERROR'
    elif len(results) == 1:
        return results[0]
    else:
        return 'MORE_THAN_ONE_ANSWER'


# 第四部分：将矩阵打印成方便阅读的形态

def print_matrix(matrix):
    print('')
    for big_row in range(3):
        for sub_row in range(3):
            for big_col in range(3):
                for sub_col in range(3):
                    cell = matrix[3 * big_row + sub_row][3 * big_col + sub_col]
                    if cell == 0:
                        cell = ' '    # 如果还没完成，则在待填单元格处打印空格
                    print(cell, end=' ')
                print(' ', end=' ')
            print('')
        print('')


def main():
    print_matrix(MATRIX)
    matrix = copy.deepcopy(MATRIX)    # 求解之前先把原始输入备个份
    matrix = optimize_to_end(matrix)
    if matrix != 'ERROR' and not is_filled(matrix):
        matrix = guess(matrix)
    if matrix in ('ERROR', 'MORE_THAN_ONE_ANSWER'):
        print(matrix)
    else:
        print_matrix(matrix)
    
if __name__ == "__main__":
    main()
