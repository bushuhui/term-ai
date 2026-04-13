
## prompt

这个程序增加一个命令行选项 --setup ，就是设置LLM的信息
- 提示用户输入 LLM 的API URL
- 提示用户输入 模型名字
- 提示用户输入 API KEY
- 然后将这些选项保存到这个程序的配置文件中
- 如果不存在配置文件的话，则创建一个默认的配置文件
- 第一次运行这个程序的时候，如果没有配置文件则执行这个设置过程：创建默认的配置文件，提示用户输入基本的模型信息，然后写入配置文件


运行 --setup 的时候，把配置文件的路径打印出来


将命令行选项 --setup 的说明增加到 README.md



## pypi

```bash
# 本地安装工具
pip install -U setuptools wheel twine build

# 打包
python -m build

# 上传
twine upload dist/*

# 本地安装
pip install --upgrade -e "."
# pip安装
pip install pi-term-ai
```
