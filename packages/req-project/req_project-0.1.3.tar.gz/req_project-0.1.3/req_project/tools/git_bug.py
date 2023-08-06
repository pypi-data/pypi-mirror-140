import os
from subprocess import PIPE, Popen
from platform import machine
import shutil
from black import out
from git import Git, PushInfo, Repo
from tools.utility import Utility 
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tools.configuration import Configuration
from commands.user import User
from urllib.request import urlretrieve
import urllib.request as ul
from bs4 import BeautifulSoup as soup
from commands.user import User
from pexpect.popen_spawn import PopenSpawn

url_basic = "https://github.com/MichaelMure/git-bug/releases/"

class GitBug:
    # init method or constructor   
    def __init__(self):
        self = self

    def availability():
        if Utility.is_tool("git-bug"):
            return True
        else:
            return False

    def get_version_online():
        url = url_basic + "latest"
        req = ul.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        client = ul.urlopen(req)
        htmldata = client.read()
        client.close()
        pagesoup = soup(htmldata, "html.parser")
        itemlocator = pagesoup.findAll('title')
        item = str(itemlocator[0])
        index = item.find("Release") + 8
        return str(item[index:index+5])

    def get_version_installed():
        if GitBug.availability():
            p = Popen(["git-bug", "--version"], stdout=PIPE)
            version = str(p.communicate()[0])
            return version[len(version)-8:len(version)-3]   
        else:
            return "None"

    def update():
        if GitBug.availability(): # just update if not available
            version_online = GitBug.get_version_online()
            version_installed = GitBug.get_version_installed()
            if version_online!=version_installed:
                print("Old git-bug version detected - updating")
                gitbug_path = shutil.which('git-bug')
                version = GitBug.get_version_online()
                OS = str(Utility.whichOS()).lower()
                machine = str(Utility.whichMachine()).lower()
                github_url = url_basic + "download/v" + version + "/git-bug_"+ OS +"_" + machine + ".exe"
                destination = f'{gitbug_path}\\git-bug.exe'
                download = urlretrieve(github_url, destination)
        else: #nothin to update 
            print("Git-bug not found - please install it")
            

    def install(path):
        if GitBug.availability():
            print("git-bug detected")
            GitBug.update()
        else:  #install git-bug in tools folder
            version = GitBug.get_version_online()
            OS = str(Utility.whichOS()).lower()
            machine = str(Utility.whichMachine()).lower()
            github_url = url_basic + "download/v" + version + "/git-bug_"+ OS +"_" + machine + ".exe"
            destination = f'{path}\\git-bug.exe'
            Utility.download(github_url,destination)
            # Mode to be set 
            mode = 0o666  
            # flags
            flags = os.O_RDWR | os.O_CREAT
            os.open(destination, flags, mode)
            pathcommand = "set PATH=%PATH%;" + path + "\\"
            os.system(pathcommand)
            installed = Utility.add_path_to_path_variable(path) and GitBug.availability()
            if installed==True:
                return True
            else:
                return False

    @staticmethod
    def addUser(projectname):
        # adds a user to gitbug in the project folder projectname
        config = Configuration.get_configuration(projectname)
        project_path = config.get_project_path()
        os.chdir(project_path)
        command = "git bug user ls"
        response = Utility.run_CLI_command(command)
        print(response)
        if response=="":
            #create user
            user = User.get_user()
            # check https://github.com/MichaelMure/git-bug/blob/master/doc/md/git-bug_user_create.md
            command = "git bug user create"
            child = PopenSpawn(command,encoding="utf-8")
            inp = "{} {}\n".format(user[0], user[1])
            child.expect(": ")
            child.sendline(inp)
            print(child.before, inp)
            child.expect(": ")
            inp = "{}\n".format(user[2])
            child.sendline(inp)
            print(child.before, inp)
            child.expect(": ")
            inp = "\n"
            print(child.before, inp)
            child.sendline(inp)
            #child.expect(pexpect.EOF)
            #child.kill()
            command = "git bug user ls"
            response = Utility.run_CLI_command(command)
            print("what is listed: " + response)
            # response = Utility.run_CLI_command(command)
            # print(response)
            # p = Popen(command, stdin=PIPE, stdout=PIPE, shell=True, universal_newlines=True)  
            # inp = "{} {}\n".format(user[0], user[1])
            # print(inp)
            # p_out = p.communicate(input=inp)[0]
            # print(p_out)
            # inp = "{}\n".format(user[2])
            # p_out = p.communicate(input=inp)[0]
            # print(p_out)
            # stderr is not connected to a pipe, so err is None
            # print(first, second, "->", end="")
            # # we just want the result of the command
            # print(output[output.rfind(" "):-1])  # -1 to strip the final newline
        else:
            print("user in list: " + response)
            return False
            

    @staticmethod
    def push(projectpath):
        current_path = os.getcwd()
        current_path = os.chdir(projectpath)
        print("Push git-bug comments from " + os.getcwd() + "to git server")
        command = ["git-bug", "push"]
        response = Utility.run_CLI_command(command)
        print(response)
        exit()

    @staticmethod
    def pull(projectpath):
        current_path = os.getcwd()
        current_path = os.chdir(projectpath)
        print("Pull git-bug comments from git server to  " + os.getcwd())
        command = ["git-bug", "pull"]
        response = Utility.run_CLI_command(command)
        print(response)
        exit()
               
