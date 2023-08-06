from commands.workspace_path import WorkspacePath
from tools.configuration import Configuration

class ProjectVersion:

    major = 0
    minor = 0
    patch = 0

    def __init__(self, 
                major = major, 
                minor = minor, 
                patch = patch):

        self.major = major
        self.minor = minor
        self.patch = patch
        
    @staticmethod
    def get_local_project_version(projectname):
        # get project version
        # returns the following versioning format
        # major.minor.patch
        config = Configuration.get_configuration(projectname)
        print("local project version: " + str(config.version))
        return config.version

    #TODO: - implement
    # @staticmethod
    # def get_server_version(projectname):
        # gets version from project folder
        # return:
        # version - if found
        # [-1, -1, -1] - if not found
        # config = Configuration.get_configuration(projectname)
        # 
        # if found:
        #   return version
        # else:
        #   return [-1, -1, -1]

    @staticmethod
    def increase_project_version(projectname, type):
        # increase project version for the defined type: major/minor/patch
        # and then write config into configuration file
        # return:
        # True - if done
        # False - if not done
        
        config = Configuration.get_configuration(projectname)

        print("old version is: " + str(config.version))

        if type=="major":
            config.version[0] = config.version[0]+1
        elif type=="minor":
            config.version[1] = config.version[1]+1
        elif type=="patch":
            config.version[2] = config.version[2]+1
        else:
            print("nothing done - please use major/minor/patch to indicate what should be increased")
            return False
        
        print("new version is: " + str(config.version))

        if Configuration.update_configuration(config):
            return True
        else:
            return False

    # TODO: implement
    # @staticmethod
    # def set_project_folder_to_version(projectname, version):
        # gets version from project folder
        # return:
        # True - if done
        # False - if not done