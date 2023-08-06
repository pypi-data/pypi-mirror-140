from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="filesort",
    version="0.1.1",
    author="Vivian Hafener",
    author_email="vhafener@outlook.com",
    description="A package that aids sorting of files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/viv-codes/filesort",
    # include_package_data=True,
    project_urls={
        "Bug Tracker": "https://github.com/viv-codes/filesort/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "src"},
    py_modules=["main"],
    packages=find_packages(where="main.py"),
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "filesort=main:cli",
        ],
    },
    # packages=find_packages(include=['prompt-toolkit', 'Click'])
    # install_requires=['prompt-toolkit', 'Click']
    python_requires=">=3.6",
)
