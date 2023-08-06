import os, sys

default_encoding = "utf-8"

# read the content of the whole textual file
def read_file(file_path, encoding=default_encoding):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding=encoding) as file:
                content = file.read()
                return content
        except:
            return None
    else:
        return None

# write the content into a textual file
def write_to_file(file_path, content, encoding=default_encoding):
    with open(file_path, "w", encoding=encoding) as file:
        print(content, file=file)

# dump the content of a file on to stdout
def dump_file(file_path, encoding=default_encoding):
    print(read_file(file_path, encoding))
