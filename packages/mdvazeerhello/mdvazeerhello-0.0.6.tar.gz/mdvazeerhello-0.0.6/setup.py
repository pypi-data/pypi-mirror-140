from setuptools import setup, find_packages
import codecs
import os

# here = os.path.abspath(os.path.dirname(__file__))

# with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()

VERSION = '0.0.6'
DESCRIPTION = 'A basic hello package'

# Setting up
setup(
    name="mdvazeerhello",
    version=VERSION,
    author="Vazeeruddin (Microchip)",
    author_email="<mdvazeer@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['colorama==0.4.4', 'inputimeout==1.0.4', 'intelhex==2.3.0', 'psutil==5.8.0', 'PyDirectInput==1.0.4', 'pyelftools==0.27', 'pywin32==301', 'termcolor==1.1.0'],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

