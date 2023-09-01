from error import Error


class Parser:
    def __init__(self, code):
        self.code = self.parse(code)

    def parse(self, code):
        code = self.parse_require(code)
        code = self.parse_comments(code)
        code = self.parse_keywords(code)
        code = self.parse_braces(code)
        code = self.parse_functions(code)
        code = self.clean_code(code)

        with open('output.py', 'w') as f:
            f.write(code)

        return code

    def parse_comments(self, code):
        for line in code.splitlines():
            if '//' in line and not self.in_string('//', line):
                if line[:2] == '//':
                    code = code.replace(line, '')

                else:
                    new_line = line.partition('//')[0]

                    code = code.replace(line, new_line)

        return code

    def parse_require(self, code):
        require_name = ''

        for line in code.splitlines():
            words = line.split()

            for word_number, word in enumerate(words):
                if word == 'require' and not self.in_string(word, line):
                    require_name = words[word_number + 1]

                    code = code.replace(line, '')

                    with open(f'{require_name.removesuffix(";")}.vs', 'r') as f:
                        code = f'{f.read()}\n{code}'

                elif word == 'native' and not self.in_string(word, line):
                    code = code.replace(line, line.replace('native ', 'import '))

        return code

    def parse_keywords(self, code):
        for line in code.splitlines():
            if 'this' in line and not self.in_string('this', line):
                code = code.replace(line, line.replace('this', 'self'))

        for line in code.splitlines():
            if 'true' in line and not self.in_string('true', line):
                code = code.replace(line, line.replace('true', 'True'))

        for line in code.splitlines():
            if 'false' in line and not self.in_string('false', line):
                code = code.replace(line, line.replace('false', 'False'))

        for line in code.splitlines():
            if 'null' in line and not self.in_string('null', line):
                code = code.replace(line, line.replace('null' 'None'))

        for line in code.splitlines():
            if 'else if' in line and not self.in_string('else if', line):
                code = code.replace(line, line.replace('else if', 'elif'))

        return code

    def parse_braces(self, code):
        left_braces_count = 0
        right_braces_count = 0

        for line in code.splitlines():
            if '{' in line:
                line_chars = list(line)

                strings_count = 0

                for char in line_chars:
                    if char in ['\'', '"']:
                        strings_count += 1

                    if char == '{':
                        left_braces_count += 1

                        break

        for line in code.splitlines():
            if '}' in line:
                line_chars = list(line)

                strings_count = 0

                for i in range(len(line_chars)):
                    if line_chars[i] in ['\'', '"']:
                        strings_count += 1

                    if line_chars[i] == '}':
                        right_braces_count += 1

                        break

        if left_braces_count != right_braces_count:
            Error('Braces amount is not equal')

        new_code = ''

        lines = code.splitlines()

        for line in lines:
            line = line.strip()

            instructions = line.split(';')

            for i in range(len(instructions)):
                instructions[i] = instructions[i].strip()

            if not instructions[-1]:
                if len(instructions) > 1:
                    instructions[-2] += ';'
                
                instructions.pop(-1)

            for i in range(len(instructions) - 1):
                instructions[i] += ';'

            new_instructions = [''] * len(instructions)

            for i, instruction in enumerate(instructions):
                instruction_chars = list(instruction)
                strings_count = 0
                first_space = None
                done = False
                stop = 0

                while not done:
                    if stop == len(instruction_chars) - 1:
                        done = True

                    for j in range(stop, len(instruction_chars)):
                        if instruction_chars[j] in ['\'', '"']:
                            strings_count += 1

                        if not strings_count % 2:
                            if instruction_chars[j] == ' ':
                                if first_space is None:
                                    first_space = j

                            else:
                                if instruction_chars[j] == ';':
                                    instruction_chars[j] = '\n'

                                elif instruction_chars[j] == '{':
                                    if first_space is None:
                                        instruction_chars = instruction_chars[:j] + list(':\n{') + list(''.join(instruction_chars[j + 1:]).lstrip())

                                        stop = j + 3

                                    else:
                                        instruction_chars = instruction_chars[:first_space] + list(':\n{') + list(''.join(instruction_chars[j + 1:]).lstrip())

                                        stop = first_space + 3

                                    break

                                elif instruction_chars[j] == '}':
                                    if first_space is None:
                                        instruction_chars = instruction_chars[:j] + list('}\n') + list(''.join(instruction_chars[j + 1:]).lstrip())

                                        stop = j + 2

                                    else:
                                        instruction_chars = instruction_chars[:first_space] + list('}\n') + list(''.join(instruction_chars[j + 1:]).lstrip())

                                        stop = first_space + 2

                                    break

                                first_space = None

                    else:
                        done = True

                new_instructions[i] += ''.join(instruction_chars)

            line = ''.join(new_instructions)

            if 'class' in line and self.in_string('class', line):
                line = '\n' + ' '.join(line.split())

            if 'function' in line:
                if line.partition('function')[0].count('\'') and not line.partition('function')[0].count('"') % 2:
                    words = line.split()

                    for word_number, word in enumerate(words):
                        if word == 'function' and \
                                    not line.partition('function')[2].count('\'') % 2 and \
                                    not line.partition('function')[2].count('"') % 2:
                            words[word_number] = 'def'

                            break

                    line = ' '.join(words)

            left_brace_expression = ''.join(line.split())

            if not self.in_string('}', line):
                line = line.replace('}', '#endindent\n')

            if not self.in_string('{', line):
                line = line.replace('{', '#startindent\n')

            new_code += line

        return new_code

    def parse_functions(self, code):
        for line in code.splitlines():
            if 'function' in line and not self.in_string('function', line):
                code = code.replace(line, line.replace('function', 'def'))

        for line in code.splitlines():
            if 'def new' in line and not self.in_string('def new', line):
                code = code.replace(line, line.replace('def new', 'def __init__'))

        return code

    def clean_code(self, code):
        lines = code.splitlines()

        for line_number, line in enumerate(lines):
            if line.strip().startswith(':'):
                lines[line_number - 1] += ':'
                lines[line_number] = ''

        new_code = ''

        for line in lines:
            new_code += f'{line}\n'

        code = new_code

        lines = new_code.splitlines()

        new_code = ''

        indent_count = 0

        for line in lines:
            if '#startindent' in line:
                if not self.in_string('#startindent', line, check_multiple=True):
                    indent_count += 1

            elif '#endindent' in line:
                if not self.in_string('#endindent', line, check_multiple=True):
                    indent_count -= 1

            new_code += f'{"    " * indent_count}{line}\n'

        code = new_code

        new_code = ''

        for line in code.splitlines():
            if '#startindent' in line and not self.in_string('#startindent', line):
                line = line.replace('#startindent', '')

            if '#endindent' in line and not self.in_string('#endindent', line):
                line = line.replace('#endindent', '')

            if line.strip():
                new_code += f'{line}\n'

        

        code = new_code

        new_code = ''

        for line in code.splitlines():
            if line != line.strip('\t\r\n'):
                line = line.strip('\t\r\n')

                new_code += line

            else:
                new_code += f'{line}\n'

        code = '\n'.join([ll.rstrip() for ll in new_code.splitlines() if ll.strip()])

        return new_code

    @staticmethod
    def in_string(phrase, line, check_multiple=False):
        if phrase not in line:
            return False

        if line.count(phrase) > 1:
            return check_multiple

        left_side = line.partition(phrase)[0]

        return left_side.count('\'') % 2 or left_side.count('"') % 2
