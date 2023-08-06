import os, sys

from .task_visitor import TaskVisitor
from .yaml_specification import YAMLSpecificationVisitor, YAMLSpecification
from .task_repository import TaskRepository
from .publication_repository import PublicationRepository
from .md_util import PandocMarkdown

from . import logger

# Specialization of the TaskVisitor for visiting tasks within a wider
# publication This class handles the possibility of having several
# different occurrences of a task in a single publication (containing
# different solutions). Each occurrence is within some section of a
# publication (at some level of nesting). These are specified as extra
# information.
class TaskInPublicationVisitor(TaskVisitor):
    def task_start(self, task):
        self.task_in_pub_start(task)
        
    def task_title(self, task):
        level = self._extra_info["level"]
        current_occurrence = self._extra_info["current_occurrence"]
        self.task_in_pub_title(task, level, current_occurrence)
        
    def task_st(self, task):
        current_occurrence = self._extra_info["current_occurrence"]
        self.task_in_pub_st(task, current_occurrence)
            
    def task_sol(self, task, sols):
        self.task_in_pub_sol(task, sols)

    def task_source_code(self, task, sol_name, sol_desc, lang):
        self.task_in_pub_source_code(task, sol_name, sol_desc, lang)
        
    def task_end(self, task):
        current_occurrence = self._extra_info["current_occurrence"]
        total_occurrences = self._extra_info["total_occurrences"]
        if current_occurrence < total_occurrences:
            self.task_in_pub_report_pending_occurrences(task, current_occurrence, total_occurrences)
        self.task_in_pub_end(task)

    # Hooks that can be specified by subclasses
    def task_in_pub_start(self, task):
        pass

    def task_in_pub_title(self, task, level, current_occurrence):
        pass
        
    def task_in_pub_st(self, task, current_occurence):
        pass

    def task_in_pub_sol(self, task, sols):
        pass
    
    def task_in_pub_source_code(self, task, sol_name, sol_desc, lang):
        pass
    
    def task_in_pub_report_pending_occurrences(self, task, current_occurrence, total_occurrences):
        pass

    def task_in_pub_end(self, task):
        pass

    
# Specialization of YAMLSpecification visitor that processes each task
# by the given visitor for a task in publication
class PublicationVisitor(YAMLSpecificationVisitor):
    def __init__(self, yaml_specification, task_repo, publication_repo, task_visitor=None, langs=[]):
        self._yaml_specification = yaml_specification
        self._task_repo = task_repo
        self._publication_repo = publication_repo
        self._task_visitor = task_visitor if task_visitor else self
        self._langs = langs
        self._task_occurrence = dict()

    # delegates task processing to the task visitor, counting task occurrences
    def task(self, section_path, level, task_id, task_spec):
        task = self._task_repo.task(task_id)
        if not task:
            logger.error(task_id, "not available in the task repository")
            return
        
        # issue a warning for all incomplete tasks
        if task.status() != "KOMPLETAN":
            logger.warn("incomplete task", task.id())

        # increment occurrence number for the current task
        self._task_occurrence[task.id()] = self._task_occurrence.get(task.id(), 0) + 1

        # delegate processing to the task in publication visitor
        extra_info = {
                        "yaml": self._yaml_specification,
                        "section_path": section_path,
                        "level": level,
                        "current_occurrence": self._task_occurrence[task.id()],
                        "total_occurrences": len(self._yaml_specification.sections_containing_task(task.id()))
                     }
        self._task_visitor.visit_task(task, self._langs, task_spec, extra_info)

################################################################################
# a very basic testing for task in publication visitor
    
class TestPublicationVisitor(PublicationVisitor, TaskInPublicationVisitor):
    def __init__(self, yaml_specification, task_repo, publication_repo, langs=[]):
        PublicationVisitor.__init__(self, yaml_specification, task_repo, publication_repo, langs=langs)
        TaskInPublicationVisitor.__init__(self)

    def task_start(self, task):
        print(task.id(), "-", task.title())
        
    def md_file(self, section_path, level, md_file_name, unnumbered=False):
        print("{" + os.path.join(section_path, md_file_name) + "}")

    def task_in_pub_st_repeated_occurrence(self, task, current_occurrence):
        print("REPEATED: ", task.id())

    def section_start(self, section_path, level, subsections, tasks):
        if self._publication_repo.contains_index(section_path):
            self.md_file(section_path, level, "index.md")
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Test publication visitor')
    parser.add_argument('yaml', type=str, help='YAML file')
    parser.add_argument('--tasks-dir', type=str, help='Directory where tasks are stored', default=None)
    parser.add_argument('--pub-dir', type=str, help='Directory where publication files are stored', default=None)
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
    yaml.traverse(TestPublicationVisitor(yaml, task_repo, pub_repo, langs=["cpp", "cs"]))
