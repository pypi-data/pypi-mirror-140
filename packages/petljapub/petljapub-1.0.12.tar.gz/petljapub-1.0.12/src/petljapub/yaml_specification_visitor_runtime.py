import sys, os, glob
import math
import tempfile
import json
import time
import statistics

from .yaml_specification import YAMLSpecification, YAMLSpecificationVisitor
from .task_repository import TaskRepository
from .task import Task

# supported programming languages
langs = ["cs", "cpp"]

# append all timings for a given task to a given csv file
def append_time_to_csv(task, csv_file):
    time_json = time_json_path(task)
    # skip all tasks for which there are no time measurments
    if not os.path.isfile(time_json):
        return
    # load data from the json file
    time_json = json.load(open(time_json, "r"))
    # process all solutions
    for sol in time_json["times"]:
        # and all languages
        for lang in time_json["times"][sol]:
            # store relevant data in a row and append it to the csv file
            row = []
            row.append("\"" + time_json["dir"] + "\"")
            row.append(time_json["id"])
            row.append(sol)
            row.append(lang)
            for time in time_json["times"][sol][lang]:
                if not time.endswith("_TO"):
                    time_str = str(time_json["times"][sol][lang][time])
                    if time + "_TO" in time_json["times"][sol][lang]:
                        time_str += "TO"
                    row.append(time_str)
            # append row to csv_file
            csv = open(csv_file, "a")
            print(",".join(row), file=csv)
            csv.close()

# determine time limits for the given task
def calibrate(task, params):
    # results of the calibration are stored in a dictionary
    calibration = {}
    calibration["dir"] = task.dir()
    calibration["id"] = task.id()
    
    times = time_tests(task, params)["times"]
    ##############################
    ### HACK - modify C# times ###
    for sol in times:
        if "cs" in times[sol]:
            for testcase, time in times[sol]["cs"].items():
                if not testcase.endswith('_TO'):
                    times[sol]["cs"][testcase] = time * 0.5
    ##############################

    # group times by expected status - OK and TLE
    OK_times = []
    TLE_times = []
    for sol in times:
        sol_times = []
        for lang in times[sol]:
            if not (lang in langs): continue
            # time for the slowest testcase
            max_time = max(times[sol][lang].values())
            sol_times.append(max_time)
        if not sol_times:
            continue
        status = task.expected_status(sol)
        if status == "WA":
            continue
        if status == "OK":
            OK_times.append(max(sol_times))
        else:
            TLE_times.append(min(sol_times))

    # calculate timeout with a given margin (125% of the slowest
    # program that should pass)
    margin = 1.25
    timeout = math.ceil(margin * max(OK_times))
    calibration["timeout"] = timeout

    # determine the quality of the calculated timeout 
    if TLE_times:
        if timeout > min(TLE_times):
            quality = "FAIL"
        elif margin * timeout > min(TLE_times):
            quality = "TIGHT"
        else:
            quality = "OK"
    else:
        quality = "OK"
    calibration["quality"] = quality

    # detailed explanation of the calibration quality
    details = {}
    for sol in times:
        details[sol] = {}
        details[sol]["status"] = task.expected_status(sol)
        for lang in times[sol]:
            if not (lang in langs): continue
            # number of testcases that pass
            OK = sum(1 for test, time in times[sol][lang].items() if test[-2:] == "in" and time <= timeout)
            # number of testcases that fail
            TLE = len(times[sol][lang].items()) - OK
            details[sol][lang] = {}
            details[sol][lang]["testcases"] = str(OK) + "+" + str(TLE)
            # max time for all testcases
            max_time = max(times[sol][lang].values())
            details[sol][lang]["max_time"] = max_time
    calibration["details"] = details

    # write the timeout value in -st.md file
    task.set_timeout(timeout)

    # return the result
    return calibration
    

# Auxiliary visitor class for processing yaml specification

# measure runtime for each task specified in the yaml specification
class RuntimeTaskVisitor(YAMLSpecificationVisitor):
    def __init__(self, repo, params):
        self._repo = repo
        self._params = params
    
    def task(self, path, level, task_id, task_spec):
        task = self._repo.task(task_id)
        task.measure_all_runtimes(self._params)

# append time data to a csv file for each task specified in the yaml specification
class TimeCSVVisitor(YAMLSpecificationVisitor):
    def __init__(self, repo, csv_file, params):
        self._repo = repo
        self._csv_file = csv_file
        self._params = params
    
    def task(self, path, level, task_id, task_spec):
        task = self._repo.task(task_id)
        task.measure_all_runtimes(self._params)
        append_time_to_csv(task, self._csv_file)

# determine timeout for each task specified in the yaml specification
class CalibrateVisitor(YAMLSpecificationVisitor):
    def __init__(self, repo, params):
        self._repo = repo
        self._params = params
    
    def task(self, path, level, task_id, task_spec):
        calibration = calibrate(self._repo.task(task_id), self._params)
        # warn of if timeout is too high
        if calibration["timeout"] >= 500:
            print("timeout greater than 0.5s " + task_id)
        # warn if calibration quality is not OK
        if calibration["quality"] != "OK":
            print(json.dumps(calibration, indent=4))

# Main program
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Measure solution runtimes')
    parser.add_argument('task_spec', type=str,
                        help='task specification (either a task base directory or a yaml file with a list of tasks)')
    parser.add_argument('-t', '--timeout', type=float, default=2,
                        help='timeout for each testcase in seconds')
    parser.add_argument('-r', '--repeat', type=int, default=3,
                        help='nuber of testcase repetitions (for better accuracy)')
    parser.add_argument('-f', '--force', action='store_true',
                        help='force execution of solutions')
    parser.add_argument('-csv', '--csv', type=str, 
                        help='generate csv of all timings')
    parser.add_argument('-c', '--calibrate', action='store_true',
                        help='calibrate time limit')

    args = parser.parse_args()

    params = {
        "force_run": args.force,
        "timeout": args.timeout,
        "repeat": args.repeat
    }

    if args.task_spec == '.':
        args.task_spec = os.getcwd()
    
    if args.task_spec.endswith('.yml') or args.task_spec.endswith('.yaml'):
        if not os.path.isfile(args.task_spec):
            sys.exit("Error reading YAML file")
        yaml = YAMLSpecification(args.task_spec)
        repo = TaskRepository(os.path.dirname(args.task_spec))
        if args.csv != None:
            yaml.traverse(TimeCSVVisitor(repo, args.csv, params))
        elif args.calibrate:
            yaml.traverse(CalibrateVisitor(repo, params))
        else:
            yaml.traverse(RuntimeTaskVisitor(repo, params))
    else:
        args.task_spec = args.task_spec.rstrip(os.path.sep)
        task = Task(args.task_spec)
        print(json.dumps(task.measure_all_runtimes(params), indent=4))
