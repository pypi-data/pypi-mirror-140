import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mumuzi",
    version="1.2.2",
    author="Neuron-Network on Mumuzi",
    author_email="mumuzi@mumuzi.mumuzi",
    description="ctf全栈全自动解题姬mumuzi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://blog.csdn.net/qq_42880719/",
    project_urls={
        "Bug Tracker": "https://blog.csdn.net/qq_42880719/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "mumuzi"},
    packages=setuptools.find_packages(where="mumuzi"),
    python_requires=">=3.6",
    install_requires=[
    'pyreadline',
    'colorama',
    'pillow',
    'pwntools'],
    package_data = {
# 包含所有.txt文件
'':['modules/misc/.py'],
'':['modules/web/.py'],
}
)