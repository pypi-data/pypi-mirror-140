from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='amhhandler',       # 包名
    version='1.2.1',         # 版本号
    description='An even better way to work with Python.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='nbyue',
    author_email='20671413@163.com',
    url='https://gitee.com/nbyue/amh-handler',
    license="MIT",    # 开源协议
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['pymysql', 'requests'],
)
