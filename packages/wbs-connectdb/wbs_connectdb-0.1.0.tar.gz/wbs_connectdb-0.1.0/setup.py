# -*- coding:UTF-8 -*-
#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup

setup(
 name="wbs_connectdb",
 version="0.1.0",
 author="WangBenSen",
 author_email="OTLXmao@126.com",
 license="Apache License",
 url="https://xxxxxxxxx",
 packages=["Connection_Tool"],
 install_requires=["psycopg2-binary <= 2.9.3 ", "pymysql <= 1.0.2"],
 classifiers=[
 "Environment :: Web Environment",
 "Intended Audience :: Developers",
 "Operating System :: OS Independent",
 "Topic :: Text Processing :: Indexing",
 "Topic :: Utilities",
 "Topic :: Internet",
 "Topic :: Software Development :: Libraries :: Python Modules",
 "Programming Language :: Python",
 "Programming Language :: Python :: 3.9"
 ],
)
