## Markdown From Tex

A short Python script I wrote to convert the .tex homework files in CS 70 into workable markdown files (primarily for Obsidian view).

Not perfect, but gets the job done.
May update to make it compatible with other tex commands when they show up on the homework.

Instructions for use:
1. Download the source code and put it in its own folder
2. Put the .tex file in the same folder as the scripts
3. Rename the .tex file to "input.tex"
4. In the terminal, run `python script.py`
5. Enjoy the outputted .md file

Note: You can edit the name of the input and/or output files in `script.py` if you want

Also note: If you are familiar with RegEx or manipulating strings in Python, feel free to also edit how the script parses and formats the files
