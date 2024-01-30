import json
import random

import pygame
from random import choice

RES = WIDTH, HEIGHT = 1202, 902
TILE = 50
cols, rows = WIDTH // TILE, HEIGHT // TILE

pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock()

START_X = 60
START_Y = 85

SHIFT_X = 60
SHIFT_Y = 61
RADIUS = 68

WALLS_THICK = 5

class Maze:
    def __init__(self):
        self.columns = 19
        self.rows = 7
        self.cells_matrix = [[TriangleCell('V' if (i + j) % 2 == 0 else 'A', START_X + SHIFT_X * i, START_Y + 2 * SHIFT_Y * j, i, j) for i in range(self.columns)] for j in range(self.rows)]

    def draw(self):
        for i in range(self.rows):
            for j in range(self.columns):
                self.cells_matrix[i][j].draw()

    def save_maze(self, path):
        data = dict()
        for i in range(self.rows):
            for j in range(self.columns):
                data[f'{i} {j}'] = {
                    'type': self.cells_matrix[i][j].type,
                    'center': (self.cells_matrix[i][j].x, self.cells_matrix[i][j].y),
                    'horizontal': self.cells_matrix[i][j].walls['horizontal'],
                    'left': self.cells_matrix[i][j].walls['left'],
                    'right': self.cells_matrix[i][j].walls['right']
                }
        with open(path, 'w') as outfile:
            json.dump(data, outfile)

    def load_maze(self, path):
        with open(path) as json_file:
            data = json.load(json_file)
            self.cells_matrix.clear()
            self.cells_matrix = [[0 for i in range(self.columns)] for j in range(self.rows)]
            for key, item in data.items():
                i, j = map(int, key.split())
                inner_dict = data[f'{i} {j}']
                walls = {'horizontal': inner_dict['horizontal'], 'right': inner_dict['right'], 'left': inner_dict['left']}
                self.cells_matrix[i][j] = TriangleCell(inner_dict['type'], inner_dict['center'][0], inner_dict['center'][1], i, j, walls)


class TriangleCell:
    def __init__(self, type, x, y, i, j, walls=None):
        self.ind_i = i
        self.ind_j = j

        self.type = type
        # Координаты центра треугольника
        self.x = x
        self.y = y

        self.h_l = None
        self.h_r = None
        self.m = None

        if walls is None:
            self.walls = {'horizontal': 'WALL', 'right': 'WALL', 'left': 'WALL'}
        else:
            self.walls = walls

        if self.type == 'V':
            self.h_l = x - SHIFT_X, y - SHIFT_Y
            self.h_r = x + SHIFT_X, y - SHIFT_Y
            self.m = x, y + SHIFT_Y
        elif self.type == 'A':
            self.h_l = x - SHIFT_X, y + SHIFT_Y
            self.h_r = x + SHIFT_X, y + SHIFT_Y
            self.m = x, y - SHIFT_Y

    def draw(self):
        pygame.draw.polygon(sc, pygame.Color('black'), [self.h_l, self.h_r, self.m])

        if self.walls['horizontal'] == 'WALL':
            pygame.draw.line(sc, pygame.Color('darkorange'), self.h_l, self.h_r, WALLS_THICK)
        elif self.walls['horizontal'] == 'EXIT':
            pygame.draw.line(sc, pygame.Color('green'), self.h_l, self.h_r, WALLS_THICK)
        elif self.walls['horizontal'] == 'EMPTY':
            pygame.draw.line(sc, pygame.Color('grey'), self.h_l, self.h_r, 1)

        if self.walls['right'] == 'WALL':
            pygame.draw.line(sc, pygame.Color('darkorange'), self.m, self.h_r, WALLS_THICK)
        elif self.walls['right'] == 'EXIT':
            pygame.draw.line(sc, pygame.Color('green'), self.m, self.h_r, WALLS_THICK)
        elif self.walls['right'] == 'EMPTY':
            pygame.draw.line(sc, pygame.Color('grey'), self.m, self.h_r, 1)

        if self.walls['left'] == 'WALL':
            pygame.draw.line(sc, pygame.Color('darkorange'), self.m, self.h_l, WALLS_THICK)
        elif self.walls['left'] == 'EXIT':
            pygame.draw.line(sc, pygame.Color('green'), self.m, self.h_l, WALLS_THICK)
        elif self.walls['left'] == 'EMPTY':
            pygame.draw.line(sc, pygame.Color('grey'), self.m, self.h_l, 1)

    def is_touch(self, mouse_x, mouse_y):
        if abs(self.h_r[0] - mouse_x) <= RADIUS and abs(self.h_r[1] - mouse_y) <= RADIUS:
            if abs(self.m[0] - mouse_x) <= RADIUS and abs(self.m[1] - mouse_y) <= RADIUS:
                return 'right'

        if abs(self.h_l[0] - mouse_x) <= RADIUS and abs(self.h_l[1] - mouse_y) <= RADIUS:
            if abs(self.m[0] - mouse_x) <= RADIUS and abs(self.m[1] - mouse_y) <= RADIUS:
                return 'left'

        if abs(self.h_r[0] - mouse_x) <= RADIUS and abs(self.h_r[1] - mouse_y) <= RADIUS:
            if abs(self.h_l[0] - mouse_x) <= RADIUS and abs(self.h_l[1] - mouse_y) <= RADIUS:
                return 'horizontal'

        return None

    def change_wall(self, ch_wall):
        if self.walls[ch_wall] == 'EMPTY':
            self.walls[ch_wall] = 'WALL'
        else:
            self.walls[ch_wall] = 'EMPTY'

    def add_exit(self, ch_wall):
        self.walls[ch_wall] = 'EXIT'

    def break_wall(self, br_wall):
        self.walls[br_wall] = 'EMPTY'

    def break_rand_wall(self):
        ch_set = {'horizontal', 'right', 'left'}

        if self.type == 'V' and self.ind_j == 0 or self.type == 'A' and self.ind_j == 6:
            ch_set.discard('horizontal')
        if self.ind_i == 0:
            ch_set.discard('left')
        if self.ind_i == 18:
            ch_set.discard('right')

        if self.walls['left'] == 'EMPTY':
            ch_set.discard('left')
        if self.walls['right'] == 'EMPTY':
            ch_set.discard('right')
        if self.walls['horizontal'] == 'EMPTY':
            ch_set.discard('horizontal')

        if len(ch_set) != 0:
            br_wall = random.choice(list(ch_set))
            self.walls[br_wall] = 'EMPTY'
            return br_wall
        else:
            return None


class Robot:
    def __init__(self, i, j, maze):
        self.ind_i = i
        self.ind_j = j

        self.maze = maze
        self.lms_cnt = 0
        self.texture = pygame.transform.scale(pygame.image.load('..//media//delrobot.png'), (90, 90))

        self.memory = [[[0 for _ in range(3)] for i in range(self.maze.columns)] for j in range(self.maze.rows)]
        # 0 - горизонтальная стена
        # 1 - левая стена
        # 2 - правая стена

        # 0 - проход не посещен
        # 1 - проход был посещен (одна точка)
        # 2 - проход является тупиком (крест)
        self.cur_path = [(0, 0, 0)] * self.maze.columns * self.maze.rows
        # массив текущего "путя"
        self.tail = 0


    # def chose_wall(self):
    #     i, j = self.cur_path[self.tail]
    #
    #     if self.memory[i][j][0] == 1 and self.memory[i][j][3] == -1:
    #         self.tail += 1
    #         self.cur_path[self.tail] = (i, j - 1)
    #         self.memory[i][j][3] = 1
    #         ans = self.left()
    #     elif self.memory[i][j][1] == 1 and self.memory[i][j][4] == -1:
    #         self.tail += 1
    #         self.cur_path[self.tail] = (i, j + 1)
    #         self.memory[i][j][4] = 1
    #         ans = self.right()
    #     elif self.memory[i][j][2] == 1 and self.memory[i][j][5] == -1:
    #         ans = self.move()
    #         self.tail += 1
    #         if ans == -1:
    #             self.cur_path[self.tail] = (i + 1, j)
    #         else:
    #             self.cur_path[self.tail] = (i - 1, j)
    #         self.memory[i][j][5] = 1
    #     else:
    #         self.tail -= 1
    #
    # def check_walls(self):
    #     i, j = self.ind_i, self.ind_j
    #
    #     if self.memory[i][j][0] == -1:
    #         self.robot_lms()
    #     if self.memory[i][j][1] == -1:
    #         self.robot_lms()
    #     if self.memory[i][j][2] == -1:
    #         ans = self.robot_vert()
    #         if ans == -1 or ans == 1:
    #             self.move()
    #         elif ans == 2:
    #             print("ROBOT WIN")
    #
    # def robot_lms(self):
    #     ans = self.lms()
    #     i, j = self.ind_i, self.ind_j
    #     if (self.lms_cnt - 1) % 2 == 0:
    #         # левая
    #         k = 0
    #         while k != ans:
    #             self.memory[i][j + k][0] = 1
    #             if j + k + 1 < 19:
    #                 self.memory[i][j + k + 1][1] = 1
    #             k += 1
    #         self.memory[i][j + k][0] = 0
    #         if j + k + 1 < 19:
    #             self.memory[i][j + k + 1][1] = 0
    #     else:
    #         # правая
    #         k = 0
    #         while k != ans:
    #             self.memory[i][j - k][0] = 1
    #             if j - k - 1 > -1:
    #                 self.memory[i][j - k - 1][1] = 1
    #             k += 1
    #         self.memory[i][j - k][0] = 0
    #         if j - k - 1 > -1:
    #             self.memory[i][j - k - 1][1] = 0
    #
    # def robot_vert(self):
    #     i, j = self.ind_i, self.ind_j
    #     if (i + j) % 2 == 0:
    #         # V
    #         ans = self.move()
    #         if ans == -1:
    #             print('EXITEXITEXITEXIT')
    #             self.memory[i][j][2] = 2
    #             return 2
    #         elif ans == 1:
    #             self.memory[i + 1][j][2] = 1
    #             self.memory[i][j][2] = 1
    #             return 1
    #         else:
    #             self.memory[i][j][2] = 0
    #             if i - 1 > -1:
    #                 self.memory[i - 1][j][2] = 0
    #             return 0
    #     else:
    #         # A
    #         ans = self.move()
    #         if ans == -1:
    #             print('EXITEXITEXITEXIT')
    #             self.memory[i][j][2] = 2
    #             return 2
    #         elif ans == -1:
    #             self.memory[i - 1][j][2] = 1
    #             self.memory[i][j][2] = 1
    #             return -1
    #         else:
    #             self.memory[i][j][2] = 0
    #             if i + 1 < 7:
    #                 self.memory[i + 1][j][2] = 0
    #             return 0

    def get_coord(self, i, j):
        cur_cell = self.maze.cells_matrix[i][j]
        x, y =  cur_cell.x,  cur_cell.y
        x_hor = x
        y_hor = y - SHIFT_Y if cur_cell.type == 'V' else y + SHIFT_Y

        x_left = x - SHIFT_X // 2
        y_left = y

        x_right = x + SHIFT_X // 2
        y_right = y

        return (x_hor, y_hor), (x_left, y_left), (x_right, y_right)

    def draw(self):
        cur_cell = self.maze.cells_matrix[self.ind_i][self.ind_j]
        if cur_cell.type == 'A':
            pos = cur_cell.x - 45, cur_cell.y - 30
        else:
            pos = cur_cell.x - 45, cur_cell.y - 65

        sc.blit(self.texture, pos)

        for i in range(self.maze.rows):
            for j in range(self.maze.columns):
                hor, l, r = self.get_coord(i, j)
                BALL_RAD = 5
                if int(self.memory[i][j][0]) == 0:
                    pygame.draw.circle(sc, pygame.Color('WHITE'), hor, BALL_RAD)
                elif int(self.memory[i][j][0]) == 1:
                    pygame.draw.circle(sc, pygame.Color('BLUE'), hor, BALL_RAD)
                elif int(self.memory[i][j][0]) == 2:
                    pygame.draw.circle(sc, pygame.Color('RED'), hor, BALL_RAD)
                else:
                    pygame.draw.circle(sc, pygame.Color('YELLOW'), hor, BALL_RAD)

                if int(self.memory[i][j][1]) == 0:
                    pygame.draw.circle(sc, pygame.Color('WHITE'), l, BALL_RAD)
                elif int(self.memory[i][j][1]) == 1:
                    pygame.draw.circle(sc, pygame.Color('BLUE'), l, BALL_RAD)
                elif int(self.memory[i][j][1]) == 2:
                    pygame.draw.circle(sc, pygame.Color('RED'), l, BALL_RAD)

                if int(self.memory[i][j][2]) == 0:
                    pygame.draw.circle(sc, pygame.Color('WHITE'), r, BALL_RAD)
                elif int(self.memory[i][j][2]) == 1:
                    pygame.draw.circle(sc, pygame.Color('BLUE'), r, BALL_RAD)
                elif int(self.memory[i][j][2]) == 2:
                    pygame.draw.circle(sc, pygame.Color('RED'), r, BALL_RAD)

    def stack_empty(self):
        return self.tail == 0

    def stack_push(self, item):
        self.cur_path[self.tail] = item
        self.tail += 1

    def stack_pop(self):
        self.tail -= 1
        return self.cur_path[self.tail]

    def stack_view(self):
        return self.cur_path[self.tail - 1]

    def move_and_mark(self, dir):
        # dir = -1 - вниз
        # dir =  0 - вверх
        # dir =  1 - влево
        # dir =  2 - вправо
        i = self.ind_i
        j = self.ind_j
        if dir == -1:
            self.memory[i][j][0] += 1
            if i + 1 < 7:
                self.memory[i + 1][j][0] += 1
            self.move()
        elif dir == 0:
            self.memory[i][j][0] += 1
            if i - 1 > -1:
                self.memory[i - 1][j][0] += 1
            self.move()
        elif dir == 1:
            self.memory[i][j][1] += 1
            if j - 1 > -1:
                self.memory[i][j - 1][2] += 1
            self.left()
        elif dir == 2:
            self.memory[i][j][2] += 1
            if j + 1 < 19:
                self.memory[i][j + 1][1] += 1
            self.right()

    def step(self):
        i, j = self.ind_i, self.ind_j

        if self.stack_empty():
            dir, ans = self.is_dead_end(-2)
            if ans == 1:
                print("NO EXIT NO EXIT NO EXIT NO EXIT NO EXIT NO EXIT NO EXIT NO EXIT NO EXIT NO EXIT NO EXIT NO EXIT")
                return -1
            else:
                if dir == 0:
                    if self.maze.cells_matrix[i][j].type == 'A':
                        dir = -1
                    else:
                        dir = 0
                    self.stack_push((i, j, 0))
                    self.move_and_mark(dir)
                elif dir == 1:
                    self.stack_push((i, j, 1))
                    self.move_and_mark(dir)
                else:
                    self.stack_push((i, j, 2))
                    self.move_and_mark(dir)
        else:
            prev = self.stack_view()
            if prev[2] == 0:
                pr_wl = 0
            elif prev[2] == 1:
                pr_wl = 2
            else:
                pr_wl = 1

            dir, ans = self.is_dead_end(pr_wl)
            if dir == -1 and ans == -1:
                return -1
            if dir == 10 and ans == 10:
                return 1

            if ans == 0:
                if dir == 0:
                    if self.maze.cells_matrix[i][j].type == 'A':
                        dir = -1
                    else:
                        dir = 0
                    self.stack_push((i, j, 0))
                    self.move_and_mark(dir)
                elif dir == 1:
                    self.stack_push((i, j, 1))
                    self.move_and_mark(dir)
                else:
                    self.stack_push((i, j, 2))
                    self.move_and_mark(dir)
            else:
                if self.tail != 1:
                    self.stack_pop()
                if dir == 0:
                    if self.maze.cells_matrix[i][j].type == 'A':
                        dir = -1
                    else:
                        dir = 0
                self.move_and_mark(dir)
        return 0

    def is_dead_end(self, fr_wall):
        # 0 - горизонтальная стена
        # 1 - левая стена
        # 2 - правая стена

        # 0 - вниз
        # 1 - влево
        # 2 - вправо
        des = self.is_move_enable()
        if des == 10:
            return 10, 10
        i, j = self.ind_i, self.ind_j
        if des == 0:
            return -1, -1
        elif des == 1:
            if fr_wall == 2:
                if self.memory[i][j][0] == 0:
                    return 0, 0
                else:
                    return 2, 1
            else:
                if self.memory[i][j][2] == 0:
                    return 2, 0
                else:
                    return 0, 1
        elif des == 2:
            if fr_wall == 1:
                if self.memory[i][j][0] == 0:
                    return 0, 0
                else:
                    return 1, 1
            else:
                if self.memory[i][j][1] == 0:
                    return 1, 0
                else:
                    return 0, 1
        elif des == 3:
            if fr_wall == 1:
                if self.memory[i][j][2] == 0:
                    return 2, 0
                else:
                    return 1, 1
            else:
                if self.memory[i][j][1] == 0:
                    return 1, 0
                else:
                    return 2, 1
        elif des == 4:
            return (0, 1) if fr_wall != -2 else (0, 0)
        elif des == 5:
            return (1, 1) if fr_wall != -2 else (1, 0)
        elif des == 6:
            return (2, 1) if fr_wall != -2 else (2, 0)
        elif des == 7:
            if fr_wall == 0:
                if self.memory[i][j][1] == 0:
                    return 1, 0
                elif self.memory[i][j][2] == 0:
                    return 2, 0
                elif self.memory[i][j][0] != 2:
                    return 0, 1
                else:
                    return -1, -1
            elif fr_wall == 1:
                if self.memory[i][j][0] == 0:
                    return 0, 0
                elif self.memory[i][j][2] == 0:
                    return 2, 0
                elif self.memory[i][j][1] != 2:
                    return 1, 1
                else:
                    return -1, -1
            else:
                if self.memory[i][j][0] == 0:
                    return 0, 0
                elif self.memory[i][j][1] == 0:
                    return 1, 0
                elif self.memory[i][j][2] != 2:
                    return 2, 1
                else:
                    return -1, -1

    def is_move_enable(self):
        # 10 - нашел выход
        # 0 - все стены
        # 1 - только левая стена
        # 2 - только правая стена
        # 3 - только горизонтальная стена
        # 4 - левая + правая
        # 5 - правая + горизонтальная
        # 6 - горизонтальная + левая
        # 7 - нет стен
        tmp_hor = self.move()
        if tmp_hor != 0:
            self.move()
        tmp_l = self.left()
        if tmp_l != 0:
            self.right()
        tmp_r = self.right()
        if tmp_r != 0:
            self.left()
        if tmp_hor == 2 or tmp_l == 1 or tmp_r == -1:
            return 10
        if tmp_hor != 0 and tmp_l != 0 and tmp_r != 0:
            return 7
        if tmp_hor == 0 and tmp_l == 0 and tmp_r != 0:
            return 6
        if tmp_hor == 0 and tmp_l != 0 and tmp_r == 0:
            return 5
        if tmp_hor != 0 and tmp_l == 0 and tmp_r == 0:
            return 4
        if tmp_hor == 0 and tmp_l != 0 and tmp_r != 0:
            return 3
        if tmp_hor != 0 and tmp_l != 0 and tmp_r == 0:
            return 2
        if tmp_hor != 0 and tmp_l == 0 and tmp_r != 0:
            return 1
        if tmp_hor == 0 and tmp_l == 0 and tmp_r == 0:
            return 0

    def move(self):
        i, j = self.ind_i, self.ind_j
        cur_cell = self.maze.cells_matrix[i][j]
        if cur_cell.type == 'A':
            if cur_cell.walls['horizontal'] == 'EXIT':
                print("FINDEXITFINDEXITFINDEXITFINDEXITFINDEXIT")
                return 2  # нашел выход
            elif cur_cell.walls['horizontal'] == 'EMPTY':
                self.ind_i += 1
                return -1  # переместился вниз
            else:
                return 0  # внизу стена
        elif cur_cell.type == 'V':
            if cur_cell.walls['horizontal'] == 'EXIT':
                print("FINDEXITFINDEXITFINDEXITFINDEXITFINDEXIT")
                return 2  # нашел выход
            elif cur_cell.walls['horizontal'] == 'EMPTY':
                self.ind_i -= 1
                return 1  # переместился вверх
            else:
                return 0  # вверху стена

    def left(self):
        i, j = self.ind_i, self.ind_j
        cur_cell = self.maze.cells_matrix[i][j]
        if cur_cell.walls['left'] == 'EXIT':
            return 1  # нашел выход слева
        elif cur_cell.walls['left'] == 'EMPTY':
            self.ind_j -= 1
            return -1  # переместился влево
        else:
            return 0  # слева стена

    def right(self):
        i, j = self.ind_i, self.ind_j
        cur_cell = self.maze.cells_matrix[i][j]
        if cur_cell.walls['right'] == 'EXIT':
            return -1  # нашел выход справа
        elif cur_cell.walls['right'] == 'EMPTY':
            self.ind_j += 1
            return 1  # переместился вправо
        else:
            return 0  # справа стена

    def lms(self):
        i, j = self.ind_i, self.ind_j
        self.lms_cnt += 1
        if self.lms_cnt % 2 == 0:

            tmp_i = i
            cnt = 1
            cur_wall = self.maze.cells_matrix[tmp_i][j].walls['left']
            while cur_wall == 'EMPTY':
                cnt += 1
                tmp_i -= 1
                cur_wall = self.maze.cells_matrix[tmp_i][j].walls['left']

            if cur_wall == 'EXIT':
                return cnt
            else:
                return -cnt
        else:
            tmp_i = i
            cnt = 1
            cur_wall = self.maze.cells_matrix[tmp_i][j].walls['right']
            while cur_wall == 'EMPTY':
                cnt += 1
                tmp_i += 1
                cur_wall = self.maze.cells_matrix[tmp_i][j].walls['right']

            if cur_wall == 'EXIT':
                return -cnt
            else:
                return cnt


# def main():
#     maze = Maze()
#     file_path = 'maze_2.txt'
#     file_path_load = 'maze_1.txt'
#     robot = Robot(0, 0, maze)
#
#     sc.fill(pygame.Color('darkslategray'))
#     for row in maze.cells_matrix:
#         for kl in row:
#             kl.draw()
#
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 exit()
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_s:
#                     maze.save_maze(f'{file_path}')
#                     print(f'Saved to {file_path}')
#                 if event.key == pygame.K_l:
#                     maze.load_maze(f'{file_path_load}')
#                     print(f'Load from {file_path_load}')
#                     maze.draw()
#
#                 if event.key == pygame.K_UP:
#                     ans = robot.move()
#                     print(f'ANS: {ans}')
#                     maze.draw()
#                     robot.draw()
#
#                     if ans == -1 and maze.cells_matrix[robot.ind_i][robot.ind_j].walls['horizontal'] == 'EXIT':
#                         sc.blit(pygame.image.load('win.jpg'), (500, 250))
#
#                 if event.key == pygame.K_LEFT:
#                     ans = robot.left()
#                     print(f'ANS: {ans}')
#                     maze.draw()
#                     robot.draw()
#
#                 if event.key == pygame.K_RIGHT:
#                     ans = robot.right()
#                     print(f'ANS: {ans}')
#                     maze.draw()
#                     robot.draw()
#
#                 if event.key == pygame.K_p:
#                     ans = robot.step()
#                     maze.draw()
#                     robot.draw()
#                     if ans == 1:
#                         print("WINWINWINWINWIN")
#
#                         #pygame.transform.scale(pygame.image.load('delrobot.png'), (90, 90))
#                         sc.blit(pygame.transform.scale(pygame.image.load('ya_robot.png'), (WIDTH, HEIGHT)), (0, 0))
#                     elif ans == -1:
#                         print("LOSELOSELOSELOSELOSE")
#                         sc.blit(pygame.transform.scale(pygame.image.load('game_over.jpeg'), (WIDTH, HEIGHT)), (0, 0))
#                         #sc.blit(pygame.image.load('game_over.jpeg'), (0, 0))
#
#                 pygame.display.update()
#
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if event.button == 1:
#                     a, b = event.pos
#                     #pygame.draw.circle(sc, pygame.Color('RED'), event.pos, 20)
#
#                     for i in range(maze.rows):
#                         for j in range(maze.columns):
#                             cur_cell = maze.cells_matrix[i][j]
#                             ans = cur_cell.is_touch(a, b)
#                             if ans is not None:
#                                 print(cur_cell.ind_i, cur_cell.ind_j)
#                                 cur_cell.change_wall(ans)
#                                 cur_cell.draw()
#                 if event.button == 2:
#                     a, b = event.pos
#                     for i in range(maze.rows):
#                         for j in range(maze.columns):
#                             cur_cell = maze.cells_matrix[i][j]
#                             ans = cur_cell.is_touch(a, b)
#                             if ans is not None:
#                                 #print(ans)
#                                 cur_cell.add_exit(ans)
#                                 cur_cell.draw()
#
#                 if event.button == 3:
#                     a, b = event.pos
#                     print(a, b)
#                     ind_i = a // SHIFT_X
#                     ind_j = (b - (START_Y - SHIFT_Y)) // (2 * SHIFT_Y)
#                     print(ind_i, ind_j)
#                     robot.ind_i = ind_j
#                     robot.ind_j = ind_i
#                     maze.draw()
#                     robot.draw()
#
#                 pygame.display.update()
#
#         pygame.display.flip()
#         clock.tick(30)
#
#
# if __name__ == '__main__':
#     main()