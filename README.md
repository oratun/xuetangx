# xuetangx
A xuetangx.com videos' spider based on Python3
使用Python爬取学堂在线公开课视频

安装依赖:
pip3 install pyquery requests

准备工作:
1. 浏览器访问xuetangx.com, 登录后复制Cookie填写到代码文件main.py中
2. 进入课程页面(如: http://www.xuetangx.com/courses/course-v1:TsinghuaX+10421094X_2015_2+sp/courseware/76976b23e6b24131a5fc9b5e3426e573/b45d1e9e41e14ff89721ede4c3547978/) 保存html源码为'xuetangx.html'(与main.py同一目录)用于解析

运行:
python3 main.py