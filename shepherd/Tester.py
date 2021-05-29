# pylint: disable=invalid-name
import sys
import os
import queue
import time
from typing import Any
from Utils import *
from LCM import *

# pylint: disable=global-statement


def get_class_from_name(name: str) -> Any:
    """
    A helper function used to get a class of name from the globals list.
    Globals is a dictionary representing the global scope of this program's
    python execution, which means that to a small extent the functions in this
    file along with everything imported above is available to this function.
    Keep this in mind, since this function is called on potentially unsafe user
    entered code.
    """
    return globals()[name]


def get_attr_from_name(source, name):
    """
    A helper function used to get an attribute of a certain name from a given
    class (source).
    """
    if not isinstance(source, type):
        raise Exception('{} is not a class.'.format(source))
    return getattr(source, name)


def parse_header(header):
    """
    A helper function that translates the headers in format
    <LCM_targer>.<header> to the string representation stored in Utils.py.
    Enforces the syntax for referencing the header, as well as the existance of
    the header in Utils.py.
    """
    parts: list = header.split('.')
    if len(parts) != 2:
        raise Exception('{} is invalid.'.format(header))
    ex = None
    klass: type = None
    try:
        klass = get_class_from_name(parts[0])
    except KeyError:
        ex = Exception(
            '{} is not recognized. Make sure this is a class of headers in Utils.py'.format(parts[0]))
    finally:
        if ex:
            raise ex
    ex = None
    name: str = ''
    try:
        name = get_attr_from_name(klass, parts[1])
    except AttributeError:
        ex = Exception('{} is not recognized. Make sure this is a header in {} in Utils.py'.format(
            parts[1], parts[0]))
    finally:
        if ex:
            raise ex
    return name


def execute_python(script):
    """
    A helper function that executes a python expression in the context of the
    local scipt enviroment.
    """
    global LOCALVARS
    exec(script, LOCALVARS)


def evaluate_python(token):
    """
    A helper function that evaluates a token against the local scipt enviroment.
    """
    global LOCALVARS
    return eval(token, LOCALVARS)


def tokenize_wait_exp(expression):
    """
    The function that parses WAIT statements.
    Enforces syntax and returns a dictionary of the deconstructed WAIT statement.
    """
    global TARGET
    original_expression = expression

    def helper_min(a, b):
        """
        A helper function that returns the min between a and b, but considers -1
        to be an unacceptable return value.
        """
        if a == -1 and b == -1:
            return None
        elif a == -1:
            return b
        elif b == -1:
            return a
        else:
            return min(a, b)
    tokens = expression.split('FROM')
    if len(tokens) != 2:
        raise Exception('expected to find FROM after <header> and before <target> in WAIT statement: WAIT {}'.format(
            original_expression))
    header = parse_header(remove_outer_spaces(tokens[0]))
    expression = tokens[1]
    whole_target = remove_outer_spaces(expression).split(' ')[0]
    if whole_target.split('.')[0] != 'LCM_TARGETS':
        raise Exception('was expecting a target in LCM_TARGETS for WAIT statement: WAIT {}'.format(
            original_expression))
    target = get_attr_from_name(LCM_TARGETS, whole_target.split('.')[1])
    if target != TARGET:
        raise Exception('target for WAIT expression is not the current target ({}): WAIT {}'.format(
            TARGET, original_expression))
    expression = expression[helper_min(expression.find(
        ' SET '), expression.find(' WITH ')):None]
    statements = {'SET': [], 'WITH': []}
    while ' SET ' in expression or ' WITH ' in expression:
        expression = remove_outer_spaces(expression)
        type = 'SET' if expression[0:4] == 'SET ' else 'WITH'
        if type == 'WITH' and expression[0:5] != 'WITH ':
            raise Exception('was expecting WITH or SET statement, or nothing after FROM in WAIT statement: WAIT {}'.format(
                original_expression))
        expression = expression[len(type):None]
        expression = remove_outer_spaces(expression)
        stop_point = helper_min(expression.find(
            ' SET '), expression.find(' WITH '))
        statements[type].append(remove_outer_spaces(
            expression[0:stop_point]))
        expression = expression[stop_point:None]
    return {'header': header, 'target': target, 'with_statements': statements['WITH'], 'set_statements': statements['SET']}


def wait_function(expression):
    """
    The function that parses WAIT statements.
    Enforces the syntax of the WAIT statement.
    Adds one or multiple new wait conditions to global CURRENT_HEADERS, and sets
    global WAITING to True.
    """
    original_expression = expression
    global CURRENT_HEADERS, WAITING

    def helper_min(a, b):
        """
        A helper function that returns the min between a and b, but considers -1
        to be an unacceptable return value.
        """
        if a == -1 and b == -1:
            return None
        elif a == -1:
            return b
        elif b == -1:
            return a
        else:
            return min(a, b)
    CURRENT_HEADERS = []
    WAITING = True
    type = 'OR'
    while ' AND ' in expression or ' OR ' in expression:
        expression = remove_outer_spaces(expression)
        found = helper_min(expression.find(' AND '), expression.find(' OR '))
        type = 'AND' if expression[found:found+5] == ' AND ' else 'OR'
        header = tokenize_wait_exp(expression[0:found])
        expression = expression[found + len(type) + 2:None]
        CURRENT_HEADERS.append(
            {'header': header, 'type': type, 'received': False})
    expression = remove_outer_spaces(expression)
    CURRENT_HEADERS.append({'header': tokenize_wait_exp(
        expression), 'type': type, 'received': False})


def read_next_line():
    """
    A helper function to maintain the file scanning abstraction.
    Advances the global LINE pointer to the next line of the script.
    """
    global LINE
    LINE += 1


def has_next_line():
    """
    A helper function to maintain the file scanning abstraction.
    Returns whether or not there is another line to be read.
    """
    global LINE, FILE
    return LINE < len(FILE)


def line_at(line):
    """
    A helper function to maintain the file scanning abstraction.
    Returns the line with the number passed in.
    """
    global FILE
    return FILE[line]


def jump_to_line(line):
    """
    A helper function to maintain the file scanning abstraction.
    Sets global LINE, can be through of as a jump.
    """
    global LINE
    LINE = line


def current_line():
    """
    A helper function to maintain the file scanning abstraction.
    Returns the line with the number in global LINE.
    """
    global LINE, FILE
    return FILE[LINE]


def process_line(line):
    """
    Takes in a line of the script and identifies the statement being used.
    Calls the correct executing function on the remainder of the line.
    Enforces that all lines start with a valid statement, and attaches
    additional information to errors thrown by the executing functions.

    """
    global LINE
    if line == '':
        return
    found = False
    for key in COMMANDS:
        if line[0:len(key)] == key:
            ex = None
            try:
                COMMANDS[key](remove_outer_spaces(line[len(key):None]))
# pylint: disable=broad-except
            except Exception as exx:
                ex = Exception(
                    'an error occured on line {}:\n{}'.format(LINE + 1, exx))
            finally:
                if ex:
                    raise ex
            found = True
            break
    if not found:
        raise Exception(
            'unrecognized command on line {}:\n{}'.format(LINE + 1, line))


def remove_outer_spaces(token):
    """
    A helper function used to strip the spaces off the outside edges of a
    string.
    Essential for making shepherd scripting ignore whitespace.
    """
    return token.strip()


def if_function(expression):
    """
    The function that parses both IF and WHILE statements.
    Enforces syntax as well as balanced END statements.
    Evaluates the condition given in the statement, and if false crawls forward
    in the script to the matching END statement and jumps there, otherwise
    execution proceedes normally.
    """
    global END_COUNT, LINE, END_COUNT_HEADS
    starting_count = END_COUNT
    starting_line = LINE
    END_COUNT_HEADS[LINE] = END_COUNT
    condition = evaluate_python(remove_outer_spaces(expression))
    END_COUNT += 1
    if not condition:
        while END_COUNT > starting_count:
            read_next_line()
            ex = None
            line = None
            try:
                line = remove_outer_spaces(current_line())
            except Exception:
                ex = Exception(
                    "reached end of file while in the IF on line {}. You are probably missing an END".format(starting_line))
            finally:
                if ex:
                    raise ex
            if line == '':
                continue
            found = False
            for key in COMMANDS.keys():
                if line[0:len(key)] == key:
                    found = True
                    break
            if not found:
                raise Exception(
                    'unrecognized command on line {}:\n{}'.format(LINE + 1, line))
            if line[0:2] == 'IF':
                END_COUNT += 1
            if line[0:5] == 'WHILE':
                END_COUNT += 1
            if line[0:3] == 'END':
                END_COUNT -= 1


def end_function(expression):
    """
    The function that parses END statements.
    Crawls backwards through the script to find the matching IF or WHILE
    statement and jumps to that line if it is a WHILE.
    Essentially no processing need happen here for an IF statement.
    """
    global END_COUNT, LINE, END_COUNT_HEADS
    END_COUNT -= 1
    end_count_heads = list(END_COUNT_HEADS.items())
    end_count_heads.sort()
    for item in end_count_heads[::-1]:
        if item[0] < LINE and item[1] == END_COUNT:
            if line_at(item[0])[0:5] == 'WHILE':
                jump_to_line(item[0]-1)
            break


def pass_function(expression):
    """
    The function that parses PASS statements.
    Enforces syntax and will print out the result as well as exit the script
    interpreter if the test is passed.
    """
    expression = remove_outer_spaces(expression)
    if expression == '' or evaluate_python(expression):
        print("TEST PASSED")
        sys.exit(0)


def fail_function(expression):
    """
    The function that parses FAIL statements.
    Enforces syntax and will print out the result as well as exit the script
    interpretter if the test is failed.
    """
    global LINE
    expression = remove_outer_spaces(expression)
    if expression == '' or evaluate_python(expression):
        print(f"TEST FAILED on line {LINE}")
        sys.exit(-1)


def assert_function(expression):
    """
    The function that parses ASSERT statements.
    Enforces syntax and will print out the result of the assertion as well as
    exit the script interpretter.
    """
    global LINE
    expression = remove_outer_spaces(expression)
    if expression == '':
        raise Exception(
            'expected a python conditional expression after ASSERT')
    if evaluate_python(expression):
        print("TEST PASSED")
        sys.exit(0)
    else:
        print(f"TEST FAILED on line {LINE}")
        sys.exit(-1)

def sleep_function(expression):
    """
    The function that parses SLEEP statements.
    Enforces syntax, and pauses the .shepherd interpreter for the specified
    number of seconds.
    """
    expression = remove_outer_spaces(expression)
    if expression == '':
        raise Exception('expected a time afer after SLEEP')
    try:
        amount = float(evaluate_python(expression))
    except ValueError as e:
        raise Exception(f'expected a time afer after SLEEP, but got {expression}')
    time.sleep(amount)

def read_function(line):
    """
    The function that parses READ statements.
    Enforces syntax, and sets the global TARGET appropriately.
    """
    global TARGET, EVENTS
    if remove_outer_spaces(line.split('.')[0]) != 'LCM_TARGETS' or len(line.split('.')) != 2:
        raise Exception(
            'was expecting a target in LCM_TARGETS for READ statement: READ {}'.format(line))
    target = get_attr_from_name(LCM_TARGETS, line.split('.')[1])
    if TARGET == target:
        print("[WARNING] Calling READ again on the same target will cause the LCM queue to be \
            cleared. Make sure that this is intended.")
    TARGET = target
    EVENTS = queue.Queue()
    lcm_start_read(TARGET, EVENTS, daemon=True)
    print('now reading from lcm target: LCM_TARGETS.{}'.format(
        line.split('.')[1]))


def tokenize_emit_exp(expression):
    """
    The function that parses EMIT statements.
    Enforces syntax and returns a dictionary of the deconstructed EMIT statement.
    """
    original_expression = expression

    def helper_find(expression, target):
        """
        A helper function to find the next instance of 'target' in 'expression',
        and return none if it does not exist.
        """
        found = expression.find(target)
        return found if found >= 0 else None
    tokens = expression.split(' TO ')
    if len(tokens) != 2:
        raise Exception('expected to find TO after <header> and before <target> in EMIT statement: EMIT {}'.format(
            original_expression))
    header = parse_header(remove_outer_spaces(tokens[0]))
    expression = tokens[1]
    if remove_outer_spaces(expression[0:helper_find(expression, ' WITH ')].split('.')[0]) != 'LCM_TARGETS':
        raise Exception('was expecting a target in LCM_TARGETS for EMIT statement: EMIT {}'.format(
            original_expression))
    target = get_attr_from_name(LCM_TARGETS, remove_outer_spaces(
        expression[0:helper_find(expression, ' WITH ')].split('.')[1]))
    expression = expression[helper_find(expression, ' WITH '):None]
    statements = []
    while 'WITH ' in expression:
        expression = remove_outer_spaces(expression)
        if expression[0:5] != 'WITH ':
            raise Exception('was expecting WITH statement, or nothing after TO in EMIT statement: EMIT {}'.format(
                original_expression))
        expression = expression[len('WITH'):None]
        expression = remove_outer_spaces(expression)
        statements.append(remove_outer_spaces(
            expression[0:helper_find(expression, ' WITH ')]))
        expression = expression[helper_find(expression, ' WITH '):None]
    return {'header': header, 'target': target, 'with_statements': statements}


def emit_function(expression):
    """
    The function called to handle the execution of an EMIT statement.
    Processes the statement, processes the WITH statements, and then emits the
    appropriate header and data via LCM.
    """
    emit_expression = tokenize_emit_exp(expression)
    data = {}
    for with_statement in emit_expression['with_statements']:
        with_function_emit(with_statement, data)
    lcm_send(emit_expression['target'], emit_expression['header'], data)


def with_function_wait(expression, data):
    """
    Takes in a WITH statement found in a WAIT statement, and the data that was
    present in the header that triggered the processing of this WAIT statement,
    and modifies the local script enviroment accordingly.
    Also handles syntax checking of the WITH statement.
    """
    parts = expression.split('=')
    if len(parts) != 2:
        raise Exception('WITH statement: {} is invalid.'.format(expression))
    parts[0] = remove_outer_spaces(parts[0])
    parts[1] = remove_outer_spaces(parts[1])
    if parts[1][0] != "'" or parts[1][-1] != "'":
        raise Exception(
            "expected second argument of WITH statement: {} to be wrapped in '.".format(expression))
    ex = None
    try:
        global LOCALVARS
        LOCALVARS[parts[0]] = data[parts[1][1:-1]]
    except ValueError:
        ex = Exception("{} is undefined".format(parts[0]))
    except Exception:
        ex = Exception("malformed WITH statement: {}".format(expression))
    finally:
        if ex:
            raise ex


def with_function_emit(expression, data):
    """
    Takes in a WITH statement found in an EMIT statement, and the data that will
    be issued to the emmited header and modifies the data appropriately.
    Also handles syntax checking of the WITH statement.
    Example:
    code: SCOREBOARD_HEADER.STAGE TO LCM_TARGETS.SCOREBOARD WITH 'stage' = AUTO
    expression: 'stage' = AUTO
    """
    parts = expression.split('=')
    if len(parts) != 2:
        raise Exception('WITH statement: {} is invalid.'.format(expression))
    # remove leading and trailing spaces around the '='
    parts[0] = remove_outer_spaces(parts[0])
    parts[1] = remove_outer_spaces(parts[1])
    if parts[0][0] != "'" or parts[0][-1] != "'":
        raise Exception(
            "expected first argument of WITH statement: {} to be wrapped in '.".format(expression))
    ex = None
    try:
        data[parts[0][1:-1]] = evaluate_python(parts[1])
    except ValueError:
        ex = Exception("{} is undefined".format(parts[1]))
    except Exception:
        ex = Exception("malformed WITH statement: {}".format(expression))
    finally:
        if ex:
            raise ex


def check_received_headers():
    """
    Returns whether or not the wait conditions are satisfied, so that script
    execution should proceed.
    This is done by taking the AND and OR statements in the WAIT litterally,
    and the python interpretter is fed a string of booleans seperated by the
    appropriate python and / or opperators.
    This function will also set the global WAITING variable to false once
    execution should resume.
    """
    global CURRENT_HEADERS, WAITING
    python_usable_string = ''
    for i in range(len(CURRENT_HEADERS)):
        header = CURRENT_HEADERS[i]
        python_usable_string += str(header['received']) + " "
        if i < len(CURRENT_HEADERS) - 1:
            python_usable_string += header['type'].lower() + " "
    if(eval(python_usable_string)):
        WAITING = False
        return True
    return False


def execute_header(header, data):
    """
    Takes in a header data structure and the data from the LCM call and will
    modify the local enviroment accordingly.
    Processes all SET and WITH statements in the header individually, and with
    no guarantee on order.
        In this implementation, all WITH statements are processed first, from
        left to right, and then all SET statements, from left to right.
    """
    global LOCALVARS
    for with_statement in header['header']['with_statements']:
        with_function_wait(with_statement, data)
    for set_statement in header['header']['set_statements']:
        local_arg = remove_outer_spaces(set_statement.split('=')[0])
        python_expression = remove_outer_spaces(set_statement.split('=')[1])
        LOCALVARS[local_arg] = evaluate_python(python_expression)


def accept_header(payload):
    """
    Accepts a header and its payload, and will check if that header is
    currently being waited on.
    If it is, accept header will process all instances of that waited on
    header and also set the wait condition to be satisfied for each instance.
    """
    global CURRENT_HEADERS
    for header in CURRENT_HEADERS:
        if header['header']['header'] == payload[0]:
            execute_header(header, payload[1])
            header['received'] = True


def run_until_wait():
    """
    A useful function that advances script execution until the next WAIT
    statement is detected.
    Once that statement is detected, it is processed and then run_until_wait
    returns.
    """
    global WAITING
    while has_next_line() and not WAITING:
        process_line(remove_outer_spaces(current_line()))
        read_next_line()
    if not has_next_line():
        print('reached end of test without failing')
        sys.exit(0)


def start():
    """
    The loop that interacts with LCM!
    Here target must be assigned before start() may be called, and so this will
    detect and error on that condition.
    Otherwise this loop binds a queue to the correct LCM target and processes
    LCM events that it recieves.
    Each LCM header that is recieved will be processed based on the current
    WAIT statements and then if all wait statements have been satisfied,
    the code execution will advance to the next WAIT before any more LCM headers
    will be processed.
    """
    global TARGET, EVENTS, CURRENT_HEADERS
    if TARGET == 'unassigned':
        raise Exception("READ needs to be called before the first WAIT.")

    # def run():
    #     i = 0
    #     while True:
    #         time.sleep(.5)
    #         print(f"running! {i}")
    #         i += 1

    # test_thread = threading.Thread(target=run)
    # test_thread.start()

    while True:
        time.sleep(0.1)
        payload = EVENTS.get(True)
        accept_header(payload)
        if(check_received_headers()):
            CURRENT_HEADERS = []
            run_until_wait()


# class worker(Thread):
#     def run(self):
#         for i in range(0, 11):
#             print(x)
#             time.sleep(1)
# worker().start()


def main():
    """
    Reads the whole file in and places it in a python list on the heap.
    Also handles errors associated with the file system.
    Returns 1 if the file cannt be found, 0 otherwise
    """
    global FILE
    if len(sys.argv) != 2:
        print('[ERROR] The tester takes a single argument, the name of a testing file')
        return 1
    script_dir = os.path.dirname(__file__)
    rel_path = "tests/{}".format(sys.argv[1])
    abs_file_path = os.path.join(script_dir, rel_path)
    file = open(abs_file_path, "r")
    for line in file:
        line = line[0:None]
        if line[-1] == '\n':
            line = line[0:-1]
        FILE.append(line)
    file.close()
    print('Starting test: {}'.format(sys.argv[1]))
    return 0


"""
The LCM target that we are currently reading from.
"""
TARGET = 'unassigned'
"""
The queue used to store incoming LCM requests. These requests are then popped
off in the start function and processed.
"""
EVENTS = queue.Queue()
"""
A list containing the contents of the file that was specified when the program
was started. Each line of the file is stored as a string in sequential indexes.
"""
FILE = []
"""
A varaible which keeps track of whether or not execution is currently happening.
This is set to True when a wait statement is encountered, and set to False when
all headers have been resolved, and execution should continue.
"""
WAITING = False
"""
A dictionary that is populated by the script's execution. This is used as an
enviroment for python execution in RUN and in the WAIT, SET, and PRINTP
statements. Unlike normal python enviroments, there are no further frames opened
for code blocks, and this is a facsimile of dynamic typing.
"""
LOCALVARS = {}
"""
A list of header dictionaries. This list is populated by WAIT statements and is
emptied when the headers are all considered resolved.
"""
CURRENT_HEADERS = []
"""
A varaible keeping track of the current line being executed.
"""
LINE = 0
"""
A variable keeping track of the current level of indentation (how many unclosed
IF / WHILE statements there are).
"""
END_COUNT = 0
"""
A dictionary used to keep track / memoize the level of indentation found at each
IF and WHILE statement. This is used by the END statement to backtrack to the
appropriate line and determine if that END is closing an IF or a WHILE.
"""
END_COUNT_HEADS = {}
"""
A dictionary of command names (that start lines) to the functions to be
executed in order to parse that kind of line. Due to how the checking
works, statements that include another statement's syntax should precede
those in this dictionary declaration.
"""
COMMANDS = {'WAIT': wait_function,
            'EMIT': emit_function,
            'RUN': execute_python,
            'READ': read_function,
            'PRINTP': lambda line: print(evaluate_python(line)),
            'PRINT': lambda line: print(line),
            'IF': if_function,
            'WHILE': if_function,
            'END': end_function,
            'PASS': pass_function,
            'FAIL': fail_function,
            'ASSERT': assert_function,
            '##': lambda line: None,
            'SLEEP': sleep_function
            }

if __name__ == '__main__':
    """
    The main function! Calls main to read the specified file into the heap,
    and then advances until the first wait command where it begins the LCM
    interaction found in start.
    """
    if main():
        exit(0)
    run_until_wait()
    start()
