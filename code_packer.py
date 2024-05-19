import json


def write_instructions_to_file(instructions, mem_dict, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps([mem_dict]+[i.to_json() for i in instructions]))

"lisp -> asm | acc | harv | hw | tick -> instr | struct | stream | port | pstr | prob2"

