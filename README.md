## Markdown From Tex

A short Python script I wrote to convert the .tex homework files in CS 70 into workable markdown files (primarily for Obsidian view).

Not perfect, but gets the job done.
May be updated to make it compatible with other tex commands when they show up on the homework in the future.

Requirements:
- Have Python installed (tested in Python 3.10.11)

Instructions for use:
1. Download `converter.py`
2. Put the .tex file in the same folder as `converter.py`
3. In the terminal, run `python converter.py`
    - Alternatively: Type `python converter.py <file_path>` in the terminal, replacing `<file_path>` with the path to the .tex file
4. The .md file will be outputted and ready to go in the same folder

Note: Feel free to edit how the files are parsed and formatted at the bottom of `converter.py`
