import json
import struct

# Пути к файлам и диапазон памяти для интерпретатора
input_path = 'C://Users//Alexander//input.txt'       # Исходный файл с программой для ассемблера
binary_path = 'output.bin'     # Бинарный файл, создаваемый ассемблером
log_path = 'log.json'          # Лог-файл в формате JSON
output_path = 'result.json'    # Результат интерпретации в формате JSON
memory_range = (200, 208)          # Диапазон памяти для сохранения результата

# Размеры памяти и регистров
MEMORY_SIZE = 1024
REGISTER_COUNT = 256

# Определение команд УВМ
COMMANDS = {
    'LOAD_CONST': 192,
    'READ_MEM': 247,
    'WRITE_MEM': 115,
    'BIN_OP_LE': 83
}

# Классы команд

class LoadConst:
    def __init__(self, b, c):
        self.a = COMMANDS['LOAD_CONST']
        self.b = b
        self.c = c

    def to_binary(self):
        return struct.pack('<BBH', self.a, self.b, self.c)

    def to_dict(self):
        return {'A': self.a, 'B': self.b, 'C': self.c}


class ReadMem:
    def __init__(self, b, c):
        self.a = COMMANDS['READ_MEM']
        self.b = b
        self.c = c

    def to_binary(self):
        return struct.pack('<BBH', self.a, self.b, self.c)

    def to_dict(self):
        return {'A': self.a, 'B': self.b, 'C': self.c}


class WriteMem:
    def __init__(self, b, c, d):
        self.a = COMMANDS['WRITE_MEM']
        self.b = b
        self.c = c
        self.d = d

    def to_binary(self):
        return struct.pack('4B', self.a, self.b, self.c, self.d)

    def to_dict(self):
        return {'A': self.a, 'B': self.b, 'C': self.c, 'D': self.d}


class BinOpLE:
    def __init__(self, b, c, d, e):
        self.a = COMMANDS['BIN_OP_LE']
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def to_binary(self):
        return struct.pack('5B', self.a, self.b, self.c, self.d, self.e)

    def to_dict(self):
        return {'A': self.a, 'B': self.b, 'C': self.c, 'D': self.d, 'E': self.e}


# Функция ассемблера
def assemble():
    with open(input_path, 'r') as f:
        lines = f.readlines()

    binary_instructions = []
    log_data = []

    for line in lines:
        parts = line.strip().split()
        cmd = parts[0]
        args = list(map(int, parts[1:]))

        if cmd == 'LOAD_CONST':
            instr = LoadConst(*args)
        elif cmd == 'READ_MEM':
            instr = ReadMem(*args)
        elif cmd == 'WRITE_MEM':
            instr = WriteMem(*args)
        elif cmd == 'BIN_OP_LE':
            instr = BinOpLE(*args)
        else:
            raise ValueError(f"Unknown command {cmd}")

        binary_instructions.append(instr.to_binary())
        log_data.append(instr.to_dict())

    # Запись бинарного файла
    with open(binary_path, 'wb') as bf:
        for instr in binary_instructions:
            bf.write(instr)

    # Запись лога в JSON
    with open(log_path, 'w') as lf:
        json.dump(log_data, lf, indent=4)


# Интерпретатор

class VM:
    def __init__(self):
        self.memory = [0] * MEMORY_SIZE
        self.registers = [0] * REGISTER_COUNT

    def execute(self):
        with open(binary_path, 'rb') as bf:
            instructions = bf.read()
        i = 0
        while i < len(instructions):
            a = instructions[i]
            if a == COMMANDS['LOAD_CONST']:
                _, b, c = struct.unpack('BBH', instructions[i:i+4])
                self.registers[b] = c
                i+=4
            elif a == COMMANDS['READ_MEM']:
                _, b, c = struct.unpack('<BBH', instructions[i:i+4])
                self.registers[b] = self.memory[c]
                i+=4
            elif a == COMMANDS['WRITE_MEM']:
                _, b, c, d = struct.unpack('4B', instructions[i:i+4])
                address = self.registers[b] + d
                self.memory[address] = self.registers[c]
                i+=4
            elif a == COMMANDS['BIN_OP_LE']:
                _, b, c, d, e = struct.unpack('5B', instructions[i:i+5])
                op1 = self.registers[c]
                op2 = self.memory[self.registers[d] + e]
                self.memory[self.registers[b]] = 1 if op1 <= op2 else 0
                i+=5

        # Сохранение выбранной области памяти
        result_data = self.memory[memory_range[0]:memory_range[1]]

        with open(output_path, 'w') as of:
            json.dump(result_data, of, indent=4)


# Основная функция
if __name__ == '__main__':
    print("Запуск ассемблера...")
    assemble()
    print("Ассемблирование завершено. Запуск интерпретатора...")
    vm = VM()
    vm.execute()
    print("Интерпретация завершена.")

