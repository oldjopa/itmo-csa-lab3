from address_manager import AddressManager
from isa import AddressingType, Opcode

"""
---no addr---
cla
inc
dec
---arithmetics---
add
sub
cmp
div
mul
and
or
---memory---
ld
st
---branch---
bz
bnz
bn
bnn
jmp
"""


def translate_req_order(address_manager, args, op):
    if isinstance(args[0], list) and isinstance(args[1], list):
        translate_level(args[1], address_manager)
        address_manager.add_instruction(Opcode.ST, address_manager.allocate_buffer_memory())
        translate_level(args[0], address_manager)
        address_manager.add_instruction(op, address_manager.free_buffer_memory())
    elif isinstance(args[0], list):
        translate_level(args[0], address_manager)
        address_manager.add_instruction(op, address_manager.get_variable(args[1]))
    elif isinstance(args[1], list):
        translate_level(args[1], address_manager)
        address_manager.add_instruction(Opcode.ST, address_manager.allocate_buffer_memory())
        address_manager.add_instruction(Opcode.LD, args[0])
        address_manager.add_instruction(op, address_manager.free_buffer_memory())
    else:
        address_manager.add_instruction(Opcode.LD, args[0])
        address_manager.add_instruction(op, args[1])


def translate_no_order(address_manager, args, op):
    if isinstance(args[0], list) and isinstance(args[1], list):
        translate_level(args[1], address_manager)
        address_manager.add_instruction(Opcode.ST, address_manager.allocate_buffer_memory())
        translate_level(args[0], address_manager)
        address_manager.add_instruction(op, address_manager.free_buffer_memory())
    elif isinstance(args[0], list):
        translate_level(args[0], address_manager)
        address_manager.add_instruction(op, args[1])
    elif isinstance(args[1], list):
        translate_level(args[1], address_manager)
        address_manager.add_instruction(op, args[0])
    else:
        address_manager.add_instruction(Opcode.LD, args[0])
        address_manager.add_instruction(op, args[1])


def add(address_manager, args):
    translate_no_order(address_manager, args, Opcode.ADD)


def sub(address_manager, args):
    translate_req_order(address_manager, args, Opcode.SUB)


def mul(address_manager, args):
    translate_no_order(address_manager, args, Opcode.MUL)


def div(address_manager, args):
    translate_req_order(address_manager, args, Opcode.DIV)


#  lint idi nahui def op_and(address_manager, args):
#  lint idi nahui     translate_no_order(address_manager, args, Opcode.AND)
# lint idi nahui
# lint idi nahui
#  lint idi nahui def op_or(address_manager, args):
#  lint idi nahui     translate_no_order(address_manager, args, Opcode.OR)


def cond_if(address_manager: AddressManager, args):
    if isinstance(args[0], list):
        translate_level(args[0], address_manager)
    else:
        address_manager.add_instruction(Opcode.LD, args[0])
    address_manager.add_instruction(Opcode.BZ)
    if_pointer = address_manager.get_instruction_pointer()
    translate_level(args[1], address_manager)
    if len(args) > 2:
        address_manager.set_arg(if_pointer, address_manager.get_instruction_pointer() + 2)
        address_manager.add_instruction(Opcode.JMP)
        if_pointer2 = address_manager.get_instruction_pointer()
        translate_level(args[2], address_manager)
        address_manager.set_arg(if_pointer2, address_manager.get_instruction_pointer() + 1)
    else:
        address_manager.set_arg(if_pointer, address_manager.get_instruction_pointer() + 1)


def loop_while(address_manager: AddressManager, args):
    start_while = address_manager.get_instruction_pointer() + 1
    if isinstance(args[0], list):
        translate_level(args[0], address_manager)
    else:
        address_manager.add_instruction(Opcode.LD, args[0])
    address_manager.add_instruction(Opcode.BZ)
    endwhile_pointer = address_manager.get_instruction_pointer()
    translate_level(args[1], address_manager)
    address_manager.add_instruction(Opcode.JMP, start_while)
    address_manager.set_arg(endwhile_pointer, address_manager.get_instruction_pointer() + 1)


def fun_print(address_manager: AddressManager, args):
    if isinstance(args[0], list):
        translate_level(args[0], address_manager)
    else:
        address_manager.add_instruction(Opcode.LD, args[0])
    address_manager.add_instruction(Opcode.OUT)


def fun_input(address_manager: AddressManager, args):
    address_manager.add_instruction(Opcode.IN)
    address_manager.add_instruction(Opcode.ST, args[0])


def fun_readline(address_manager: AddressManager, args):
    pointer = address_manager.get_address_for(args[0] + 1)
    counter = address_manager.allocate_static_memory(0)
    newline = address_manager.allocate_static_memory(ord("\n"))
    address_manager.add_instruction(Opcode.IN)
    branch_pointer = address_manager.get_instruction_pointer()
    address_manager.add_instruction(Opcode.ST, pointer, AddressingType.INDIRECT)
    address_manager.add_instruction(Opcode.CMP, newline)
    address_manager.add_instruction(Opcode.BZ, address_manager.get_instruction_pointer() + 9)
    address_manager.add_instruction(Opcode.LD, pointer)
    address_manager.add_instruction(Opcode.INC)
    address_manager.add_instruction(Opcode.ST, pointer)
    address_manager.add_instruction(Opcode.LD, counter)
    address_manager.add_instruction(Opcode.INC)
    address_manager.add_instruction(Opcode.ST, counter)
    address_manager.add_instruction(Opcode.JMP, branch_pointer)
    address_manager.add_instruction(Opcode.LD, counter)
    address_manager.add_instruction(Opcode.ST, args[0])
    address_manager.free_buffer_memory()


def fun_print_string(address_manager: AddressManager, args):
    string_pointer = address_manager.get_address_for(args[0])
    out_counter = address_manager.allocate_buffer_memory()
    address_manager.add_instruction(Opcode.LD, args[0])
    address_manager.add_instruction(Opcode.ST, out_counter)
    address_manager.add_instruction(Opcode.LD, string_pointer)
    branch_pointer = address_manager.get_instruction_pointer()
    address_manager.add_instruction(Opcode.INC)
    address_manager.add_instruction(Opcode.ST, string_pointer)
    address_manager.add_instruction(Opcode.LD, string_pointer, AddressingType.INDIRECT)
    address_manager.add_instruction(Opcode.OUT)
    address_manager.add_instruction(Opcode.LD, out_counter)
    address_manager.add_instruction(Opcode.DEC)
    address_manager.add_instruction(Opcode.ST, out_counter)
    address_manager.add_instruction(Opcode.BNZ, branch_pointer)
    address_manager.free_buffer_memory()


def logic_operation(address_manager, args, branch_condition, req_order=True):
    if req_order:
        translate_req_order(address_manager, args, Opcode.CMP)
    else:
        translate_no_order(address_manager, args, Opcode.CMP)
    address_manager.add_instruction(branch_condition, address_manager.get_instruction_pointer() + 4)
    address_manager.add_instruction(Opcode.CLA)
    address_manager.add_instruction(Opcode.BZ, address_manager.get_instruction_pointer() + 4)
    address_manager.add_instruction(Opcode.CLA)
    address_manager.add_instruction(Opcode.INC)


def compare_eq(address_manager, args):
    logic_operation(address_manager, args, Opcode.BZ, False)


def compare_not_eq(address_manager, args):
    logic_operation(address_manager, args, Opcode.BNZ, False)


def compare_more(address_manager, args):
    logic_operation(address_manager, args, Opcode.BNN)


def compare_less(address_manager, args):
    logic_operation(address_manager, args, Opcode.BN)


# def compare_more_eq(address_manager, args):
#     pass
#
#
# def compare_less_eq(address_manager, args):
#     pass


def create_var(address_manager, args):
    try:
        args[1] = int(args[1])
    except ValueError:
        pass
    pointer = address_manager.add_variable(args[0], args[1])
    print("loaded " + str(args[1]) + " into " + str(pointer))


def set_var(address_manager, args):
    if isinstance(args[1], list):
        translate_level(args[1], address_manager)
    else:
        address_manager.add_instruction(Opcode.LD, args[1])
    # lint pointer = address_manager.get_variable(args[0])
    address_manager.add_instruction(Opcode.ST, args[0])


def translate_level(operations, address_manager):
    if isinstance(operations[0], list):  # скобка с чисто выражениями
        for op in operations:
            translate_level(op, address_manager)
    if len(operations) == 1:
        try:
            address_manager.add_instruction(Opcode.LD, address_manager.get_address_for(operations[0]))
        except Exception:
            print("no such variable: " + operations[0])
    operation = operations[0]
    funcname = ""
    if operation == "funcall":
        funcname = operations[1]
        operations = operations[1:]
    for i, op in enumerate(operations[1:]):
        if not isinstance(op, list) and operation not in define:
            operations[i + 1] = address_manager.get_address_for(op)
    if operation == "funcall":
        operations = [funcname] + operations
    return instructions_mapping[operation](address_manager, operations[1:])


def push(address_manager: AddressManager):
    address_manager.add_instruction(Opcode.ST, address_manager.swap_pop)
    address_manager.add_instruction(Opcode.LD, address_manager.stack_pointer)
    address_manager.add_instruction(Opcode.INC)
    address_manager.add_instruction(Opcode.ST, address_manager.stack_pointer)
    address_manager.add_instruction(Opcode.LD, address_manager.swap_pop)
    address_manager.add_instruction(Opcode.ST, address_manager.stack_pointer, addressing=AddressingType.INDIRECT)


def pop(address_manager: AddressManager, addr):
    address_manager.add_instruction(Opcode.LD, address_manager.stack_pointer, addressing=AddressingType.INDIRECT)
    address_manager.add_instruction(Opcode.ST, addr)
    address_manager.add_instruction(Opcode.LD, address_manager.stack_pointer)
    address_manager.add_instruction(Opcode.DEC)
    address_manager.add_instruction(Opcode.ST, address_manager.stack_pointer)


def define_function(address_manager: AddressManager, args):
    funcname = args[0]
    variables = args[1]
    address_manager.add_instruction(Opcode.JMP, "end_def")
    ip = address_manager.get_instruction_pointer()
    var_copy = address_manager.variables.copy()
    address_manager.add_function(funcname)
    address_manager.variables = dict()
    for v in variables:
        address_manager.add_variable(v, 0)
        pop(address_manager, address_manager.get_variable(v))
    translate_level(args[2], address_manager)
    address_manager.variables = var_copy
    address_manager.add_instruction(Opcode.JMP, address_manager.stack_pointer, addressing=AddressingType.INDIRECT)
    address_manager.set_arg(ip, address_manager.get_instruction_pointer() + 1)


def call_function(address_manager: AddressManager, args):
    funcname = args[0]
    address_manager.enter_func()
    addr = address_manager.allocate_static_memory(0)
    address_manager.add_instruction(Opcode.LD, addr)
    push(address_manager)
    for op in args[1:][0]:
        translate_level(op, address_manager)
        push(address_manager)
    address_manager.add_instruction(Opcode.JMP, address_manager.get_function(funcname))
    address_manager.memory[addr] = address_manager.get_instruction_pointer() + 1
    address_manager.add_instruction(Opcode.ST, address_manager.swap_pop)
    address_manager.add_instruction(Opcode.LD, address_manager.stack_pointer)
    address_manager.add_instruction(Opcode.DEC)
    address_manager.add_instruction(Opcode.ST, address_manager.stack_pointer)
    address_manager.add_instruction(Opcode.LD, address_manager.swap_pop)
    address_manager.exit_func()


default_func = ["address_manager.add_instruction", "input"]
math = [
    "+",
    "-",
    "*",
    "/",
]
logic = ["and", "or"]
comparators = ["=", ">=", ">", "<", "<="]
operators = ["var", "set", "defun", "loop"]
define = ["var", "defunc"]
loop = ["for", "in", "from", "do"]
const = ["T", "Nil"]

instructions_mapping = {
    "+": add,
    "-": sub,
    "*": mul,
    "/": div,
    "if": cond_if,
    "while": loop_while,
    "var": create_var,
    "set": set_var,
    "printc": fun_print,
    "print_string": fun_print_string,
    "input": fun_input,
    "read_line": fun_readline,
    "=": compare_eq,
    "!=": compare_not_eq,
    ">": compare_more,
    "<": compare_less,
    # "and": op_and,
    # "or": op_or,
    "defunc": define_function,
    "funcall": call_function,
    # "<=": compare_less_eq,
    # ">=": compare_more_eq
}
