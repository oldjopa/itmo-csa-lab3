"""Instruction set architecture
"""

import json

from enum import Enum


class AddressingType(int, Enum):
    DIRECT = 0
    INDIRECT = 1


class Opcode(str, Enum):
    '''Команды'''
    DEC = 'dec'
    INC = 'inc'
    IN = 'in'
    OUT = 'out'
    CLA = 'cla'
    HLT = 'hlt'
    ST = 'st'
    LD = 'ld'
    ADD = 'add'
    SUB = 'sub'
    DIV = 'div'
    MUL = 'mul'
    CMP = 'cmp'
    JMP = 'jmp'
    BZ = 'bz'
    BNZ = 'bnz'
    BNN = 'bnn'
    BN = 'bn'
    AND = 'and'
    OR = 'or'



control_commands = [Opcode.BZ, Opcode.BNZ, Opcode.BN, Opcode.JMP, Opcode.BNN]


def write_code(filename, code):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, indent=4))


def read_code(filename):
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())
    return code[1:], code[0]
