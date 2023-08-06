import os, sys, glob, shutil, getpass
import re
import json
from datetime import date
from string import Template
import tempfile

from invoke import task

from petljapub import logger

from petljapub.translit import lat_to_cyr, cyr_to_lat
from petljapub.util import read_file, write_to_file
from petljapub.md_util import PandocMarkdown
from petljapub.serialization import ZipWriter

from petljapub.task import Task
from petljapub.task_repository import TaskRepository
from petljapub.publication_repository import PublicationRepository
from petljapub.yaml_specification import YAMLSpecification, YAMLSpecificationVisitor
from petljapub.yaml_specification_visitor_stats import YAMLSpecificationVisitorStats
from petljapub.yaml_specification_visitor_runtime import RuntimeTaskVisitor
from petljapub.task_visitor_html import TaskVisitorHTML
from petljapub.publication_visitor_test import PublicationVisitorTest
from petljapub.publication_visitor_html import PublicationVisitorHTML, PublicationVisitorHTMLPetljaPackage
from petljapub.publication_visitor_tex import PublicationVisitorTeX
from petljapub.compilation import tgen_dir
from petljapub.plot_times import plot_times
from petljapub.configure_compilers import configure_compilers

sys.stdout.reconfigure(encoding='utf-8')
# enable terminal colors on windows
if sys.platform == "win32":
    try:
        os.system("color")
    except:
        logger.warn("Could not set colored terminal")
        logger.color(False)

# directory where all auxiliary data files are stored
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# identifier of the task in the current directory
def task_id():
    return Task.extract_id_from_dir(os.path.basename(os.getcwd()))

# check if the script is invoked from a task directory
def is_task_dir(dir, is_new_dir=False):
    st = task_id() + "-st.md"
    return re.match(r"\d{2}\ .+", dir) and (is_new_dir or os.path.isfile(st))

# ensure that script is called within a task directory
def ensure_task_dir(is_new_dir=False):
    dir = os.path.basename(os.getcwd())
    if not is_task_dir(dir, is_new_dir):
        logger.error("Task directory must start by two leading zeroes and must contain -st.md file")
        return False
    return True
    
# check if the file exists and if it does not try to find it in the given default directory
def obtain_file(file, default_dir):
    if file and not os.path.isfile(file):
        default_file = os.path.join(default_dir, file)
        if not os.path.isfile(default_file):
            logger.warn("ignoring non-existent file", file)
            file = None
        else:
            logger.info("using preinstalled file:", default_file)
            file = default_file
    return file

# suffix of the solution file
def solution(n):
    return "ex" + str(n)

################################################################################
## initial configuration

@task
def configure(ctx):
    """
    Detect compilers for programming langauges (C++, C#, C, Python) and pandoc for generating LaTeX and HTML from Markdown. This command must be run prior to using petljapub.
    """
    configure_compilers()

################################################################################
## Processing of the current task
    
@task
def new(ctx):
    """
    Start working on a new task (template files are generated)
    """
    if not ensure_task_dir(True):
        return
    if len(os.listdir(os.getcwd())) != 0:
        logger.error("directory must be empty")
        return
    template_dir = os.path.join(data_dir, '_task_template')
    task_name_cyr = lat_to_cyr(task_id().replace("_", " ").capitalize())
    subst = {
        "TASK_NAME": task_id(),
        "TASK_NAME_CYR": lat_to_cyr(task_id().replace("_", " ").capitalize()),
        "TASK_OWNER": getpass.getuser(),
        "DATE": date.today().strftime("%Y-%m-%d")
    }

    try:
        for file in os.listdir(template_dir):
            if file.startswith("__"):
                continue
            file_contents = read_file(os.path.join(template_dir, file))
            write_to_file(os.path.basename(file).replace("task", task_id()),
                          Template(file_contents).safe_substitute(subst))
    except:
        logger.error("Error copying template files")

@task
def clean(ctk):
    """
    Delete all generated files
    """

    if not ensure_task_dir(True):
        return

    if os.path.isdir(Task.build_dir_name()):
        try:
            shutil.rmtree(Task.build_dir_name())
        except:
            logger.error("Error removing directory", Task.build_dir_name())
        

@task(help = {
    'lang': "Programming language of the solution that is compiled (e.g., cpp, cs, py)",
    'sol': "The number of the solution that is compiled (e.g. for compiling program-ex2.cpp the value 2 should be given). If not specified, the main solution is compiled (e.g., program.cpp)."
})
def compile(ctx, lang, sol=0):
    """
    Compile a solution file for the current task
    """

    if not ensure_task_dir():
        return
    task = Task(os.getcwd())
    task.compile(solution(sol), lang)
    

@task
def c(ctx, lang, sol=0):
    """
    Compile a solution file for the current task (shortcut for 'petljapub compile')
    """
    compile(ctx, lang, sol)


@task(help = {
    'lang': "Programming language of the solution that is run (e.g., cpp, cs, py)",
    'sol': "The number of alternative solution that is run (for running program-ex2.cpp the value 2 should be given). If not specified, the main solution is run (e.g., program.cpp).",
    'testcase': "Run on the testcase with the given number, printing result to stdout."
})
def run(ctx, lang, sol=0, testcase=-1):
    """
    Run a solution interactively (using stdin and stdout)
    """

    if not ensure_task_dir():
        return
    task = Task(os.getcwd())
    if testcase >= 1:
        task.run(solution(sol), lang, testcase, output="stdout")
    else:
        task.run_interactive(solution(sol), lang)
    
@task
def r(ctx, lang, sol=0, testcase=-1):
    """
    Run a solution interactively (shortcut for 'petljapub run')
    """
    run(ctx, lang, sol, testcase)
    
    
@task(help={
    'crafted_dir': "Directory where crafted tests are stored"
    })
def tests_gen(ctx, crafted_dir=None, verbosity=3):
    """
    Generate all testcases for the current task
    """
    if not ensure_task_dir():
        return
    
    logger.verbosity(verbosity)
    
    task = Task(os.getcwd())
    task.extract_example_testcases()
    task.generate_testcases()
    if crafted_dir:
        task.prepare_crafted_testcases(crafted_dir)

@task
def tg(ctx, crafted_dir=None, verbosity=3):
    """
    Generate all testcases for the current task (shortcut for 'petljapub tests-gen')
    """
    tests_gen(ctx, crafted_dir, verbosity)
    
@task
def tests_zip(ctx):
    """
    Generate zip with all testcases for the current task
    """
    if not ensure_task_dir():
        return

    clean(ctx)
    
    task = Task(os.getcwd())
    task.generate_testcases()
    
    zip_file = os.path.join(task.build_dir(), "testcases.zip")
    writer = ZipWriter(zip_file)
    writer.open()

    i = 1
    for testcase_in in (task.example_testcases() + task.crafted_testcases() + task.generated_testcases()):
        logger.info(testcase_in)
        writer.copy_file(testcase_in, "{:02d}.in".format(i))
        testcase_out = testcase_in[0:-2] + "out"
        logger.info(testcase_out)
        writer.copy_file(testcase_out, "{:02d}.out".format(i))
        i += 1
    writer.close()
    logger.info("Testcases stored in", zip_file)

@task
def tz(ctx):
    """
    Generate zip with all testcases for the current task (shortcut for 'petljapub tests-zip')

    """

    tests_zip(ctx)
    
@task
def compile_checker(ctx):
    """
    Compile custom checker (if exists)
    """
    if not ensure_task_dir():
        return
    task = Task(os.getcwd())
    task.compile_checker()

@task(help={
    'lang': "Programming language of the solution that is tested (e.g., cpp, cs, py)",
    'sol': "The number of the solution that is tested (e.g. for compiling program-ex2.cpp the value 2 should be given). If not specified, the main solution is tested (e.g., program.cpp).",
    'recompile': "Recompile the solution (and the custom checker if it exists) before checking",
    'timeout': "Timeout in seconds for each testcase (1 seconds is the default value)",
    'verbosity': "Level of messages printed to the user (from 0/quiet to 5/full)"
})
def test(ctx, lang, sol=0, recompile=True, timeout=1.0, verbosity=3):
    """
    Test the given solution for the current task
    """
    if not ensure_task_dir():
        return
    
    task = Task(os.getcwd())
    logger.verbosity(verbosity)
    task.test_on_all_testcases("ex" + str(sol), lang, force_recompile=recompile, timeout=timeout)

@task
def t(ctx, lang, sol=0, recompile=True, timeout=1.0, verbosity=3):
    """
    Test the given solution for the current task (shortcut for 'petljapub test')
    """
    test(ctx, lang, sol, recompile, timeout, verbosity)
    
    
@task(help={'recompile': "Recompile all solutions (and the custom checker if it exists) before checking",
            'timeout': "Timeout for every testcase (in seconds)",
            'verbosity': "Level of messages printed to the user (from 0/quiet to 5/full)"})
def test_all(ctx, recompile=True, timeout=1.0, verbosity=3):
    """
    Test all solutions for the current task
    """
    if not ensure_task_dir():
        return
    task = Task(os.getcwd())
    logger.verbosity(verbosity)
    task.test_all(force_recompile=recompile, timeout=timeout)


@task(help={
    'lang': "Programming language of the solution that is tested (e.g., cpp, cs, py)",
    'sol': "The number of the solution that is tested (e.g. for compiling program-ex2.cpp the value 2 should be given). If not specified, the main solution is tested (e.g., program.cpp).",
    'recompile': "Recompile all solutions (and the custom checker if it exists) before checking"})
def test_examples(ctx, lang, sol=0, recompile=True):
    """
    Extract and test examples from the problem statement of the current task and test the given solution on those tests.
    """
    if not ensure_task_dir():
        return
    task = Task(os.getcwd())
    task.test_on_example_testcases("ex" + str(sol), lang, recompile)

@task(help={})
def scoring_yaml(ctx, subtask=False):
    """
    Generate yaml for scoring testcases
    """
    if not ensure_task_dir():
        return
    task = Task(os.getcwd())
    task.scoring_yaml(subtask)
    
    
@task(help={
    'force-run': "If not true, times can be read from time.json file (if it is available)",
    'timeout': "Timeout (in seconds) for each solution run",
    'repeat': "For better accurracy, solutions runs are repeated and median value is used",
    'plot': "Graphically show runtimes (using bar plot)",
    'lang': "Plot only runtime for the given language",
    'sol': "Plot only runtime for the given solution"
})
def show_runtime(ctx, force_run=False, timeout=1.0, repeat=3, plot=False, sol=None, lang=None):
    """
    Measure runtime for the current task
    """
    if not ensure_task_dir():
        return
    task = Task(os.getcwd())
    params = {
        "force_run": force_run,
        "timeout": timeout,
        "repeat": repeat
    }
    times = task.measure_all_runtimes(params)
    if plot:
        plot_times(times, lang=lang, sol=sol)
    print(json.dumps(times, indent=4))

@task(iterable=["langs"])
def html_preview(ctx, langs=None, css="pandoc.css", header=None):
    """
    Generate html preview for the current task
    """
    
    # default languages
    if not langs:
        langs = ["cpp", "cs", "py"]
    
    if not ensure_task_dir():
        return

    # if files do not exist, try to find preinstalled files in the data directory
    css = obtain_file(css, os.path.join(data_dir, "html"))
    header = obtain_file(header, os.path.join(data_dir, "md"))

    task = Task(os.getcwd(), normalize_md=PandocMarkdown.fix)

    task_visitor = TaskVisitorHTML(css, header)
    task_visitor.visit_task(task, langs)

################################################################################
## Processing of yaml specifications

@task(help={'tasks-dir': "Directory where tasks are stored (if different from the one where the YAML file resides)"})
def generate_yaml(ctx, tasks_dir):
    if tasks_dir and not os.path.isdir(tasks_dir):
        logger.error(tasks_dir, "is not a directory")
    task_repo = TaskRepository(tasks_dir)
    for task in task_repo.tasks():
        print(task)


@task(help={'yaml': "YAML specification of the publication",
            'tasks-dir': "Directory where tasks are stored (if different from the one where the YAML file resides)",
            'recompile': "Recompile all solutions (and the custom checker if it exists) before checking",
            'timeout': "Timeout in seconds for running each testcase"})
def yaml_test(ctx, yaml, tasks_dir=None, pub_dir=None, recompile=False, timeout=1.0, verbosity=3):
    """
    Check correctness of all solutions for all tasks specified in a yaml file
    """
    logger.verbosity(verbosity)

    if not tasks_dir:
        tasks_dir = os.path.dirname(yaml)
    if not pub_dir:
        pub_dir = os.path.dirname(yaml)

    if not os.path.exists(yaml):
        logger.error(yaml, "does not exist")
        return

    if tasks_dir and not os.path.isdir(tasks_dir):
        logger.error(tasks_dir, "is not a directory")

    if pub_dir and not os.path.isdir(pub_dir):
        logger.error(pub_dir, "is not a directory")
        
    task_repo = TaskRepository(tasks_dir)
    pub_repo = PublicationRepository(pub_dir)
    yaml_specification = YAMLSpecification(yaml)
    yaml_specification.traverse(PublicationVisitorTest(yaml_specification, task_repo, recompile, timeout))

@task(help={
    'yaml': "YAML specification of the publication",
    'tasks-dir': "Directory where tasks are stored (if different from the one where the YAML file resides)",
    'force-run': "If not true, times can be read from time.json file (if it is available)",
    'timeout': "Timeout (in seconds) for each solution run",
    'repeat': "For better accurracy, solutions runs are repeated and median value is used",
})
def yaml_runtime(ctx, yaml, tasks_dir=None, pub_dir=None, force_run=False, timeout=1.0, repeat=3):
    """
    Measure runtime for all tasks specified in the yaml file
    """
    params = {
        "force_run": force_run,
        "timeout": timeout,
        "repeat": repeat
    }

    if not tasks_dir:
        tasks_dir = os.path.dirname(yaml)
        
    if not os.path.exists(yaml):
        logger.error(yaml, "does not exist")
        return

    if tasks_dir and not os.path.isdir(tasks_dir):
        logger.error(tasks_dir, "is not a directory")
        
    task_repo = TaskRepository(tasks_dir)
    yaml_specification = YAMLSpecification(yaml)
    yaml_specification.traverse(RuntimeTaskVisitor(task_repo, params))

# report statistics about the publication
@task(help={'yaml': "YAML specification of the publication",
            'tasks-dir': "Directory where tasks are stored (if different from the one where the YAML file resides)"})
def yaml_stats(ctx, yaml, tasks_dir=None):
    """
    Report statistics about tasks in yaml file and repository

    """
    if not tasks_dir:
        tasks_dir = os.path.dirname(yaml)

    if not os.path.exists(yaml):
        logger.error(yaml, "does not exist")
        return

    if tasks_dir and not os.path.isdir(tasks_dir):
        logger.error(tasks_dir, "is not a directory")

    yaml = YAMLSpecification(yaml)
    task_repo = TaskRepository(tasks_dir)
    yaml.traverse(YAMLSpecificationVisitorStats(yaml, task_repo))
    
# build the publication in html format
@task(help={'yaml': "YAML specification of the publication",
            'tasks-dir': "Directory where tasks are stored (if different from the one where the YAML file resides)",
            'pub-dir': "Directory where publication files are stored (if different from the one where the YAML file resides)",
            'dst': "Location where generated files are stored (directory or a ZIP file)",
            'standalone': "Controls if standalone HTML files are generated, or just HTML fragments to be included in other HTML files",
            'join-langs': "Controls whether a single or seperate HTML files are generated for different programming languages",
            'css': "CSS stylesheet to be applied to standalone HTML files",
            'header': "A header to be prepended to each Markdown file before conversion to HTML is applied",
            'lat': "If this flag is set, all content ist transliterated to latin alphabet"})
def yaml_html(ctx, yaml, dst, tasks_dir=None, pub_dir=None, standalone=True, join_langs=True, css=None, header=None, lat=False, verbosity=3):
    """
    Build task or publication in HTML format
    """
    logger.verbosity(verbosity)

    if not tasks_dir:
        tasks_dir = os.path.dirname(yaml)
    if not pub_dir:
        pub_dir = os.path.dirname(yaml)

    if not os.path.exists(yaml):
        logger.error(yaml, "does not exist")
        return

    if tasks_dir and not os.path.isdir(tasks_dir):
        logger.error(tasks_dir, "is not a directory")
        return

    if pub_dir and not os.path.isdir(pub_dir):
        logger.error(pub_dir, "is not a directory")
        return

    css = obtain_file(css, os.path.join(data_dir, "html"))
    header = obtain_file(header, os.path.join(data_dir, "md"))
        
    task_repo = TaskRepository(tasks_dir, normalize_md=PandocMarkdown.fix)
    pub_repo = PublicationRepository(pub_dir, normalize_md=PandocMarkdown.fix)

    yaml = YAMLSpecification(yaml)
    translit = (lambda x: x) if not lat else cyr_to_lat
    visitor = PublicationVisitorHTML(yaml, task_repo, pub_repo, dst, langs=yaml.langs(),
                                     html=True, standalone=standalone, css=css, header=header, join_langs=join_langs, translit=translit)
    yaml.traverse(visitor)

# build the publication in html format for petlja publishing
@task(help={'yaml': "YAML specification of the publication",
            'dst': "Location where generated files are stored (directory or a zip file)",
            'tasks-dir': "Directory where tasks are stored (if different from the one where the YAML file resides)",
            'pub-dir': "Directory where publication files are stored (if different from the one where the YAML file resides)",
            'join-langs': "Controls whether a single or seperate HTML files are generated for different programming languages",
            'header': "A header to be prepended to each Markdown file before conversion to HTML is applied",
            'lat': "If this flag is set, all content ist transliterated to latin alphabet",
            'generate-tests': "Forces generating all test cases from scratch"})
def yaml_petlja_package(ctx, yaml, dst, tasks_dir=None, pub_dir=None, join_langs=True, header=None, lat=False, generate_tests=False):
    """
    Build package for publishing the publication on petlja.org
    """

    if not tasks_dir:
        tasks_dir = os.path.dirname(yaml)
    if not pub_dir:
        pub_dir = os.path.dirname(yaml)

    if not os.path.exists(yaml):
        logger.error(yaml, "does not exist")
        return

    if tasks_dir and not os.path.isdir(tasks_dir):
        logger.error(tasks_dir, "is not a directory")
        return

    if pub_dir and not os.path.isdir(pub_dir):
        logger.error(pub_dir, "is not a directory")
        return

    header = obtain_file(header, os.path.join(data_dir, "md"))
    
    task_repo = TaskRepository(tasks_dir, normalize_md=PandocMarkdown.fix)
    pub_repo = PublicationRepository(pub_dir, normalize_md=PandocMarkdown.fix)
    
    yaml = YAMLSpecification(yaml)
    translit = (lambda x: x) if not lat else cyr_to_lat
    visitor = PublicationVisitorHTMLPetljaPackage(yaml, task_repo, pub_repo, dst, langs=yaml.langs(),
                                                  html=True, header=header, join_langs=join_langs, translit=translit)
    visitor._generate_tests = generate_tests
    yaml.traverse(visitor)

# build the publication in latex format ready for producing pdf
@task(help={'yaml': "YAML specification of the publication",            
            'dst': "Path of the resulting file (all image files are saved in the same directory)",
            'tasks-dir': "Directory where tasks are stored (if different from the one where the YAML file resides)",
            'pub-dir': "Directory where publication files are stored (if different from the one where the YAML file resides)",
            'tex': "If tex is false, Markdown is not converted to TeX",
            'header': "A header to be prepended to the Markdown file before conversion to TeX is applied",
            'tex-template': "A tex template to be used",
})
def yaml_tex(ctx, yaml, dst, tasks_dir=None, pub_dir=None, tex=True, header='header.md', standalone=True, tex_template='default.latex', lat=False):
    """
    Build publication in LaTeX format
    """
    if not tasks_dir:
        tasks_dir = os.path.dirname(yaml)
    if not pub_dir:
        pub_dir = os.path.dirname(yaml)

    if not os.path.exists(yaml):
        logger.error(yaml, "does not exist")
        return

    if tasks_dir and not os.path.isdir(tasks_dir):
        logger.error(tasks_dir, "is not a directory")
        return

    if pub_dir and not os.path.isdir(pub_dir):
        logger.error(pub_dir, "is not a directory")
        return

    if os.path.exists(dst) and not os.path.isfile(dst):
        logger.error(args.dst, "exists but is not a regular file")
        return

    header = obtain_file(header, os.path.join(data_dir, "md"))
    tex_template = obtain_file(tex_template, os.path.join(data_dir, "tex"))
    translit = (lambda x: x) if not lat else cyr_to_lat
    
    task_repo = TaskRepository(tasks_dir, normalize_md=PandocMarkdown.fix)
    pub_repo = PublicationRepository(pub_dir, normalize_md=PandocMarkdown.fix)
    
    yaml = YAMLSpecification(yaml)
    visitor = PublicationVisitorTeX(yaml, task_repo, pub_repo, dst, langs=yaml.langs(), tex=tex, header=header, standalone=standalone, tex_template=tex_template, translit=translit)
    yaml.traverse(visitor)

# @task
# def tgen_hpp(ctx):
#    """
#    Copy tgen include files to current directory
#    """
#    for filename in glob.glob(os.path.join(tgen_dir(), "tgen*.hpp")):
#        shutil.copy(filename, os.getcwd())
