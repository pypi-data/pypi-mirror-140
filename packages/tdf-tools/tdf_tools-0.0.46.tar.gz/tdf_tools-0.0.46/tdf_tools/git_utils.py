#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from operator import mod
import os
from tdf_tools.python_gitlab_api import GitlabAPI
from tdf_tools.tdf_print import printStage, printError, printTitle, printStr
from tdf_tools.json_data_read import getInitJsonData, getModuleJsonData, getModuleNameList, projectModuleDir
import subprocess


class GitUtils(object):

    def __init__(self):
        printStage("git管理")
        self.initJsonData = getInitJsonData()
        self.moduleJsonData = getModuleJsonData()
        self.moduleNameList = getModuleNameList()

    def _runCmd(cmd):
        subprocess_result = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE)
        subprocess_return = subprocess_result.stdout.read()
        return subprocess_return.decode('utf-8')

    def _checkModuleExist(moduleName):
        os.chdir(projectModuleDir)
        return os.path.exists(moduleName)

    def diff(self, targetBranch='master'):
        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            res = GitUtils._runCmd(
                "git diff --name-only {0}..{1}".format(GitUtils._getCurBranch(), targetBranch)).splitlines()
            if len(res) > 0:
                printStr("{0}: {1} files diff".format(module, len(res)))
            else:
                printStr("{0}: 已经是最新了。".format(module))

    # def undiff(self):
        # for module in self.moduleNameList:
        #     moduleDir = os.path.join(projectModuleDir, module)
        #     os.chdir(moduleDir)
        #     res = GitUtils._runCmd(
        #         "git diff --name-only {0}..{1}".format(self.initJsonData['featureBranch'], self.initJsonData['testBranch'])).splitlines()
        #     if len(res) > 0:
        #         printStr("{0}: {1} files diff".format(module, len(res)))
        #     else:
        #         printStr("{0}: 已经是最新了。".format(module))

    def commit(self, message):
        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            printTitle(module)
            printStr(os.popen("git add .").read())
            printStr(os.popen("git commit -m {0}".format(message)).read())

    def status(self):
        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            res = GitUtils._runCmd("git status -s")
            if len(res.splitlines()) > 0:
                printTitle(module)
                printStr(res)

    def unChangeValidate(self):
        hasChange = False
        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            res = GitUtils._runCmd("git status -s")
            if len(res.splitlines()) > 0:
                print("模块{0}本地仍有修改，请先提交代码".format(module))
                printStr(res)
                hasChange = True
        if hasChange:
            exit(1)

    def clone(self):
        for module in self.moduleNameList:
            if not GitUtils._checkModuleExist(module):
                os.chdir(projectModuleDir)
                # 这边给clone下的项目重命名一下，避免仓库名和模块名不一致
                res = os.popen('git clone {0} {1}'.format(
                    self.moduleJsonData[module]['git'], module)).read()
                printStr(res)

    def merge(self, source_branch):
        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            printTitle(module)

            cmd = f'git merge {source_branch}'
            state = os.system(cmd)
            GitUtils.checkStateWithMsg(state, cmd)

    # 一个模块创建MR
    # def mergeRequestCreateForOneModule(self, module):
        # api = GitlabAPI()
        # printStr("模块{0}创建MR：from <{1}> into <{2}>".format(
        #     module, self.initJsonData['featureBranch'], self.initJsonData['testBranch']))
        # api.createMR(
        #     self.moduleJsonData[module]['id'], self.initJsonData['featureBranch'], self.initJsonData['testBranch'])

        # 为所有模块创建MR

    def mergeRequestCreate(self, sourceBranch, targetBranch):
        api = GitlabAPI()
        for module in self.moduleNameList:
            printStr("模块{0}创建MR：from <{1}> into <{2}>".format(
                module, sourceBranch, targetBranch))
            api.createMR(
                self.moduleJsonData[module]['id'], sourceBranch, targetBranch)
        # 命令形式提交mr
        # for module in moduleNameList:
        #     moduleDir = os.path.join(projectModuleDir, module)
        #     os.chdir(moduleDir)
        #     printTitle(module)

        #     # 确保本地代码都应提交了，以免出现代码有忘记提交的，导致提测代码不是最新的
        #     GitUtils.unChangeValidate()

        #     cmd = 'git push -o merge_request.create -o merge_request.source={0} -o merge_request.target={1} -o merge_request.assignee_id={2}'.format(
        #         initJsonData['featureBranch'], initJsonData['testBranch'], "819")
        #     state = os.system(cmd)
        #     GitUtils.checkStateWithMsg(state, cmd)
        # print()

    def _getCurBranch():
        cmd = f'git branch'
        branchList = GitUtils._runCmd(cmd).splitlines()
        for branch in branchList:
            if branch.startswith('*'):
                return branch.split(' ')[1]

    def branch(self):
        isSame = True
        curBranch = ''
        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            printTitle(module)
            cmd = f'git branch'
            branchList = GitUtils._runCmd(cmd).splitlines()
            for branch in branchList:
                if branch.startswith('*'):
                    if curBranch == '':
                        curBranch = branch.split(' ')[1]
                    elif curBranch != branch.split(' ')[1]:
                        isSame = False
                    print(branch.split(' ')[1])
        if isSame:
            printStr("所有模块都在同一分支")
        else:
            printError("分支不统一，请检查")

    def pull(self):
        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            printTitle(module)

            cmd = f'git pull'
            state = os.system(cmd)
            GitUtils.checkStateWithMsg(state, cmd)

    def checkout(self, featureBranch, shouldPush=False):
        # for module in self.moduleNameList:
        #     res = os.system('git checkout {0}'.format(
        #         featureBranch))
        #     if res == 0:
        #         printStr("the branch:{0} is already exists!".format(
        #             featureBranch))
        #     else:
        #         os.system(
        #             'git checkout -b {0}'.format(featureBranch))
        #     if shouldPush:
        #         os.system(
        #             "git push --set-upstream origin {0}".format(featureBranch))

        api = GitlabAPI()

        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            printTitle(module)
            # 在远端创建feature分支和test分支，执行pull后直接切换到feature分支，会自动跟随远端的feature分支
            printStr("模块：{0}检测远端是否存在feature分支".format(module))
            api.createBranch(
                self.moduleJsonData[module]['id'], self.initJsonData['featureBranch'])
            # printStr("模块：{0}检测远端是否存在test分支".format(module))
            # api.createBranch(
            #     self.moduleJsonData[module]['id'], self.initJsonData['testBranch'])

            cmd = f'git pull'
            state = os.system(cmd)
            GitUtils.checkStateWithMsg(state, cmd)

            checkoutState = os.system('git checkout {0}'.format(
                featureBranch))
            GitUtils.checkStateWithMsg(checkoutState, cmd)

    def _branchJudge(self):
        isSame = True
        curBranch = ''
        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            cmd = f'git branch'
            branchList = GitUtils._runCmd(cmd).splitlines()
            for branch in branchList:
                if branch.startswith('*'):
                    if curBranch == '':
                        curBranch = branch.split(' ')[1]
                    elif curBranch != branch.split(' ')[1]:
                        isSame = False
        return isSame

    def push(self):
        if self._branchJudge():
            for module in self.moduleNameList:
                moduleDir = os.path.join(projectModuleDir, module)
                os.chdir(moduleDir)
                printTitle(module)
                cmd = f'git branch'
                branchList = GitUtils._runCmd(cmd).splitlines()
                for branch in branchList:
                    if branch.startswith('*'):
                        pushCmd = 'git push origin {0}'.format(
                            branch.split(' ')[1])
                        state = os.system(pushCmd)
                        GitUtils.checkStateWithMsg(state, pushCmd)
        else:
            printStr("所有模块开发分支不一致！")
            printError("为防止出现不可预测的问题，请保证所有模块的开发分支一致！")

    def checkStateWithMsg(state, cmd):
        if state != 0:
            printError(f"execute '{cmd}' failed")

    def executeRawCommand(self, rawCmd):
        for module in self.moduleNameList:
            moduleDir = os.path.join(projectModuleDir, module)
            os.chdir(moduleDir)
            printTitle(module)
            printStr(GitUtils._runCmd(rawCmd))
            # print(os.popen(rawCmd).read())
