import yaml
import re
import os
import traceback

from .util import default_encoding
from . import logger

################################################################################
# Visitor of the YAML specifiction content 

class YAMLSpecificationVisitor:
    # called on the start of the YAML content
    def start(self):
        pass
  
    # called on start of each section
    def section_start(self, section_path, level, subsections, tasks):
        pass

    # called on end of each section
    def section_end(self, section_path, level):
        pass

    # called for each Markdown file listed in the YAML content
    def md_file(self, section_path, level, md_file_name, unnumbered):
        pass
    
    # called for each task listed in the YAML content (task_spec is
    # the specification written in the YAML file)
    def task(self, section_path, level, task_id, task_spec):
        pass

    # called on the end of YAML content
    def end(self):
        pass


################################################################################
# Parses and processes the YAML specification of a publication. The
# main functionality is given by the recursive traverse method, that
# accepts visitors.

class YAMLSpecification:
    # YAML file is specifed in the constructor
    def __init__(self, yaml_file, encoding=default_encoding):
        # the whole YAML file is loaded
        self._yaml = yaml.safe_load(open(yaml_file, encoding=encoding))
        # for each task, sections where it occurrs are collected
        self._task_sections = self.collect_task_sections()

    # method that collects all sections for each task
    def collect_task_sections(self):
        # Auxiliary visitor used to collect task sections
        class CollectTaskSectionsVisitor(YAMLSpecificationVisitor):
            def __init__(self):
                self._task_sections = dict()

            def task(self, path, level, task_id, task_spec):
                if task_id in self._task_sections:
                    self._task_sections[task_id].append(path)
                else:
                    self._task_sections[task_id] = [path]

            def task_sections(self):
                return self._task_sections
        
        visitor = CollectTaskSectionsVisitor()
        self.traverse(visitor)
        return visitor.task_sections()
        

    # traversal of the whole publication content specified in the YAML
    # file for each item in the content, appropriate actions are
    # performed by the given visitor
    def traverse(self, visitor):
        # auxiliary function that recursively traverses the given YAML fragment
        def traverse_rec(visitor, yaml_fragment, path, level):
            if not yaml_fragment:
                return
            # all top level elements are analyzed
            for element in yaml_fragment:
                # they can be either raw Markdown files
                if isinstance(element, str) and element.endswith(".md"):
                    # files starting with . should have unnumbered headings (used for Preface, Appendix, ...)
                    unnumbered = element[0] == '.'
                    md_file_name = element[1:] if unnumbered else element
                    # visitor is notified about the raw Markdown file
                    visitor.md_file(path, level, md_file_name, unnumbered=unnumbered)
                # or section paths or task specifications (both given as dictionaries)
                if isinstance(element, dict):
                    # for each key and value in the dictionary
                    for key, val in element.items():
                        # sections contain lists
                        if isinstance(val, list):
                            try:
                                # the current key is the section name
                                section = key
                                # and the value is the content of that section
                                section_contents = val
                                # path is extended by the section name
                                section_path = os.path.join(path, section)

                                # extract subsections and tasks
                                subsections = []
                                tasks = []
                                for item in section_contents:
                                    if isinstance(item, str) and item.endswith(".md"):
                                        continue
                                    
                                    key = list(item)[0]
                                    val = item[key]
                                    if isinstance(val, list):
                                        subsection = key
                                        subsections.append(os.path.join(section_path, subsection))
                                    else:
                                        task_id = key
                                        tasks.append(task_id)

                                # visitor is notified about the start of the current section
                                visitor.section_start(section_path, level, subsections, tasks)
                                # recursively process the section content
                                traverse_rec(visitor, section_contents, section_path, level+1)
                                # visitor is notified about the end of the current section
                                visitor.section_end(section_path, level)
                            except:
                                traceback.print_exc()
                                logger.error("section", section_path, "failed")
                                
                        # otherwise, the dictionary describes the task
                        else:
                            # the key is the task identifier
                            task_id = key
                            # the value is the task specification
                            task_spec = val
                            try:
                                # visitor is notified about the task
                                visitor.task(path, level, task_id, task_spec)
                            except:
                                traceback.print_exc()
                                logger.error("task", task_id, "failed")

        # visitor is notified about the start of the publication
        visitor.start()
        # recursively traverse the whole content
        traverse_rec(visitor, self._yaml["content"], "", 1)
        # visitor is notified about the end of the publication
        visitor.end()

    # Various metadata read from the YAML file
        
    def title(self):
        return self.metadatum("title").strip()

    def alias(self):
        return self.metadatum("alias").strip()
    
    def thumb(self):
        return self.metadatum("thumb").strip()

    def short_description(self):
        return self.metadatum("short-description").strip()

    def full_description(self):
        return self.metadatum("full-description")

    def languages(self):
        return self.metadatum("languages")

    def langs(self):
        return self.metadatum("languages")
    
    def authors(self):
        return self.metadatum("authors").strip()

    def metadatum(self, key):
        return self._yaml.get(key, "")

    # path to the section where the task with the given id occurrs for the first time
    def first_section_containing_task(self, task_id):
        return self._task_sections.get(task_id, [None])[0]

    # all sections where the task with the given id occurrs
    def sections_containing_task(self, task_id):
        return self._task_sections.get(task_id, [])
        

################################################################################
# A very simple test for this class
class ListTasks(YAMLSpecificationVisitor):
    def __init__(self, yaml):
        self._yaml = yaml
        
    def task(self, path, level, task_id, task_spec):
      print(task_id, self._yaml.sections_containing_task(task_id))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Read and analyze YAML specification')
    parser.add_argument('yaml', type=str,
                        help='YAML file')
    args = parser.parse_args()
    yaml = YAMLSpecification(args.yaml)
    yaml.traverse(ListTasks(yaml))
