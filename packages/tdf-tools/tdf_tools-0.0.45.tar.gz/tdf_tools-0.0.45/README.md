**帮助文档**

```python
-h or --help:           输出帮助文档
        -c :                  对所有模块执行自定义 git 命令, 例如: -c git status.

        项目初始化
        ------------------------------------------------------------------------
        init                    请确保已配置initial_config.json文件，然后会执行以下步骤：
                                1.clone所有配置的模块
                                2.切换所有模块的分支到配置的feature分支
                                3.重写所有依赖为本地依赖


        git相关
        ------------------------------------------------------------------------
        status                              聚合展示所有模块的仓库状态
        commit                              对所有模块执行add 和 commit
        diff                                对所有模块执行 git diff --name-only 当前分支..master
        diff [branch]                       对所有模块执行 git diff --name-only 当前分支..[branch]
        undiff                              对所有模块执行 git diff --name-only [feature分支]..[test分支] 比对feature和test分支的代码（确保提测代码没有遗漏）
        pull or sync                        对所有模块执行 git pull
        checkout                            对所有模块执行 git checkout 切换到配置在initial_config.json中的feature分支
        checkout [branch]                   对所有模块执行 git checkout branch
        checkout [branch] -p                对所有模块执行 git checkout 并push到远程，跟踪来自 'origin' 的远程分支
        merge                               对所有模块执行 git merge
        branch                              聚合展示所有模块的当前分支
        push                                对所有模块执行 git push origin 当前分支
        push -t                             对所有模块执行 git push origin 当前分支 并为所有开发模块创建MR
        mr -c sourceBranch targetBranch     对所有模块提交一个merge request 源分支featureBranch，目标分支testBranch
        mr -l 模块1 模块2 模块3               ⬇⬇⬇
        mr -list 模块1 模块2 模块3            对模块1，2，3提交mr
```





- **initial_config.json文件说明**

  ```json
  {
      "featureBranch": "feature/test_dev_1", // 开发分支
      "testBranch": "test/test_dev_1", // 提测分支
      // 项目需要开发的模块
      "moduleNameList": [
          "flutter_reset_module",
          "tdf_smart_devices",
          "tdf_widgets",
          "tdf_channel"
      ]
  }
  ```

- **module_config.json文件说明**

  ```json
  {
      "flutter_globalyun_us_module": {
        	"id": "11111"
          "type": "shell",
          "git": "git@git.2dfire.net:app/flutter/app/flutter_globalyun_us_module.git"
      },
      "tdf_router_anno": {
          "type": "base",
          "git": "git@git.2dfire.net:app/flutter/app/tdf_router_anno.git"
      },
  }
  //语意
  {
    "模块名":{
      "id": 项目gitlab id
      "类型": gitlab group名
      "git": gitlab地址
    }
  }
  ```





**工具使用流程说明**

安装python包
```
python3 -m pip install tdf-tools --user
```
安装并更新python包
```
python3 -m pip install --upgrade tdf-tools --user
```

安装测试环境python包
```
python3 -m pip install -i https://test.pypi.org/simple/ tdf-tools --user
```

安装并更新测试环境python包
```
python3 -m pip install --upgrade -i https://test.pypi.org/simple/ tdf-tools --user
```



**准备工作**

在~目录下，创建.tdf_tools_config文件并配置相关必需属性如下

```json
git_private_token=***
```

* git_private_token是gitlab的token

  获取途径：进入gitlab页面，点击右上角头像，选择Preferences，选择左侧列表中的AccessToken进行创建


1. 初始化
    执行tdf_init
    1. 会自动生成.tdf_flutter目录
    2. 会自动生成.gitignore文件
    3. 会自动生成initial_config.json文件
    4. 会自动生成module_config.json文件（这一步需要点时间，会从gitlab获取项目信息）


2. 进入.tdf_flutter目录，配置initial_config.json文件<span style="color:#ff0000">【脚本会对该文件进行数据校验】</span>
   1. 配置开发分支featureBranch
   2. 配置测试分支testBranch
   3. 配置shellName（这个属性一般后续就不再改变了，配置的名称需要是module_config.json中type为app的模块）
   3. 配置需要开发的模块的名称，模块名可以在module_config.json中查找



3. 执行tdf_tools init
   1. 自动clone所有配置的开发模块
   2. 调用gitlab api在远端创建feature分支和test分支，并在pull后直接切换到feature分支（这边会默认跟随远端的同名分支）
   3. 自动分析依赖树，并**由下至上**对所有模块自动执行flutter pub upgrade



**<span style="color:#ff0000">FAQ</span>**

windows系统请使用bash命令；






**额外功能说明**

- python3 process.py map

生成一个二维数组，可根据该二维数组的数据进行并发打tag

```json
[
	["tdf_channel", "tdf_event", "tdf_network"], 
	["tdf_widgets"], 
	["tdf_smart_devices", "tdf_account_module"], 
	["flutter_reset_module"]
]
```

如上数据，数组中每一个节点中的模块均可同时打tag，节点之间需要由上至下的顺序进行tag操作



- python3 module_config_update.py

更新module_config.json文件，更新会遍历组id1398和1489下的所有项目，判断是否存在yaml文件，存在则为flutter模块，记录数据；



- 依赖树分析原理

采用有向有/无环图进行依赖树的分析

数据结构采用如下：

```python
class DependencyNode:
    def __init__(self):
        self.nodeName = ''
        self.parent = []  # 父亲节点列表
        self.children = []  # 子孙节点列表
        self.delete = False
```

![dependency](./README_DIR/dependency.png)

如上图1：一个正常的依赖树表示；

如上图2：对图1中，依赖树所有节点去重，变换为图2有向图；	



**分析流程：**

**依赖图构建**

```python
# 生成依赖图
    def _generateDependenciesMap(self):
        for package in self.__moduleDependenciesMap:
            for module in moduleNameList:
                if package == module:
                    # 到这一步表明当前这个模块属于开发模块且在当前模块的依赖模块列表中，是当前模块的子模块
                    self._mNodeDict[self.__moduleName].children.append(package)
                    self._mNodeDict[package].parent.append(self.__moduleName)
```

- 共5个节点

  - node构建：

    - ```python
      {
      	"模块1":{
          "nodeNmae": "模块1",
          "parent": [],
          "children": ["模块2","模块3","模块4","模块5"],
          "delete": False
      	},
      	"模块2":{
          "nodeNmae": "模块2",
          "parent": ["模块1"],
          "children": ["模块4","模块5"],
          "delete": False
      	}
      	"模块3":{
          "nodeNmae": "模块3",
          "parent": ["模块1"],
          "children": ["模块5"],
          "delete": False
      	}
      	"模块4":{
          "nodeNmae": "模块4",
          "parent": ["模块1","模块2"],
          "children": [],
          "delete": False
      	}
      	"模块5":{
          "nodeNmae": "模块5",
          "parent": ["模块1","模块2","模块3"],
          "children": [],
          "delete": False
      	}
      }
      ```

**依赖图解析伪代码（以一维数组为例）**

```python
# 返回二维数组，用于并发打tag
    def _generateDependenciesOrder(self):
        resList = []
        while 存在节点delete属性不为True:
            
            for：查找子节点为0的节点
            	设置节点delete属性为True
              
            for：deleteItemList = 拿到所有delete属性为true的节点

            for：遍历所有节点，如果节点的子节点中包含deleteItemList的节点，则将其从子节点列表中删除
```









**后续计划**

<span style="color:#ff0000">**问题：**</span>由于现在flutter ci 【lint】【tag】任务脚本成功率过于低，很多时候是因为项目模块的配置问题导致的，且后续会接入一键打tag工具

方案：在执行统一push前，对所有模块的项目配置信息进行校验，确保数据规范；


**打包**
```
python3 setup.py sdist bdist_wheel
```
**发布**
```
python3 -m twine upload --repository pypi dist/* --verbose
```