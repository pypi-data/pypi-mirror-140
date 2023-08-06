import os
from tools.passwords import Passwords
import commands.workspace_path as workspace_path
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from commands.workspace_path import WorkspacePath

class User:
    @staticmethod
    def execute(gname, fname, email, password):
        #write user data into config file
        ws = workspace_path.WorkspacePath()
        if ws.configfile_available():
            ws_saved = ws.read_configfile()
            if (ws_saved.fname!=fname and fname!="0") or \
                    (ws_saved.gname!=gname and gname!="0") or \
                    (ws_saved.email!=email and email!="0") or \
                    (ws_saved.password!=Passwords.encrypt_password(password) and password!="0"):
                #write new data
                if gname=="0":
                    gname = ws_saved.gname
                if fname=="0":
                    fname = ws_saved.fname
                if email=="0":
                    email = ws_saved.email
                print("Old user vs. new user")
                print("Given name: " + ws_saved.gname + " vs. " + gname)
                print("Family name: " + ws_saved.fname + " vs. " + fname)
                print("Email: " + ws_saved.email + " vs. " + email)
                print("Password: not shown for security reaseans")
                if input("Do you want to overwrite it? (y/n) ") == "y":
                    try:
                        print("Overwriting user name")
                        ws_saved.gname = gname
                        ws_saved.fname = fname
                        ws_saved.email = email
                        if password!=0:  #only change it if password is given
                            ws_saved.password = Passwords.encrypt_password(password)
                        ws_saved.write_configfile()
                    except:
                        print("No changes saved")
                        exit()
            else:
                print("User name is up to date")
                exit()
        else: #no config file available
            print("Please configure workspace -p option")
            exit()

    def get_user():
        # returns user data
        # [gname, fname, email]
        ws = workspace_path.WorkspacePath()
        if ws.configfile_available():
            ws_saved = ws.read_configfile()
            return [ws_saved.gname, ws_saved.fname, ws_saved.email]
        else: #no config file available
            print("Please configure workspace -p option")
            exit()

    def availability():
        # checks if user name is set
        # returns
        # True - if set, meaning is something different then "xxx" (initiate like that)
        # False - if not set
        ws = workspace_path.WorkspacePath()
        if ws.configfile_available():
            ws_saved = ws.read_configfile()
            if ws_saved.fname!="xxx" and ws_saved.gname!="xxx" and ws_saved.email!="xxx":
                return True
            else:
                return False
        else: #no config file available
            print("No user information found - please configure workspace -p option")
            return False
