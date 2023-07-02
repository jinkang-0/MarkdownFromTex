import re
import os
import sys

###########
# HELPERS #
###########

# @source https://www.geeksforgeeks.org/python-program-to-convert-integer-to-roman/
def int_to_roman(number):
    num = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000]
    sym = ["i", "iv", "v", "ix", "x", "xl", "l", "xc", "c", "cd", "d", "cm", "m"]

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
    return re.search('(?<=\{)(.+)(?=\})', command).group(0)

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
        if c in ['{', '[']:
            bracket_nest += 1

        if bracket_nest <= 0 and c in [' ', '\\', '\n', '.']:
            return cmd, i + ind
        elif bracket_nest > 0 and c in ['}', ']']:
            bracket_nest -= 1
        cmd += c

    return cmd, len(str)

# given a latex command, return a list with all the bracket parameters
def get_params(cmd):
    params = []
    bracket_nest = 0
    param = ""

    for c in cmd:
        if c in ['{', '[']:
            bracket_nest += 1

            # clear params after passing first bracket
            if bracket_nest == 1:
                param = ""
                continue
        elif c in ['}', ']']:
            bracket_nest -= 1
            if bracket_nest == 0:
                params.append(param)
                param = ""
        param += c
    return params



############
# COMMANDS #
############

# vars for command matchers
matchers = []
block_matchers = []
part = '`'
enumerating = False
subpart = 0
question = 0
figures = []
bulleting = False

"""
match_cmds: a list of commands that will trigger the function
func: the function to be triggered, takes a string command, returns formatted string
"""
def matcher(match_cmds):
    def decorator(func):
        matchers.append({
            "commands": match_cmds,
            "adjust": func
        })
    return decorator

@matcher(['section', 'section*'])
def header_adjust(cmd):
    return f"\n## {clean_command(cmd)}\n"

@matcher(['Question'])
def question_adjust(cmd):
    global question
    question += 1
    return f"«## {question}. {clean_command(cmd)}»\n"

@matcher(['begin', 'end'])
def handle_block(cmd):
    block_type = clean_command(cmd)
    for block_matcher in block_matchers:
        if block_type in block_matcher["blocks"]:
            return block_matcher["adjust"](cmd)
    return ""

@matcher(['Part', 'item'])
def handle_part(cmd):
    global part, subpart, enumerating, bulleting
    if enumerating:
        subpart += 1
        return f"\n- ({int_to_roman(subpart)})"
    elif bulleting:
        return "-"
    part = add_char(part, 1)
    return f"\n({part})"

@matcher(['href'])
def link_parser(cmd):
    vals = get_params(cmd)
    return f"[{vals[1]}]({vals[0]})"

@matcher(['notelinks', 'notelinks*'])
def parse_notelinks(cmd):
    raw_params = get_params(cmd)
    params = [p for p in raw_params[0].split('\\') if p != '']

    parsed = ""
    for p in params:
        link_vals = get_params(p)
        parsed += f"[{link_vals[1]}]({link_vals[0]})\n†"
    return parsed

@matcher(['textbf'])
def bold_text(cmd):
    return f"**{get_params(cmd)[0]}**"

@matcher(['emph'])
def italic_text(cmd):
    param = get_params(cmd)[0]
    content = process_content(param)
    return f"*{content}*"

@matcher(['includegraphics'])
def add_images(cmd):
    return f"![[{get_params(cmd)[1]}]]"

@matcher(['caption'])
def image_caption(cmd):
    content = process_content(get_params(cmd)[0])
    return f"> {content.strip()}"

@matcher(['label'])
def handle_label(cmd):
    param = get_params(cmd)[0]
    if param.startswith('fig:'):
        global figures
        fig = param[4:]
        figures.append(fig)
        return f"Figure {len(figures)}: "
    return ""

@matcher(['ref'])
def handle_ref(cmd):
    param = get_params(cmd)[0]
    if param.startswith('fig:'):
        global figures
        fig = param[4:]
        index = figures.index(fig) + 1
        return f"{index}"
    return ""

@matcher(['LaTeX'])
def parse_latex(cmd):
    return "LaTeX"

@matcher(['frac', 'hdots', 'forall', 'in', 'mathbb', 'le', 'ge', 'nmid', 'wedge', 'cup', 'subseteq'])
def math_cmd(cmd):
    return f"\\{cmd}"


##
## this section handles block commands
##

"""
blocks: list of blocks that will trigger the function
func: the function that processes the block strings (and cause side efffects), returns formatted string
"""
def block_matcher(blocks):
    def decorator(func):
        block_matchers.append({
            "blocks": blocks,
            "adjust": func
        })
    return decorator

@block_matcher(['Parts'])
def parts_block(cmd):
    global part
    part = "`"
    return ""

@block_matcher(['enumerate'])
def enumerate_block(cmd):
    global enumerating, subpart
    enumerating = cmd.startswith('begin')
    subpart = 0
    return ""

@block_matcher(['itemize'])
def handle_itemize(cmd):
    global bulleting
    bulleting = not bulleting
    return ""

@block_matcher(['align', 'align*'])
def align_block(cmd):
    return "$$"




#########################
# BEGIN FILE PROCESSING #
#########################

# process backslash commands
def process_command(command):
    for match in matchers:
        for cmd in match["commands"]:
            if command.startswith(cmd):
                return match["adjust"](command)
    return ""

# process contents
def process_content(string):
    skip_commands = False
    skip_ind = -1
    output_string = ""

    for ind, char in enumerate(string):
        if ind < skip_ind:
            continue

        # filter content to process commands
        if not skip_commands and char == '\\':
            cmd, skip_ind = get_command(string, ind+1)
            output_string += process_command(cmd)
            continue
        elif char == '$':
            skip_commands = not skip_commands

        output_string += char

    return output_string



# get file name
input_file_name = ''
output_file_name = ''

if len(sys.argv) > 2:
    raise SyntaxError(f"Expected 1 argument to the script, but got {len(sys.argv)} instead.")
elif len(sys.argv) == 2:
    file = sys.argv[1]
    if not file.endswith('.tex'):
        raise TypeError("Target file must end with .tex")
    input_file_name = file
    output_file_name = file[:-4] + ".md"
else:
    for file in os.listdir('./'):
        if file.endswith('.tex'):
            input_file_name = file
            output_file_name = file[:-4] + ".md"
            break

if input_file_name == '':
    raise RuntimeError("No TeX file detected! Move the desired TeX file you want to convert in the same directory (folder) as this script.")

# read input file
with open(input_file_name, 'r') as f:
    input = f.read()

# process input
input = "\n".join([line.strip() for line in input.split("\n") if not line.strip() in ['\n', '']])
processed = process_content(input)
contents = processed.strip() + '\n'

# convert latex cmds to mathjax
contents = re.sub(r'\\[RNZQC]', lambda match: f"\\mathbb{{{match.group(0)[1:]}}}", contents)
contents = re.sub(r'hdots', "dots", contents)

# beautify processed contents
contents = re.sub(r'~', ' ', contents)
contents = re.sub(r'(?<=\([a-z]\))\n', ' ', contents)
contents = re.sub(r'  ', ' ', contents)
contents = re.sub(r'»\n{0,}', '\n\n', contents)
contents = re.sub(r'\n{0,}«', '\n\n\n\n', contents)
contents = re.sub(r'†\n+', '\n', contents)
contents = re.sub(r'†', '', contents)

# write to output
with open(output_file_name, 'w') as output:
    output.write(contents)
