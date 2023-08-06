from commands.git_for_project import GitProject
import git
import winapps
from tools.git_bug import GitBug

class Testing:
    # init method or constructor   
    def __init__(self):
        self = self

    @staticmethod
    def execute(projectname):
        # git_for_project functions
        remote_repo ="https://github.com/mnaderhirn"
        password = "6265"
        # GitProject.existsRemoteOrigin(projectname)
        # GitProject.addRemoteRepo(projectname, remote_repo, password)
        # GitProject.list_history(projectname)
        # GitBug.addUser(projectname=projectname)
        for app in winapps.search_installed('git'):
            print(app)
