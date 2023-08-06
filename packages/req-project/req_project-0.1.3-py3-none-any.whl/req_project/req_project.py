#!/usr/bin/env python3

import argparse
from msilib import type_string
from pickle import FALSE
from secrets import choice

from commands.version import VersionCommand
from commands.init_project import InitProject
from commands.delete_project import DeleteProject
from commands.check_project import CheckProject
from commands.workspace_path import WorkspacePath
from commands.generate_documentation import GenerateDocumentation
from commands.project_version import ProjectVersion
from commands.push import Push
from commands.pull import Pull
from commands.user import User
from commands.testing import Testing
from commands.git_for_project import GitProject
#from commands.map_project import MapProject

import tools.logging as logging

# Defining main function
def main():
    parser = argparse.ArgumentParser(description='Setup requirements project.')
    parser.add_argument('name', type=str,  
                        help='project name NAME')                                                            
    parser.add_argument('-p', '--path', nargs=1, type=str, default=0,
                        help='workspace path') 
    parser.add_argument('-c', '--check', default=0, action="store_true",
                        help='check if infrastructure is correct')
    parser.add_argument('-v', '--version', default=0, action="store_true",
                        help='version of requirements management tool')
    parser.add_argument('-m', '--mapping', default=0, action="store_true",
                        help='version of requirements management tool')
    parser.add_argument('-t', '--test', default=0, action="store_true",
                        help='test internal commands')

    g_parser = parser.add_subparsers(help='sub-commands')

    n_parser = g_parser.add_parser("generate" ,help='generate documentation')
    n_parser.add_argument('type', choices=['html', 'pdf'], help='export pdf/html')

    project_version = g_parser.add_parser("project_version", help='info about project version number')
    pv_subparser = project_version.add_subparsers(dest='project_version_command')
    pv_subparser.add_parser('info', help='project version number - format: major.minor.patch')
    pv_subsubparser = pv_subparser.add_parser('increase',
                        help='increment project version number major.minor.patch')
    pv_subsubparser.add_argument('choice', default=0,
                        choices=['major', 'minor', 'patch'], help='export pdf/html')

    version_control = g_parser.add_parser("project", help='handle project commands')
    vc_subparser = version_control.add_subparsers(dest='project_command')
    vc_subsubparser = vc_subparser.add_parser('remote_url', help='remote repo url') 
    vc_subsubparser.add_argument('-a','--add', nargs=2, type=str, default=0, help='add remote url and password')
    vc_subsubparser1 = vc_subparser.add_parser('history', help='list commit history')
    vc_subsubparser2 = vc_subparser.add_parser('push', help='push project folder to remote repo')
    vc_subsubparser2 = vc_subparser.add_parser('pull', help='pull project folder from remote repo')
    vc_subsubparser3 = vc_subparser.add_parser('user', help='change user settings')
    vc_subsubparser3.add_argument('-gn', '--given_name', nargs=1, type=str, default=0,
                        help='given name')
    vc_subsubparser3.add_argument('-fn', '--family_name', nargs=1, type=str, default=0,
                        help='family name')
    vc_subsubparser3.add_argument('-em', '--email', nargs=1, type=str, default=0,
                        help='email')
    vc_subsubparser3.add_argument('-pw', '--password', nargs=1, type=str, default=0,
                        help='password')
    vc_subsubparser3 = vc_subparser.add_parser('delete', help='delete project folder')

    init_project = g_parser.add_parser("new_project", help='initiate new project')
    ip_subparser = init_project.add_subparsers(dest='new_project_command')
    ip_subsubparser = ip_subparser.add_parser('clone', help='clone requirements project from remote url')
    ip_subsubparser.add_argument('-g','--git', nargs=2, type=str, default=0, \
        help='general git remote url https://github.com/max_mustermann/any_project_name.git (GIT1) \
            with password (GIT2) into folder workspace/name.\
            !!! Make sure that name equals any_project_name !!!')
    ip_subsubparser.add_argument('-gh','--github', nargs=2, type=str, default=0, \
        help='github remote url https://github.com/username (GITHUB1) with password (GITHUB2), \
        https://github.com/max_mustermann/name.git is used internal to clone project into folder\
            workspace/name')
    ip_subsubparser1 = ip_subparser.add_parser('local', help='init a requirements project in folder NAME defined with -n option')

    try:
        args = parser.parse_args()
        print(args)

        if args.path!=0:
            print("Workspace path")
            ws = WorkspacePath()
            WorkspacePath.execute(ws,args.path[0])

        if args.check!=0:
            print("Checking infrastructure and tools")
            CheckProject.execute(args.name)

        if args.__contains__("name") and args.mapping != 0 and args.init == 0 and args.delete == 0:
            print("Mapping project")
 #           MapProject.execute(args.name)      
        
        if args.version:
            VersionCommand.execute()

        if args.test!=0:
            Testing.execute(args.name)

        if args.__contains__("name") and args.__contains__("type"):
            print("Generate documentation for project " + args.name + " to type " + args.type)
            GenerateDocumentation.execute(args.name,args.type)

        if args.__contains__("project_version_command"):
            if args.project_version_command=="info":
                print("project version info")
                print(args.name)
                ProjectVersion.get_local_project_version(args.name)

            if args.project_version_command=="increase":
                if args.choice=="major":
                    print("increase major")
                    ProjectVersion.increase_project_version(args.name,"major")
                elif args.choice=="minor":
                    print("increase minor")
                    ProjectVersion.increase_project_version(args.name,"minor")
                elif args.choice=="patch":
                    print("increase patch")
                    ProjectVersion.increase_project_version(args.name,"patch")
                else:
                    print("missing the right command")

        if args.__contains__("project_command"):
            if args.project_command=="remote_url":
                print("remote url commands")
                if args.add!=0:
                    print("add remote url to local folder")
                    GitProject.addRemoteRepo(args.name, args.add[0], args.add[1])
            if args.project_command=="push":
                print("Push command ")
                Push.execute(args.name)
            if args.project_command=="pull":
                print("Pull command ")
                Pull.execute(args.name)
            if args.project_command=="history":
                print("History command ")
                GitProject.list_history(args.name)
            if args.project_command=="user":
                print("User commands ")
                if args.given_name==0:
                    args.given_name = str(args.given_name)
                if args.family_name==0:
                    args.family_name = str(args.family_name)
                if args.email==0:
                    args.email = str(args.email)
                if args.password==0:
                    args.password = str(args.password)
                User.execute(args.given_name[0],args.family_name[0],args.email[0],args.password[0])
            if args.project_command=="delete":
                print("delete project ")
                DeleteProject.execute(args.name)

        if args.__contains__("new_project_command"):
            if args.new_project_command=="local":
                print("create new local project")
                InitProject.execute(args.name)
            elif args.new_project_command=="clone":
                print("clone requirements project from remote url")
                if args.__contains__("github"):
                    remote_repo = args.github[0] + "/" + args.name + ".git"
                    GitProject.cloneRemoteRepo(args.name, remote_repo, args.github[1])
                elif args.__contains__("git"):
                    GitProject.cloneRemoteRepo(args.name, args.git[0], args.git[1])

    except Exception as ex:
        logging.print_error(ex)
  
  
# Using the special variable 
# __name__
if __name__=="__main__":
    main()
