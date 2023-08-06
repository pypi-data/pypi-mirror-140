import os
import getpass
import json

from tools.passwords import Passwords
from tools.vs_code import VsCode
from tools.git_bug import GitBug

class WorkspacePath:

    config_file = "project_config.json"
    user = getpass.getuser()
    config_path = os.path.normpath(os.path.join("C:\\","Users",user,"AppData","Local","req_project"))
    workspace = None
    email = "xxx"
    gname = "xxx"
    fname = "xxx"
    password = Passwords.encrypt_password("xxx")


    def __init__(self,
                 config_file = config_file,
                 config_path = config_path,
                 workspace = workspace,
                 email = email,
                 gname = gname,
                 fname = fname,
                 password = password):
        self.config_file = config_file
        self.config_path = config_path
        self.workspace = workspace
        self.email = email
        self.gname = gname
        self.fname = fname
        self.password = password

    def execute(self, workspace):
        self.workspace = workspace
        if os.path.exists(self.config_path):   #config path exists
            print("config path exists")
            if self.configfile_available():  #config file exists, ask to overwrite
                config = self.read_configfile()
                print("old workspace path: " + config.workspace)
                print("new workspace path: " + workspace)
                if config.workspace!=self.workspace:
                    print("old workspace path: " + config.workspace)
                    print("new workspace path: " + self.workspace)
                    if input("overwrite all config file (y/n) ") == "y":
                            self.write_configfile()
                
            else:  #config file does not exist, so write it
                self.write_configfile()
        else:  #config path does not exists
            os.mkdir(self.config_path)    #create config folder
            if os.path.exists(self.config_path):  #config path 
                self.write_configfile()
            else:
                print("config path not created, something went wrong")
                return False

        #create folder for tools
        tools_path = os.path.normpath(os.path.join(workspace, "tools"))
        if os.path.exists(tools_path): #project path exists:
            print("tools path " + tools_path + "already exisits, nothing to do")
        else:
            os.mkdir(tools_path)
            if os.path.exists(tools_path):
                print("tools path " + tools_path + "successfully created!")
            else:
                print("Something went wrong when creating tools path " + tools_path)

        #install git-gub
        print("checking for git-bug")
        GitBug.install(tools_path)

        #install VSCode
        print("checking for VS Code")
        VsCode.install(tools_path)
        VsCode.extension_installation("textX.textX")
        VsCode.extension_installation("James-Yu.latex-workshop")

    def configfile_available(self):
        #checks if configuration file available
        # return:
        # - true - if file found
        # - false - if file not found 
        filename = os.path.join(os.path.normpath(self.config_path), os.path.normpath(self.config_file))
        if os.path.isfile(filename):
            return True
        else:
            return False

    def read_configfile(self):
        filename = os.path.join(os.path.normpath(self.config_path), os.path.normpath(self.config_file)) 
        with open(filename, "r") as jsonfile:
            data = json.load(jsonfile)
            return WorkspacePath(**data)

    def write_configfile(self):
        myJSON = json.dumps(self.__dict__)
        filename = os.path.join( self.config_path, self.config_file)
        with open(filename, "w") as jsonfile:
            jsonfile.write(myJSON)
            print("Write workspace config successful: " + filename)
       