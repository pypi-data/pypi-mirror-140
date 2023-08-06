import os

from git import Git
from tools.git_bug import GitBug
from commands.workspace_path import WorkspacePath
from commands.git_for_project import GitProject

class Pull:
    @staticmethod
    def execute(projectname):
        ws = WorkspacePath()
        ws_available = ws.configfile_available()
        if ws_available:
            ws_path = (ws.read_configfile()).workspace
            project_path = ws_path + "\\" + projectname
            # TODO add push for git
            GitProject.pull(projectname)
            # push gitbug comments
            GitBug.pull(project_path)
        else:
            print("can not push workspace configuration not found - use --PATH option to set")
            exit()