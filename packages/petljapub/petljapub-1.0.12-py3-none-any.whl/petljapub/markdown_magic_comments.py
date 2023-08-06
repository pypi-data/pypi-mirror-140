import re, sys
from . import logger
from . import messages

def magic_comment_re(key, value):
    return r"\s*<!---\s*({})\s*:\s*({})\s*--->".format(key, value)

def is_magic_comment(key, value, str):
    return re.match(magic_comment_re(key, value), str)

def is_magic_comment_end(key, str):
    return is_magic_comment(key, "end", str)

def is_magic_comment_start(key, str):
    return is_magic_comment(key, "\S+", str) and not is_magic_comment_end(key, str)

def magic_comment_key_value(str):
    m = re.match(magic_comment_re("\S+", "\S+"), str)
    return (m.group(1), m.group(2))

# Checks if there is a block surrounded by the given key
# <!--- key:... --->
# ...
# <!--- key:end --->
def contains_block(md, key):
    for line in md.split("\n"):
        if is_magic_comment_start(key, line):
            return True
    return False

    
# Add the given content to the block marked by
# <!--- key:value --->
#  ...
# <!--- key:end --->
# - If there is a directive 
#     <!--- key_place:value_place --->
#   inside the block, the content is inserted in place of that directive.
# - If there is no such directive, the content is added to the end of
#   the block.
# - If there is no such block, the given content is added to the end of md
def insert_content(md, key, value, content, key_place=None, value_place=None):
    # automaton states
    sWAIT_START = 0
    sWAIT_END = 1
    sCOPY_TO_END = 2
    # copy one by one line
    result = []
    state = sWAIT_START
    content_inserted = False
    for line in md.split("\n"):
        if is_magic_comment(key, value, line):
            state = sWAIT_END
        elif state == sWAIT_END:
            if key_place and value_place and is_magic_comment(key_place, value_place, line):
                content_inserted = True
                result.append(content)
            if is_magic_comment_end(key, line):
                if not content_inserted:
                    result.append(content)
                state = sCOPY_TO_END
        result.append(line + "\n")
    # if we did not find the sought block, the content is added to the end
    if state == sWAIT_START:
        logger.warn("magic comments insert content - block not found, key={}, value={}".format(key, value))
        result.append(content)
    return "".join(result)


def process_by_key(md, key, f=lambda lines, value: lines):
    value_stack = []
    result_stack = [[]]
    for line in md.split("\n"):
        if is_magic_comment_start(key, line):
            (_, value) = magic_comment_key_value(line)
            value_stack.append(value)
            result_stack.append([line + '\n'])
        elif is_magic_comment_end(key, line):
            if not value_stack:
                logger.error("magic comments")
            result_stack[-1].append(line + '\n')
            value = value_stack.pop()
            top = result_stack.pop()
            result_stack[-1].extend(f(top, value))
        else:
            result_stack[-1].append(line + '\n')
    return "".join(result_stack[-1])


def process_by_key_value(md, key, value, f=lambda lines: lines):
    def f_val(lines, val):
        if val != value:
            return lines
        return f(lines)
    return process_by_key(md, key, f_val)
        

# The markdown content md contains blocks
# <!--- key:value --->
#    ...
# <!--- key:end --->
# the next function excludes everything that is marked by values different from
# the give ones (if ok=True) or equal to the give ones (if ok=False)
def filter_by_key(md, key, given_values, ok=True):
    if not given_values:
        logger.warn("filtering magic comments - empty list of values")

    # check if the value is among given_values
    def value_is_given(value, given_values):
        return not set(given_values).isdisjoint(re.split(r",\s*", value))

    def keep_value(block, value):
        if value_is_given(value, given_values) == ok:
            return block
        else:
            return []

    return process_by_key(md, key, keep_value)

# The markdown content md contains blocks
# <!--- key:value --->
#    ...
# <!--- key:end --->
# the next function excludes everyt block that is marked by one of the given values
def exclude(md, key, exclude_values):
    return filter_by_key(md, key, exclude_values, False)
    
# The markdown content md contains blocks
# <!--- key:value --->
#    ...
# <!--- key:end --->
# the next function excludes everyt block that is not marked by one of the given values
def exclude_all_except(md, key, keep_values):
    return filter_by_key(md, key, keep_values, True)


def format_divs(md, div_titles=messages.div_titles):
    value_stack = []
    result = []
    for line in md.split('\n'):
        if is_magic_comment_start('div', line):
            (_, value) = magic_comment_key_value(line)
            result.append("<div class={}>\n".format(value))
            if value in div_titles:
                result.append("**{}.** ".format(div_titles[value]))
        elif is_magic_comment_end('div', line):
            result.append("</div>\n")
        else:
            result.append(line + "\n")
    return "".join(result)


if __name__ == '__main__':
    from .task_repository import TaskRepository
    repo = TaskRepository('_zadaci/02 Zbirka_2')
    print(filter_by_key(repo.task('neupareni_element').sol_content(), "lang", ["cs"], ok=False))
#    print(insert_content(repo.task('neupareni_element').sol_content(), "sol", "ex1", "#include\n"))
