from github import Github
import os


class GitAccount:
    '''This class creates git account intance
    Make sure that git token is not exposed in github'''

    def __init__(self, token: str = None) -> None:
        try:
            print('connecting to git server')
            self.g = Github(token)
            self.user = self.g.get_user()
            print('connection successfull')
        except Exception as e:
            print(e)
            self.__del__()

    def __str__(self) -> str:
        return str(self.user.name)

    def push_dir(self, project_name: str,  path: str, org: str , branch: str = 'main', message: str = 'Initial', safe:bool=True) -> None:
        rep = self.g.get_organization(org).get_repo(project_name)
        print('getting files ready for updating...')
        ls = self.__ls_list(path)
        print('Files ready')
        print(f'Selected branch : {branch}')
        if safe : 
            while input('password :') != '111':
                print('incorrect password')
        for i in ls:
            print('uploading', i, end='  ')
            try:
                with open(i) as f:
                    content = open(i, 'rb').read()
                    try:
                        rep.create_file(i, message, content, branch=branch)
                    except:
                        contents = rep.get_contents(i)
                        rep.update_file(contents.path, message,
                                        content, contents.sha, branch=branch)
                print('100%')
            except Exception as e:
                print('Error uploading', i, '\n', e)

    def initialize(
        self, 
        path: str, 
        project_name: str, 
        org: str = 'LogicPlum',
        message: str = 'Initial', 
        branch: str = 'main', 
        branches=['develop', ], 
        private=True, 
        gitignore_template: str = 'Python', 
        safe:bool=True
    ):
        '''
        path: str, 
        project_name: str, 
        org: str,
        message: str = 'Initial', 
        branch: str = 'main', 
        branches=['develop', ], 
        private=True, 
        gitignore_template: str = 'Python', 
        safe:bool=True
        '''
        orgz = self.g.get_organization(org)
        print('Organization :', orgz.login)
        try:
            orgz.create_repo(
                project_name, gitignore_template=gitignore_template, private=private)

        except Exception as e:
            if e.status == 422:
                print(f"Repo '{project_name}' already exists and connected")
        repo = orgz.get_repo(project_name)
        print('Repo full name :', repo.full_name)
        if safe:
            while input('password :') != '111':
                print('incorrect password')
        sb = repo.get_branch('main')
        for i in branches:
            try:
                repo.create_git_ref(ref='refs/heads/' + i, sha=sb.commit.sha)
            except Exception as e:
                if e.status == 422:
                    print(f'Branch {i} already exists')
        self.push_dir(path=path, project_name=project_name,
                      branch=branch, message=message, org=org)

    def __ls_list(self, dirName, out=True):
        listOfFile = os.listdir(dirName)
        result = []
        allFiles = list()
        for entry in listOfFile:
            fullPath = os.path.join(dirName, entry)
            if os.path.isdir(fullPath):
                allFiles = allFiles + self.__ls_list(fullPath)
            else:
                allFiles.append(fullPath)
        for i in allFiles:
            result.append(i.replace(f'\\', f'/'))
        if out:
            for i in result:
                print('>', i)
        return result


def ls_list(dirName):
    listOfFile = os.listdir(dirName)
    result = []
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + ls_list(fullPath)
        else:
            allFiles.append(fullPath)
    for i in allFiles:
        result.append(i.replace(f'\\', f'/'))
    return result
