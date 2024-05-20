import code_packer
from isa import AddressingType

ONE_WORD = 1


class Instruction:
    def __init__(self, opcode, instruction_arg, instruction_address, addressing_type):
        self.opcode = opcode
        self.instruction_arg = instruction_arg
        self.addressing_type = addressing_type
        self.instruction_address = instruction_address

    def to_json(self):
        return {
            "opcode": self.opcode,
            "arg": self.instruction_arg,
            "addressingType": self.addressing_type,
        }

    def __repr__(self):
        return self.opcode + " " + str(self.instruction_arg) + "*" * self.addressing_type


class AddressManager:
    def __init__(self, instruction_pointer=0x0, buffer_pointer=0x1FF):
        self.memory = dict()
        self.variables = dict()
        self.address_pointer = instruction_pointer
        self.buffer_pointer = buffer_pointer
        self.instructions = []
        self.stack_pointer = 256
        self.memory[self.stack_pointer] = self.stack_pointer
        self.swap_pop = self.stack_pointer - 1
        self.functions = dict()
        self.depth = 0

    def _allocate_new_mem(self, n, value):
        self.memory[self.address_pointer] = value
        self.address_pointer += n
        return self.address_pointer - n

    def allocate_static_memory(self, value):
        return self._allocate_new_mem(ONE_WORD, value)

    def add_variable(self, varlabel, value):
        if isinstance(value, str):
            if "[" in value:
                length = int(value[value.index("[") + 1 : -1])
                self.variables[varlabel] = self._allocate_new_mem(length, length)
            else:
                self.variables[varlabel] = self.allocate_static_string(value)
        else:
            self.variables[varlabel] = self._allocate_new_mem(ONE_WORD, value)
        return self.variables[varlabel]

    def get_variable(self, varlabel):
        return self.variables[varlabel]

    def allocate_string(self, varlabel, string):
        self.variables[varlabel] = self._allocate_new_mem(varlabel, len(string))
        self._allocate_new_mem(ONE_WORD, len(string))
        for char in string:
            self._allocate_new_mem(ONE_WORD, ord(char))
            self.address_pointer += 1 + len(string)
        return self.variables[varlabel]

    def allocate_buffer_memory(self):
        self.buffer_pointer += 1
        return self.buffer_pointer - 1

    def free_buffer_memory(self):
        self.buffer_pointer -= 1
        return self.buffer_pointer

    def add_instruction(self, instruction, arg="", addressing=AddressingType.DIRECT):
        self.instructions.append(Instruction(instruction, arg, self.get_instruction_pointer() + 1, addressing))

    def get_instruction_pointer(self):
        return len(self.instructions) - 1

    def set_arg(self, pointer: int, arg: int):
        self.instructions[pointer].instruction_arg = arg

    def get_instructions(self):
        for pointer, instruction in enumerate(self.instructions):
            print(str(pointer), " : ", str(instruction))

    def write_to_file(self, filename="out"):
        self.get_instructions()
        code_packer.write_instructions_to_file(self.instructions, self.memory, filename)

    def get_address_for(self, token):
        if not isinstance(token, list):
            if token in self.variables.keys():
                return self.variables[token]
        try:
            number = int(token)
            return self.allocate_static_memory(number)
        except ValueError:
            return self.allocate_static_string(token)

    def enter_func(self):
        self.depth += 1

    def exit_func(self):
        self.depth -= 1

    def add_function(self, function):
        self.functions[function] = self.get_instruction_pointer() + 1

    def get_function(self, function):
        return self.functions[function]

    def allocate_static_string(self, string: str):
        string = string.replace("\\\\n", "\n")
        pointer = self._allocate_new_mem(ONE_WORD, len(string) - 2)
        for c in string[1:-1]:
            self._allocate_new_mem(ONE_WORD, ord(c))
        # print(pointer, string)
        return pointer

    def allocate_array(self, length):
        self._allocate_new_mem(length, length)
