from helper import *

matchers = []
block_matchers = []
part = '`'
enumerating = False
subpart = 0
question = 0

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
    return f"## {clean_command(cmd)}\n"

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
    global part, subpart, enumerating
    if enumerating:
        subpart += 1
        return f"\n- ({int_to_roman(subpart)})"
    part = add_char(part, 1)
    return f"({part})"

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

@matcher(['LaTeX'])
def parse_latex(cmd):
    return "LaTeX"

#####################################################
#                                                   #
# This section handles \begin{} and \end{} commands #
#                                                   #
#####################################################

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

@block_matcher(['center'])
def center_block(cmd):
    return "```"

@block_matcher(['Parts'])
def parts_block(cmd):
    global part
    part = "`"
    return ""

@block_matcher(['enumerate'])
def enumerate_block(cmd):
    global enumerating
    enumerating = not enumerating
    return ""
