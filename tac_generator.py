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
    "and": "AND",
    "or": "OR",
    "if": "IF",
    "elif": "ELIF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
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

    def type_check(self, symbolsTable):
        def is_bool_type(exp):
            return exp in ['BOOLVAL', 'AND', 'OR', 'BOOL']

        for child in self.childrens:
            child.type_check(symbolsTable)

        # Verify numeric-type operations
        if self.type in ['+', '-', '*', '/', '^', '<', '>', '<=', '>=']:
            for child in self.childrens:
                childType = symbolsTable[child.val]['type'] if child.type == 'ID' else child.type
                if is_bool_type(child.type):
                    print("ERROR: Invalid type for operation '%s'" %
                          self.type + " on " + child.type)
                    exit(1)
        # Verify numeric and boolean-type operations
        if self.type in ['==', '!=']:
            childOneType = symbolsTable[self.childrens[0]
                                        .val]['type'] if self.childrens[0].type == 'ID' else self.childrens[0].type
            childTwoType = symbolsTable[self.childrens[1]
                                        .val]['type'] if self.childrens[1].type == 'ID' else self.childrens[1].type
            if is_bool_type(childOneType) != is_bool_type(childTwoType):
                print("ERROR: Invalid type for operation '%s'" %
                      self.type + " on " + childOneType + " and " + childTwoType)
                exit(1)

        # Verify scope of variables
        if self.type == 'BLOCK':
            for child in self.childrens:
                if child.type == 'ID':
                    if child.val not in symbolsTable:
                        print("ERROR: Variable '%s'" % child.val +
                              " is not defined in the scope")
                        exit(1)

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

####################
# PROGRAM
####################


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

####################
# STATEMENTS
####################


def p_statement_assign(p):
    'statement : NAME "=" expression ";"'
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


def p_statement_num_dcl(p):
    'statement : numdcl'
    p[0] = p[1]


def p_dcl_int(p):
    '''numdcl : INTDCL NAME ";"
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


def p_dcl_float(p):
    '''numdcl : FLOATDCL NAME ";"
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
    'statement : PRINT "(" expression ")" ";"'
    n = Node()
    n.type = 'PRINT'
    n.childrens.append(p[3])
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
        n2.type = 'BLOCK'
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
        n2.type = 'BLOCK'
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
        n2.type = 'BLOCK'
        n2.childrens.extend(p[6])
        n.childrens.append(n2)
        p[0] = [n] + p[8]
    else:
        n = Node()
        n.type = 'ELIF'
        n.childrens.append(p[3])
        n2 = Node()
        n2.type = 'BLOCK'
        n2.childrens.extend(p[6])
        n.childrens.append(n2)
        p[0] = [n]


def p_statement_else(p):
    'elsestmt : ELSE "{" stmts "}"'
    n = Node()
    n.type = 'ELSE'
    n2 = Node()
    n2.type = 'BLOCK'
    n2.childrens.extend(p[3])
    n.childrens.append(n2)
    p[0] = [n]


def p_statement_while(p):
    'statement : WHILE "(" boolexp ")" "{" stmts "}"'
    n = Node()
    n.type = 'WHILE'
    n.childrens.append(p[3])
    n2 = Node()
    n2.type = 'BLOCK'
    n2.childrens.extend(p[6])
    n.childrens.append(n2)
    p[0] = n


def p_statement_for_loop_stmt(p):
    '''loopstmt : NAME "+" "+"
                | NAME "-" "-"
                | NAME "+" "=" numexp
                | NAME "-" "=" numexp
                | NAME "=" numexp'''
    n = Node()
    n.type = 'ASSIGN'
    n2 = Node()
    n2.type = 'ID'
    n2.val = p[1]
    n.childrens.append(n2)
    n3 = Node()
    if p[2] == "=":
        n.childrens.append(p[3])
    elif p[2] == "+":
        n3.type = '+'
        n3.childrens.append(n2)
        if p[3] == "+":
            n4 = Node()
            n4.type = 'INUMBER'
            n4.val = 1
            n3.childrens.append(n4)
        else:
            n3.childrens.append(p[4])
        n.childrens.append(n3)
    elif p[2] == "-":
        n3.type = '-'
        n3.childrens.append(n2)
        if p[3] == "-":
            n4 = Node()
            n4.type = 'INUMBER'
            n4.val = 1
            n3.childrens.append(n4)
        else:
            n3.childrens.append(p[4])
        n.childrens.append(n3)
    p[0] = n


def p_statement_for(p):
    'statement : FOR "(" numdcl boolexp ";" loopstmt ")" "{" stmts "}"'
    n = Node()
    n.type = 'FOR'
    n.childrens.append(p[3])
    n.childrens.append(p[4])
    n.childrens.append(p[6])
    n2 = Node()
    n2.type = 'BLOCK'
    n2.childrens.extend(p[9])
    n.childrens.append(n2)
    p[0] = n


####################
# EXPRESSIONS
####################


def p_expression_name(p):
    "expression : NAME"
    if p[1] in symbolsTable["table"]:
        n = Node()
        n.type = 'ID'
        n.val = p[1]
        p[0] = n


def p_expression_boolval(p):
    "expression : boolexp"
    p[0] = p[1]


def p_bool_expression(p):
    '''boolexp : BOOLVAL
               | NAME
               | compexp
               | logicalop
               | "(" boolexp ")"'''
    if len(p) == 4:
        p[0] = p[2]
    elif p[1] in ('true', 'false'):
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


def p_logical_operation(p):
    '''logicalop : boolexp AND boolexp
                 | boolexp OR boolexp'''
    if p[2] in ('and', 'or'):
        n = Node()
        n.type = p[2].upper()
        n.childrens.append(p[1])
        n.childrens.append(p[3])
        p[0] = n


def p_comparison_expression(p):
    '''compexp : expression EQUALS expression
               | expression NOTEQUALS expression
               | expression GREATER expression
               | expression LESS expression
               | expression LESSEQUALS expression
               | expression GREATEREQUALS expression'''
    n = Node()
    n.type = p[2]
    n.childrens.append(p[1])
    n.childrens.append(p[3])
    p[0] = n


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


def p_expression_numexp(p):
    '''numexp : binopexp
              | "(" numexp ")"'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


def p_expression_binop(p):
    '''binopexp : binoperand "+" binoperand
                | binoperand "-" binoperand
                | binoperand "*" binoperand
                | binoperand "/" binoperand
                | binoperand "^" binoperand'''
    if p[2] in ('+', '-', '*', '/', '^'):
        n = Node()
        n.type = p[2]
        n.childrens.append(p[1])
        n.childrens.append(p[3])
        p[0] = n


def p_expression_binoperand(p):
    '''binoperand : numexp
                   | NAME'''
    if p[1] in symbolsTable["table"]:
        n = Node()
        n.type = 'ID'
        n.val = p[1]
        p[0] = n
    else:
        p[0] = p[1]


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


# Open input file
f = open("input.txt")
content = f.read()

# Build the parser
parser = yacc.yacc()
yacc.parse(content)

# Print the AST
abstractTree.type_check(symbolsTable["table"])
abstractTree.print()

varCounter = 0
labelCounter = 0


def getDefaultValue(type):
    if type == 'INTDCL':
        return 0
    elif type == 'FLOATDCL':
        return 0.0
    elif type == 'BOOLDCL':
        return False


def genTAC(node):
    global varCounter
    global labelCounter
    if (node.type == "ASSIGN"):
        print(node.childrens[0].val + " := " + genTAC(node.childrens[1]))
    elif (node.type in ["INTDCL", "FLOATDCL"]):
        print(node.val + " := " + str(getDefaultValue(node.type)))
    elif (node.type in ["ID", "INUMBER", "FNUMBER", "BOOLVAL"]):
        return str(node.val)
    elif (node.type in ["+", "-", "*", "/", "^"]):
        tempVar = "TEMP_" + str(varCounter)
        varCounter = varCounter + 1
        print(tempVar + " := " +
              genTAC(node.childrens[0]) + " " + node.type + " " + genTAC(node.childrens[1]))
        return tempVar
    elif (node.type in ["==", "!=", ">", "<", ">=", "<=", "AND", "OR"]):
        tempVar = "TEMP_" + str(varCounter)
        varCounter = varCounter + 1
        print(tempVar + " := " +
              genTAC(node.childrens[0]) + " " + node.type + " " + genTAC(node.childrens[1]))
        return tempVar
    elif (node.type == "PRINT"):
        print("PRINT " + genTAC(node.childrens[0]))
    elif (node.type == "IF"):
        tempVar = "TEMP_" + str(varCounter)
        varCounter = varCounter + 1
        print(tempVar + " := !" + genTAC(node.childrens[0]))
        tempLabel = "LABEL_" + str(labelCounter)
        print("gotoLabelIf " + tempVar + " " + tempLabel)
        genTAC(node.childrens[1])
        print("gotoLabelIf true LABEL_ENDIF")
        for child in node.childrens[2:]:
            genTAC(child)
        if node.childrens[-1].type != "ELSE":
            print("LABEL_" + str(labelCounter))
        print("LABEL_ENDIF")
    elif (node.type == "ELIF"):
        print("LABEL_" + str(labelCounter))
        labelCounter = labelCounter + 1
        tempVar = "TEMP_" + str(varCounter)
        varCounter = varCounter + 1
        print(tempVar + " := !" + genTAC(node.childrens[0]))
        tempLabel = "LABEL_" + str(labelCounter)
        print("gotoLabelIf " + tempVar + " " + tempLabel)
        genTAC(node.childrens[1])
        print("gotoLabelIf true LABEL_ENDIF")
        for child in node.childrens[2:]:
            genTAC(child)
    elif (node.type == "ELSE"):
        print("LABEL_" + str(labelCounter))
        labelCounter = labelCounter + 1
        genTAC(node.childrens[0])
    elif (node.type == "WHILE"):
        tempLabel = "LABEL_" + str(labelCounter)
        labelCounter = labelCounter + 1
        print(tempLabel)
        tempVar = "TEMP_" + str(varCounter)
        varCounter = varCounter + 1
        print(tempVar + " := !" + genTAC(node.childrens[0]))
        tempLabel2 = "LABEL_" + str(labelCounter)
        labelCounter = labelCounter + 1
        print("gotoLabelIf " + tempVar + " " + tempLabel2)
        genTAC(node.childrens[1])
        print("gotoLabelIf " + "true " + tempLabel)
        print(tempLabel2)
    elif (node.type == "FOR"):
        genTAC(node.childrens[0])
        tempLabel = "LABEL_" + str(labelCounter)
        labelCounter = labelCounter + 1
        print(tempLabel)
        tempVar = "TEMP_" + str(varCounter)
        varCounter = varCounter + 1
        print(tempVar + " := !" + genTAC(node.childrens[1]))
        tempLabel2 = "LABEL_" + str(labelCounter)
        labelCounter = labelCounter + 1
        print("gotoLabelIf " + tempVar + " " + tempLabel2)
        genTAC(node.childrens[3])
        genTAC(node.childrens[2])
        print("gotoLabelIf " + "true " + tempLabel)
        print(tempLabel2)
    else:
        for child in node.childrens:
            genTAC(child)


# Output TAC to file
outputFilename = sys.argv[1]
print("\n\n*TAC output to " + outputFilename)
f = open(outputFilename, "w")
sys.stdout = f
genTAC(abstractTree)
f.close()
