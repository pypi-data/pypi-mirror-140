import os
from cgitb import reset
from importlib.resources import path
from turtle import update
import git
from git import PushInfo, Repo
from commands.workspace_path import WorkspacePath

from tools.configuration import Configuration
from tools.utility import Utility
from tools.passwords import Passwords


class GitProject:
    # init method or constructor   
    def __init__(self):
        self = self

    @staticmethod
    def init_git(projectname):
        # initiate git repo in project folder
        # returns: 
        # True - successfull
        # False - not sucessfull
        # TODO: potentially add automatic installation
        config = Configuration.get_configuration(projectname)
        project_path = config.get_project_path()
        repo = Repo.init(project_path)
        repo.git.add(all=True)
        repo.git.commit('-m', 'inital commit')
        GitProject.VersionRepo(projectname)

    def git_installed():
        # checks if GIT is installed
        # return:
        # True - if git can be called
        # False - if git can not be called
        result = Utility.run_CLI_command("git --version") # executes git command
        if result.__contains__("git version"):
            return True
        else:
            return False

    @staticmethod
    def existsRemoteOrigin(projectname):
        # checks if remote origins are in project repo
        # result 
        # [True, url] - True if one or more exist, url of remote repo
        # [False, []] - False if none exist, url = []

        config = Configuration.get_configuration(projectname)
        project_path = config.get_project_path()
        repo = Repo.init(project_path)
        try:
            remote_refs = repo.remote("origin")
            if remote_refs.exists():
                return True, remote_refs.url
            else:
                return False, []
        except:
            return False, "Origin Missing"
        
    
    @staticmethod
    def addRemoteRepo(projectname, remote_repo, password):
        # adds a remote repo to the project folder
        config = Configuration.get_configuration(projectname)
        ws = WorkspacePath()
        if ws.configfile_available():
            ws_loaded = ws.read_configfile()
            username = ws_loaded.email
            hash = ws_loaded.password
            if not Passwords.check_encrypted_password(password, hash):
                raise Exception("given password not correct")
            if remote_repo.__contains__("github"):
                # log in to github account
                # based on example https://github.com/mnaderhirn/req_draft
                #url_remote_repo_1 = remote_repo[0:7]
                #url_remote_repo_2 = remote_repo[8:]
                # url_remote = f"{url_remote_repo_1}{username}:{password}@{url_remote_repo_2}/{projectname}.git"
                url_remote = f"{remote_repo}/{projectname}.git"
                print(url_remote)
            else:
                url_remote = remote_repo

            # Create a new remote
            config = Configuration.get_configuration(projectname)
            project_path = config.get_project_path()
            repo = Repo.init(project_path)
            remote_exists, remote_url_existing = GitProject.existsRemoteOrigin(projectname)
            if remote_exists:
                print("remote url exists: " + remote_url_existing)
                print("new url exists: " + url_remote)
                Question = input("Sure you want to replace existing remote url (y/n) ")
                if Question == ("y"):
                    # TODO: add code to automatically replace remote url
                    repo.delete_remote("origin")
                    repo.create_remote('origin', url=url_remote)
                    config.remote_repo = url_remote
                    Configuration.update_configuration(config)
                    print ("Please replace remote url manually - not implemented yet")
                    return True
                return False
            else:
                remote = repo.create_remote('origin', url=url_remote)
                Configuration.update_configuration(config)
                return True

        else:
            raise Exception("No workspace defined - Please iniate workspace using -p command!")
            return False
        
        return False

    @staticmethod
    def cloneRemoteRepo(projectname, remote_repo, password):
        # clones remote repo into workspace folder
        ws = WorkspacePath()
        if ws.configfile_available():
            ws_loaded = ws.read_configfile()
            username = ws_loaded.email
            hash = ws_loaded.password
            if not Passwords.check_encrypted_password(password, hash):
                raise Exception("given password not correct")
            else:  # clone project from remote url
                path = os.path.join(ws_loaded.workspace, projectname)
                #print(path)
                if os.path.exists(path): #project path exists
                    #return warning 
                    print("Warning: project exists already please delete it before cloning a new one!")
                    exit()
                else: #project path does not exist so create prototype project
                    print(path)
                    try: 
                        os.mkdir(path) 
                        if os.path.exists(path):
                            #Clone requirements project from project fodler path
                            #remote_repo = "https://github.com/mnaderhirn"
                            print("Cloning draft project from GIT URL: " + remote_repo + " into path " + path)
                            Repo.clone_from(remote_repo, path)
                    except OSError as error: 
                        print(error)
        else:
            raise Exception("No worspace defined - Please iniate workspace using -p command!")


    @staticmethod
    def TagRepo(path, tag):
        repo = Repo(path)
        repo.create_tag(tag)

    @staticmethod
    def VersionRepo(projectname):
        # generates a tag for the local repo of the last local version number 
        config = Configuration.get_configuration(projectname)
        project_path = config.get_project_path()
        repo = Repo(project_path)
        tag = "v" + str(Configuration.version[0]) + "." + str(Configuration.version[1]) + "." + str(Configuration.version[2])
        repo.create_tag(tag)
    
    @staticmethod
    def GetLocalTags(projectname):
        # returns a list of local tags like version numbers
        config = Configuration.get_configuration(projectname)
        project_path = config.get_project_path()
        repo = Repo(project_path)
        tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
        return tags
        #latest_tag = tags[-1]

    # TODO: implement GetGlobalTags

    @staticmethod
    def push(projectname):
        # push files to server
        config = Configuration.get_configuration(projectname)
        project_path = config.get_project_path()
        repo = Repo(project_path)
        # set working directory
        os.chdir(project_path)
        print(project_path)
        # see - https://stackoverflow.com/questions/33733453/get-changed-files-using-gitpython#42792158
        untracked_files = repo.untracked_files
        modified_file_list = [ item.a_path for item in repo.index.diff(None) ]
        staged_file_list = [ item.a_path for item in repo.index.diff("HEAD") ]
        changed_files = modified_file_list + staged_file_list + untracked_files    
        if changed_files!=[]: # commit the following file list
            print(changed_files)
            repo.index.add(changed_files)
            print("Tell us what you changed")
            commit_message = ""  #generate commit message
            # TODO: add comments for each change
            for item in changed_files:
                message = input("What changed in: " + item + ": ")
                commit_message = commit_message + item + " - " + message + "\n"
            print(commit_message)
            repo.index.commit(commit_message)
        else:
            print("Nothing to commit, so just push is performed")

        result, url = GitProject.existsRemoteOrigin(projectname)
        if result:
            try:
                origin = repo.remote(name="origin")
                assert origin.exists
                result = origin.push(refspec="master:master")
                # result = origin.push()
            except git.GitError as error:
                print("Error " + str(error) + " while pushing")
                return False
            
            return True
        else:
            print("Remote origin does not exist - please iniate in project folder")
            return False

    @staticmethod
    def pull(projectname):
        # pull files from remote repo to project folder
        print("pull files from remote repo to project folder")
        config = Configuration.get_configuration(projectname)
        project_path = config.get_project_path()
        repo = Repo(project_path)
        # set working directory
        os.chdir(project_path)
        print(project_path)
        result, url = GitProject.existsRemoteOrigin(projectname)
        if result:
            try:
                origin = repo.remote(name="origin")
                assert origin.exists
                result = origin.pull(refspec="master:master")
            except git.GitError as error:
                print("Error " + str(error) + " while pulling")
                return False
            
            return True
        else:
            print("Remote origin does not exist - please iniate in project folder")
            return False
    @staticmethod
    def list_history(projectname):
        # returns the commit history
        config = Configuration.get_configuration(projectname)
        project_path = config.get_project_path()
        repo = Repo(project_path)
        commits = list(repo.iter_commits("master", max_count=5))
        for iter in commits:
            print("Date: " + str(iter.committed_datetime) + " author: " + str(iter.author))
            print("Msg: " + str(iter.message))