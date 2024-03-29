from utils import Utils, Constants
from algorithms.base_alg import Algorithm
from helpers.time_logger import Time_logger

import numpy as np

np.set_printoptions(precision=8, suppress=True)


class LUGJF(Algorithm):
    def __init__(self, matrix_num: int = 1) -> None:

        super().__init__(matrix_num)
        self.limit = 100
        self.alg_type = Constants.ALG_TYPE_LUGJF
        super().post_init()

        self.b = np.zeros((self.limit, self.limit), np.double)
        self.c = np.zeros((self.limit, self.limit), np.double)

        self.y = np.zeros(self.limit)
        self.x = np.zeros(self.limit)

        self.initial_limit = 10

    def make_cell_one(self, matrix: np.array, answers_vec: np.array, cell_row: int, cell_col: int, last_col: int = -1):

        divider = matrix[cell_row][cell_col]
        if cell_row != cell_col or divider == 1:
            return

        if last_col == -1:
            last_col = self.limit if cell_col < Utils.NMAX else Utils.NMAX
        if divider == 0:
            non_zero_element_index = self.get_first_non_zero_col(
                cell_row, cell_col + 1)
            matrix[cell_row], matrix[non_zero_element_index] = matrix[non_zero_element_index], matrix[cell_row]
            divider = matrix[cell_row][cell_col]

        elif divider != 1:
            for col in range(cell_col, last_col):
                matrix[cell_row][col] /= divider
            answers_vec[cell_row] /= divider
        # self.steps_for_print_step += 1
        # Utils.print_step(self.steps_for_print_step, matrix, answers_vec, cell_row, cell_col, False)

    def calculate_cell(self, matrix: np.array, answers_vec: np.array, cell_row: int, cell_col: int, last_col: int = -1):

        if cell_row == cell_col or matrix[cell_col][cell_col] != 1.0:
            self.make_cell_one(matrix, answers_vec,
                               cell_col, cell_col, last_col)

        if last_col == -1:
            last_col = self.limit if cell_col < Utils.NMAX else Utils.NMAX
        if matrix[cell_row][cell_col] != 0:
            divider = -matrix[cell_row][cell_col]
            for col in range(cell_col, last_col):
                matrix[cell_row][col] += matrix[cell_col][col] * divider
            answers_vec[cell_row] += answers_vec[cell_col] * divider

    def get_first_non_zero_col(self, row: int, first_col: int) -> int:

        last_col = self.limit
        for col in range(first_col, last_col):
            if self.a[row][col] != 0:
                return col
        return -1

    def build_triangle_matrix(self):

        for i in range(self.limit):
            for j in range(self.limit):
                if i <= j:
                    sum_b_c_i = 0

                    for k in range(i):
                        sum_b_c_i += self.b[i, k] * self.c[k, j]
                    self.c[i, j] = self.a[i, j] - sum_b_c_i
                if i >= j:
                    sum_b_c_j = 0
                    for k in range(j):
                        sum_b_c_j += self.b[i, k] * self.c[k, j]
                    self.b[i, j] = (self.a[i, j] - sum_b_c_j) / self.c[j, j]

        # for i in range(self.limit):
        #     for left_lower_col in range(i):
        #         if self.b[i, left_lower_col] != 0:
        #             divider = -self.b[i][left_lower_col]
        #             for inner_col in range(left_lower_col, i):
        #                 self.b[i][inner_col] += self.b[left_lower_col][inner_col] * divider
        #             self.f[i] += self.f[left_lower_col] * divider

        #     if self.b[i, i]:
        #         self.y[i] = self.f[i] / self.b[i, i]

    def calculate_y_using_podstanovka(self):

        for row in range(self.limit):
            s = 0
            for left_lower_col in range(row):
                s += self.b[row][left_lower_col] * self.y[left_lower_col]
            self.y[row] = (self.f[row] - s) / self.b[row][row]

    def solve(self):
        Time_logger.get_instance().start_timer_for_event('SCR matrix division')
        self.build_triangle_matrix()

        print(f'\nwhile-loop begin:')
        print(f'b | f\n')
        Utils.print_mat(self.b, self.f, 5, 6)
        print(f'c | y\n')
        Utils.print_mat(self.c, self.y, 5, 6)
        print()

        self.calculate_y_using_podstanovka()
        Time_logger.get_instance().mark_timestamp_for_event('SCR matrix division')

        d = 1.0
        row = 0

        while True:
            print(f'row: {row}')

            # work with self.c moving row by row starting with last_row to 0

            for cur_row in range(row, -1, -1):
                prev_f_row = -1.0
                cur_f_row = self.y[cur_row]
                for cur_col in range(cur_row, row + 1):
                    calculated_this_step = False
                    # print(
                    #     f'cur_row, cur_col : {cur_row}, {cur_col}, ', end='')
                    initial_c_value = self.c[cur_row, cur_col]

                    if cur_row == cur_col:  # on main diagonal
                        if self.c[cur_row, cur_col] == 1:  # opt
                            # print()
                            continue
                        # for it_col in range(cur_row, row):  # self.limit ?
                        self.make_cell_one(
                            self.c, self.y, cur_row, cur_col, -1)
                        calculated_this_step = True
                    else:
                        if self.c[cur_row, cur_col] == 0:  # opt
                            # print()
                            continue
                        self.calculate_cell(
                            self.c, self.y, cur_row, cur_col, -1)
                        calculated_this_step = True

                    if calculated_this_step:
                        prev_f_row = cur_f_row
                        cur_f_row = self.y[cur_row]
                        d = abs(cur_f_row - prev_f_row)

            # print(f'\nwhile-loop end:')
            # print(f'c | y\n')
            # Utils.print_mat(self.c, self.y, row + 1)
            # print()
            row += 1

            # do-while-emu exit condition
            if d < 1e-10 or row >= self.limit:  # todo: move d to utils
                break

        # print(f'\nwhile-loop end:')
        # print(f'b | f\n')
        # Utils.print_mat(self.b, self.f, 10)
        # print(f'c | y\n')
        # Utils.print_mat(self.c, self.y, 10)
        # print()

        print(f'n: {row}')
        print(f'd: {d}')

        # print(f'b:\n{self.b}')
        # print(f'c:\n{self.c}')
        # print(f'y:\n{self.y}')
        # print(f'f:\n{self.f}')
