#!/usr/bin/env python
# encoding=utf-8

import getopt
import json
import os
import sys
from tdf_tools.dependencies_analysis import DependencyAnalysis
from tdf_tools.git_utils import GitUtils

from tdf_tools.json_data_read import branchInvalidate, getModuleJsonData, getModuleNameList, moduleInvalidate
from tdf_tools.json_data_read import getInitJsonData, moduleExistJudge
from tdf_tools.module_dependencies_rewrite import ModuleDependenciesRewriteUtil
from tdf_tools.python_gitlab_api import GitlabAPI
from tdf_tools.tdf_print import printError, printStage


def processHelp():
    txt = \
        """
        -h or --help:           输出帮助文档
        -c :                  对所有模块执行自定义 git 命令, 例如: -c git status.

        项目初始化
        ------------------------------------------------------------------------
        init                    请确保已配置initial_config.json文件，然后会执行以下步骤：
                                1.clone所有配置的模块
                                2.切换所有模块的分支到配置的feature分支
                                3.重写所有依赖为本地依赖
        deps                    修改initial_config.json文件后，执行该命令，更新依赖
        update                  更新存储项目git信息的json文件


        git相关
        ------------------------------------------------------------------------
        status                              聚合展示所有模块的仓库状态
        commit                              对所有模块执行add 和 commit
        diff                                对所有模块执行 git diff --name-only 当前分支..master
        diff [branch]                       对所有模块执行 git diff --name-only 当前分支..[branch]
        # undiff                              对所有模块执行 git diff --name-only [feature分支]..[test分支] 比对feature和test分支的代码（确保提测代码没有遗漏）
        pull or sync                        对所有模块执行 git pull
        checkout                            对所有模块执行 git checkout 切换到配置在initial_config.json中的feature分支
        checkout [branch]                   对所有模块执行 git checkout branch
        checkout [branch] -p                对所有模块执行 git checkout 并push到远程，跟踪来自 'origin' 的远程分支
        merge                               对所有模块执行 git merge
        branch                              聚合展示所有模块的当前分支
        push                                对所有模块执行 git push origin 当前分支
        # push -t                             对所有模块执行 git push origin 当前分支 并为所有开发模块创建MR
        mr -c sourceBranch targetBranch     对所有模块提交一个merge request 源分支sourceBranch，目标分支targetBranch
        """
    print(txt)


name = "tdf_tools"
curDir = os.getcwd()


# 更新模块配置信息


def initModuleConfig():
    dirValidate()
    FLUTTER_GROUP_ID = "1398"  # Flutter仓库组

    HPP_FLUTTER_GROUP_ID = "1489"  # 火拼拼的Flutter仓库组
    FLUTTER_REPOSITORY_GROUP_IDS = [FLUTTER_GROUP_ID, HPP_FLUTTER_GROUP_ID]

    # start
    projectInfo = dict()

    cachePath = os.getcwd()

    api = GitlabAPI()

    os.chdir(cachePath)

    for groupId in FLUTTER_REPOSITORY_GROUP_IDS:
        groupProjectList = api.get_all_projects_in_group(groupId)
        for project in groupProjectList:
            tup = api.getContent(project.id, project.name)
            if tup[0] == True:
                print("{0}, {1}, {2}, {3}".format(
                    tup[1], project.id, project.ssh_url_to_repo, project.namespace['name']))
                projectInfo[tup[1]] = dict()
                projectInfo[tup[1]]['id'] = project.id
                projectInfo[tup[1]]['git'] = project.ssh_url_to_repo
                projectInfo[tup[1]]['type'] = project.namespace['name']

    file = 'module_config.json'
    if os.path.exists(file):
        os.remove(file)
    f = open(file, 'w+')
    f.write(json.dumps(projectInfo, indent=2))
    f.close()


def create():
    if os.path.exists('.tdf_flutter') is not True:
        os.mkdir('.tdf_flutter')

        os.chdir('.tdf_flutter')

        initialData = dict()

        initialData["featureBranch"] = ""
        # initialData["testBranch"] = ""
        initialData["shellName"] = ""
        initialData["moduleNameList"] = []

        # 判断是否有初始化文件
        if os.path.exists('initial_config.json') is not True:
            f = open('initial_config.json', 'w+')
            f.write(json.dumps(initialData, indent=2))
            f.close()

        if os.path.exists('.gitignore') is not True:
            f = open('.gitignore', 'w+')
            f.write('./project_module')
            f.close()

        if os.path.exists('module_config.json') is not True:
            initModuleConfig()


# 路径校验，当前路径必存在initial_config.json文件，不然会提示报错


def dirValidate():
    if os.path.exists('initial_config.json') is not True:
        print("请在.tdf_flutter文件夹所在目录执行脚本")
        exit(-1)

# 校验配置是否正确，所有需要开发的库是否存在于模块配置json文件中


def validateConfig(moduleJsonData):
    moduleNameList = getModuleNameList()
    for module in moduleNameList:
        if module not in moduleJsonData.keys():
            printError(
                "配置的开发模块没有找到git仓库信息。请确保 1. 模块名配置正确； 2. 执行 tdf_tools update 更新git信息配置文件")


def process():
    if os.path.exists('.tdf_flutter') is not True:
        printError('请先执行tdf_init进行初始化')

    os.chdir('.tdf_flutter')
    dirValidate()
    branchInvalidate()
    moduleInvalidate()

    initJsonData = getInitJsonData()
    moduleJsonData = getModuleJsonData()
    validateConfig(moduleJsonData)
    if os.path.exists('.project_module') == False:
        os.mkdir('.project_module')

    try:
        options, args = getopt.getopt(
            sys.argv[1:], 'chd:r:', ['help', 'dr', 'rd'])
        for name, value in options:
            if name in ('-h', '--help'):
                processHelp()
                return
            if name == '-c':
                gitUtils = GitUtils()
                rawGitCommand = ' '.join(args)
                gitUtils.executeRawCommand(rawGitCommand)
                return
        if len(args) >= 1:
            arg = args[0]
            if arg == 'init':
                moduleExistJudge()
                gitUtils = GitUtils()
                gitUtils.clone()
                gitUtils.checkout(
                    initJsonData['featureBranch'], shouldPush=True)
                reWrite = ModuleDependenciesRewriteUtil()
                reWrite.rewrite()
            elif arg == 'deps':
                gitUtils = GitUtils()
                gitUtils.clone()
                gitUtils.checkout(
                    initJsonData['featureBranch'], shouldPush=True)
                reWrite = ModuleDependenciesRewriteUtil()
                reWrite.rewrite(reWriteOnlyChange=True)
            elif arg == 'update':
                initModuleConfig()
            elif arg == 'map':
                analysis = DependencyAnalysis()
                analysis.generate()
            elif arg == 'diff':
                if len(args) > 1:
                    gitUtils = GitUtils()
                    gitUtils.diff(args[1])
                else:
                    gitUtils = GitUtils()
                    gitUtils.diff()
            elif arg == 'status':
                gitUtils = GitUtils()
                gitUtils.status()
            elif arg == 'commit':  # add . and commit
                if len(args) > 1:
                    gitUtils = GitUtils()
                    gitUtils.commit(args[1])
                else:
                    printError(
                        "no commit message, please exec Example: python3 process.py commit \"commit message\"")
            elif arg == 'pull' or arg == 'sync':
                gitUtils = GitUtils()
                gitUtils.pull()
            elif arg == 'push':
                gitUtils = GitUtils()
                gitUtils.push()
                # if len(args) == 2 and args[1] == '-t':
                #     gitUtils = GitUtils()
                #     gitUtils.mergeRequestCreate(
                #         initJsonData['featureBranch'], initJsonData['testBranch'])
            elif arg == 'mr':
                if len(args) > 2:
                    if args[1] == '-c' and len(args) == 4:
                        gitUtils = GitUtils()
                        gitUtils.mergeRequestCreate(args[2], args[3])
                    elif args[1] == '-c' and len(args) != 4:
                        printError("参数不正确")

            elif arg == 'checkout':
                if len(args) > 2:
                    if args[2] == "-p":
                        gitUtils = GitUtils()
                        gitUtils.checkout(args[1], True)
                    else:
                        gitUtils = GitUtils()
                        gitUtils.checkout(args[1])
                elif len(args) > 1:
                    gitUtils = GitUtils()
                    gitUtils.checkout(args[1])
                else:
                    # 默认切换到配置的feature分支
                    gitUtils = GitUtils()
                    gitUtils.checkout(initJsonData['featureBranch'])
            elif arg == 'branch':
                gitUtils = GitUtils()
                gitUtils.branch()
            elif arg == 'merge':
                if len(args) > 1:
                    gitUtils = GitUtils()
                    gitUtils.merge(args[1])
                else:
                    printError(
                        "no source branch, please exec Example: python3 process.py merge beanch")
            # elif arg == 'undiff':
            #     gitUtils = GitUtils()
            #     gitUtils.checkout(initJsonData['featureBranch'])
            #     gitUtils.pull()
            #     gitUtils.checkout(initJsonData['testBranch'])
            #     gitUtils.pull()
            #     printStage("feature 和 test分支")
            #     gitUtils.undiff()

    except getopt.GetoptError as err:
        printError(f"{err}, see 'python3 process.py -h or --help'")
