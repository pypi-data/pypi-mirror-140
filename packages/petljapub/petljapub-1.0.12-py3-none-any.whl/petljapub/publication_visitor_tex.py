import os, sys
import re

from .md_util import PandocMarkdown, md_source_code, images_in_md, links_in_md, replace_link, degrade_headings
from .serialization import DirectoryWriter, ZipWriter, MarkdownSerializer, TeXMarkdownSerializer

from . import markdown_magic_comments, source_code_magic_comments

from .publication_visitor import PublicationVisitor, TaskInPublicationVisitor
from .task import Task
from .task_repository import TaskRepository
from .publication_repository import PublicationRepository
from .yaml_specification import YAMLSpecification, YAMLSpecificationVisitor

from . import logger
from . import messages as msg

# Prepares a publication in a single Markdown (or LaTeX) file, ready
# for converting to PDF
class PublicationVisitorTeX(PublicationVisitor, TaskInPublicationVisitor):
    def __init__(self, yaml_specification, task_repo, publication_repo, dst,
                 tex=False, langs=[], header=None, translit=lambda x: x, standalone=True, tex_template=None):
        TaskInPublicationVisitor.__init__(self)
        PublicationVisitor.__init__(self, yaml_specification, task_repo, publication_repo, langs=langs)

        # filename of the resulting md or tex document
        self._dst_file = os.path.basename(dst)
        
        # construct a writing mechanism to dst directory
        self._writer = DirectoryWriter(os.path.dirname(dst))

        # construct appropriate Markdown serialization object (either
        # raw markdown or conversion to HTML)
        if tex:
            self._md_serializer = TeXMarkdownSerializer(self._writer, header=header, standalone=standalone, tex_template=tex_template, translit=translit)
        else:
            self._md_serializer = MarkdownSerializer(self._writer, header, translit=translit)        

    # all links are replaced with task identifiers and task titles are inserted
    # [](task_id) -> [Task title](#task_id)
    def format_links(self, text):
        def exclude_links_not_in_publication(lines):
            links_in_pub = True
            for (_, link_id) in links_in_md("".join(lines)):
                if not self._yaml_specification.sections_containing_task(link_id):
                    links_in_pub = False
                    break
            return lines if links_in_pub else []

        text = markdown_magic_comments.process_by_key_value(text, "span", "link",
                                                            exclude_links_not_in_publication)
        
        for (given_link_title, link_id) in links_in_md(text):
            if given_link_title or ("/" in link_id):
                logger.warn("raw link", given_link_title, link_id)
            if self._task_repo.contains_task(link_id):
                # find the title of the linked task
                link_title = self._task_repo.task(link_id).title()
                text = replace_link(text, given_link_title, link_id, link_title, "#" + link_id)
#                logger.warning("link not marked", link_id, given_link_title)
            else:
                logger.error("non-existent link", link_id)
        return text
            
    # start of the whole publication
    def start(self):

        # open file serialization 
        self._md_serializer.open()
        
        # resulting content
        self._result_md = ""

    # process a single markdown file to be included in publication
    def md_file(self, section_path, level, md_file_name, unnumbered=False):
        path = os.path.join(section_path, md_file_name)
        title, content = self._publication_repo.read_md_file(path)
        content = markdown_magic_comments.filter_by_key(content, "lang", self._langs)
        # degrade headings in the content
        content = degrade_headings(content, level + 1)

        # format links
        content = self.format_links(content)
        
        self._result_md += (level * "#") + " " + title + "\n\n"
        self._result_md += content


        if unnumbered:
            logger.info(md_file_name, " - unnumbered")
            self._result_md = re.sub(r"(?m)(^#.*)", r"\1 {.unnumbered}", self._result_md)
        
        # copy images
        for (title, image_path) in images_in_md(content):
            logger.info("Copy image:", image_path)
            src = os.path.join(self._publication_repo.full_path(os.path.join(section_path, image_path)))
            dst = image_path
            self._writer.copy_file(src, dst)

    # start of a section in a publication
    def section_start(self, section_path, level, subsections, tasks):
        # process index.md, if exists
        if self._publication_repo.contains_index(section_path):
            self.md_file(section_path, level, "index.md")
        else:
            logger.warning("non-existent section:", section_path)

    # start of a new task
    def task_in_pub_start(self, task):
        logger.info(task.id())
        self._task_md = ""

    # print the task title
    def task_in_pub_title(self, task, level, current_occurrence):
        title = task.title()
        # build an anchor for referrencing this task  
        anchor_num = "_" + str(current_occurrence) if current_occurrence > 1 else ""
        anchor = "{#" + task.id() + anchor_num + " " + " .unnumbered" + "}"
        self._task_md += (level * "#") + " {}: ".format(msg.TASK) + title + " " + anchor + "\n\n"

    # first time the task occurs, we print its full statement
    def task_in_pub_st(self, task, current_occurrence):
        # inner headings are collapsed to save space
        def format_inner_headings(text):
            # second and third level headings are replaced by bold and italic
            def degrade_inner_headings(text):
                text = re.sub(r"^## (\S+([ ]\S+)*)[ ]*$", r"**\1**", text, flags=re.MULTILINE)
                text = re.sub(r"^### (\S+([ ]\S+)*)[ ]*$", r"*\1*", text, flags=re.MULTILINE)
                return text
                    
            # collapse inner headings
            text = degrade_inner_headings(text)
            # remove blank lines behind inner headings so that they
            # are printed in the same line with the rest of the text (to save space)
            for m in (msg.INPUT, msg.OUTPUT):
                text = re.sub(r"^\*\*{}\*\*\s*(?![-])".format(m), "**{}:** ".format(m), text, flags=re.MULTILINE)
                # the exception are itemized enumerations behind inner headings
                text = re.sub(r"^\*\*{}[:]?\*\*\s*-".format(m), "**{}:**\n\n-".format(m), text, flags=re.MULTILINE)
            return text

        if current_occurrence == 1:
            # load the problem statement from the repository
            st = task.st_content()
            # format inner headings
            st = format_inner_headings(st)
            # append message to the resulting string
            self._task_md += st + "\n\n"
            # copy images
            for (title, image_path) in images_in_md(st):
                logger.info("Copy image:", image_path)
                src = os.path.join(task.dir(), image_path)
                dst = image_path
                self._writer.copy_file(src, dst)
        else:
            # append message to the resulting string
            msg_repeated = msg.REPEATED_TASK
            self._task_md += "*{} [{}](#{})*\n\n*{}*\n\n".format(msg.REPEATED_TASK, msg.LOOKUP_TASK, task.id(), msg.TRY_TO_SOLVE)
        
    def task_in_pub_sol(self, task, sols):
        # load the problem solution from the repository
        sol = task.sol_content()
        # if some solutions are selected, then print only them
        if sols:
            sol = markdown_magic_comments.filter_by_key(sol, "sol", sols)
        # if some languages are selected, print only them
        if self._langs:
            sol = markdown_magic_comments.filter_by_key(sol, "lang", self._langs)
        # exclude divs and spans
        sol = markdown_magic_comments.filter_by_key(sol, "div", ["exclude"], False)
        sol = markdown_magic_comments.filter_by_key(sol, "span", ["exclude"], False)
        # format divs
        sol = markdown_magic_comments.format_divs(sol)
        # format links
        sol = self.format_links(sol)
        # degrade headings
        level = self._extra_info["level"]
        sol = degrade_headings(sol, level, unnumbered=True)
        # append solution to the resulting string
        self._task_md += "**{}**\n\n{}".format(msg.SOLUTION, sol)
        # copy images
        for (title, image_path) in images_in_md(sol):
            logger.info("Copy image:", image_path)
            src = os.path.join(task.dir(), image_path)
            dst = image_path
            self._writer.copy_file(src, dst)
        

    def task_in_pub_source_code(self, task, sol_name, sol_desc, lang):
        # load the source code from the repository
        code = task.src_code(sol_name, lang)
        # process the magic comments
        code = source_code_magic_comments.process_magic_comments(code)
        # add appropriate markdown markup
        code = "\n" + md_source_code(code, lang)
        # insert formated code to appropriate places within the resulting solution
        self._task_md = markdown_magic_comments.insert_content(self._task_md, "sol", sol_name, code, "code", "here")

    def task_in_pub_report_pending_occurrences(self, task, current_occurrence, total_occurrences):
        # append message and link to the additional occurrences  to the resulting string
        self._task_md += "\n\n*[{}](#{}_{})*\n\n".format(msg.ADDITIONAL_SOLUTIONS, task.id(), current_occurrence + 1)

    def task_in_pub_end(self, task):
        # add formated task to the publication
        self._result_md += self._task_md
            
    def end(self):
        # write the result to the file (converting to TeX if necessary)
        self._md_serializer.write(self._dst_file, self._result_md)
    
            
################################################################################

if __name__ == "__main__":
    import argparse

    import argparse
    parser = argparse.ArgumentParser(description='Read and analyze YAML specification')
    parser.add_argument('yaml', type=str, help='YAML file')
    parser.add_argument('dst', type=str, help='Destination (directory or a zip file path)')
    parser.add_argument('--tasks-dir', type=str, help='Directory where tasks are stored', default=None)
    parser.add_argument('--pub-dir', type=str, help='Directory where publication files are stored', default=None)
    parser.add_argument('--standalone', '-s', action='store_true', help='Generate standalone HTML files')
    parser.add_argument('--css', '-c', type=str, help='CSS file')
    parser.add_argument('--header', type=str, help='Header of each md file')
    
    args = parser.parse_args()

    tasks_dir = args.tasks_dir
    if not tasks_dir:
        tasks_dir = os.path.dirname(args.yaml)
        
    pub_dir = args.pub_dir
    if not pub_dir:
        pub_dir = os.path.dirname(args.yaml)
    
    if not os.path.isfile(args.yaml):
        logger.error("YAML file does not exist")
        sys.exit(-1)

    if tasks_dir and not os.path.isdir(tasks_dir):
        logger.error(tasks_dir, "is not a directory")
        sys.exit(-1)

    if pub_dir and not os.path.isdir(pub_dir):
        logger.error(pub_dir, "is not a directory")
        sys.exit(-1)

    if os.path.exists(args.dst) and not os.path.isfile(args.dst):
        logger.error(args.dst, "exists but is not a regular file")
        sys.exit(-1)
    
    task_repo = TaskRepository(tasks_dir, normalize_md=PandocMarkdown.fix)
    pub_repo = PublicationRepository(pub_dir, normalize_md=PandocMarkdown.fix)
    yaml = YAMLSpecification(args.yaml)
    visitor = PublicationVisitorTeX(yaml, task_repo, pub_repo, args.dst, tex=True, langs=yaml.langs())
    yaml.traverse(visitor)
