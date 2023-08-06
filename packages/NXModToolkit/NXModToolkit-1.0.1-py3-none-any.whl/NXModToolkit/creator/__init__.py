import sys

from cookiecutter.main import cookiecutter


def run(args):
    cookiecutter("https://github.com/withertech/SimpleModManagerModTemplate.git")
