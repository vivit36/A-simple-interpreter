import ply.lex as lex


# Лексический анализатор
class LexerClass:

    # Зарезервированные ключевые слова
    reserved = {
        'false': 'FALSE',
        'true': 'TRUE',
        'undefined': 'UNDEFINED',

        'bool': 'BOOL',
        'int': 'INT',
        'short': 'SHORT',

        'set': 'SET',
        'sizeof': 'SIZEOF',
        'add': 'ADD',
        'sub': 'SUB',

        'or': 'OR',
        'and': 'AND',
        'not': 'NOT',

        'smaller': 'SMALLER',
        'larger': 'LARGER',
        'first': 'FIRST',
        'second': 'SECOND',

        'begin': 'BEGIN',
        'end': 'END',
        'do': 'DO',
        'while': 'WHILE',
        'if': 'IF',
        'then': 'THEN',
        'else': 'ELSE',

        'move': 'MOVE',
        'right': 'RIGHT',
        'left': 'LEFT',
        'lms': 'LMS',

        'function': 'FUNCTION',
        'return': 'RETURN',
    }

    # Токены
    tokens = [
        'INTVAR',
        'SHORTVAR',
        'STRVAR',
        'OPBR', 'CLBR',
        'OPSQBR', 'CLSQBR',
        'OPCUBR', 'CLCUBR',
        'SEMICOLON',
        'COMMA',
        'NL',
        'VECTOROF'
    ] + list(reserved.values())

    # Пробел и табуляция игнорируется
    t_ignore = ' \t'

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def input(self, smth):
        return self.lexer.input(smth)

    def token(self):
        return self.lexer.token()

    def t_VECTOROF(self, t):
        r'vector[ ]+of'
        return t

    def t_INTVAR(self, t):
        r'\-?[0-9]+'
        return t

    def t_SHORTVAR(self, t):
        r'\-?s[0-9]+'
        return t

    def t_STRVAR(self, t):
        r'\_?[a-z][a-z0-9]*'
        t.type = self.reserved.get(t.value, 'STRVAR')
        return t

    def t_OPBR(self, t):
        r'\('
        return t

    def t_CLBR(self, t):
        r'\)'
        return t

    def t_OPSQBR(self, t):
        r'\['
        return t

    def t_CLSQBR(self, t):
        r'\]'
        return t

    def t_OPCUBR(self, t):
        r'\{'
        return t

    def t_CLCUBR(self, t):
        r'\}'
        return t

    def t_COMMA(self, t):
        r'\,'
        return t

    def t_SEMICOLON(self, t):
        r'\;'
        return t

    def t_NL(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')
        return t

    # Ошибка при встрече не подходящих символов
    def t_error(self, t):
        print("Illegal character '%s' " % t.value[0])
        t.lexer.skip(1)
        return t


test_string = '''function work()
begin
bool bva1;
bool bval2 set true;
bool bval3 set false;
short sval1;
short int sval2;
short sval3 set s123;
vector of int;
vector of short[10];
vector of int array1 set {1, 2, 3}
vector of vector of int array2;
array1[0] set -5 add -6;
end
return 0;
'''

test_string_2 = '''function work()
begin
vector of int array[2] set {1, 2};
vector of bool test set array;
end
return 0;
'''

if __name__ == '__main__':
    analyzer = LexerClass()
    analyzer.input(test_string)
    while True:
        tok = analyzer.token()
        if not tok:
            break
        print(tok)