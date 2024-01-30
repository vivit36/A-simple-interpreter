import sys
import ply.yacc as yacc
from my_flex import LexerClass
from syntax_tree import Node
from ply.lex import LexError


# Парсер
class ParserClass:
    tokens = LexerClass.tokens

    def __init__(self):
        self.lexer = LexerClass()
        self.parser = yacc.yacc(module=self, optimize=1, debug=False, write_tables=False)
        self.flag = False
        self.func = dict()
        self.correct = True

    def parse(self, s):
        try:
            res = self.parser.parse(s)
            return res, self.func, self.correct
        except LexError:
            sys.stderr.write(f'Illegal token {s}\n')

    def p_program(self, p):
        """program : stat_list"""
        p[0] = Node('program', ch=p[1], no=p.lineno(1))

    def p_stat_group(self, p):
        """stat_group : BEGIN NL stat_list END NL
                      | statement"""
        if p[1] == 'begin':
            p[1] = Node('border', val=p[1], no=p.lineno(1))
            p[4] = Node('border', val=p[4], no=p.lineno(1))
            p[0] = Node('group_stat', ch=[p[1], p[3], p[4]], no=p.lineno(2)+1)
        else:
            p[0] = p[1]

    def p_stat_list(self, p):
        """stat_list : stat_list statement
                     | statement
                     | NL"""
        if len(p) == 3:
            p[0] = Node('statement list', ch=[p[1], p[2]], no=p.lineno(1))
        else:
            if p[0] != '\n':
                p[0] = p[1]
            else:
                p[0] = Node('NL', no=p.lineno(1))

    def p_statement(self, p):
        """statement : declaration SEMICOLON NL
                     | assignment SEMICOLON NL
                     | sizeof SEMICOLON NL
                     | while
                     | if
                     | function
                     | callfunc SEMICOLON NL
                     | command SEMICOLON NL
                     | SEMICOLON NL"""
        if len(p) == 4 or len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('EOS', no=p.lineno(1))

    def p_declaration(self, p):
        """declaration : type var_list"""
        p[0] = Node('declaration', ch=[p[1], p[2]], no=p.lineno(1))

    def p_var_list(self, p):
        """var_list : variable
                    | assignment
                    | var_list COMMA var_list """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('var_list', ch=[p[1], p[3]], no=p.lineno(2))

    def p_assignment(self, p):
        """assignment : variable SET expr"""
        if len(p) == 4:
            p[0] = Node('assignment', val=p[2], ch=[p[1], p[3]], no=p.lineno(2))
        else:
            p[0] = Node('assignment array', val=p[2], ch=[p[1], p[4]], no=p.lineno(2))

    def p_ass_array(self, p):
        """assignment : variable SET arr_set"""
        p[0] = Node('assignment array', val=p[2], ch=[p[1], p[3]], no=p.lineno(2))

    def p_ass_error(self, p):
        """assignment : variable SET error"""
        p[0] = Node('error', val='Wrong assignment', ch=p[1], no=p.lineno(2))
        sys.stderr.write(f'>>> Wrong assignment\n')

    def p_type(self, p):
        """type : INT
                | SHORT INT
                | SHORT
                | BOOL"""
        if len(p) == 2:
            p[0] = Node('type', val=p[1], no=p.lineno(1))
        else:
            p[0] = Node('type', val='short', no=p.lineno(1))

    def p_type_vec(self, p):
        """type : vectorof"""
        p[0] = p[1]

    def p_vectorof(self, p):
        """vectorof : VECTOROF type
                    | VECTOROF vectorof"""
        p[0] = Node('arr', val=str(p[1]), ch=p[2], no=p.lineno(1))

    def p_vectorof_error(self, p):
        """vectorof : VECTOROF type vectorof error"""
        p[0] = Node('error', val='Wrong array assignment', ch=p[1], no=p.lineno(1))
        sys.stderr.write(f'>>> Wrong assignment\n')

    def p_digit(self, p):
        """digit : INTVAR
                 | SHORTVAR"""
        p[0] = Node('digit', val=p[1], no=p.lineno(1))

    def p_bool(self, p):
        """bool : TRUE
                | FALSE
                | UNDEFINED"""
        p[0] = Node('bool', val=p[1], no=p.lineno(1))

    def p_expr(self, p):
        """expr : variable
                | const
                | callfunc
                | math_expr
                | command"""
        p[0] = p[1]

    def p_math_expr(self, p):
        """math_expr : expr ADD expr
                     | expr SUB expr
                     | expr FIRST SMALLER expr
                     | expr SECOND LARGER expr
                     | expr SECOND SMALLER expr
                     | expr FIRST LARGER expr
                     | expr OR expr
                     | expr NOT OR expr
                     | expr AND expr
                     | expr NOT AND expr"""
        if len(p) == 4:
            p[0] = Node('calculation', val=p[2], ch=[p[1], p[3]], no=p.lineno(2))
        else:
            p[0] = Node('calculation', val=p[2]+' '+p[3], ch=[p[1], p[4]], no=p.lineno(2))

    def p_mexp_error(self, p):
        """math_expr : expr SMALLER expr
                     | expr LARGER expr"""
        p[0] = Node('error', val='Comparison error', ch=[p[1], p[3]], no=p.lineno(2))
        sys.stderr.write(f'>>> Wrong comparison\n')

    def p_expr_br(self, p):
        """expr : OPBR expr CLBR"""
        p[1] = Node('bracket', val=p[1], no=p.lineno(1))
        p[3] = Node('bracket', val=p[3], no=p.lineno(3))
        p[0] = Node('expression', ch=[p[1], p[2], p[3]], no=p.lineno(1))

    def p_callfunc(self, p):
        """callfunc : STRVAR OPBR var_arr CLBR"""
        p[0] = Node('call_func', val=p[1], ch=p[3], no=p.lineno(1))

    def p_var_arr(self, p):
        """var_arr : variable
                   | const
                   | var_arr const
                   | var_arr variable
                   | """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = Node('func_param', ch=[p[1], p[2]], no=p.lineno(1))
        else:
            p[0] = Node('func_param', val='none')

    def p_const(self, p):
        """const : digit
                 | bool
                 | sizeof"""
        p[0] = p[1]

    def p_sizeof(self, p):
        """sizeof : SIZEOF OPBR type CLBR
                  | SIZEOF OPBR variable CLBR"""
        p[0] = Node('sizeof', val=p[1], ch=p[3], no=p.lineno(1))

    def p_arr_set(self, p):
        """arr_set : OPCUBR arr_set CLCUBR
                   | OPCUBR const_arr CLCUBR
                   | arr_set COMMA arr_set """
        if len(p) == 4:
            if p[2] == ',':
                p[0] = Node('array_comma', ch=[p[1], p[3]], no=p.lineno(2))
            else:
                p[0] = Node('array_lvl', ch=p[2], no=p.lineno(1))

    def p_const_arr(self, p):
        """const_arr : const
                     | const COMMA const_arr"""
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = Node('array item', ch=[p[1], p[3]], no=p.lineno(2))

    def p_variable(self, p):
        """variable : STRVAR
                    | STRVAR index"""
        if len(p) == 2:
            p[0] = Node('variable', val=p[1], no=p.lineno(1))
        else:
            p[0] = Node('arr variable', val=p[1], ch=p[2], no=p.lineno(1))

    def p_index(self, p):
        """index : OPSQBR expr CLSQBR
                 | OPSQBR expr CLSQBR index"""
        if len(p) == 4:
            p[0] = Node('index', ch=p[2], no=p.lineno(1))
        else:
            p[0] = Node('index', ch=[p[2], p[4]], no=p.lineno(1))

    def p_while(self, p):
        """while : DO NL stat_group WHILE expr SEMICOLON NL"""
        p[0] = Node('do_while', ch={'body': p[3], 'condition': p[5]}, no=p.lineno(1))

    def p_if(self, p):
        """if : IF expr THEN NL stat_group ELSE NL stat_group
              | IF expr THEN NL stat_group ELSE SEMICOLON NL"""
        if p[7] != ';':
            p[0] = Node('if_th_el', ch={'condition': p[2], 'body_1': p[5], 'body_2': p[8]}, no=p.lineno(1))
        else:
            p[0] = Node('if_then', ch={'condition': p[2], 'body': p[5]}, no=p.lineno(1))

    def p_if_error(self, p):
        """if : IF expr error"""
        p[0] = Node('error', val='Wrong if declaration', no=p.lineno(1))

    def p_function(self, p):
        """function : FUNCTION STRVAR OPBR typearr CLBR NL stat_group RETURN expr SEMICOLON NL"""
        if p[2] in self.func.keys():
            p[0] = Node('error', val='Function declared earlier',  no=p.lineno(1))
            sys.stderr.write(f'>>> Redeclared function\n')
        else:
            p[0] = Node('function', val=str(p[2]), ch={'parameters': p[4], 'body': p[7], 'return': p[9]},
                        no=p.lineno(1))
            self.func[p[2]] = p[0]

    def p_func_error(self, p):
        """function : FUNCTION error"""
        p[0] = Node('error', val='Wrong function declaration', ch=p[1], no=p.lineno(1))
        sys.stderr.write(f'>>> Wrong function declaration\n')

    def p_typearr(self, p):
        """typearr : typevar
                   | typearr typevar
                   | """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = Node('param_arr', ch=[p[1], p[2]], no=p.lineno(1))
        else:
            p[0] = Node('param_none', val='none')

    def p_typevar(self, p):
        """typevar : type variable"""
        p[0] = Node('param', ch=[p[1], p[2]], no=p.lineno(1))

    def p_command(self, p):
        """command : MOVE
                   | MOVE RIGHT
                   | MOVE LEFT
                   | LEFT
                   | RIGHT
                   | LMS"""
        if len(p) == 2:
            p[0] = Node('command', val=p[1], no=p.lineno(1))
        else:
            p[0] = Node('command', val=p[2], no=p.lineno(1))

    def p_error(self, p):
        try:
            sys.stderr.write(f'Syntax error at {p.lineno} line\n')
        except Exception:
            sys.stderr.write(f'Syntax error in input!')
        self.correct = False


if __name__ == '__main__':
    f = open('../language/test_prog.txt')
    data = f.read().lower()
    f.close()
    parser = ParserClass()
    tree = parser.parser.parse(data, debug=True)
    tree.graphviz_tree()
