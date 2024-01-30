import copy
import time

from my_yacc import ParserClass
from errors import *

ROBOT = True

if ROBOT is True:
    from maze_ta.robot_pygame import *


class Variable:
    def __init__(self, v_type, v_name, v_value=None):
        if v_type == 'short int':
            v_type = 'short'
        self.type = v_type
        self.name = v_name
        if v_value is None:
            self.value = 0
        else:
            if self.type == 'bool':
                self.value = v_value
            elif self.type == 'short' and isinstance(v_value, str):
                if v_value[0] == 's':
                    self.value = int(v_value[1:])
                else:  # if var = -s1
                    v_value = v_value[0] + v_value[2:]
                    self.value = int(v_value)
            else:
                self.value = int(v_value)

    def __repr__(self):
        return f'{self.type} {self.name} = {self.value}'


class ArrVariable:
    def __init__(self, v_type, v_name, v_scope, v_array=None):
        if v_type == 'short int':
            v_type = 'short'
        self.type = v_type
        self.name = v_name
        self.scope = v_scope
        if v_array is None:
            self.array = []
            nuls = 0
            for i in list(v_scope.values()):
                nuls += i
            for j in range(nuls):
                self.array.append(0)
        else:
            self.array = v_array

    def __repr__(self):
        scopes = list(self.scope.values())
        return f'{self.type} {self.name}{scopes} = {self.array}'


"""  SIZES:
    sizeof(int) = 8     
    sizeof(short) = 2       -128 <= short <= 127
    sizeof(bool) = 1 
"""


class TypeConverser:
    def __init__(self):
        pass

    def converse(self, var, vartype):
        if vartype == var.type:
            return var
        elif vartype == 'bool':
            return self.sint_to_bool(var)
        elif vartype == 'int':
            if var.type == 'short':
                return self.short_to_int(var)
            elif var.type == 'bool':
                return self.bool_to_int(var)
        elif vartype == 'short':
            if var.type == 'int':
                return self.int_to_short(var)
            elif var.type == 'bool':
                return self.bool_to_short(var)

    def sint_to_bool(self, var):
        if isinstance(var, Variable):
            if var.value > 0:
                return Variable('bool', '', 'true')
            elif var.value < 0:
                return Variable('bool', '', 'false')
            else:
                return Variable('bool', '', 'undefined')
        else:
            arr = copy.deepcopy(var.array)
            for i in range(len(var.array)):
                if var.array[i][0] == 's':
                    if int(var.array[i][1:]) > 0:
                        arr[i] = 'true'
                    else:
                        arr[i] = 'undefined'
                elif var.array[i][0] == '-' and var.array[i][1] == 's':
                    if int(var.array[i][2:]) > 0:
                        arr[i] = 'false'
                    else:
                        arr[i] = 'undefined'
                else:
                    if int(var.array[i]) > 0:
                        arr[i] = 'true'
                    elif int(var.array[i]) < 0:
                        arr[i] = 'false'
                    else:
                        arr[i] = 'undefined'
            return ArrVariable('bool', '', var.scope, arr)

    def int_to_short(self, var):
        if isinstance(var, Variable):
            return Variable('short', '', var.value)
        else:
            return ArrVariable('short', '', var.scope, var.array)

    def short_to_int(self, var):
        if isinstance(var, Variable):
            if isinstance(var.value, int):
                return Variable('int', '', var.value)
            else:
                return Variable('int', '', var.value[1:])
        else:
            arr = copy.deepcopy(var.array)
            for i in range(len(var.array)):
                if var.array[i][0] == 's':
                    arr[i] = var.array[i][1:]
                elif var.array[i][0] == '-' and var.array[i][1] == 's':
                    arr[i] = '-' + var.array[i][2:]
                else:
                    arr[i] = var.array[i]
            return ArrVariable('int', '', var.scope, arr)

    def bool_to_int(self, var):
        if isinstance(var, Variable):
            if var.value == 'true':
                return Variable('int', '', 1)
            elif var.value == 'false':
                return Variable('int', '', -1)
            else:
                return Variable('int', '', 0)
        else:
            arr = copy.deepcopy(var.array)
            for i in range(len(var.array)):
                if var.array[i] == 'true':
                    arr[i] = '1'
                elif var.array[i] == 'false':
                    arr[i] = '-1'
                else:
                    arr[i] = '0'
            return ArrVariable('int', '', var.scope, arr)

    def bool_to_short(self, var):
        if isinstance(var, Variable):
            if var.value == 'true':
                return Variable('short', '', 1)
            elif var.value == 'false':
                return Variable('short', '', -1)
            else:
                return Variable('short', '', 0)
        else:
            arr = copy.deepcopy(var.array)
            for i in range(len(var.array)):
                if var.array[i] == 'true':
                    arr[i] = '1'
                elif var.array[i] == 'false':
                    arr[i] = '-1'
                else:
                    arr[i] = '0'
            return ArrVariable('short', '', var.scope, arr)


class Interpreter:
    def __init__(self, program=None, robot=False):
        self.parser = ParserClass()
        self.converse = TypeConverser()
        self.error = ErrorHandler()
        self.scope = 0
        self.symbol_table = [dict()]
        self.er_types = {
            'UnexpectedError': 0,
            'WorkLackError': 1,
            'IndexError': 2,
            'RedeclarationError': 3,
            'UndeclaredVariableError': 4,
            'ArrayDeclarationError': 5,
            'ArrayToVariableError': 6,
            'UndeclaredFunctionError': 7,
            'WrongParameterError': 8
        }
        self.tree = None
        self.funcs = None
        self.correct = None
        self.program = program

        self.steps = 0
        self.exit = False

        if robot:
            self.maze = Maze()
            self.maze.load_maze('..//maze_ta//maze_1.txt')
            self.robot = Robot(6, 17, self.maze)
            self.draw_state()
        else:
            self.robot = None

    def draw_state(self):
        sc.fill(pygame.Color('darkslategray'))
        self.maze.draw()
        self.robot.draw()
        pygame.display.flip()
        clock.tick(30)
        time.sleep(0.25)

    def draw_good(self):
        sc.blit(pygame.transform.scale(pygame.image.load('..//media//ya_robot.png'), (WIDTH, HEIGHT)), (0, 0))
        pygame.display.flip()
        clock.tick(30)
        time.sleep(10)

    def draw_bad(self):
        sc.blit(pygame.transform.scale(pygame.image.load('..//media//game_over.jpeg'), (WIDTH, HEIGHT)), (0, 0))
        pygame.display.flip()
        clock.tick(30)
        time.sleep(10)

    def next_step(self):
        self.robot.step()
        self.draw_state()


    def interpret(self):
        self.tree, self.funcs, self.correct = self.parser.parse(self.program)
        #self.tree.graphviz_tree()
        if self.correct:
            if 'work' not in self.funcs.keys():
                self.error.call(self.er_types['WorkLackError'])
                return

            self.interp_node(self.funcs['work'].child['body'])
            return True
        else:
            sys.stderr.write(f'Incorrect input file\n')

    def interp_node(self, node):
        if node is None:
            return
        elif node.type == 'NL':
            pass
        elif node.type == 'EOS':
            pass
        elif node.type == 'error':
            self.error.call(self.er_types['UnexpectedError'], node)
        elif node.type == 'program':
            self.interp_node(node.child)
        elif node.type == 'group_stat':
            self.interp_node(node.child[1])
        elif node.type == 'statement list':
            self.interp_node(node.child[0])
            self.interp_node(node.child[1])
        # statement
        elif node.type == 'declaration':
            decl_type = node.child[0]
            decl_child = node.child[1]
            try:
                if decl_child.type == 'var_list':
                    while decl_child.type == 'var_list':
                        self.declaration(decl_type, decl_child.child[0])
                        if decl_child.child[1].type != 'var_list':
                            self.declaration(decl_type, decl_child.child[1])
                        decl_child = decl_child.child[1]
                else:
                    self.declaration(decl_type, decl_child)
            except RedeclarationError:
                self.error.call(self.er_types['RedeclarationError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
            except ArrayDeclarationError:
                self.error.call(self.er_types['ArrayDeclarationError'], node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)

        elif node.type == 'assignment':
            try:
                self.assign_variable(node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
            except UndeclaredVariableError:
                self.error.call(self.er_types['UndeclaredVariableError'], node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)
            except ArrayToVariableError:
                self.error.call(self.er_types['ArrayToVariableError'], node)
        elif node.type == 'assignment array':
            self.error.call(self.er_types['UnexpectedError'], node)
        elif node.type == 'variable':
            try:
                return self._variable(node)
            except UndeclaredVariableError:
                self.error.call(self.er_types['UndeclaredVariableError'], node)
        elif node.type == 'arr variable':
            try:
                return self._arr_variable(node)
            except UndeclaredVariableError:
                self.error.call(self.er_types['UndeclaredVariableError'], node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
        elif node.type == 'digit':
            if node.value[0] == 's':
                return Variable('short', '', node.value)
            else:
                return Variable('int', '', node.value)
        elif node.type == 'bool':
            return Variable('bool', '', node.value)
        elif node.type == 'EOS' or node.type == 'bracket':
            return node.value
        elif node.type == 'sizeof':
            try:
                return Variable('int', '', self._sizeof(node))
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)
        elif node.type == 'calculation':
            return self._calculation(node)
        elif node.type == 'expression':
            return self.interp_node(node.child[1])
        elif node.type == 'if_then':
            try:
                self.func_if_then(node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
        elif node.type == 'if_th_el':
            try:
                self.func_if_th_el(node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)
        elif node.type == 'do_while':
            try:
                self.func_while(node)
            except IndexError:
                self.error.call(self.er_types['IndexError'], node)

        elif node.type == 'function':
            pass
        elif node.type == 'param':
            try:
                return self.combine_param(node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)
        elif node.type == 'call_func':
            try:
                return self.call_function(node)
            except UndeclaredFunctionError:
                self.error.call(self.er_types['UndeclaredFunctionError'], node)
            except WrongParameterError:
                self.error.call(self.er_types['WrongParameterError'], node)

        elif node.type == 'command':
            # if self.robot is None:
            #     self.error.call(self.er_types['RobotError'], node)
            #     self.correct = False
            #     return 0
            if node.value == 'lms':
                return ArrVariable('int', '', 2, [self.robot.ind_i, self.robot.ind_j])
            elif node.value == 'move':
                x = self.robot.move()
                if x == 2:
                    self.draw_good()
                    exit()
                return Variable('int', '', x)
            elif node.value == 'left':
                x = self.robot.left()
                if x == 1:
                    self.draw_good()
                    exit()
                return Variable('int', '', x)
            elif node.value == 'right':
                x = self.robot.right()
                if x == -1:
                    self.draw_good()
                    exit()
                return Variable('int', '', x)

        # else:
        #     print('Not all nodes checked')

    # CHECK NAME IN SYMBOLTABLE
    def get_name(self, name):
        res = None
        length = len(name)
        for var in sorted(self.symbol_table[self.scope].keys()):
            #if var[:length] == name:
            if var == name:
                if res is None:
                    res = var
                    if len(var) == len(name):
                        return res
                else:
                    raise NameError
        return res

    # CALCULATION
    def _calculation(self, node):
        first_term = copy.deepcopy(self.interp_node(node.child[0]))
        second_term = copy.deepcopy(self.interp_node(node.child[1]))
        if node.value == 'add':
            return self._add(first_term, second_term)
        if node.value == 'sub':
            return self._sub(first_term, second_term)
        if node.value == 'and':
            return self._and(first_term, second_term)
        if node.value == 'or':
            return self._or(first_term, second_term)
        if node.value == 'not or':
            return self._not_or(first_term, second_term)
        if node.value == 'not and':
            return self._not_and(first_term, second_term)
        elif node.value == 'first smaller' or node.value == 'second larger':
            return self._first_smaller(first_term, second_term)
        elif node.value == 'first larger' or node.value == 'second smaller':
            return self._first_larger(first_term, second_term)

    def _add(self, first, second):
        if first.type == 'bool':
            if second.type == 'short':
                self.converse.converse(first, 'short')
            else:
                self.converse.converse(first, 'int')
        if second.type == 'bool':
            if first.type == 'short':
                self.converse.converse(second, 'short')
            else:
                self.converse.converse(second, 'int')
        elif first.type == 'short' and second.type == 'int':
            self.converse.converse(first, 'int')
        elif first.type == 'int' and second.type == 'short':
            self.converse.converse(second, 'int')
        return Variable('int', 'res', first.value + second.value)

    def _sub(self, first, second):
        if first.type == 'bool':
            if second.type == 'short':
                self.converse.converse(first, 'short')
            else:
                self.converse.converse(first, 'int')
        if second.type == 'bool':
            if first.type == 'short':
                self.converse.converse(second, 'short')
            else:
                self.converse.converse(second, 'int')
        elif first.type == 'short' and second.type == 'int':
            self.converse.converse(first, 'int')
        elif first.type == 'int' and second.type == 'short':
            self.converse.converse(second, 'int')
        return Variable('int', 'res', first.value - second.value)

    def _first_smaller(self, first, second):
        if first.type == 'bool':
            first = self.converse.converse(first, 'int')
        if second.type == 'bool':
            second = self.converse.converse(second, 'int')
        if first.value > second.value:
            return Variable('bool', 'res', 'false')
        elif first.value < second.value:
            return Variable('bool', 'res', 'true')
        else:
            return Variable('bool', 'res', 'undefined')

    def _first_larger(self, first, second):
        if first.type == 'bool':
            first = self.converse.converse(first, 'int')
        if second.type == 'bool':
            second = self.converse.converse(second, 'int')
        if first.value > second.value:
            return Variable('bool', 'res', 'true')
        elif first.value < second.value:
            return Variable('bool', 'res', 'false')
        else:
            return Variable('bool', 'res', 'undefined')

    def _and(self, first, second):
        if first.type != 'bool':
            first = self.converse.converse(first, 'bool')
        if second.type != 'bool':
            second = self.converse.converse(second, 'bool')
        if first.value == 'true' and second.value == 'true':
            return Variable('bool', 'res', 'true')
        elif first.value == 'true' and second.value == 'false':
            return Variable('bool', 'res', 'false')
        elif first.value == 'true' and second.value == 'undefined':
            return Variable('bool', 'res', 'undefined')
        elif first.value == 'false' and second.value == 'true':
            return Variable('bool', 'res', 'false')
        elif first.value == 'false' and second.value == 'false':
            return Variable('bool', 'res', 'false')
        elif first.value == 'false' and second.value == 'undefined':
            return Variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'true':
            return Variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'false':
            return Variable('bool', 'res', 'false')
        elif first.value == 'undefined' and second.value == 'undefined':
            return Variable('bool', 'res', 'undefined')

    def _or(self, first, second):
        if first.type != 'bool':
            first = self.converse.converse(first, 'bool')
        if second.type != 'bool':
            second = self.converse.converse(second, 'bool')
        if first.value == 'true' or second.value == 'true':
            return Variable('bool', 'res', 'true')
        elif first.value == 'false' and second.value == 'false':
            return Variable('bool', 'res', 'false')
        elif first.value == 'false' and second.value == 'undefined':
            return Variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'false':
            return Variable('bool', 'res', 'undefined')
        elif first.value == 'undefined' and second.value == 'undefined':
            return Variable('bool', 'res', 'undefined')

    def _not_or(self, first, second):
        var = self._or(first, second)
        if var.value == 'true':
            var.value = 'false'
        elif var.value == 'false':
            var.value = 'true'
        return var

    def _not_and(self, first, second):
        var = self._and(first, second)
        if var.value == 'true':
            var.value = 'false'
        elif var.value == 'false':
            var.value = 'true'
        return var

    def _variable(self, node):
        var = self.get_name(node.value)
        if var is None:
            raise UndeclaredVariableError
        else:
            return self.symbol_table[self.scope][var]

    def _arr_variable(self, node):
        name = self.get_name(node.value)
        if name is None:
            raise UndeclaredVariableError
        var = self.symbol_table[self.scope][name]
        i = self.get_el_index(node, var)
        # val = var.array[i]
        # return self.symbol_table[self.scope][node.value].array[i]
        type_var = var.type
        new_var = Variable(type_var, name + str(i), self.symbol_table[self.scope][name].array[i])
        return new_var

    def get_el_index(self, node, var):
        ind = []
        ind = self.get_var_indexes(node, ind)
        if len(list(var.scope.values())) != len(ind):
            raise IndexError
        for i in range(len(ind)):
            if ind[i] > var.scope[i] - 1 or ind[i] < 0:
                raise IndexError
        if len(ind) == 1:
            return ind[0]
        scp = list(var.scope.values())

        if len(ind) == 3:
            return ind[2] + scp[2] * (ind[1] + scp[1] * ind[0])

        if len(ind) == 2:
            return ind[1] + scp[1] * ind[0]

        # while i < len(ind):
        #     sc *= scp[i]
        #     res += ind[i] * sc
        #     i += 1
        # return res

    def get_var_indexes(self, node, ind):
        if isinstance(node.child, list) and len(node.child) > 0:
            index = self.interp_node(node.child[0])
            if isinstance(index, ArrVariable):
                raise IndexError
            index = copy.deepcopy(self.converse.converse(index, 'int'))
            if index.value < 0:
                raise IndexError
            ind.append(index.value)
            ind = self.get_var_indexes(node.child[1], ind)
        elif node.type != 'index' and node.type != 'arr variable':
            index = self.interp_node(node)
            if isinstance(index, ArrVariable):
                raise
            index = copy.deepcopy(self.converse.converse(index, 'int'))
            if index.value < 0:
                raise IndexError
            ind.append(index.value)
        else:
            ind = self.get_var_indexes(node.child, ind)
        return ind

    def _sizeof(self, node):
        if node.child.type == 'type':
            tip = node.child.value
            return self.sizeof_type(tip)
        else:
            var = self.interp_node(node.child)
            if isinstance(var, ArrVariable):
                raise WrongParameterError
            return self.sizeof_type(var.type)

    def sizeof_type(self, type):
        if type == 'short' or type == 'short int':
            return 2
        elif type == 'int':
            return 8
        else:
            return 1

    def declaration(self, type, node):
        if node.type == 'var_list':
            for child in node.child:
                self.declaration(type, child)
        if type.type == 'arr':
            if node.type == 'variable':
                raise ArrayDeclarationError
            arr_scope = self._arr_scope(type, 1)  # counting vector of
            arr_type = self._arr_type(type)
            if node.type == 'arr variable':
                if node.value in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                index_scope = self._index_scope(node.child, 1)
                if index_scope != arr_scope:
                    raise ArrayDeclarationError
                arr_indexes = {}
                arr_indexes = self.get_indexes(node.child, arr_indexes, 0)
                var = ArrVariable(arr_type, node.value, arr_indexes)
                self.symbol_table[self.scope][node.value] = var
            elif node.type == 'var_list':
                for ch in node.child:
                    self.declaration(type, ch)
            elif node.type == 'assignment':
                raise ArrayDeclarationError
            elif node.type == 'assignment array':
                var_ch = node.child[0]
                expr_ch = node.child[1]
                arr_name = var_ch.value
                if arr_name in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                if var_ch.type == 'arr variable':
                    index_scope = self._index_scope(var_ch.child, 1)
                    if index_scope != arr_scope:
                        raise ArrayDeclarationError
                    arr_indexes = {}
                    arr_indexes = self.get_indexes(var_ch.child, arr_indexes, 0)
                    arr_values = self.get_arr_values(expr_ch, arr_type, arr_indexes)
                    amount_items = self.count_items(arr_indexes)
                    if amount_items != len(arr_values):
                        raise ArrayDeclarationError
                    if index_scope != len(arr_indexes.keys()):
                        raise ArrayDeclarationError
                    var = ArrVariable(arr_type, arr_name, arr_indexes, arr_values)
                    if var is not None:
                        self.symbol_table[self.scope][arr_name] = var
                elif var_ch.type == 'variable':
                    arr_indexes = {}
                    for i in range(arr_scope):
                        arr_indexes[i] = -1
                    arr_values = self.get_arr_values(expr_ch, arr_type, arr_indexes)
                    for i in arr_indexes.values():
                        if i == -1:
                            raise ArrayDeclarationError
                    var = ArrVariable(arr_type, arr_name, arr_indexes, arr_values)
                    if var is not None:
                        self.symbol_table[self.scope][arr_name] = var

        else:  # if type.type == 'type'
            if node.type == 'variable':
                if node.value in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                else:
                    self.symbol_table[self.scope][node.value] = Variable(type.value, node.value)
            elif node.type == 'assignment array':
                raise ArrayDeclarationError
            else:  # if node.type == 'assignment'
                var = node.child[0].value
                if var in self.symbol_table[self.scope].keys() or node.value in self.funcs:
                    raise RedeclarationError
                if node.child[0].type != 'arr variable':
                    expr = self.interp_node(node.child[1])
                    if expr is not None:
                        expr = self.converse.converse(expr, type.value)
                        self.symbol_table[self.scope][var] = Variable(type.value, var, expr.value)

    def _arr_scope(self, node, i):
        if node.child.type == 'type':
            return i
        else:
            return self._arr_scope(node.child, i + 1)

    def _index_scope(self, node, i):
        if isinstance(node.child, list):
            return self._index_scope(node.child[1], i + 1)
        else:
            return i

    def _arr_type(self, node):
        if node.type == 'type':
            return node.value
        else:
            return self._arr_type(node.child)

    def get_indexes(self, node, indexes, layer):
        if isinstance(node.child, list):
            var = self.interp_node(node.child[0])
            if isinstance(var, ArrVariable):
                raise IndexError
            var = copy.deepcopy(self.converse.converse(var, 'int'))
            if var.value < 0:
                raise IndexError
            indexes[layer] = var.value
            return self.get_indexes(node.child[1], indexes, layer + 1)
        else:
            var = self.interp_node(node.child)
            if isinstance(var, ArrVariable):
                raise IndexError
            var = copy.deepcopy(self.converse.converse(var, 'int'))
            if var.value < 0:
                raise IndexError
            indexes[layer] = var.value
            return indexes

    def get_arr_values(self, node, type, indexes):
        arr = []
        if node.type == 'array_comma':
            raise ArrayDeclarationError
        else:
            self.get_arr_next(node.child, type, arr, indexes, 0, 0)
        return arr

    def get_arr_next(self, node, type, arr, indexes, lvl, amount):
        if node.type == 'array_comma':
            amount += 1
            self.get_arr_next(node.child[0], type, arr, indexes, lvl, amount)
            amount = self.get_arr_next(node.child[1], type, arr, indexes, lvl, amount)
            if indexes[lvl] is None:
                raise ArrayDeclarationError
            if indexes[lvl] == -1:
                indexes[lvl] = amount+1
            else:
                if indexes[lvl] != amount+1:
                    raise ArrayDeclarationError
        elif node.type == 'array_lvl':
            self.get_arr_next(node.child, type, arr, indexes, lvl+1, 0)
        else:
            st = len(arr)
            self.get_arr_const(node, type, arr)
            things = len(arr) - st
            if indexes[lvl] is None:
                raise ArrayDeclarationError
            if indexes[lvl] == -1:
                indexes[lvl] = things
            else:
                if indexes[lvl] != things:
                    raise ArrayDeclarationError
        return amount

    def get_arr_const(self, node, type, arr):
        if node.type == 'array item':
            arr.append(self.get_const(node.child[0], type))
            self.get_arr_const(node.child[1], type, arr)
        else:
            arr.append(self.get_const(node, type))

    def get_const(self, node, type):
        if node.type == 'bool':
            if type != 'bool':
                raise ArrayDeclarationError
            return node.value
        elif node.type == 'digit':
            if node.value[0] == 's' and type == 'int':
                raise ArrayDeclarationError
            return node.value
        elif node.type == 'sizeof':
            if type == 'bool':
                raise ArrayDeclarationError
            return self._sizeof(node)

    def count_items(self, ind):
        sum = 1
        for i in list(ind.values()):
            sum = sum * i
        return sum

    def assign_variable(self, node):
        var = node.child[0]
        if var.type == 'variable':
            name = self.get_name(var.value)
            if name is None:
                raise UndeclaredVariableError
            expr = self.interp_node(node.child[1])
            variab = self.symbol_table[self.scope][name]
            if expr is None:
                return
            if expr.type != variab.type:
                expr = self.converse.converse(expr, variab.type)
            if self.robot is None:
                if isinstance(variab, ArrVariable) and isinstance(expr, ArrVariable):
                    if variab.scope != expr.scope:
                        raise IndexError
                    self.symbol_table[self.scope][name].array = expr.array
                elif isinstance(variab, Variable) and isinstance(expr, Variable):
                    self.symbol_table[self.scope][name].value = expr.value
                else:
                    raise ArrayToVariableError
            else:
                if isinstance(variab, ArrVariable):
                    self.symbol_table[self.scope][name].array = expr.array
                else:
                    self.symbol_table[self.scope][name].value = expr.value
            # if isinstance(variab, variable):
            #     if isinstance(expr, variable):
            #         self.symbol_table[self.scope][name].value = expr.value
            #     else:
            #         raise ArrayToVariableError
            # else:
            #     if isinstance(expr, ArrVariable):
            #         self.symbol_table[self.scope][name].array = expr.array
            #     else:
            #         raise ArrayToVariableError
        elif var.type == 'arr variable':
            name = self.get_name(var.value)
            if name is None:
                self.error.call(self.er_types['UndeclaredVariableError'], node)
                raise UndeclaredVariableError
            expr = self.interp_node(node.child[1])
            if expr is not None:
                var_class = self.symbol_table[self.scope][name]
                if expr.type != var_class.type:
                    expr = self.converse.converse(expr, var_class.type)
                ind = self.get_el_index(var, var_class)
                self.symbol_table[self.scope][var_class.name].array[ind] = str(expr.value)

    def func_if_then(self, node):
        condition = self.interp_node(node.child['condition'])
        condition = self.converse.converse(condition, 'bool').value
        if condition == 'true':
            self.interp_node(node.child['body'])

    def func_if_th_el(self, node):
        condition = self.interp_node(node.child['condition'])
        condition = self.converse.converse(condition, 'bool').value
        if condition == 'true':
            self.interp_node(node.child['body_1'])
        else:
            self.interp_node(node.child['body_2'])

    def func_while(self, node):
        try:
            while self.converse.converse(self.interp_node(node.child['condition']), 'bool').value == 'true':
                self.interp_node(node.child['body'])
        except IndexError:
            self.error.call(self.er_types['IndexError'], node)
        except UndeclaredVariableError:
            self.error.call(self.er_types['UndeclaredVariableError'], node)
        except RedeclarationError:
            self.error.call(self.er_types['RedeclarationError'], node)

    def call_function(self, node):
        name = node.value
        if self.scope > 100:
            self.scope = -1
            raise RecursionError
        if name not in self.funcs.keys():
            raise UndeclaredFunctionError

        if name == "step":
            wtf = 0
            for i in range(7):
                for j in range(19):
                    for k in range(3):
                        self.robot.memory[i][j][k] = self.symbol_table[0]['memory'].array[wtf]
                        wtf += 1
            i = self.robot.ind_i
            j = self.robot.ind_j
            if (int(self.robot.memory[i][j][0]) > 1 or self.robot.maze.cells_matrix[i][j].walls['horizontal'] == 'WALL') \
                    and (int(self.robot.memory[i][j][1]) > 1 or self.robot.maze.cells_matrix[i][j].walls['left'] == 'WALL') \
                    and (int(self.robot.memory[i][j][2]) > 1 or self.robot.maze.cells_matrix[i][j].walls['right'] == 'WALL'):
                self.draw_bad()
                exit()



            # print('STEP')
            # print(self.symbol_table[0]['tmpee'])
            # if len(self.symbol_table) >= 2:
            #     print(self.symbol_table[1]['flag'])
            self.draw_state()



        param = node.child
        input_param = []
        change_value = []
        try:
            while param is not None:
                if param.type == 'func_param':
                    if param.value == 'none':
                        input_param = []
                        break
                    else:
                        input_param.append(self.interp_node(param.child[1]))
                        if param.child[1].type == 'arr variable':
                            change_value.append(len(input_param) - 1)
                        param = param.child[0]
                else:
                    input_param.append(self.interp_node(param))
                    if param.type == 'arr variable':
                        change_value.append(len(input_param) - 1)
                    break
            input_param.reverse()
            for i in range(len(change_value)):
                change_value[i] = -change_value[i] - 1
        except IndexError:
            self.error.call(self.er_types['IndexError'], node)
        self.scope += 1
        self.symbol_table.append(dict())
        func_param = []
        node_param = self.funcs[name].child['parameters']
        func_param = self.get_parameter(node_param)
        if len(func_param) != len(input_param):
            raise WrongParameterError
        for i in range(len(input_param)):
            self.set_param(input_param[i], func_param[i])
        for par in func_param:
            self.symbol_table[self.scope][par.name] = par
        self.interp_node(self.funcs[name].child['body'])
        result = copy.deepcopy(self.interp_node(self.funcs[name].child['return']))
        self.symbol_table.pop()
        self.scope -= 1
        for i in range(len(input_param)):
            name = input_param[i].name
            input_param[i] = self.converse.converse(func_param[i], input_param[i].type)
            input_param[i].name = name
        for p in change_value:
            par = input_param[p]
            arr_type = self.symbol_table[self.scope][par.name[:-1]].type
            if par.type != arr_type:
                par = self.converse.converse(par, arr_type)
            self.symbol_table[self.scope][par.name[:-1]].array[int(par.name[-1])] = str(par.value)
            input_param[p] = None
            func_param[p] = None
            for var in input_param:
                if var is not None:
                    self.symbol_table[self.scope][var.name] = var
        return result

    def get_parameter(self, node):
        if node.type == 'param_none':
            return []
        param = []
        while isinstance(node.child, list):
            if node.type == 'param_arr':
                nhd = self.interp_node(node.child[0])
                if node.child[0].type != 'param_arr':
                    param.append(nhd)
                param.append(self.interp_node(node.child[1]))
            elif node.type == 'param':
                param.append(self.combine_param(node))
            if len(node.child) == 0 or node.child[0].type == 'param':
                break
            node = node.child[0]
        param.reverse()
        if len(param) > 1:
            tmp = param[0]
            param[0] = param[1]
            param[1] = tmp
        return param

    def combine_param(self, node):
        type_node = node.child[0]
        ch_node = node.child[1]
        if ch_node.type == 'arr variable':
            raise WrongParameterError
        if type_node.type == 'type':
            type = type_node.value
            return Variable(type, ch_node.value)

        else:  # type_node.type == 'arr':
            arr_scope = self._arr_scope(type_node, 1)
            arr_type = self._arr_type(type_node)
            scope = {}
            for i in range(arr_scope):
                scope[i] = 0
            return ArrVariable(arr_type, ch_node.value, scope)

    def set_param(self, input, func):
        if isinstance(input, ArrVariable) and isinstance(func, ArrVariable):
            t = self.converse.converse(input, func.type)
            func.array = t.array
            func.scope = t.scope
        elif isinstance(input, Variable) and isinstance(func, Variable):
            t = self.converse.converse(input, func.type)
            func.value = t.value
        else:
            raise WrongParameterError




def main():
    #f = open("error_file.txt")
    f = open("..//language//robot.txt")
    #f = open("..//language//test_prog.txt")
    prog = f.read().lower()
    i = Interpreter(program=prog, robot=ROBOT)

    res = i.interpret()
    if res:
        print('Variables:')
        for symbol_table in i.symbol_table:
            for k, v in symbol_table.items():
                print(v)
    else:
        print('Error, PROG IS DEAD')
    f.close()


if __name__ == '__main__':
    main()