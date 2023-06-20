from helper import get_command
from commands import matchers
import re
import os

# get file name
input_file_name = ''
output_file_name = ''

for file in os.listdir('./'):
    if file.endswith('.tex'):
        input_file_name = file
        output_file_name = file[:-4] + ".md"
        break

if input_file_name == '':
    raise RuntimeError("No TeX file detected! Move the desired TeX file you want to convert to .md in the same directory (folder) as this script.")

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
contents = re.sub(r'(?<=\([a-z]\))\n', ' ', contents)
contents = re.sub(r'  ', ' ', contents)
contents = re.sub(r'»\n{0,}', '\n\n', contents)
contents = re.sub(r'\n{0,}«', '\n\n\n\n', contents)
contents = re.sub(r'†\n+', '\n\n', contents)
contents = re.sub(r'†', '', contents)

# write to output
with open(output_file_name, 'w') as output:
    output.write(contents)
