from collections import deque
import io
import tokenize
import sys


# Здравствуйте, обратите внимение на то, как у меня реализован if (функция iff). Теперь в if можно писать условия,
# оперирующие с values_stack, при этом сам стек не изменится

# в самом начале отделяем все функции и процедуры от основного кода (всё, что ограниченно : и ;)
# В терминологии этого задания функция (функция - то что с ключевым словл return) добавит на вершину стека
# только то, что вернёт функция. А процедура просто добавит свой код в конец code основной Machine


class Stack(deque):
    push = deque.append

    def top(self):
        return self[-1]


def parse(text):
    stream = io.StringIO(text)
    tokens = tokenize.generate_tokens(stream.readline)

    for toknum, tokval, _, _, _ in tokens:
        if toknum == tokenize.NUMBER:
            yield int(tokval)
        else:
            yield tokval


def exec_func(name, code, now, values_stack, call_stack, heap, heap_func):
    func = heap_func[name]
    if func[0] == 'proc':
        return code[:now + 1] + func[1] + code[now + 1:]
    else:
        func_machine = Machine('', old_code=func[1][:-1],
                               values_stack=values_stack,
                               call_stack=call_stack,
                               heap=heap,
                               heap_func=heap_func)
        func_machine.run()
        return func_machine.top()


def parse_funcs(lst):
    result_dict = dict()
    last_index = None
    func_name = None
    for i in range(len(lst)):
        if lst[i] == ':':
            last_index = i
            func_name = lst[i + 1]
        elif lst[i] == ';':
            if lst[i - 1] == 'return':
                result_dict[func_name] = ('func', lst[last_index + 2:i])
            else:
                result_dict[func_name] = ('proc', lst[last_index + 2:i])

    return result_dict


def parse_help(lst):
    result = []
    for elem in lst:
        if isinstance(elem, str):
            result.append(elem.replace("\'", ""))
        else:
            result.append(elem)
    return result


def del_func(lst):
    result = []
    flag = 0
    for elem in lst:
        if flag == 1 and elem == ';':
            flag = 0
        elif elem == ':':
            flag = 1
        elif flag == 0:
            result.append(elem)
    return result


class Machine:
    def __init__(self, code, old_code=[], now=0, values_stack=Stack(),
                 call_stack=Stack(), heap=dict(), heap_func=dict()):
        self.values_stack = values_stack
        self.call_stack = call_stack
        self.code = list(parse(code))[:-2]
        self.heap_func = parse_funcs(self.code)
        self.code = del_func(self.code)
        self.heap_func.update(heap_func)
        self.code = parse_help(old_code + self.code)
        self.now = now
        self.heap = heap
        self.slo = {
            '+': self.add,
            '-': self.sub,
            '*': self.mult,
            '/': self.div,
            '%': self.rem,
            '==': self.eq,
            '>': self.more,
            '<': self.less,
            '>=': self.more_eq,
            '<=': self.less_eq,
            '!=': self.not_eq,
            'println': self.println,
            'exit': exit,
            'read': self.read,
            'drop': self.drop,
            'dup': self.dup,
            'swap': self.swap,
            'cast_int': self.cast_int,
            'cast_str': self.cast_str,
            'jmp': self.jmp,
            'store': self.store,
            'load': self.load,
            'if': self.iff,
            'over': self.over,
            'info': self.info,

        }

    def pop(self):
        return self.values_stack.pop()

    def push(self, arg):
        return self.values_stack.push(arg)

    def top(self):
        return self.values_stack.top()

    def jmp(self):
        self.now = self.pop() - 1

    def iff(self):
        condition = self.pop()
        false_clause = list(parse(self.pop()))[:-2]
        true_clause = list(parse(self.pop()))[:-2]

        condition_machine = Machine(condition, old_code=self.code[:self.now + 1], now=self.now + 1,
                                    values_stack=self.values_stack,
                                    call_stack=self.call_stack, heap=self.heap)
        condition_machine.run()
        decision = condition_machine.top()
        if decision:
            self.code = self.code[:self.now + 1] + true_clause + self.code[self.now + 1:]
        else:
            self.code = self.code[:self.now + 1] + false_clause + self.code[self.now + 1:]

    def store(self):
        key = self.pop()
        value = self.pop()
        self.heap[key] = value

    def info(self):
        print(self.values_stack)
        print(self.now)
        print(self.call_stack)
        print(self.code)
        print(self.heap)

    def load(self):
        self.push(self.heap[self.pop()])

    def more(self):
        first = self.pop()
        second = self.pop()
        self.push(second > first)

    def less(self):
        first = self.pop()
        second = self.pop()
        self.push(second < first)

    def more_eq(self):
        first = self.pop()
        second = self.pop()
        self.push(second >= first)

    def less_eq(self):
        first = self.pop()
        second = self.pop()
        self.push(second <= first)

    def not_eq(self):
        self.push(self.pop() != self.pop())

    def add(self):
        arg_1 = self.pop()
        arg_2 = self.pop()
        self.push(arg_1 + arg_2)

    def eq(self):
        self.push(self.pop() == self.pop())

    def sub(self):
        x1 = self.pop()
        x2 = self.pop()
        self.push(x2 - x1)

    def mult(self):
        x1 = self.pop()
        x2 = self.pop()
        self.push(x1 * x2)

    def div(self):
        self.push(self.pop() / self.pop())

    def rem(self):
        self.push(self.pop() % self.pop())

    def drop(self):
        self.pop()

    def over(self):
        top = self.pop()
        bottom = self.pop()
        self.push(bottom)
        self.push(top)
        return bottom

    def cast_int(self):
        self.push(int(self.pop()))

    def cast_str(self):
        self.push(str(self.pop()))

    def dup(self):
        arg_1 = self.pop()
        self.push(arg_1)
        self.push(arg_1)

    def swap(self):
        arg_1 = self.pop()
        arg_2 = self.pop()
        self.push(arg_1)
        self.push(arg_2)

    def println(self):
        sys.stdout.write("%s\n" % self.pop())
        sys.stdout.flush()

    def read(self):
        new_var = input()
        try:
            new_var = int(new_var)
        except ValueError:
            pass
        self.push(new_var)

    def exe_func(self, name):
        func = self.heap_func[name]
        if func[0] == 'proc':
            self.code = exec_func(name, self.code, self.now, self.values_stack, self.call_stack, self.heap,
                                  self.heap_func)
        else:
            vs = self.values_stack.copy()
            self.push(exec_func(name, self.code, self.now, vs, self.call_stack, self.heap,
                                self.heap_func))

    def run(self):
        # self.code.append('exit')
        while self.now < len(self.code):
            if self.code[self.now] in self.heap_func:
                self.exe_func(self.code[self.now])
                self.now += 1
            if self.code[self.now] in self.slo.keys():
                self.slo[self.code[self.now]]()
                self.now += 1
            else:
                self.push(self.code[self.now])
                self.now += 1

