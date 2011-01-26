#-*- coding: utf-8 -*-
"""This module contains the database mappers and tables for ReferenceMixin.

See examples/extending/great_entity.py for an example.
"""



from sqlalchemy.orm import relationship, synonym
from sqlalchemy import (
    Table,
    Column,
    Integer,
    ForeignKey,
)
from stalker import db
from stalker.db import tables
from stalker.core.models import link



#----------------------------------------------------------------------
def setup(class_, class_table, mapper_arguments={}):
    """creates the necessary tables and properties for the mappers for the
    mixed in class
    
    use the returning dictionary (mapper_arguments) in your mapper
    
    :param class_: the mixed in class, in other words the class which will be
      extended with the mixin functionalities
     
    :param class_table: the table holding the information about the class
    
    :param mapper_arguments: incoming mapper arugments for the
      SQLAlchemy.Orm.Mapper, it will be updated with the properties of the
      current mixin
    
    :returns: a dictionary holding the mapper_arguments
    """
    
    class_name = class_.__name__
    
    # there is no extra columns in the base table so we don't need to update
    # the given class_table
    
    # use the given class_name and the class_table
    secondary_table = Table(
        class_name.lower() + "_references", db.metadata,
        Column(
            class_name.lower() + "_id",
            Integer,
            ForeignKey(class_table.c.id),
            primary_key=True,
        ),
        
        Column(
            "reference_id",
            Integer,
            ForeignKey(tables.links.c.id),
            primary_key=True,
        )
    )
    
    new_properties = {
        "_references": relationship(
            link.Link,
            secondary=secondary_table,
            primaryjoin=\
                class_table.c.id==\
                eval("secondary_table.c." + class_name.lower() + "_id"),
            secondaryjoin=\
                secondary_table.c.reference_id==\
                tables.links.c.id,
        ),
        "references": synonym("_references"),
    }
    
    try:
        mapper_arguments["properties"].update(new_properties)
    except KeyError:
        mapper_arguments["properties"] = new_properties
    
    return mapper_arguments








