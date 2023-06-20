import re

# @source https://www.geeksforgeeks.org/python-program-to-convert-integer-to-roman/
def int_to_roman(number):
    num = [1, 4, 5, 9, 10, 40, 50, 90,
        100, 400, 500, 900, 1000]
    sym = ["i", "iv", "v", "ix", "x", "xl",
        "l", "xc", "c", "cd", "d", "cm", "m"]
    i = 12
    
    roman = ""
    while number:
        div = number // num[i]
        number %= num[i]
 
        while div:
            roman += sym[i]
            div -= 1
        i -= 1
    
    return roman

# gets the clean word only command
def clean_command(command):
    return re.search('\{(.+)\}', command).group(0).removesuffix('}').removeprefix('{')

# gets the character x places away from the input character
def add_char(character, x):
    return chr(ord(character) + x)

# gets the first command from a string and an index in the string
def get_command(str, ind):
    if str[ind] in ['\\', '&', '$']:
        return str[ind], ind

    cmd = ""
    bracket_nest = 0
    for i, c in enumerate(str[ind:]):
        if c == '{':
            bracket_nest += 1

        if bracket_nest <= 0 and c in [' ', '\\', '\n', '.']:
            return cmd, i + ind
        elif bracket_nest > 0 and c == '}':
            bracket_nest -= 1
        cmd += c

# given a latex command, return a list with all the bracket parameters
def get_params(cmd):
    params = []
    bracket_nest = 0
    param = ""

    for c in cmd:
        if c == "{":
            bracket_nest += 1

            # clear params after passing first bracket
            if bracket_nest == 1:
                param = ""
                continue
        elif c == "}":
            bracket_nest -= 1
            if bracket_nest == 0:
                params.append(param)
                param = ""
        param += c
    return params

