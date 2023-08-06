from setuptools import setup, find_packages
import codecs
import os



VERSION = '0.0.1'
DESCRIPTION = 'Topsis rank genrator'
LONG_DESCRIPTION = 'A simple package that can used in multi-decision criterion process ,helps you to pick up the best option out of all available alternatives'

# Setting up
setup(
    name="Topsis-Prabhjot-101903373",
    version=VERSION,
    author="Prabhjot singh sodhi",
    author_email="<abhijot104@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[ 'pandas', 'numpy'],
    keywords=['python','numpy','rank','score',],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)