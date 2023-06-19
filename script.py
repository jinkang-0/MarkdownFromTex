from helper import get_command
from commands import matchers

# config
input_file_name = 'input.tex'
output_file_name = 'output.md'

# read input file
with open(input_file_name, 'r') as f:
    input = f.read()

# process backslash commands
def process_command(command):
    for match in matchers:
        for cmd in match["commands"]:
            if command.startswith(cmd):
                return match["adjust"](command)
    return ""

# vars
contents = ""
processed = ""
skip_commands = False
skip_ind = -1

# process contents
input = "\n".join([line.strip() for line in input.split('\n')])
for ind, char in enumerate(input):
    if ind < skip_ind:
        continue

    # filter content to process commands
    if not skip_commands and char == '\\':
        cmd, skip_ind = get_command(input, ind+1)
        processed += process_command(cmd)
        continue
    elif char == '$':
        skip_commands = not skip_commands
    processed += char

# beautify processed contents
contents = processed.strip() + '\n'

##### add any other post-modifications here #####

# write to output
with open(output_file_name, 'w') as output:
    output.write(contents)
