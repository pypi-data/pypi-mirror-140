import os, sys
import re
import argparse

from .task import Task
from .task_visitor import TaskVisitor
from .md_util import PandocMarkdown, md_source_code, images_in_md
from . import markdown_magic_comments
from . import source_code_magic_comments
from . import javascript
from .serialization import DirectoryWriter, ZipWriter, MarkdownSerializer, HTMLMarkdownSerializer
from . import logger

class TaskVisitorHTML(TaskVisitor):
    def __init__(self, css=None, header=None):
        self._md = ""
        self._css = css
        self._header = header

    # task is started
    def task_start(self, task):
        # open writer and HTML serializer
        self._writer = DirectoryWriter(task.build_dir())
        self._md_serializer = HTMLMarkdownSerializer(self._writer, standalone=True, css=self._css, header=self._header)
        self._md_serializer.open()
        
        
    # a hook called to process the task title
    def task_title(self, task):
        self._md += "# " + task.title() + "\n\n"
        
    # a hook called to process the task statement
    def task_st(self, task):
        # append the statement content, read from the task repository
        st_md = task.st_content()
        
        self._md += st_md + "\n\n"
        # copy images
        for (title, image_path) in images_in_md(st_md):
            logger.info("Copy image:", image_path)
            src = os.path.join(task.dir(), image_path)
            dst = os.path.join(task.build_dir(), image_path)
            self._writer.copy_file(src, dst)
        

    # resolving all links to work in the output directory structure
    def format_links(self, text):
        # iterate through all links in the given markdown text
        for link in re.finditer(r"\[\]\((\w+)\)", text):
            text = text.replace(link.group(), "*[{}]*".format(link.group(1)))
        return text
        
    # a hook called to process solution description, including only
    # solutions from the given list of solutions ("ex0", "ex1", ...)
    # and only on selected languages ("cs", "cpp", "py", ...)
    def task_sol(self, task, sols):
        self._sol_md = dict()
        
        # iterate through all included languages
        for lang in self._langs:
            # resulting description in markdown format
            sol_md = ""
            sol_md += task.sol_content()
            
            sol_md = markdown_magic_comments.filter_by_key(sol_md, "lang", [lang])
            # retain only the selected solutions
            if sols:
                sol_md = markdown_magic_comments.filter_by_key(sol_md, "sol", sols)
            # format divs
            sol_md = markdown_magic_comments.format_divs(sol_md)
            # resolve links
            sol_md = self.format_links(sol_md)
            
            self._sol_md[lang] = sol_md

        # copy images
        for (title, image_path) in images_in_md(task.sol_content()):
            logger.info("Copy image:", image_path)
            src = os.path.join(task.dir(), image_path)
            dst = os.path.join(task.build_dir(), image_path)
            self._writer.copy_file(src, dst)
            
        

    # a hook called to process a single source code for the task with
    # the given task_id, with the given solution name (e.g., "ex0"),
    # in the given language (e.g., "cs"), where the metadata
    # description of the solution is also known
    def task_source_code(self, task, sol_name, sol_desc, lang):
        # read the source code from the repository
        code = task.src_code(sol_name, lang)
        if not code:
            logger.error("missing code", task.id(), sol_name, lang)
            return
        # remove the magic comments (retain the whole source code)
        code = source_code_magic_comments.remove_magic_comments(code)
        # surround it with Markdown markup for program source code
        code = "\n" + md_source_code(code, lang)
        # insert the code to appropriate place in the solution for its language
        self._sol_md[lang] = markdown_magic_comments.insert_content(self._sol_md[lang], "sol", sol_name, code, "code", "here")
        
    
    # task is ended
    def task_end(self, task):
        # join solutions in all languages and write them into a single file
        joined_sol_md = ""
        for lang in self._langs:
            joined_sol_md += "<div id='sol-{}' class='sol'>\n{}\n</div>\n".format(lang, self._sol_md[lang])

        # add javascript language switcher
        if len(self._langs) != 1:
            joined_sol_md = javascript.add_switcher(joined_sol_md, self._langs)

        self._md += "# Решење\n\n" + joined_sol_md
        self._md_serializer.write(task.id() + ".md", self._md)

        logger.info("HTML file written:", os.path.join(task.build_dir_name(), task.id() + ".html"))
        
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test visiting a single task')
    parser.add_argument('task', type=str, help='Dir of the task')
    parser.add_argument('--langs', type=str, help='Languages', nargs="*", default=["cpp", "cs"])
    args = parser.parse_args()
    dir = os.path.abspath(args.task)
    task = Task(dir)
    task_visitor = TaskVisitorHTML()
    task_visitor.visit_task(task, langs=args.langs)
