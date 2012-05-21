# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
""" store the declarative_base in this module
"""

from sqlalchemy.ext.declarative import declarative_base

class ORMClass(object):
    @classmethod
    def query(class_):
        from stalker.db.session import DBSession
        return DBSession.query(class_)

Base = declarative_base(cls=ORMClass)