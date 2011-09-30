
from dcentity.models import Entity
from django.db import connection
from piston.handler import BaseHandler
from piston.utils import rc


# at the database level -1 is used to indicate summation over all cycles
ALL_CYCLES = '-1'
DEFAULT_LIMIT = '10'
DEFAULT_CYCLE = ALL_CYCLES

class SQLBindingError(Exception):
    pass


def execute_top(stmt, *args):
    cursor = connection.cursor()

    execute(cursor, stmt, args)

    return list(cursor)

def execute_pie(stmt, *args):
    cursor = connection.cursor()
    execute(cursor, stmt, args)
    return dict([(category, (count, amount)) for (category, count, amount) in cursor])

def execute_one(stmt, *args):
    cursor = connection.cursor()
    execute(cursor, stmt, args)

    if cursor.rowcount <= 0:
        return None
    else:
        return cursor.fetchone()

def execute(cursor, stmt, args):
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
            return {}

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


