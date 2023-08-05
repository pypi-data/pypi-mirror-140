#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 依赖分析【有向无环图，有向有环图】


import json
import os
from ruamel import yaml
import copy
from tdf_tools.tdf_print import printStage, printError, printStr

from tdf_tools.json_data_read import getInitJsonData, getModuleJsonData, getModuleNameList, projectModuleDir


class DependencyNode:
    def __init__(self):
        self.nodeName = ''
        self.parent = []  # 父亲节点列表
        self.children = []  # 子孙节点列表
        self.delete = False


class DependencyAnalysis(object):

    def __init__(self):
        printStage("依赖分析")
        self.initJsonData = getInitJsonData()
        self.moduleJsonData = getModuleJsonData()
        self.moduleNameList = getModuleNameList()

    # 分析lock文件，获取所有的packages
    def _analysisLock(self):
        os.chdir(self.__moduleGenPath)
        # 读取lock内容
        with open('pubspec.lock', encoding='utf-8') as f:
            doc = yaml.round_trip_load(f)
            if (isinstance(doc, dict) and doc.__contains__('packages')):
                f.close()
                return doc['packages']

    # 生成依赖图
    def _generateDependenciesMap(self):
        for package in self.__moduleDependenciesMap:
            for module in self.moduleNameList:
                if package == module:
                    # 到这一步表明当前这个模块属于开发模块且在当前模块的依赖模块列表中，是当前模块的子模块
                    self._mNodeDict[self.__moduleName].children.append(package)
                    self._mNodeDict[package].parent.append(self.__moduleName)

    # 返回二维数组，用于并发打tag
    def _generateDependenciesOrder(self):
        resList = []
        while self._existNode():
            itemList = []

            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    if not node.delete:
                        if len(node.children) == 0:
                            itemList.append(node.nodeName)
                            node.delete = True

            deleteNodeList = []
            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    if node.delete:
                        deleteNodeList.append(node.nodeName)

            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    for deleteItem in deleteNodeList:
                        if node.children.__contains__(deleteItem):
                            node.children.remove(deleteItem)

            if len(itemList) == 0:
                break
            resList.append(itemList)
        exit(json.dumps(resList))

    # 返回一维数组，用于从下至上执行upgrade
    def _generateDependenciesOrderForUpgrade(self):
        resList = []
        while self._existNode():
            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    if not node.delete:
                        if len(node.children) == 0:
                            resList.append(node.nodeName)
                            node.delete = True

            deleteNodeList = []
            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    if node.delete:
                        deleteNodeList.append(node.nodeName)

            for item in self._mNodeDict:
                node = self._mNodeDict[item]
                if isinstance(node, DependencyNode):
                    for deleteItem in deleteNodeList:
                        if node.children.__contains__(deleteItem):
                            node.children.remove(deleteItem)

        print(resList)

        return resList

    def _existNode(self):
        for item in self._mNodeDict:
            node = self._mNodeDict[item]
            if isinstance(node, DependencyNode) and node.delete == False:
                return True
        return False

    def _subChildCount(self, childName):
        for item in self._mNodeDict:
            node = self._mNodeDict[item]
            if isinstance(node, DependencyNode):
                if node.delete == False:
                    if node.children.__contains__(childName):
                        node.children.remove(childName)

    def generate(self):

        self._mNodeDict = dict()
        # 初始化节点列表
        for module in self.moduleNameList:
            node = DependencyNode()
            node.nodeName = module
            self._mNodeDict[module] = node

        # 读取lock文件
        for module in self.moduleNameList:
            self.__moduleName = module
            self.__moduleGenPath = projectModuleDir + "/" + module
            self.__moduleDependenciesMap = self._analysisLock()
            self._generateDependenciesMap()

        self._generateDependenciesOrder()

    def getDependencyOrder(self):

        self._mNodeDict = dict()
        # 初始化节点列表
        for module in self.moduleNameList:
            node = DependencyNode()
            node.nodeName = module
            self._mNodeDict[module] = node

        # 读取lock文件
        for module in self.moduleNameList:
            self.__moduleName = module
            self.__moduleGenPath = projectModuleDir + "/" + module
            self.__moduleDependenciesMap = self._analysisLock()
            self._generateDependenciesMap()

        return self._generateDependenciesOrderForUpgrade()
