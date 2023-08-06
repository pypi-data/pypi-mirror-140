from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Learning python modules'

# Setting up
setup(
    name="test_sayhello",
    version=VERSION,
    author="Prathamesh Sable",
    author_email="prathameshks2003@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'hello', 'test_sayhello'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)