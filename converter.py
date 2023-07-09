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
# starts after the first \
def get_command(str, ind):
    if ind > len(str):
        return "", ind
    
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

def find_bracket(str, ind):
    bracket_nest = 0
    bracket_str = ""

    for i, c in enumerate(str[ind:]):
        if c == '[':
            bracket_nest += 1
        
        if bracket_nest == 0:
            return bracket_str, i + ind
        elif bracket_nest > 0 and c == ']':
            bracket_nest -= 1
        bracket_str += c


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

# starts at the \ in \begin{block}
def get_block(str, ind):
    block_content = ""
    block_nest = 0
    block_type = ""
    skip_ind = -1

    for i, c in enumerate(str[ind:]):
        if ind + i > skip_ind and c == '\\':
            cmd, skip_ind = get_command(str, ind+i+1)
            is_begin = cmd.startswith('begin')
            is_end = cmd.startswith('end')

            if is_begin or is_end:
                # match block type
                params = get_params(cmd)
                btype = params[0]
                if block_type == "":
                    block_type = btype
                if block_type != btype:
                    block_content += c
                    continue

                # begin and end cases
                if is_begin:
                    block_nest += 1
                elif is_end and block_type == btype:
                    block_nest -= 1

        # termination condition
        if block_nest == 0:
            return block_content + '\\' + cmd, block_type, ind + i
        block_content += c

    return (None, None, -1)

# only get the content without \begin and \end
def clean_block(string):
    no_begin = re.sub(r'^\\begin{[\w\*]+}(\[[\w{()}.*]*\])*(\{[|\d\s\w]*\})*', '', string)
    no_end = re.sub(r'\\end{[\w\*]+}$', '', no_begin)
    return no_end



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

@matcher(['documentclass', 'usepackage', 'def', 'title', 'maketitle', 'fontsize', 'selectfont', 'vspace', 'end', 'hline', 'centering'])
def ignored_commands(cmd):
    return ""

@matcher(['section', 'section*'])
def header_adjust(cmd):
    return f"\n## {clean_command(cmd)}\n"

@matcher(['Question'])
def question_adjust(cmd):
    global question
    question += 1
    return f"«## {question}. {clean_command(cmd)}»\n"

@matcher(['item'])
def handle_item(cmd):
    global subpart, enumerating, bulleting
    if enumerating == 'a':
        subpart += 1
        return f"({add_char('`', subpart)})"
    elif enumerating == 'i':
        subpart += 1
        return f"\n- ({int_to_roman(subpart)})"
    elif bulleting:
        return "-"
    return ""

@matcher(['Part'])
def handle_part(cmd):
    global part
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

@block_matcher(['document', 'figure'])
def do_nothing_block(content):
    clean_content = clean_block(content)
    return process_content(clean_content)

@block_matcher(['center'])
def center_block(content):
    clean_content = clean_block(content)
    slashes_removed = ""
    for line in clean_content.splitlines(True):
        slashes_removed += re.sub(r'\\\\$', '', line)
    return process_content(slashes_removed)

@block_matcher(['Parts'])
def parts_block(content):
    global part
    part = "`"
    clean_content = clean_block(content)
    return process_content(clean_content)

@block_matcher(['enumerate'])
def enumerate_block(content):
    global enumerating, subpart
    cmd, skip_ind = get_command(content, 1)
    params = get_params(cmd)
    enumerate_style = params[1]

    enumerating = re.search(r'\w', enumerate_style).group(0)
    subpart = 0
    clean_content = clean_block(content)
    enumerated_string = process_content(clean_content)
    enumerating = ""
    return enumerated_string

@block_matcher(['itemize'])
def handle_itemize(content):
    global bulleting
    bulleting = True
    clean_content = clean_block(content)
    bulleted = process_content(clean_content)
    bulleting = False
    return bulleted

@block_matcher(['align', 'align*'])
def align_block(content):
    clean_content = clean_block(content)
    processed_content = process_content(clean_content)
    return "$$\\begin{align}" + processed_content + "\\end{align}$$"

@block_matcher(['tabular'])
def tabular_block(content):
    clean_content = clean_block(content)
    processed_content = process_content(clean_content)
    table = ""
    lines = processed_content.strip().splitlines()
    for i, line in enumerate(lines):
        processed_line = re.sub(r'\&', '|', line.strip())
        processed_line = re.sub(r'\\\\$', '', processed_line)
        table += '| ' + processed_line + ' |\n'

        # make table separator
        if i == 0:
            separator_line = "|---"
            for c in line:
                if c == '&':
                    separator_line += "|---"
            separator_line += '|\n'
            table += separator_line
    
    return table



#########################
# BEGIN FILE PROCESSING #
#########################

# process backslash commands
def process_command(command):
    for match in matchers:
        for cmd in match["commands"]:
            if command.startswith(cmd):
                return match["adjust"](command)
    return f"\\{command}"

# process blocks
def process_block(btype, content):
    for match in block_matchers:
        if btype in match["blocks"]:
            return match["adjust"](content)
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
            # for the weird \[\] syntax without $$
            if string[ind+1] == '[':
                str, skip_ind = find_bracket(string, ind+1)
                format_str = re.sub(r'\\]', '', str[1:])
                output_string += f"$${format_str}$$"
                continue

            # double backslash exception
            elif string[ind+1] == '\\':
                output_string += '\\'
                continue

            # get commands
            cmd, skip_ind = get_command(string, ind+1)
            
            # block vs single line command
            if cmd.startswith('begin'):
                content, block_type, skip_ind = get_block(string, ind)
                output_string += process_block(block_type, content)
            else:
                output_string += process_command(cmd)
            continue

        # catch math mode
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
