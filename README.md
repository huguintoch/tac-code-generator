# Three Address Code Generator
Compiler design final project. It consists of a parser and lexical analyzer that prints the input program's abstract tree and generates TAC as output.

## Requirements
```
pip install ply
```

## Usage
Default input is at input.txt
```
py tac_generator.py <output_file_name>
```

## Especifications
### Operations
- Arithmetic
    - Addition: +
    - Subtraction: -
    - Multiplication: *
    - Division: /
    - Exponentiation: ^
- Comparison
    - ==
    - !=
    - \>
    - \<
    - \>=
    - \<=
- Boolean
    - and
    - or
- Block
    - ()
    - {}
### Type system
- Integer
- Float
- Boolean
### Allowed operations between types
|         | int                    | float                  | boolean         |
|---------|------------------------|------------------------|-----------------|
| int     | arithmetic, comparison | arithmetic, comparison | ----            |
| float   | arithmetic, comparison | arithmetic, comparison | ----            |
| boolean | ----                   | ----                   | and, or, ==, != |
    
### Control flows
They must follow a structure similar to C language. For simplicity everything must have braces:
- if, else, elif
- while() {}
- for (;;) {}

### General
- To mark the end of a statement, use ";"
- It is allowed to declare and assign a variable on the same line

## Example
### Input
```
int a = 0;
float b;
boolean testBool = false;

a = 1;
b = 2 ^ 3;

if ((2 - 0 / a) > 2 and true or testBool) {
    int c;
    c = 4;
} elif (testBool) {
    int d;
    d = 4;
} elif (false) {
    boolean x = false;
} else {
    float e = 5.5;
}

while (a < 2+1) {
    boolean y = true;
    if (y) {
        a = a + 1;
    }
}

for (int i = 0; i <= 10; i++) {
    a = a - 1;
    print(a);
}
```
### AST
```
ROOT :
-ASSIGN :
--INTDCL : a        
--INUMBER : 0       
-FLOATDCL : b       
-ASSIGN :
--BOOLDCL : testBool
--BOOLVAL : false   
-ASSIGN :
--ID : a
--INUMBER : 1       
-ASSIGN :
--ID : b
--^ :
---INUMBER : 2      
---INUMBER : 3      
-IF :
--AND :
---> :
----- :
-----INUMBER : 2    
-----/ :
------INUMBER : 0   
------ID : a        
----INUMBER : 2     
---OR :
----BOOLVAL : true  
----ID : testBool   
--BLOCK :
---INTDCL : c       
---ASSIGN :
----ID : c
----INUMBER : 4     
--ELIF :
---ID : testBool    
---BLOCK :
----INTDCL : d      
----ASSIGN :        
-----ID : d
-----INUMBER : 4
--ELIF :
---BOOLVAL : false
---BLOCK :
----ASSIGN :
-----BOOLDCL : x
-----BOOLVAL : false
--ELSE :
---BLOCK :
----ASSIGN :
-----FLOATDCL : e
-----FNUMBER : 5.5
-WHILE :
--< :
---ID : a
---+ :
----INUMBER : 2
----INUMBER : 1
--BLOCK :
---ASSIGN :
----BOOLDCL : y
----BOOLVAL : true
---IF :
----ID : y
---- :
-----ASSIGN :
------ID : a
------+ :
-------ID : a
-------INUMBER : 1
-FOR :
--ASSIGN :
---INTDCL : i
---INUMBER : 0
--<= :
---ID : i
---INUMBER : 10
--ASSIGN : 
---ID : i
---+ :
----ID : i
----INUMBER : 1
--BLOCK :
---ASSIGN :
----ID : a
----- :
-----ID : a
-----INUMBER : 1
---PRINT :
----ID : a
```
### TAC output
```
a := 0
b := 0.0
testBool := false
a := 1
TEMP_0 := 2 ^ 3
b := TEMP_0
TEMP_5 := 0 / a
TEMP_4 := 2 - TEMP_5
TEMP_3 := TEMP_4 > 2
TEMP_6 := true OR testBool
TEMP_2 := TEMP_3 AND TEMP_6
TEMP_1 := !TEMP_2
gotoLabelIf TEMP_1 LABEL_0
c := 0
c := 4
gotoLabelIf true LABEL_ENDIF
LABEL_0
TEMP_7 := !testBool
gotoLabelIf TEMP_7 LABEL_1
d := 0
d := 4
gotoLabelIf true LABEL_ENDIF
LABEL_1
TEMP_8 := !false
gotoLabelIf TEMP_8 LABEL_2
x := false
gotoLabelIf true LABEL_ENDIF
LABEL_2
e := 5.5
LABEL_ENDIF
LABEL_3
TEMP_11 := 2 + 1
TEMP_10 := a < TEMP_11
TEMP_9 := !TEMP_10
gotoLabelIf TEMP_9 LABEL_4
y := true
TEMP_12 := !y
gotoLabelIf TEMP_12 LABEL_5
TEMP_13 := a + 1
a := TEMP_13
gotoLabelIf true LABEL_ENDIF
LABEL_5
LABEL_ENDIF
gotoLabelIf true LABEL_3
LABEL_4
i := 0
LABEL_5
TEMP_15 := i <= 10
TEMP_14 := !TEMP_15
gotoLabelIf TEMP_14 LABEL_6
TEMP_16 := a - 1
a := TEMP_16
PRINT a
TEMP_17 := i + 1
i := TEMP_17
gotoLabelIf true LABEL_5
LABEL_6

```