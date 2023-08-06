import os, sys
import re
import tempfile
from datetime import date

import json, yaml
import xml.etree.ElementTree as ET
from xml.dom import minidom

from .util import read_file
from .md_util import PandocMarkdown, md_source_code, links_in_md, images_in_md, replace_link, degrade_headings
from .serialization import DirectoryWriter, ZipWriter, MarkdownSerializer, HTMLMarkdownSerializer

from . import markdown_magic_comments
from . import source_code_magic_comments
from . import javascript
from .publication_visitor import PublicationVisitor, TaskInPublicationVisitor
from .task_repository import TaskRepository
from .publication_repository import PublicationRepository
from .yaml_specification import YAMLSpecification, YAMLSpecificationVisitor
from . import logger

from . import messages as msg


# Prepares a publication in a series of HTML files, ready for publishing on the web
class PublicationVisitorHTML(PublicationVisitor, TaskInPublicationVisitor):
    # yaml_specification - yaml specification of the publication
    # task_repo, publication_repo - repositories of tasks and publication texts
    # dst - destination to store the resulting files (either a directory path, or a zip file path)
    # langs - programming languages included in the publication
    # html - if True, then the Markdown files are converted to HTML (using pypandoc)
    # join_langs - if True, then solutions for all included languages are stored in a single file
    # standalone - if True, all HTML files are standalone (they include a header and the footer and are ready for viewin)
    # css - link to the css file used to style the resulting HTML
    def __init__(self, yaml_specification, task_repo, publication_repo, dst, langs,
                 html=False, join_langs=False, standalone=False,
                 css=None, header=None, translit=lambda x: x):
        TaskInPublicationVisitor.__init__(self)
        PublicationVisitor.__init__(self, yaml_specification, task_repo, publication_repo, langs=langs)

        # construct appropriate file writing mechanism (either a zip
        # file, or an ordinary file system)
        if dst.endswith(".zip"):
            self._writer = ZipWriter(dst)
        else:
            self._writer = DirectoryWriter(dst)

        # construct appropriate Markdown serialization object (either
        # raw markdown or conversion to HTML)
        if html:
            self._md_serializer = HTMLMarkdownSerializer(self._writer, header=header, standalone=standalone, css=css, translit=translit)
        else:
            self._md_serializer = MarkdownSerializer(self._writer, header, translit=translit)
        
        self._join_langs = join_langs
        self._standalone = standalone

        # dictionary that maps section paths to section titles (read from index.md files)
        self.section_titles = {}
        

    # resolving all links to work in the output directory structure
    def format_links(self, text, task=None, section=None):
        if task:
            current_file = task.id()
            current_dir = self.task_output_dir(task.id())
        if section:
            current_file = section
            current_dir = section
        
        # iterate through all links in the given markdown text
        for (link_text, link_task_id) in links_in_md(text):
            if link_task_id.endswith(".html"):
                continue
            # check if the task with that id exists in the repository
            if self._task_repo.contains_task(link_task_id):
                # find the title of the linked task
                link_task_title = self._task_repo.task(link_task_id).title()
                # find the sections that it occurrs in
                link_task_sections = self._yaml_specification.sections_containing_task(link_task_id)
                if link_task_sections:
                    link_target = os.path.join(self.task_output_dir(link_task_id, link_task_sections[0]), link_task_id + "-st.html")
                    link_path = os.path.relpath(link_target, current_dir)
                    text = replace_link(text, link_text, link_task_id, link_task_title, link_path)
                else:
                    # warn if the task exists, does not occurr in the publication, and remove link
                    # (only print the linked task title in italic plain text)
                    text = remove_link(link_text, link_task_id, "*{}*".format(link_task_title))
                    logger.warn(current_file, "- link to task not in publication")
            else:
                logger.error("non-existent link", link_task_id, "in", current_file)
        return text
        
    def start(self):
        # open file serialization 
        self._md_serializer.open()
        
        # resulting table of contents in MarkDown format
        self._toc_md = ""


    def read_and_process_md(self, section_path, level, md_file_name):
        # read the content
        path = os.path.join(section_path, md_file_name)
        title, content = self._publication_repo.read_md_file(path)

        if md_file_name == "index.md":
            self.section_titles[section_path] = title
        
        # Add entry to the table of contents
        link_target = self._md_serializer.path(path)
        self._toc_md += "\n" + ("#" * level) + " " + "[" + title + "]" + "(" + link_target + ")" + "\n\n"
        
        # build the title and preppend it to the content
        md = level * "#" + " " + title + "\n\n"
        # degrade other headings in the content
        content = degrade_headings(content, level + 1)
        md += content

        # exclude divs and spans
        md = markdown_magic_comments.exclude(md, "div", ["exclude"])
        # format divs
        md = markdown_magic_comments.format_divs(md)
        # format internal links
        md = self.format_links(md, section=section_path)
        # handle programming language specifics
        if markdown_magic_comments.contains_block(content, "lang"):
            # process each language separately
            joined_md = ""
            for lang in self._langs:
                lang_content = markdown_magic_comments.exclude_all_except(md, "lang", [lang])
                joined_md += "<div id='sol-{}' class='sol'>\n{}\n</div>\n".format(lang, lang_content)
            # add switcher
            if len(self._langs) > 1:
                joined_md = javascript.add_switcher(joined_md, self._langs)
            md = joined_md
        
        # copy images
        for (title, image_path) in images_in_md(md):
            logger.info("Copy image:", image_path)
            src = os.path.join(self._publication_repo.full_path(os.path.join(section_path, image_path)))
            dst = os.path.join(section_path, image_path)
            self._writer.copy_file(src, dst)
        
        return md
        
    # process the given publication source Markdown file
    def md_file(self, section_path, level, md_file_name, unnumbered=False):
        md = self.read_and_process_md(section_path, level, md_file_name)
        # write the result to the file (converting to HTML if necessary)
        path = os.path.join(section_path, md_file_name)
        self._md_serializer.write(path, md)

    def section_start(self, section_path, level, subsections, tasks):
        # process index.md for the section, if available
        if self._publication_repo.contains_index(section_path):
            md = self.read_and_process_md(section_path, level, "index.md")
        else:
            logger.error(section_path, "does not exist in the publication repository")
            return
        # process subsections
        if subsections:
            md += "\n**{}:**\n\n".format(msg.CHAPTERS)
            for subsection in subsections:
                index_md = os.path.join(subsection, "index.md")
                title, _ = self._publication_repo.read_index(subsection)
                index = self._md_serializer.path(index_md)
                link_target = os.path.relpath(index, section_path)
                md += "  - [" + title + "]" + "(" + link_target + ")" + "\n"
        if tasks:
            # process tasks
            md += "\n**{}:**\n\n".format(msg.TASKS)
            for task_id in tasks:
                task = self._task_repo.task(task_id)
                if not task:
                    logger.error(task_id, "not present in the task repository")
                    continue
                st_md_file = task.id() + "-st.md"
                task_dir = self.task_output_dir(task.id(), section_path)
                st_md_path = os.path.join(task_dir, st_md_file)
                st_path = self._md_serializer.path(st_md_path)
                link_traget = os.path.relpath(st_path, section_path)
                md += "  - [" + task.title() + "]" + "(" + link_traget + ")" + "\n"
            
        # write the result to the file (converting to HTML if necessary)
        path = os.path.join(section_path, "index.md")
        self._md_serializer.write(path, md)


    def task_in_pub_start(self, task):
        logger.info(task.id())
        # task statement in Markdown format
        self._st_md = ""
        # add entry to the table of contents
        st_file = task.id() + "-st.md"
        st_path = os.path.join(self.task_output_dir(task.id()), st_file)
        link = self._md_serializer.path(st_path)
        self._toc_md += "  - [" + task.title() + "]" + "(" + link + ")" + "\n"
        
    def task_in_pub_title(self, task, level, current_occurrence):
        # append the title of the task as a heading
        self._st_md += "# " + task.title() + "\n\n"
        
    def task_in_pub_st(self, task, occurrence):
        if occurrence > 1:
            # warn that this is a repeated task and that it already occurred in the publication
            self._st_md += "*{}*\n\n".format(msg.REPEATED_TASK)
            
        # append the statement content, read from the task repository
        st_md = task.st_content()
        self._st_md += st_md + "\n\n"
        # append the link to the solution
        if self._standalone and "solution" in self._what_to_print:
            self._st_md += "\n\n[*{}*]({})\n\n".format(msg.SOLUTION, self._md_serializer.path(task.id() + "-sol.md"))

        # copy images
        for (title, image_path) in images_in_md(st_md):
            logger.info("Copy image:", image_path)
            src = os.path.join(task.dir(), image_path)
            dst = os.path.join(self.task_output_dir(task.id()), image_path)
            self._writer.copy_file(src, dst)
            
    def task_in_pub_sol(self, task, sols):
        # map each language to the solution in that language
        self._sol_md = dict()
        # iterate through all included languages
        for lang in self._langs:
            # resulting description in markdown format
            sol_md = ""
            sol_md = "# " + task.title() + " - {}\n".format(msg.SOLUTION)
            # add link to the problem statement
            if self._standalone:
                sol_md += "[*{}*]({})\n\n".format(msg.STATEMENT, self._md_serializer.path(task.id() + "-st.md"))
            # add the source code of the solution, with only the current language included
            sol_md += task.sol_content()
            sol_md = markdown_magic_comments.exclude_all_except(sol_md, "lang", [lang])
            # retain only the selected solutions
            if sols:
                sol_md = markdown_magic_comments.filter_by_key(sol_md, "sol", sols)
            # exclude divs
            sol_md = markdown_magic_comments.exclude(sol_md, "div", ["exclude"])
            # format divs
            sol_md = markdown_magic_comments.format_divs(sol_md)
            # resolve links
            sol_md = self.format_links(sol_md, task=task)
            # remember the current solution
            self._sol_md[lang] = sol_md + "\n\n"

            # copy images
            for (title, image_path) in images_in_md(sol_md):
                logger.info("Copy image:", image_path)
                src = os.path.join(task.dir(), image_path)
                dst = os.path.join(self.task_output_dir(task.id()), image_path)
                self._writer.copy_file(src, dst)

    def task_in_pub_source_code(self, task, sol_name, sol_desc, lang):
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

    def task_in_pub_report_pending_occurrences(self, task, current_occurrence, total_occurrences):
        # notify that the problem has other solutions
        self._st_md += "*{}*\n\n".format(msg.ADDITIONAL_SOLUTIONS_EXIST)

    def task_in_pub_end(self, task):
        # write statement to file
        st_path = os.path.join(self.task_output_dir(task.id()), task.id() + "-st.md")
        self._md_serializer.write(st_path, self._st_md, task.modification_time())

        if "solution" in self._what_to_print:
            if not self._join_langs:
                # write solutions in every language into separate files (converting to HTML if necessary)
                for lang in self._langs:
                    sol_path = os.path.join(self.task_output_dir(task.id()), "{}-{}-sol.md".format(task.id(), lang))
                    self._md_serializer.write(sol_path, self._sol_md[lang])
            else:
                # join solutions in all languages and write them into a single file
                joined_sol_md = ""
                for lang in self._langs:
                    joined_sol_md += "<div id='sol-{}' class='sol'>\n{}\n</div>\n".format(lang, self._sol_md[lang])
                    
                # add javascript language switcher
                if self._standalone and len(self._langs) != 1:
                    joined_sol_md = javascript.add_switcher(joined_sol_md, self._langs)

                # write the result into a single solution file (converting to HTML if necessary)
                sol_path = os.path.join(self.task_output_dir(task.id()), "{}-sol.md".format(task.id()))
                self._md_serializer.write(sol_path, joined_sol_md, task.modification_time())
            
    # action called at the end of publication processing 
    def end(self):
        self._md_serializer.write("toc.md", self._toc_md)
        self._md_serializer.close()

    # directory for the task in the output structure
    def task_output_dir(self, task_id, section_path=None):
        if not section_path:
            section_path = self._extra_info["section_path"]
        task = self._task_repo.task(task_id)
        return os.path.join(section_path, os.path.basename(task.dir()))

    
        
# Extend HTML publication visitor with additional functionallity
# related to the Petlja foundation packaging
class PublicationVisitorHTMLPetljaPackage(PublicationVisitorHTML):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start(self):
        super().start()
        self.write_index_json()

    def end(self):
        self._writer.write("section-titles.json", json.dumps(self.section_titles, indent=4, ensure_ascii=False))
        super().end()
        

    def task_in_pub_end(self, task):
        super().task_in_pub_end(task)
        
        task_dir = os.path.join("metadata", self.task_output_dir(task.id()))

        # Write metadata about the task to XML files
        self._writer.write(os.path.join(task_dir, "ProblemAttributes.xml"),
                           self.attributes_XML(task))
        self._writer.write(os.path.join(task_dir, "ProblemContent.xml"),
                           self.content_XML(task))

        # Copy all testcases to the output directory for the task
        if self._generate_tests:
            task.clear_testcases()
        
        if task.number_of_generated_testcases() == 0:
            task.extract_example_testcases()
            task.generate_testcases()

        def write_testcase(testcase):
            testcase_content = read_file(testcase)
            if testcase_content is None:
                logger.error(testcase, " - invalid file")
                return
            testcases_dir = os.path.join(task_dir, "TestCases")
            testcase_path = os.path.join(testcases_dir, os.path.basename(testcase))
            self._writer.write(testcase_path, testcase_content)
        
        for testcase in task.all_testcases():
            write_testcase(testcase)
            write_testcase(testcase[:-2] + "out")

        # Copy custom checker if it exists
        if task.has_checker():
            self._writer.copy_file(task.checker_src_path(), os.path.join(task_dir, task.checker_src_file_name()))
        
    def write_index_json(self):
        yaml = self._yaml_specification
        index = dict()
        index["Alias"] = yaml.alias()
        index["Title"] = yaml.title()
        index["ImageUrl"] = yaml.thumb()
        index["Description"] = yaml.short_description()
        index["Path"] = "index.html"
        index["Sections"] = []
        self._writer.write("index.json", json.dumps(index, indent=4, ensure_ascii=False))
        desc = yaml.full_description()
        desc_title, desc_content = self._publication_repo.read_md_file(desc)
        self._md_serializer.write(desc, desc_content)

    def attributes_XML(self, task):
        metadata = task.metadata()
        
        xml = dict()
        xml["Type"] = metadata.get("type", 0)
        xml["Title"] = metadata["title"]
        xml["Timelimit"] = round(metadata.get("timelimit", 1) * 1000)
        xml["Memlimit"] = metadata.get("memlimit", 64)
        xml["Owner"] = metadata.get("owner", "")
        xml["Origin"] = metadata.get("origin", "")
        xml["StatusUpdated"] = metadata.get("status-od", date.today().strftime("%Y-%m-$d"))
        root = ET.Element("ProblemAttributes")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        for (key, value) in xml.items():
            child = ET.SubElement(root, key)
            child.text = str(value)
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        return xml_str

    def content_XML(self, task):
        def dict_to_XML(dct, root):
            for (key, value) in dct.items():
                child = ET.SubElement(root, key)
                if isinstance(value, str):
                    child.text = str(value)
                else:
                    dict_to_XML_string(value, child)
        
        xml = dict()
        xml["ProblemStatement"] = (os.path.sep + os.path.join(self.task_output_dir(task.id()), task.id() + "-st.md")).replace("/", "\\")
        xml["Input"] = ""
        xml["Output"] = ""
        xml["ExampleInput"] = ""
        xml["ExampleOutput"] = ""
        xml["ProblemSolution"] = (os.path.sep + os.path.join(self.task_output_dir(task.id()), task.id() + "-sol.md")).replace("/", "\\") if self._task_spec.get("print", "full") == "full" else ""
        xml["SolutionPublic"] = "true" if self._task_spec.get("print", "full") == "full" else "false"

        if "extra-info" in self._task_spec:
            xml["ExtraInfo"] = self._task_spec["extra-info"]
        
        root = ET.Element("Data")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        problem = ET.SubElement(root, "ProblemCardPart")
        for (key, value) in xml.items():
            child = ET.SubElement(problem, key)
            child.text = str(value)
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        return xml_str

        
################################################################################

if __name__ == "__main__":
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

    
    task_repo = TaskRepository(tasks_dir, normalize_md=PandocMarkdown.fix)
    pub_repo = PublicationRepository(pub_dir, normalize_md=PandocMarkdown.fix)
    yaml = YAMLSpecification(args.yaml)
    visitor = PublicationVisitorHTML(yaml, task_repo, pub_repo, args.dst, langs=["cs", "cpp", "py"],
                                     standalone=args.standalone, css=args.css, header=args.header, join_langs=True)
    yaml.traverse(visitor)
