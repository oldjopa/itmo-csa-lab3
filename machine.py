from __future__ import annotations

import logging
import sys

from isa import AddressingType, Opcode, control_commands, read_code

ACC_MAX_VALUE = 2**31 - 1
ACC_MIN_VALUE = -(2**31) + 1


class DataPath:
    data_memory_size = None
    data_memory = None
    data_address = None
    acc = None
    input_buffer = None
    output_buffer = None

    def __init__(self, data_memory_size: int, input_buffer: list[str], memory_dict: dict):
        assert data_memory_size > 0, "Data_memory size should be non-zero"
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        for key in memory_dict.keys():
            self.data_memory[int(key)] = int(memory_dict[key])
        self.data_address = 0
        self.acc = 0
        self.data_reg = 0
        self.input_buffer = input_buffer
        self.input_buffer_pointer = 0
        self.output_buffer = []

    def signal_latch_data_addr_from_cu(self, addr: int):
        self.data_address = addr
        assert 0 <= self.data_address < self.data_memory_size, "out of memory: {}".format(self.data_address)

    def signal_latch_data_reg(self):
        self.data_reg = self.data_memory[self.data_address]

    def signal_input(self):
        self.acc = ord(self.input_buffer[self.input_buffer_pointer])
        self.input_buffer_pointer += 1

    def signal_output(self):
        symbol = chr(self.acc)
        logging.debug("output: %s << %s", "".join(self.output_buffer), symbol)
        self.output_buffer.append(symbol)

    def zero_flag(self):
        return self.acc == 0

    def neg_flag(self):
        return self.acc < 0

    def sub(self):
        self.set_acc(self.acc - self.data_reg)

    def add(self):
        self.set_acc(self.acc + self.data_reg)

    def mul(self):
        self.set_acc(int(self.acc * self.data_reg))

    def div(self):
        self.set_acc(self.acc // self.data_reg)

    def cla(self):
        self.acc = 0

    def signal_latch_data_addr_from_data_reg(self):
        self.data_address = self.data_reg

    def latch_memory(self):
        self.data_memory[self.data_address] = self.acc
        logging.debug("latch_memory: %s : %s", self.data_address, self.acc)

    def set_acc(self, value: int):
        if value > ACC_MAX_VALUE:
            self.acc = int(str(bin(self.acc))[len(str(bin(self.acc))) - 32 :], 2)
        elif value < ACC_MIN_VALUE:
            self.acc = int(str(bin(self.acc))[len(str(bin(self.acc))) - 32 :], 2)
        else:
            self.acc = value

    def inc(self):
        self.set_acc(self.acc + 1)

    def dec(self):
        self.set_acc(self.acc - 1)


class ControlUnit:
    instruction_memory = None
    program_counter = None
    data_path = None
    _tick = None

    def __init__(self, program, data_path: DataPath):
        self.instruction_memory = program
        self.program_counter = 0
        self.data_path = data_path
        self._tick = 0
        self.instruction = None

    def tick(self):
        self._tick += 1
        logging.info(self)

    def current_tick(self):
        return self._tick

    def signal_latch_program_counter(self, sel_next):
        if sel_next:
            self.program_counter += 1
        else:
            self.program_counter = int(self.instruction["arg"])

    def instruction_fetch_cycle(self):
        self.instruction = self.instruction_memory[self.program_counter].copy()
        # logging.info(self.instruction_memory)
        self.tick()

    def data_fetch_cycle(self):
        arg = self.instruction["arg"]
        addressing = self.instruction["addressingType"]
        if arg != "":
            self.data_path.signal_latch_data_addr_from_cu(arg)
            self.tick()
            self.data_path.signal_latch_data_reg()
            if addressing == AddressingType.INDIRECT:
                self.data_path.signal_latch_data_addr_from_cu(self.data_path.data_reg)
                self.tick()
                self.data_path.signal_latch_data_reg()
            self.tick()

    def decode_and_execute_instruction(self):
        logging.info("instruction: %s", self.instruction_memory[self.program_counter])
        # logging.info(self.data_path.data_memory)
        self.instruction_fetch_cycle()
        opcode = self.instruction["opcode"]

        if opcode not in control_commands + [Opcode.ST]:
            self.data_fetch_cycle()
        elif self.instruction["addressingType"] == AddressingType.INDIRECT and opcode == Opcode.ST:
            self.instruction["addressingType"] = 0
            self.data_fetch_cycle()
            self.instruction["arg"] = self.data_path.data_reg
            # logging.debug(self.instruction["arg"])
        elif self.instruction["addressingType"] == AddressingType.INDIRECT:
            self.data_fetch_cycle()
            self.instruction["arg"] = self.data_path.data_reg
            # logging.debug(self.instruction["arg"])
        sel_next = True

        if opcode == Opcode.LD:
            self.data_path.cla()
            self.data_path.add()
            self.tick()
        elif opcode == Opcode.ST:
            self.data_path.signal_latch_data_addr_from_cu(int(self.instruction["arg"]))
            self.tick()
            self.data_path.latch_memory()
            self.tick()
        elif opcode == Opcode.CLA:
            self.data_path.cla()
            self.tick()
        elif opcode == Opcode.INC:
            self.data_path.inc()
            self.tick()
        elif opcode == Opcode.DEC:
            self.data_path.dec()
            self.tick()
        elif opcode == Opcode.IN:
            if self.data_path.input_buffer_pointer == len(self.data_path.input_buffer):
                logging.error("end of Input")
                self.data_path.acc = 0
            else:
                self.data_path.signal_input()
            self.tick()
        elif opcode == Opcode.OUT:
            self.data_path.signal_output()
            self.tick()
        elif opcode == Opcode.HLT:
            raise StopIteration()
        elif opcode == Opcode.ADD:
            self.data_path.add()
            self.tick()
        elif opcode == Opcode.SUB:
            self.data_path.sub()
            self.tick()
        elif opcode == Opcode.DIV:
            self.data_path.div()
            self.tick()
        elif opcode == Opcode.MUL:
            self.data_path.mul()
            self.tick()
        elif opcode == Opcode.CMP:
            self.data_path.sub()
            self.tick()
        elif opcode == Opcode.JMP:
            sel_next = False
            self.tick()
        elif opcode == Opcode.BZ:
            sel_next = not self.data_path.zero_flag()
            self.tick()
        elif opcode == Opcode.BNZ:
            sel_next = self.data_path.zero_flag()
            self.tick()
        elif opcode == Opcode.BNN:
            sel_next = self.data_path.neg_flag()
            self.tick()
        elif opcode == Opcode.BN:
            sel_next = not self.data_path.neg_flag()
            self.tick()
        else:
            logging.error("not in commands: '" + opcode + "'")

        self.signal_latch_program_counter(sel_next=sel_next)
        self.tick()

    def __repr__(self):
        """Вернуть строковое представление состояния процессора."""
        state_repr = "TICK: {:3} PC: {:3} ADDR: {:3} MEM_OUT: {} DATA_REG {} ACC: {}".format(
            self._tick,
            self.program_counter,
            self.data_path.data_address,
            self.data_path.data_memory[self.data_path.data_address],
            self.data_path.data_reg,
            self.data_path.acc,
        )

        instr = self.instruction_memory[self.program_counter]
        opcode = instr["opcode"]
        instr_repr = str(opcode)

        if "arg" in instr:
            instr_repr += " {}".format(instr["arg"])

        if "term" in instr:
            term = instr["term"]
            instr_repr += "  ('{}'@{}:{})".format(term.symbol, term.line, term.pos)

        return "{} \t{}".format(state_repr, instr_repr)


def simulation(code, memory_dict, input_tokens, data_memory_size, limit):
    data_path = DataPath(data_memory_size, input_tokens, memory_dict)
    control_unit = ControlUnit(code, data_path)
    instr_counter = 0

    try:
        while instr_counter < limit:
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
    except EOFError:
        logging.warning("Input buffer is empty!")
    except StopIteration:
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded!")
    logging.info("output_buffer: %s", repr("".join(data_path.output_buffer)))
    return "".join(data_path.output_buffer), instr_counter, control_unit.current_tick()


def main(code_file, input_file):
    code, mem_dict = read_code(code_file)
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_token = []
        for char in input_text:
            input_token.append(char)

    output, instr_counter, ticks = simulation(
        code,
        mem_dict,
        input_tokens=input_token,
        data_memory_size=2048,
        limit=2000,
    )

    print("".join(output))
    print("instr_counter: ", instr_counter, "ticks:", ticks)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
