#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 模块重写脚本

from inspect import getmodule
import os
from unicodedata import name
from ruamel import yaml
from tdf_tools.dependencies_analysis import DependencyAnalysis
from tdf_tools.tdf_print import printStage, printError, printStr
from enum import Enum
from tdf_tools.json_data_read import getInitJsonData, getModuleJsonData, getModuleNameList, projectModuleDir


class ModuleDependenciesRewriteUtil(object):

    def __init__(self):
        self.moduleJsonData = getModuleJsonData()
        self.moduleNameList = getModuleNameList()
        self.initJsonData = getInitJsonData()

    # 分析lock文件，获取所有的packages
    def _analysisLock(self):
        os.chdir(self.__moduleGenPath)
        # 分析前先执行pub upgrade
        os.popen('flutter pub upgrade').read()

        # 读取lock内容
        with open('pubspec.lock', encoding='utf-8') as f:
            doc = yaml.round_trip_load(f)
            if (isinstance(doc, dict) and doc.__contains__('packages')):
                f.close()
                return doc['packages']

    # 是否是壳模块
    def _isShellModule(self):
        return self.moduleJsonData[self.__moduleName]['type'] == 'app'

    # 确认哪些依赖需要重写
    def _confirmRewriteDependencies(self):
        if self._isShellModule():  # 壳模块重写所有配置的依赖
            for item in self.moduleNameList:
                if (item != self.__moduleName):  # 壳自己不加入重写列表
                    self.__needRewriteDependencies.append(item)
        else:  # 如果不是壳模块，则进行lock文件内的package列表和开发模块匹配，匹配上则添加到override列表
            for package in self.__moduleDependenciesMap:
                for module in self.moduleNameList:
                    if package == module:
                        self.__needRewriteDependencies.append(module)

        printStage("{0}中以下依赖将被override".format(self.__moduleName))
        printStr(self.__needRewriteDependencies)

    def _addOverrideDependencies(self):
        mDict = dict()
        for item in self.__needRewriteDependencies:
            mDict[item] = {
                "path": "../{0}/".format(item)}

        return mDict

    # 添加dependency_overrides

    def _rewriteDependencies(self):
        os.chdir(self.__moduleGenPath)
        with open('pubspec.yaml', encoding='utf-8') as f:
            doc = yaml.round_trip_load(f)
            if isinstance(doc, dict):
                self._confirmRewriteDependencies()
                if doc.__contains__('dependency_overrides') and doc['dependency_overrides'] != None:
                    # printError(
                    #     "dependency_overrides遗留，发现开发不规范，强制删除dependency_overrides", False)
                    # printStr(doc['dependency_overrides'])
                    doc['dependency_overrides'] = None

                # 重写依赖
                overrideDict = dict()
                for item in self.__needRewriteDependencies:
                    overrideDict[item] = {
                        "path": "../{0}/".format(item)}
                if len(self.__needRewriteDependencies) > 0:
                    doc['dependency_overrides'] = overrideDict

                with open('pubspec.yaml', 'w+', encoding='utf-8') as reW:
                    yaml.round_trip_dump(
                        doc, reW, default_flow_style=False, encoding='utf-8', allow_unicode=True)
                    reW.close()
                    # 依赖重写完，执行pub upgrade更新lock文件
                    os.popen('flutter pub upgrade').read()
                    printStr("lock文件已更新")
            f.close()

    # 添加dependency_overrides，如果已存在模块的override，则不修改

    def _rewriteDependenciesIfUpdate(self):
        os.chdir(self.__moduleGenPath)
        with open('pubspec.yaml', encoding='utf-8') as f:
            doc = yaml.round_trip_load(f)
            if isinstance(doc, dict):
                self._confirmRewriteDependencies()

                global existUpdate
                existUpdate = False

                # 删除不存在于重写依赖列表中的key
                if doc.__contains__('dependency_overrides') and doc['dependency_overrides'] != None and isinstance(doc['dependency_overrides'], dict):
                    for item in doc['dependency_overrides'].keys():
                        if item not in self.__needRewriteDependencies:
                            printStr("${0}依赖被删除".format(item))
                            existUpdate = True
                            del doc['dependency_overrides'][item]

                overrideDict = dict()
                for item in self.__needRewriteDependencies:
                    if doc.__contains__('dependency_overrides') and doc['dependency_overrides'] != None and isinstance(doc['dependency_overrides'], dict) and doc['dependency_overrides'].get(item, -1) != -1:
                        printStr("${0}依赖已存在（不予修改）".format(item))
                    else:
                        printStr("${0}依赖不存在（添加）".format(item))
                        existUpdate = True
                        overrideDict[item] = {
                            "path": "../{0}/".format(item)}
                doc['dependency_overrides'] = overrideDict
                if existUpdate:
                    with open('pubspec.yaml', 'w+', encoding='utf-8') as reW:
                        yaml.round_trip_dump(
                            doc, reW, default_flow_style=False, encoding='utf-8', allow_unicode=True)
                        reW.close()
                        # 依赖重写完，执行pub upgrade更新lock文件
                        os.popen('flutter pub upgrade').read()
                        printStr("lock文件已更新")
                else:
                    printStr("yaml无更新")

            f.close()

    # 重写依赖 本地依赖

    def rewrite(self, reWriteOnlyChange=False):
        for module in self.moduleNameList:
            self.__moduleGenPath = projectModuleDir + "/" + module
            # 这一步会生成lock文件
            self.__moduleDependenciesMap = self._analysisLock()

        # 分析依赖树，从下至上之行upgrade
        dependencyAnalysis = DependencyAnalysis()
        dependencyList = dependencyAnalysis.getDependencyOrder()

        for module in dependencyList:
            self.__moduleName = module
            self.__moduleGenPath = projectModuleDir + "/" + module
            self.__moduleDependenciesMap = self._analysisLock()
            self.__needRewriteDependencies = []
            if reWriteOnlyChange:
                self._rewriteDependenciesIfUpdate()
            else:
                self._rewriteDependencies()
