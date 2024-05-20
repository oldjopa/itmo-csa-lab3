"""
s_expression ::= atomic_symbol | "(" s_expression "." s_expression ")"
atomic_symbol ::= letter atom_part
atom_part ::= empty | letter atom_part | number atom_part
letter ::= "a" | "b" | " ..." | "z"
number ::= "1" | "2" | " ..." | "9"
empty ::= " "
newline ::= "\\n"
"""

import sys
from instructions import *
from address_manager import AddressManager


# lisp -> asm | acc | harv | hw | tick -> instr | struct | stream | port | pstr | prob2 | cache


def tokenize(content: str):
    token = ""
    skip_space = False
    for ch in content:
        if ch == " " and not skip_space:
            if len(token) > 0:
                yield token
                token = ""
            continue
        elif ch in "()":
            if len(token) > 0:
                yield token
                token = ""
            yield ch
            continue
        else:
            if ch == '"':
                skip_space = not skip_space
            token += ch
    if len(token) > 0:
        yield token
    yield None


def parse(content: str):
    sexp = []
    stack = []
    tokenizer = tokenize(content)
    while True:
        token = next(tokenizer)
        if token is None:
            break
        elif token in "(":
            stack.append(sexp)
            sexp = []
        elif token in ")":
            temp = sexp
            sexp = stack.pop()
            sexp.append(temp)
        else:
            sexp.append(token)
    return sexp


def translate(in_filename, out_filename):
    with open(in_filename, "r") as code:
        text = code.read().replace("\n", "")
        operations = parse(text)
        # print(operations)
        address_manager = AddressManager()
        translate_level(operations, address_manager)
        address_manager.add_instruction(Opcode.HLT)
        print(address_manager.memory)
        # address_manager.get_instructions()
        address_manager.write_to_file(out_filename)


def main(in_filename, out_filename):
    translate(in_filename, out_filename)


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    main(sys.argv[1], sys.argv[2])
