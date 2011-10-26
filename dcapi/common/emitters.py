from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.http import HttpResponse
from django.utils import simplejson
from django.db.models import Model
from django.db import connections
from piston.emitters import Emitter
from django.forms.models import model_to_dict
from piston.utils import HttpStatusCode
from dcapi.models import Invocation
from dcapi.validate_jsonp import is_valid_jsonp_callback_value
from dcdata.contribution.models import NIMSP_TRANSACTION_NAMESPACE, CRP_TRANSACTION_NAMESPACE
from time import time
import csv
import cStringIO
import datetime
import uuid
from xlwt import XFStyle
import xlwt


class AmnesiacFile(object):
    def __init__(self):
        self.content = ""
    def write(self, chunk):
        self.content += chunk
    def read(self, size=None):
        value = self.content
        self.content = ""
        return value

class StatsLogger(object):
    def __init__(self):
        self.stats = { 'total': 0 }
    def log(self, record):
        self.stats['total'] += 1


class StreamingLoggingEmitter(Emitter):

    def construct_record(self, record):
        """ Serialize just one record of the data into a dict.

        This is a workaround because the superclass method will only
        serialize the self.data parameter.
        """

        old_data = self.data
        try:
            self.data = record
            return self.construct()
        finally:
            self.data = old_data


    def stream(self, request, stats):
        raise NotImplementedError('please implement this method')
    
    def stream_render(self, request):
        if isinstance(self.data, HttpResponse):
            raise HttpStatusCode(self.data)
        return self.stream_render_generator(request)
    
    def stream_render_generator(self, request):
        
        stats = self.handler.statslogger() if hasattr(self.handler, 'statslogger') else StatsLogger()
        
        start_time = time()
        
        for chunk in self.stream(request, stats):
            yield chunk
            
        end_time = time()
            
        Invocation.objects.create(
            caller_key=request.apikey.key,
            method=self.handler.__class__.__name__,
            query_string=request.META['QUERY_STRING'],
            total_records=stats.stats['total'],
            crp_records=stats.stats.get(CRP_TRANSACTION_NAMESPACE, 0),
            nimsp_records=stats.stats.get(NIMSP_TRANSACTION_NAMESPACE, 0),
            execution_time=(end_time - start_time) * 1000,
        )
        connections['meta'].close()
        
            
class StreamingLoggingJSONEmitter(StreamingLoggingEmitter):
    
    def stream(self, request, stats):
        
        cb = request.GET.get('callback', None)
        cb = cb if cb and is_valid_jsonp_callback_value(cb) else None
                
        if cb:
            yield '%s(' % cb
        if isinstance(self.data, (Model, dict)):
            seria = simplejson.dumps(self.construct(), cls=DateTimeAwareJSONEncoder, ensure_ascii=False)
            yield seria
        elif isinstance(self.data, HttpResponse):
            pass
        else:
            yield '['
            for record in self.data:
                seria = simplejson.dumps(self.construct_record(record), cls=DateTimeAwareJSONEncoder, ensure_ascii=False)
                if stats.stats['total'] == 0:
                    yield seria
                else:
                    yield ',%s' % seria
                stats.log(record)
            yield ']'
        
        if cb:
            yield ');'


class StreamingLoggingCSVEmitter(StreamingLoggingEmitter):
    
    def stream(self, request, stats):
        f = AmnesiacFile()
        writer = csv.DictWriter(f, fieldnames=self.fields)
        yield ",".join(self.fields) + "\n"
        for record in self.data:
            stats.log(record)
            writer.writerow(self.construct_record(record))
            yield f.read()


class ExcelEmitter(StreamingLoggingEmitter):
    
    def __init__(self, *args, **kwargs):
        
        super(ExcelEmitter, self).__init__(*args, **kwargs)
        
        self.mdy_style = XFStyle()
        self.mdy_style.num_format_str = 'MM/DD/YYYY'
    
        self.mdyhm_style = XFStyle()
        self.mdyhm_style.num_format_str = 'MM/DD/YYYY h:mm'

    def construct_record(self, record):
        return record if isinstance(record, dict) else model_to_dict(record)

    def write_row(self, ws, row, values):
        col = 0
        for value in values:
            if isinstance(value, datetime.datetime):
                ws.write(row, col, value, self.mdyhm_style)
            elif isinstance(value, datetime.date):
                ws.write(row, col, value, self.mdy_style)
            elif isinstance(value, uuid.UUID):
                ws.write(row, col, str(value))
            else:
                ws.write(row, col, value)
            col += 1
    
    def stream(self, request, stats):

        output = cStringIO.StringIO()

        if self.handler.model:

            sheet_name = self.handler.model._meta.object_name.lower()
        else:
            sheet_name = 'Sheet1'

        wb = xlwt.Workbook()
        ws = wb.add_sheet(sheet_name)

        sorted_fields = sorted(self.fields) # output the spreadsheets with columns in alphabetical order

        self.write_row(ws, 0, sorted_fields)

        row = 0
        for record in self.data:
            row += 1

            record_as_dict = self.construct_record(record)

            values = [record_as_dict[f] for f in sorted_fields]
            self.write_row(ws, row, values)
            stats.log(record)

        stats.stats['total'] = row

        wb.save(output)
        xls = output.getvalue()
        output.close()

        yield xls

