from .publication_visitor import TaskInPublicationVisitor, PublicationVisitor
import json
import os

class TestReporter:
    def __init__(self, task, report_json_file):
        self._task = task
        self._report_json_file = report_json_file
        if os.path.isfile(self._report_json_file):
            self._report = json.load(open(self._report_json_file, "r"))
        else:
            self._report = dict()
            self._report["id"] = task.id()

    def should_test(self, sol, lang):
        if not os.path.isfile(self._report_json_file):
            return True
        if os.path.getmtime(self._report_json_file) < self._task.modification_time():
            return True
        if not sol in self._report:
            return True
        if not lang in self._report[sol]:
            return True
        return False

    def report_testcase(self, sol, lang, testcase, result, time):
        if not sol in self._report:
            self._report[sol] = dict()
        if not lang in self._report[sol]:
            self._report[sol][lang] = dict()
        if not "testcases" in self._report[sol][lang]:
            self._report[sol][lang]["testcases"] = dict()
        self._report[sol][lang]["testcases"][testcase] = (result, time)

    def report_solution(self, sol, lang, statuses, max_time):
        if not sol in self._report:
            self._report[sol] = dict()
        if not lang in self._report[sol]:
            self._report[sol][lang] = dict()
        self._report[sol][lang]["status"] = statuses
        self._report[sol][lang]["max_time"] = max_time

    def end(self):
        print(json.dumps(self._report, indent=4), file=open(self._report_json_file, "w"))

        

class PublicationVisitorTest(PublicationVisitor, TaskInPublicationVisitor):
    def __init__(self, yaml_specification, task_repo, recompile=False, timeout=2):
        PublicationVisitor.__init__(self, yaml_specification, task_repo, None)
        TaskInPublicationVisitor.__init__(self)
        self._recompile = recompile
        self._timeout = timeout
            
    def task_in_pub_sol(self, task, sols):
        reporter = TestReporter(task, os.path.join(task.build_dir(), "test_report.json"))
        task.test_all(sols=sols, force_recompile=self._recompile, timeout=self._timeout, reporter=reporter)
