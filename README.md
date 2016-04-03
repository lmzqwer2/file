# LM File

整个项目旨在提供一个图形化的文件界面。

# 用法

## 0. 依赖

本项目依赖于python的tornado框架，linux下的file命令。没有则无法运行。

同时，本项目也依赖于AceEditor项目，但是没有该项目只是浏览器端表现受到影响。

## 1. 运行

可以直接使用主文件不带参数运行，默认以当前文件夹作为根目录。

``` shell
python file.py
```

同时，如果将该项目添加至python的模块文件夹，则可以使用python的模块调用方法直接运行。

``` shell
python -m file
```

## 2. 配置

所有配置均写于config.py中，可以直接运行该文件获取所有配置参数。

``` shell
python config.py
python -m file.config
```

可以使用该文件测试配置，而后再运行主程序。详细配置文件可以使用--help参数查看。

``` shell
python config.py --help
```
