import os

import shutil


def create():
    project = input("请输入项目名:")
    if os.path.exists(project):
        os.remove(project)
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = current_dir + os.sep + "kAuto" + os.sep + "source"
    shutil.copytree(source_dir, project)
