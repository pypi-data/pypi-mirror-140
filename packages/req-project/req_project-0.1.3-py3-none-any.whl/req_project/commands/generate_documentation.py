import os
import subprocess

from black import out
from commands.workspace_path import WorkspacePath
from tools.configuration import Configuration
from tools.utility import Utility

class GenerateDocumentation:
    @staticmethod
    def execute(projectname,exporttype):
        ws = WorkspacePath()
        workspace_config_available = ws.configfile_available()
        if workspace_config_available:
            ws_config = ws.read_configfile()
            workspace = ws_config.workspace
        else:
            print("can not generate documentation")
            print("please provide a workspace path using -p PATH option. See -h for help")
            exit()

        config_intermidiate = Configuration(projectname=projectname,workspace=workspace)
        
        if config_intermidiate.poject_exists():
            path = config_intermidiate.get_project_path()
            os.chdir(path)
            config = config_intermidiate.read_configfile(path)
            sdoc_doc_path = config.get_sdoc_docu_path()
            sdoc_path = config.get_sdoc_path()
            sdoc_file_list = config.get_sdoc_file_list()
            if exporttype=="html":
                print("html export")
                command = "strictdoc export " + sdoc_path + " --formats=html --output-dir " + sdoc_doc_path
                output = Utility.run_CLI_command(command)
                print(output)
            elif exporttype=="pdf":
                print("pdf export only partially implmented yet")
                print("rst file is created")
                print("please check for more information")
                print("https://strictdoc.readthedocs.io/en/stable/strictdoc.html#pdf-export-via-sphinx-latex")
                command = "strictdoc export " + sdoc_path + " --formats=rst --output-dir " + sdoc_doc_path
                output = Utility.run_CLI_command(command)
            else:
                print("define epxort type - see help")
        else:
            print("project not existing please initialize it using -i option")
