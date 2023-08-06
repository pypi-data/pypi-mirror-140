# from setuptools import setup, find_packages

# VERSION = '1.0.0'
# DESCRIPTION = 'Topsis Package'
# LONG_DESCRIPTION = 'A package as part of Predictive Analysis course at Thapar Institute of Engineering and'

# # Setting up
# setup(
#     name="jj-101903706-Topsis",
#     version=VERSION,
#     author="Rohit Jain",
#     author_email="<rjain1_be19@thapar.edu>",
#     description=DESCRIPTION,
#     long_description_content_type="text/markdown",
#     long_description=LONG_DESCRIPTION,
#     packages=find_packages(),
#     setup_requires=['wheel'],
#     install_requires=['numpy', 'pandas'],
#     keywords=['python', 'topsis', 'thapar', 'Prdictive-Analysis', '101903797'],
#     classifiers=[
#     'Development Status :: 3 - Alpha',     
#     'Intended Audience :: Developers',   
#     'Topic :: Software Development :: Build Tools',
#     'License :: OSI Approved :: MIT License', 
#     'Programming Language :: Python :: 3',
#     'Programming Language :: Python :: 3.7',  
#     'Programming Language :: Python :: 3.8',
#     'Programming Language :: Python :: 3.9',
#   ],
#   entry_points={
#     "console_scripts":[
#       "topsis=topsis.topsis:get_topsis_result",
#     ]
#   },
# )

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    #name="Topsis-JiteshSilhi-101903797",
    name="Topsis1234",
    #version="1.0.2",
    version="1.0.0",
    description="It gives a csv file that includes the topsis result",
    long_description=README,
    long_description_content_type="text/markdown",
    
    author="Jitesh Silhi",
    author_email="jsilhi@protonmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=['pandas','numpy'],
    setup_requires=['wheel'],
    entry_points={
        "console_scripts": [
            "topsis=topsis.topsis:get_topsis_result",
        ]
    },
)