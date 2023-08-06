import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyiocare",
    version="0.0.1",
    author="Robert Drinovac",
    author_email="unlisted@gmail.com",
    description="A Python library for Coway Air Purifiers ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/RobertD502/pyiocare',
    keywords='coway, iocare, iocare api, coway api, airmega',
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ),
    project_urls={  # Optional
    'Bug Reports': 'https://github.com/RobertD502/pyiocare/issues',
    'Source': 'https://github.com/RobertD502/pyiocare/',
    },
)
