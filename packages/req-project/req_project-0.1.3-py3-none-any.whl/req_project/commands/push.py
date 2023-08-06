import os
from tools.git_bug import GitBug
from commands.workspace_path import WorkspacePath
from commands.git_for_project import GitProject

class Push:
    @staticmethod
    def execute(projectname):
        ws = WorkspacePath()
        ws_available = ws.configfile_available()
        if ws_available:
            ws_path = (ws.read_configfile()).workspace
            project_path = ws_path + "\\" + projectname
            # push for git
            GitProject.push(projectname)
            # push gitbug comments
            GitBug.push(project_path)

        else:
            print("can not push workspace configuration not found - use --PATH option to set")
            exit()