from dcentity.models import Entity
from django.db import connection
from django.conf import settings
from piston.handler import BaseHandler
from piston.utils import rc


# at the database level -1 is used to indicate summation over all cycles
ALL_CYCLES = '-1'
DEFAULT_LIMIT = '10'
DEFAULT_CYCLE = ALL_CYCLES

class SQLBindingError(Exception):
    pass

def cast_values(row,type_list):
    return [c(s) for s,c in zip(row,type_list)]

def execute_top(stmt, *args):
    cursor = connection.cursor()

    execute(cursor, stmt, args)

    return list(cursor)

def execute_pie(stmt, *args):
    cursor = connection.cursor()
    execute(cursor, stmt, args)
    return dict([(category, (count, amount)) for (category, count, amount) in cursor])

def execute_rollup(stmt, *args):
    cursor = connection.cursor()
    execute(cursor, stmt, args)
    return [(category, count, amount) for (category,count,amount) in cursor]

def execute_one(stmt, *args):
    cursor = connection.cursor()
    execute(cursor, stmt, args)

    if cursor.rowcount <= 0:
        return None
    else:
        return cursor.fetchone()

def execute_all(stmt, *args):
    cursor = connection.cursor()
    execute(cursor,stmt,args)
    return cursor.fetchall()

def execute(cursor, stmt, args):
    if settings.DEBUG:
        print cursor.mogrify(stmt, args)

        cursor.execute('explain ' + stmt, args)
        for x in cursor.fetchall():
            print x[0]
        
    try:
        # Just gonna leave this here...
        # print cursor.mogrify(stmt, args)
        cursor.execute(stmt, args)
    except IndexError:
        raise SQLBindingError("You didn't include the right number of binding parameters in your query.")


def check_empty(result, *entity_ids):
    """ Empty results are normally fine, except when the entity ID doesn't exist at all--then return 404. """

    if not result and Entity.objects.filter(id__in=entity_ids).count() < len(entity_ids):
        error_response = rc.NOT_FOUND
        error_response.write('No entity with the given ID.')
        return error_response

    return result

class TopListHandler(BaseHandler):

    args = ['cycle', 'limit']
    fields = None
    stmt = None

    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)})

        raw_result = execute_top(self.stmt, *[kwargs[param] for param in self.args])
        labeled_result = [dict(zip(self.fields, row)) for row in raw_result]

        return labeled_result


class EntityTopListHandler(BaseHandler):

    args = ['entity_id', 'cycle', 'limit']
    fields = None
    stmt = None

    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)})
        kwargs.update({'limit': request.GET.get('limit', DEFAULT_LIMIT)})

        raw_result = execute_top(self.stmt, *[kwargs[param] for param in self.args])
        labeled_result = [dict(zip(self.fields, row)) for row in raw_result]

        return check_empty(labeled_result, kwargs['entity_id'])


class EntitySingletonHandler(BaseHandler):

    args = ['entity_id', 'cycle']
    fields = None
    stmt = None

    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)})

        result = execute_one(self.stmt, *[kwargs[param] for param in self.args])

        if result:
            result = dict(zip(self.fields, result))
        else:
            result = {}

        return check_empty(result, kwargs['entity_id'])


class PieHandler(BaseHandler):

    args = ['entity_id', 'cycle']
    category_map = {}
    default_key = None
    stmt = None

    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)})

        raw_result = execute_pie(self.stmt, *[kwargs[param] for param in self.args])

        if self.default_key:
            labeled_result = dict([(self.category_map[key], value) for (key, value) in raw_result.items() if key in self.category_map])

            extra_keys = [k for k in raw_result.keys() if k not in self.category_map.keys()]
            if extra_keys:
                labeled_result[self.default_key] = (sum([value[0] for (key, value) in raw_result.items() if key in extra_keys]), sum([value[1] for (key, value) in raw_result.items() if key in extra_keys]))
        else:
            labeled_result = dict([(self.category_map[key], value) if key in self.category_map else (key, value) for (key, value) in raw_result.items() ])

        return check_empty(labeled_result, kwargs['entity_id'])

class SummaryHandler(BaseHandler):

    rollup = None
    breakout = None
    key_function = None

    def read(self, request, **kwargs):
        parents = self.rollup.read(request,**kwargs)
        children = self.breakout.read(request,**kwargs)
        try:
            if self.rollup.default_key:
                other_children = []
                for child in children:
                    k = self.key_function(child)
                    if k in parents:
                        parents[k]['children'].append(child)
                    else:
                        other_children.append(child)
                other_children.extend(parents[self.rollup.default_key].pop('children'))
                parents[self.rollup.default_key]['children'] = sorted(other_children,
                            reverse=True, key= lambda x: x['amount'])[0:10]
            else:
                for child in children:
                    k = self.key_function(child)
                    parents[k]['children'].append(child)
                for p in parents:
                    parents[p]['children'] = sorted(parents[p]['children'],
                            reverse=True, key= lambda x: x['amount'])

        except:
            print sys.exc_info()

        result = []

        for k,v in parents.iteritems():
            v['name'] = k
            result.append(v)

        return result

class SummaryRollupHandler(BaseHandler):

    args = ['cycle']
    category_map = {}
    default_key = None
    stmt = None
    type_list = [int,float]

    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', DEFAULT_CYCLE)})

        raw_result = execute_pie(self.stmt, *[kwargs[param] for param in self.args])

        typed_result = dict((key,tuple(cast_values(vals,self.type_list))) for (key,vals) in raw_result.iteritems())

        if not self.category_map:
            labeled_result = dict([(key,
                                  {'count': count, 'amount': amount, 'children' : []})
                                  for (key, (count, amount)) in typed_result.items() ])

        elif self.default_key:
            labeled_result = dict([(self.category_map[key],
                                  {'count':count,'amount': amount, 'children' : []})
                                  for (key, (count, amount)) in typed_result.items()
                                  if key in self.category_map])

            extra_keys = [k for k in typed_result.keys() if k not in self.category_map.keys()]
            if extra_keys:
                labeled_result[self.default_key] = {
                                    'count':  sum([count for
                                               (key, (count, amount)) in typed_result.items()
                                               if key in extra_keys]),
                                    'amount': sum([amount for
                                               (key, (count, amount)) in typed_result.items()
                                               if key in extra_keys]),
                                    'children' : []}
        else:
            labeled_result = dict([(self.category_map[key],
                                    {'count':count, 'amount': amount, 'children' : []})
                                    if key in self.category_map
                                    else (key, {'count': count, 'amount': amount, 'children': []})
                                    for (key, (count, amount)) in typed_result.items() ])
        return labeled_result

class SummaryBreakoutHandler(BaseHandler):
    args = ['cycle','limit']
    stmt = None
    type_list = [str,str,str,float]

    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', DEFAULT_CYCLE)})
        kwargs.update({'limit': request.GET.get('limit', DEFAULT_LIMIT)})

        raw_results = execute_all(self.stmt, *[kwargs[param] for param in
            self.args])

        typed_results = [tuple(cast_values(result,self.type_list)) for result in raw_results]

        labeled_results = [dict(zip(self.fields,result)) for result in typed_results]

        return labeled_results
