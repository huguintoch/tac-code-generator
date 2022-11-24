import ply.yacc as yacc
import ply.lex as lex
import sys
sys.path.insert(0, "..")

reserved = {
    "int": "INTDCL",
    "float": "FLOATDCL",
    "print": "PRINT",
    "boolean": "BOOLDCL",
    "true": "BOOLVAL",
    "false": "BOOLVAL",
    "if": "IF",
    "elif": "ELIF",
    "else": "ELSE",
    "and": "AND",
    "or": "OR"
}


tokens = [
    'NAME', 'INUMBER', 'FNUMBER', 'EQUALS', 'NOTEQUALS', 'LESS', 'GREATER', 'LESSEQUALS', 'GREATEREQUALS'
]
tokens.extend(reserved.values())

literals = ['=', '+', '-', '*', '/', '^', ';', '(', ')', '{', '}']

# Tokens


def t_NAME(t):
    r'[a-zA-Z_]+[a-zA-Z0-9]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t


def t_FNUMBER(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_INUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


t_EQUALS = r'=='
t_NOTEQUALS = r'!='
t_LESS = r'<'
t_GREATER = r'>'
t_LESSEQUALS = r'<='
t_GREATEREQUALS = r'>='

t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Parsing rules


class Node:
    def __init__(self):
        self.childrens = []
        self.type = ''
        self.val = ''

    def print(self, lvl=0):
        r = ('-' * lvl) + self.type + " : " + str(self.val)
        print(r)
        for c in self.childrens:
            c.print(lvl+1)


# dictionary of names
symbolsTable = {
    "table": {},
    "parent": None,
}
abstractTree = None


def p_prog(p):
    'prog : stmts'
    global abstractTree
    abstractTree = Node()
    abstractTree.type = 'ROOT'
    abstractTree.childrens.extend(p[1])


def p_statements_recursion(p):
    '''stmts : statement stmts
             | statement '''
    stmt = p[1]
    if len(p) == 3:
        stmts = [stmt]
        stmts.extend(p[2])
        p[0] = stmts
    else:
        p[0] = [stmt]


def p_dcl_declare_int(p):
    '''statement : INTDCL NAME ";"
                 | INTDCL NAME "=" numexp ";"'''
    if len(p) == 4:
        symbolsTable["table"][p[2]] = {"type": "INT", "value": 0}
        n = Node()
        n.type = "INTDCL"
        n.val = p[2]
        p[0] = n
    else:
        symbolsTable["table"][p[2]] = {"type": "INT", "value": p[4]}
        n = Node()
        n.type = "INTDCL"
        n.val = p[2]
        n2 = Node()
        n2.type = "ASSIGN"
        n2.childrens.append(n)
        n2.childrens.append(p[4])
        p[0] = n2


def p_statement_declare_float(p):
    '''statement : FLOATDCL NAME ";"
                 | FLOATDCL NAME "=" numexp ";"'''
    if len(p) == 4:
        symbolsTable["table"][p[2]] = {"type": "FLOAT", "value": 0.0}
        n = Node()
        n.type = "FLOATDCL"
        n.val = p[2]
        p[0] = n
    else:
        symbolsTable["table"][p[2]] = {"type": "FLOAT", "value": p[4]}
        n = Node()
        n.type = "FLOATDCL"
        n.val = p[2]
        n2 = Node()
        n2.type = "ASSIGN"
        n2.childrens.append(n)
        n2.childrens.append(p[4])
        p[0] = n2


def p_statement_declare_bool(p):
    '''statement : BOOLDCL NAME ";"
                 | BOOLDCL NAME "=" boolexp ";"'''
    if len(p) == 4:
        symbolsTable["table"][p[2]] = {"type": "BOOL", "value": False}
        n = Node()
        n.type = "BOOLDCL"
        n.val = p[2]
        p[0] = n
    else:
        symbolsTable["table"][p[2]] = {"type": "BOOL", "value": p[4]}
        n = Node()
        n.type = "BOOLDCL"
        n.val = p[2]
        n2 = Node()
        n2.type = "ASSIGN"
        n2.childrens.append(n)
        n2.childrens.append(p[4])
        p[0] = n2


def p_statement_print(p):
    'statement : PRINT expression ";"'
    n = Node()
    n.type = 'PRINT'
    n.childrens.append(p[2])
    p[0] = n


def p_statement_if(p):
    '''statement : IF "(" boolexp ")" "{" stmts "}"
                 | IF "(" boolexp ")" "{" stmts "}" elifstmt
                 | IF "(" boolexp ")" "{" stmts "}" elifstmt elsestmt
                 | IF "(" boolexp ")" "{" stmts "}" elsestmt'''
    if len(p) == 10:
        n = Node()
        n.type = 'IF'
        n.childrens.append(p[3])
        n2 = Node()
        n2.childrens.extend(p[6])
        n.childrens.append(n2)
        n.childrens.extend(p[8])
        n.childrens.extend(p[9])
        p[0] = n
    elif len(p) == 9:
        n = Node()
        n.type = 'IF'
        n.childrens.append(p[3])
        n2 = Node()
        n2.childrens.extend(p[6])
        n.childrens.append(n2)
        n.childrens.extend(p[8])
        p[0] = n
    else:
        n = Node()
        n.type = 'IF'
        n.childrens.append(p[3])
        n2 = Node()
        n2.childrens.extend(p[6])
        n.childrens.append(n2)
        p[0] = n


def p_statement_elif(p):
    '''elifstmt : ELIF "(" boolexp ")" "{" stmts "}"
                | ELIF "(" boolexp ")" "{" stmts "}" elifstmt'''
    if len(p) == 9:
        n = Node()
        n.type = 'ELIF'
        n.childrens.append(p[3])
        n2 = Node()
        n2.childrens.extend(p[6])
        n.childrens.append(n2)
        p[0] = [n] + p[8]
    else:
        n = Node()
        n.type = 'ELIF'
        n.childrens.append(p[3])
        n2 = Node()
        n2.childrens.extend(p[6])
        n.childrens.append(n2)
        p[0] = [n]


def p_statement_else(p):
    'elsestmt : ELSE "{" stmts "}"'
    n = Node()
    n.type = 'ELSE'
    n2 = Node()
    n2.childrens.extend(p[3])
    n.childrens.append(n2)
    p[0] = [n]


def p_statement_assign(p):
    'statement : NAME "=" expression ";"'
    if p[1] not in symbolsTable["table"]:
        print("You must declare a variable before using it")
    n = Node()
    n.type = 'ASSIGN'
    if p[1] in symbolsTable["table"]:
        n1 = Node()
        n1.type = 'ID'
        n1.val = p[1]
        n.childrens.append(n1)
    else:
        print("Error undeclared variable")
    n.childrens.append(p[3])
    p[0] = n


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_binop(p):
    '''binopexp : numexp '+' numexp
                | numexp '-' numexp
                | numexp '*' numexp
                | numexp '/' numexp
                | numexp '^' numexp'''
    if p[2] in ('+', '-', '*', '/', '^'):
        n = Node()
        n.type = p[2]
        n.childrens.append(p[1])
        n.childrens.append(p[3])
        p[0] = n


def p_expression_numexp(p):
    '''numexp : binopexp
              | NAME'''
    if type(p[1]) is Node:
        p[0] = p[1]
    elif p[1] in symbolsTable["table"]:
        n = Node()
        n.type = 'ID'
        n.val = p[1]
        p[0] = n
    else:
        print("Error undeclared variable {}".format(p[1]))


def p_expression_number(p):
    '''expression : numexp'''
    p[0] = p[1]


def p_expression_inumber(p):
    "numexp : INUMBER"
    n = Node()
    n.type = 'INUMBER'
    n.val = int(p[1])
    p[0] = n


def p_expression_fnumber(p):
    "numexp : FNUMBER"
    n = Node()
    n.type = 'FNUMBER'
    n.val = float(p[1])
    p[0] = n


def p_expression_boolval(p):
    "expression : boolexp"
    p[0] = p[1]


def p_bool_expression(p):
    '''boolexp : '(' boolexp ')'
               | boolexp AND boolexp
               | boolexp OR boolexp
               | BOOLVAL
               | NAME
               | compexp'''
    if len(p) == 2:
        if p[1] in ('true', 'false'):
            n = Node()
            n.type = 'BOOLVAL'
            n.val = p[1]
            p[0] = n
        elif p[1] in symbolsTable["table"]:
            n = Node()
            n.type = 'ID'
            n.val = p[1]
            p[0] = n
        else:
            p[0] = p[1]
    else:
        if p[2] in ('and', 'or'):
            n = Node()
            n.type = p[2].upper()
            n.childrens.append(p[1])
            n.childrens.append(p[3])
            p[0] = n
        else:
            p[0] = p[2]


def p_comparison_expression(p):
    '''compexp : boolexp EQUALS boolexp
               | boolexp NOTEQUALS boolexp
               | numexp EQUALS numexp
               | numexp NOTEQUALS numexp
               | numexp GREATER numexp
               | numexp LESS numexp
               | numexp LESSEQUALS numexp
               | numexp GREATEREQUALS numexp'''
    n = Node()
    n.type = p[2]
    n.childrens.append(p[1])
    n.childrens.append(p[3])
    p[0] = n


def p_expression_name(p):
    "expression : NAME"
    if p[1] in symbolsTable["table"]:
        n = Node()
        n.type = 'ID'
        n.val = p[1]
        p[0] = n


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()


f = open("code.txt")
content = f.read()
yacc.parse(content)


abstractTree.print()

# varCounter = 0
# labelCounter = 0
# def genTAC(node):
#     global varCounter
#     global labelCounter
#     if ( node.type == "ASSIGN" ):
#         print(node.childrens[0].val  + " := " + genTAC(node.childrens[1]) )
#     elif ( node.type == "INUMBER"):
#         return str(node.val)
#     elif ( node.type in ["+", "-", "*", "/", "^"] ):
#         tempVar = "t" + str(varCounter)
#         varCounter = varCounter +1
#         print( tempVar + " := " + genTAC(node.childrens[0]) + " " + node.type + " " + genTAC(node.childrens[1]))
#         return tempVar
#     elif ( node.type == "PRINT"):
#         print( "PRINT " + genTAC(node.childrens[0]))
#     elif ( node.type == "IF" ):
#         tempVar = "t" + str(varCounter)
#         varCounter = varCounter +1
#         print ( tempVar + " := !" + str(node.childrens[0].val))
#         tempLabel = "l" + str(labelCounter)
#         labelCounter = labelCounter + 1
#         print ( "gotoLabelIf " + tempVar + " " + tempLabel)
#         genTAC(node.childrens[1])
#         print ( tempLabel)
#     else:
#         for child in node.childrens:
#             genTAC(child)


# print ("\ntac:\n")
# genTAC(abstractTree)


# Some examples
# for ( i = 0; i < 3; i++){
#     stamentes
# }
# i := 0
# t1 = i < 3
# t0 = !t1
# gotoLabelif t0 Label1

# staments
# i = i + 1
# Label1


# while ( condicion ) {
#     staments
# }
# WHILE
# t1 = condicion
# t0 = !t1
# gotoLabelif t0 Label1

# staments

# Label1
