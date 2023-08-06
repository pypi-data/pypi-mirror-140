from importlib.resources import path
import os
from pathlib import Path
from tkinter import W

from black import json
import git
import json
import commands.workspace_path as workspace_path
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from commands.workspace_path import WorkspacePath

class Configuration:

    config = "config"
    config_file = "config.json"
    capella = "" #"capella" # the capella project files have to be located in the project root
    sdoc = "sdoc"
    reqif = "reqif"
    src = "src"
    docu = "docu"
    tools = "tools"
    version = [0, 0, 0]
    remote_repo = "xxx"
  
    # TODO: need the docu subfolders configured somewhere as well!    
    docu_fha = "fha"
    docu_overall = "overall"
    docu_requirements = "requirements"
    docu_src = "src"
    docu_systemarchi = "system_architecture"
  
    capella_model_file = None
    sdoc_file = "draft.sdoc"
    reqif_file = "output.reqif"

    # init method or constructor
    # nothing is stored just the constructor use self.write_configfile() to save configuration 
    def __init__(self,                
                 config = config,
                 config_file = config_file,
                 capella = capella,
                 sdoc = sdoc,
                 src = src,
                 docu = docu,
                 tools = tools,
                 version = version,
                 remote_repo = remote_repo,
                 docu_fha = docu_fha,
                 docu_overall = docu_overall,
                 docu_requirements = docu_requirements,
                 docu_src = docu_src,
                 docu_systemarchi = docu_systemarchi,
                 capella_model_file = capella_model_file,
                 sdoc_file = sdoc_file,
                 reqif_file = reqif_file,
                 projectname=None, 
                 workspace=None,
                 ):  
        if projectname==None:
            self.projectname = "draft_project"
        else:
            self.projectname = projectname

        if workspace==None:
            ws = workspace_path.WorkspacePath(workspace = workspace)
            if ws.configfile_available():   #workspace configuration found
                workspaceconfig = ws.read_configfile()
                self.workspace = workspaceconfig.workspace
            else:   #workspace configuration not found
                print("Can not iniate project, workspace configuration not found")
                print("please use req_project.py -p PATH to define workspace path")
                raise Exception("Execption - see description above")
        else:   #workspace variable given through interface
            self.workspace = workspace
            ws = workspace_path.WorkspacePath(workspace = workspace)
            if ws.configfile_available():  #workspace configuration found
                ws_loaded = ws.read_configfile()
                if ws_loaded.workspace!=self.workspace:
                    print("workspace configuration found, but given workspace is not the same as the stored one")
                    print("please use req_project.py -p PATH to define workspace path")
                    raise Exception("Execption - see description above")
            else:   #workspace configuration not found
                print("Can not iniate project, workspace configuration not found")
                print("please use req_project.py -p PATH to define workspace path")
                raise Exception("Execption - see description above")

        # TODO: Remove
        # moved to class scope to have them available in static method as well
        #self.config = "/config"
        #self.config_file = "/config.json"
        #self.capella = "/capella"
        #self.sdoc = "/sdoc"
        #self.src = "/src"
        #self.docu = "/docu"
        self.config = config
        self.config_file = config_file
        self.capella = capella
        self.sdoc = sdoc
        self.src = src
        self.docu = docu
        self.tools = tools
        self.version = version
        self.remote_repo = remote_repo

        # TODO: need the docu subfolders configured somewhere as well!    
        self.docu_fha = docu_fha
        self.docu_overall = docu_overall
        self.docu_requirements = docu_requirements
        self.docu_src = docu_src
        self.docu_systemarchi = docu_systemarchi

        # TODO: need project file information for: how, when and by whom are their names defined?!?       
        # capella.aird
        # strictdoc.reqif
        # strictdoc.sdoc
        # 
        self.capella_model_file = self.projectname+".aird"
        self.sdoc_file = self.projectname+".sdoc"
        self.reqif_file = reqif_file

    def poject_exists(self):
        # checks if the project folder is available
        # returns:
        # - true - project folder exists
        # - false - project folder does not exist
        project_path = os.path.join(self.workspace, self.projectname)
        if os.path.exists(project_path):
            return True
        else:
            return False

    def get_project_path(self):
        project_path = os.path.normpath(os.path.join(self.workspace, self.projectname))
        return project_path

    def get_sdoc_file(self):
        filename = os.path.normpath(os.path.join(self.workspace, self.projectname, self.sdoc, self.sdoc_file))
        return filename

    def get_sdoc_file_list(self):
        filepath = os.path.normpath(os.path.join(self.workspace, self.projectname, self.sdoc))
        filelist = []
        for i in os.listdir(filepath):
            # List files with .py
            if i.endswith(".sdoc"):
                filelist.insert(0,i)
        return filelist

    def get_sdoc_path(self):
        sdoc_doc_path = os.path.normpath(os.path.join(self.workspace, self.projectname, self.sdoc))
        return sdoc_doc_path

    def get_sdoc_docu_path(self):
        sdoc_doc_path = os.path.normpath(os.path.join(self.workspace, self.projectname, self.docu, self.docu_requirements))
        return sdoc_doc_path

    def change_projectname(self, projectname):
        self.projectname = projectname

    def change_projectpath(self, workspace):
        self.workspace = workspace

    def checkfor_configfile(self):
        project_file = os.path.normpath(os.path.join(self.workspace, self.projectname,self.config,"config.json"))
        try:
            with open(project_file, "r") as jsonfile:
                data = json.load(jsonfile)
                #print(data)
            return True
        except FileNotFoundError:
            print('Configuration file is not present.')
            return False

    @staticmethod
    def get_configuration(projectname):
        # return configuration data for project name
        # returns:
        # - if project name is found: configuration data
        ws = workspace_path.WorkspacePath()
        workspace_config_available = ws.configfile_available()
        if workspace_config_available:
            ws_config = ws.read_configfile()
            workspace = ws_config.workspace
        else:
            print("get configuration error: ")
            print("please provide a workspace path using -p PATH option. See -h for help")
            exit()

        config_intermidiate = Configuration(projectname=projectname,workspace=workspace)
        
        if config_intermidiate.poject_exists():
            project_path = os.path.join(workspace, projectname)
            config = Configuration.read_configfile(project_path)
            return config
        else:
            print("get configuration error: ")
            print("proejct path not existing - please initiate using -i parameter")
            exit()

    @staticmethod
    def update_configuration(new_config):
        # static method to update configuration data
        # returns:
        # - True is successfull
        # - False if not successfull

        ws = workspace_path.WorkspacePath()
        workspace_config_available = ws.configfile_available()
        if workspace_config_available:
            ws_config = ws.read_configfile()
            workspace = ws_config.workspace
        else:
            print("update configuration error: ")
            print("please provide a workspace path using -p PATH option. See -h for help")
            exit()

        if new_config.poject_exists():
            config = new_config.write_configfile()
            return True
        else:
            print("update configuration error: ")
            print("proejct path not existing - please initiate using -i parameter")
            return False
        

    @staticmethod
    def read_configfile(projectpath):
        #opens configuration file and returns 
        #config from given project path
        proj = os.path.basename(os.path.normpath(projectpath))
        ws = os.path.dirname(os.path.normpath(projectpath))

        filename = os.path.join(ws, proj, os.path.normpath(Configuration.config), os.path.normpath(Configuration.config_file))
        with open(filename, "r") as jsonfile:
            data = json.load(jsonfile)
            return Configuration(**data)

    def write_configfile(self):
        print("write file")
        myJSON = json.dumps(self.__dict__)
        filename = os.path.join( self.workspace, self.projectname, self.config, self.config_file)
        print(filename)
        with open(filename, "w") as jsonfile:
            jsonfile.write(myJSON)
            print("Write successful")