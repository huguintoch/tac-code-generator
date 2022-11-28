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