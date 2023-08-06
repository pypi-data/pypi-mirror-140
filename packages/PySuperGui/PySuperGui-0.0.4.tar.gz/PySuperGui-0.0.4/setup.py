from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.4'
DESCRIPTION = 'This library creates guis in a simpler way using Tkinter'
LONG_DESCRIPTION = ''

# Setting up
setup(
    name="PySuperGui",
    version=VERSION,
    author="PySuperGui (Aliscreative)",
    author_email="<test@test.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    keywords=['python', 'gui','tkinter', 'UI', 'Simple Ui', 'Simple Gui', 'window'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 3 - Alpha"
    ]
)