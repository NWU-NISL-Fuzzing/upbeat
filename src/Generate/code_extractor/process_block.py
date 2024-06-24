import re

from class_for_info.block_info import CodeBlockInfo


regex_for_var = r"(let|mutable|set|use) (.*?) [=w\/+-] (.*?);"
regex_for_var_name = r"[A-Za-z0-9_]+"


def is_first_part(line: str):
    tag_for_first = ['while', 'for ', 'for(', 'if ', 'if(',  'within', 'repeat', 'using']
    for tag in tag_for_first:
        if tag in line:
            return True
    if 'use' in line and '{' in line:
        return True
    return False


def is_second_part(line: str):
    return 'elif' in line or 'else' in line or 'until' in line or 'fixup' in line or 'apply ' in line


def specify_namespace(line: str) -> str:
    if "Diag." in line:
        line = line.replace("Diag.", "Microsoft.Quantum.Diagnostics.")
    elif "AssertPhase(" in line and ".AssertPhase(" not in line:
        line = line.replace("AssertPhase", "Microsoft.Quantum.Diagnostics.AssertPhase")
    if "Meas." in line:
        line = line.replace("Meas.", "Microsoft.Quantum.Measurement.")
    if "ML." in line:
        line = line.replace("ML.", "Microsoft.Quantum.MachineLearning.")
    if "ApplyIfZero" in line:
        line = line.replace("ApplyIfZero", "Microsoft.Quantum.Canon.ApplyIfZero")
    elif "ApplyIfOne" in line:
        line = line.replace("ApplyIfOne", "Microsoft.Quantum.Canon.ApplyIfOne")
    elif "ApplyIfElse" in line:
        line = line.replace("ApplyIfElse", "Microsoft.Quantum.Canon.ApplyIfElse")
    elif "Convert." in line:
        line = line.replace("Convert.", "")
    return line


if __name__ == "__main__":
    func = ['let var = Ceil(\n', '0\n', ');\n']
    code_string = "".join(func)
    block_list = get_block_list(func)
    for block in block_list:
        print(block.content_list)
