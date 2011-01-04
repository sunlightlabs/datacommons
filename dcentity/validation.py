# this isn't necessarily code to be reused. It's just a place for routines
# that I've found useful while working with entities in the shell.

from dcentity.models import Entity, EntityAttribute, EntityAlias
from django.db import connection
from uuid import UUID

def e_info(*ids):
    for id in ids:
        e = Entity.objects.get(id=UUID(id))
    
        print "%s: %s" % (e.id, e.name)
        print "Aliases: %s" % ", ".join(["%s: %s" % (a.namespace, a.alias) for a in e.aliases.all()])
        print "Attributes: %s" % ", ".join(["%s: %s" % (a.namespace, a.value) for a in e.attributes.all()])


        
