import sys
import syntax_tree


class ErrorHandler:
    def __init__(self):
        self.type = None
        self.node = None
        self.types = [
            'UnexpectedError',
            'WorkLackError',
            'IndexError',
            'RedeclarationError',
            'UndeclaredVariableError',
            'ArrayDeclarationError',
            'ArrayToVariableError',
            'UndeclaredFunctionError',
            'WrongParameterError'
        ]

    def call(self, err_type, node=None):
        self.type = err_type
        self.node = node
        sys.stderr.write(f'Error {self.types[int(err_type)]}: ')
        if self.type == 0:
            # UnexpectedError
            sys.stderr.write(f'Incorrect syntax at {self.node.children[0].lineno} line \n')
            return
        elif self.type == 1:
            # WorkLackError
            sys.stderr.write(f'No WORK function in program\n')
        elif self.type == 2:
            # IndexError
            sys.stderr.write(f'Index is wrong at line {self.node.lineno}\n')
        elif self.type == 3:
            # RedeclarationError
            sys.stderr.write(f'Redeclaration of a variable "{self.node.child[1].child[0].value}" at line {self.node.child[1].child[0].lineno}\n')
        elif self.type == 4:
            # UndeclaredVariableError
            if node.type == 'variable' or node.type == 'arr variable':
                sys.stderr.write(f'Using undeclared variable "{self.node.value}" at line {self.node.lineno}\n')
            else:
                sys.stderr.write(f'Using undeclared variable "{self.node.child[0].value}" at line {self.node.child[0].lineno}\n')
        elif self.type == 5:
            # ArrayDeclarationError
            if node.child[1].type == 'variable' or node.child[1].type == 'arr variable':
                sys.stderr.write(
                    f'Wrong declaration of array "{self.node.child[1].value}" at line {self.node.child[1].lineno}\n')
            else:
                sys.stderr.write(f'Wrong declaration of array "{self.node.child[1].child[0].value}" at line {self.node.child[1].child[0].lineno}\n')
        elif self.type == 6:
            # ArrayToVariableError
            sys.stderr.write(f'Can\'t assign variable to array variable at line {self.node.lineno}\n')
        elif self.type == 7:
            # UndeclaredFunctionError
            sys.stderr.write(f'Calling undeclared function "{self.node.value}" at line {self.node.lineno}\n')
        elif self.type == 8:
            # WrongParameterError
            sys.stderr.write(f'Wrong parameters in function "{self.node.value}" at line {self.node.lineno}\n')


class UnexpectedError(Exception):
    pass


class WorkLackError(Exception):
    pass


class IndexError(Exception):
    pass


class RedeclarationError(Exception):
    pass


class UndeclaredVariableError(Exception):
    pass


class ArrayDeclarationError(Exception):
    pass


class ArrayToVariableError(Exception):
    pass


class UndeclaredFunctionError(Exception):
    pass


class WrongParameterError(Exception):
    pass

