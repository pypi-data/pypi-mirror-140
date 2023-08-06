from setuptools import setup, find_packages ,find_namespace_packages          #这个包没有的可以pip一下
setup(
    name = "MxbaiduAi",      #这里是pip项目发布的名称
    version = "0.0.2",  #版本号，数值大的会优先被pip
    keywords = ("pip", "SICA","featureextraction"),
    description = "MxPi",
    long_description = "结合MxPi调用百度AI，MxPi是一款树莓派可视化编程工具",
    license = "MIT Licence",

    url = "https://github.com/yuanyunqiang/",     #项目相关文件地址，一般是github
    author = "YuanYunQiang",
    author_email = "649756903@qq.com",
    packages = find_namespace_packages(
                     include=["MxbaiduAi", "MxbaiduAi.*"], ),
    include_package_data = True,
    platforms = "any",
    install_requires = ['requests'] ,       
)
