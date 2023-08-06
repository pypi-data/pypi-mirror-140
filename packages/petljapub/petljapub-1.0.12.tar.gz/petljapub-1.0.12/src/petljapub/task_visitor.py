import sys, os

from .md_util import PandocMarkdown
from . import logger

# Visits and processes a single task.
# Based on the given task specification it is determined which
# components (statement, solutions, source codes) should be processed.
# Details of processing need to be specified in subclasses.

# Task specification is a dictionary in the same forma as given in
# yaml specifications of a publication.
class TaskVisitor:
    # called to process a single task it analyzes the given task
    # specification and based on it processes chosen components of the
    # task
    def visit_task(self, task, langs=[], task_spec=dict(), extra_info=None):
        # memorize auxiliary data so that it does not need to be
        # passed around in method parameters
        self._langs = langs
        self._task_spec = task_spec
        self._extra_info = extra_info

        # a hook called when the processing of the task is started
        # (the hook is defined by subclasses)
        self.task_start(task)
        
        # determine what components to print - if it is not specified
        # in the task specification, everything is processed
        print_spec = task_spec.get("print", "full")
        self._what_to_print = {
            "full": ["statement", "solution", "source"],
            "solution": ["statement", "solution"],
            "statement": ["statement"],
            "exclude": []
        }[print_spec]

        # print the task title
        self.task_title(task)

        # if the task statement should be processed
        if "statement" in self._what_to_print:
            # the hook (defined in subclasses) is called
            self.task_st(task)
    
        # if task solutions should be processed
        if "solution" in self._what_to_print:
            # solutions that need to be processed
            # it is not specified in the task_specification, then all solutions are processed
            solutions = task_spec.get("solutions", [])
            self.task_sol(task, solutions)
            
        # if source codes should be processed
        if "source" in self._what_to_print:
            # codes that need to be processed
            # it is not specified in the task_specification, then all solutions are processed
            codes = task_spec.get("code", None)
            # auxiliary function used to process individual source codes 
            self.task_source_codes(task, codes)

        # a hook called when the processing of the task is finished
        # (the hook is defined by subclasses)
        self.task_end(task)
            

    # analyzes task metadata and the task repository to find all
    # available source codes, and processes the ones given by the task
    # specification
    def task_source_codes(self, task, selected_codes):
        # find all available solutions (specified in the task metadata)
        all_sol_descs = task.solutions()
        # if metadata is missing, it is assumed that only one solution exists
        if not all_sol_descs:
            all_sol_descs = [{"name": "ex0", "lang": ["cpp", "cs", "c", "py"]}]
        # itterate through all solutions (and their descriptions)
        for sol_desc in all_sol_descs:
            # solution name ("ex0", "ex1", ...)
            sol_name = sol_desc["name"]
            # if some codes need to be selected and the current
            # solution is not among them, then the current code is
            # skipped
            if selected_codes != None and not sol_name in selected_codes:
                continue
            for lang in sol_desc["lang"]:
                # process only codes in the current list of languages
                # (if the list is empty, all codes are processed)
                if not self._langs or lang in self._langs:
                    # a hook called for an individual source code
                    # (defined in subclasses)
                    self.task_source_code(task, sol_name, sol_desc, lang)

    # a list of hooks that need to be defined in subclasses
                
    # a hook called when the processing of the gien task is started
    def task_start(self, task):
        pass

    # a hook called to process the task title
    def task_title(self, task):
        pass
        
    # a hook called to process the task statement
    def task_st(self, task):
        pass

    # a hook called to process solution description, including only
    # solutions from the given list of solutions ("ex0", "ex1", ...)
    # and only on selected languages ("cs", "cpp", "py", ...)
    def task_sol(self, task, sols):
        pass

    # a hook called to process a single source code for the task with
    # the given task_id, with the given solution name (e.g., "ex0"),
    # in the given language (e.g., "cs"), where the metadata
    # description of the solution is also known
    def task_source_code(self, task, sol_name, sol_desc, lang):
        pass
    
    # a hook called when the processing of the gien task is ended
    def task_end(self, task):
        pass

################################################################################
# a very basic testing for task visitor

class TestTaskVisitor(TaskVisitor):
    def task_start(self, task):
        print("START:", task.id(), "EXTRA INFO:", self._extra_info)

    def task_end(self, task):
        print("END:", task.id())
        
    def task_st(self, task):
        print("ST:", task.id())

    def task_sol(self, task, sols):
        print("SOLUTIONS TO PRINT:", sols)
    
    def task_source_code(self, task, sol_name, sol_desc, lang):
        print(task.src_file_name(sol_name, lang))
    
if __name__ == "__main__":
    import argparse
    from .task import Task
    
    parser = argparse.ArgumentParser(description='Test visiting a single task')
    parser.add_argument('task', type=str, help='Dir of the task')
    args = parser.parse_args()

    if not os.path.isdir(args.task):
        logger.error("Task does not exist")
        sys.exit(-1)
    
    dir = os.path.abspath(args.task)
    task = Task(dir)
    task_visitor = TestTaskVisitor()
    task_visitor.visit_task(task)
    task_visitor.visit_task(task,
                            task_spec={"print": "statement"})
