from invoke import Collection, Program
from petljapub import tasks
program = Program(namespace=Collection.from_module(tasks), version='1.0.0')
