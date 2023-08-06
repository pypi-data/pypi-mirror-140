import os
#internal tools
from tools.vs_code import VsCode
from tools.git_bug import GitBug
from tools.configuration import Configuration
from commands.user import User
from commands.workspace_path import WorkspacePath
from commands.git_for_project import GitProject

class CheckProject:
    @staticmethod
    def execute(project_name):
        #used to check project requirements
        #result:
        # - true if ok
        # - flase if not ok
        check_correct = True

        ws = WorkspacePath()
        if ws.configfile_available():
            print("Config file for workspace for project " + project_name + " detected")
        else:
            print("Config file for workspace for project " + project_name + " not detected!")
            check_correct = False

        workspace_path = ws.read_configfile()
        project_config = Configuration(projectname=project_name, workspace=workspace_path.workspace)
        if project_config.poject_exists(): #chekc if path exists
            print("Config path for project " + project_name + " detected")

            if project_config.checkfor_configfile(): #check if project config file exists
                print("Config file for project " + project_name + " detected")
            else:
                print("Config file for project " + project_name + " not detected!")
                check_correct = False

        else:
            print("Config path for project " + project_name + " not detected!")
            check_correct = False

        if User.availability():
            print("user information detected")
        else:
            print("user information not detected, please install it")
            check_correct = False

        if GitBug.availability():
            print("git-bug detected")
        else:
            print("git-bug not detected, please install it")
            check_correct = False

        if VsCode.availability():
            print("VS Code detected")
            if VsCode.extension_available("textX.textX"):  # install for sdoc language server
                print("TextX.TextX extension for VS Code detected")
            else:
                print("TextX.TextX extension for VS Code not detected, please install")
                check_correct = False
            if VsCode.extension_available("James-Yu.latex-workshop"):  # install for latex editor
                print("latex-workshop extension for VS Code detected")
            else:
                print("latex-workshop extension for VS Code not detected, please install")
                check_correct = False
        else:
            print("VS Code not detected, please install it")
            check_correct = False

        if GitProject.git_installed():
            print("GIT detected")
        else:
            print("GIT not detected, please install")
            check_correct = False

        return check_correct