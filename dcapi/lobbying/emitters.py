from dcapi.common.emitters import ExcelEmitter
from dcdata.lobbying.models import Lobbying, Lobbyist, Issue
import cStringIO
import xlwt

class LobbyingExcelEmitter(ExcelEmitter):
    
    def stream(self, request, stats):
        
        output = cStringIO.StringIO()
        
        wb = xlwt.Workbook()
        ws_lobbying = wb.add_sheet('lobbying')
        ws_lobbyist = wb.add_sheet('lobbyists')
        ws_issue = wb.add_sheet('issues')
        
        fields_lobbying = [f.name for f in Lobbying._meta.fields]
        fields_lobbyist = [f.name for f in Lobbyist._meta.fields]
        fields_lobbyist.remove('transaction')
        fields_lobbyist.insert(0, 'transaction_id')
        fields_issue = [f.name for f in Issue._meta.fields]
        fields_issue.remove('transaction')
        fields_issue.insert(0, 'transaction_id')
        
        self.write_row(ws_lobbying, 0, fields_lobbying)
        self.write_row(ws_lobbyist, 0, fields_lobbyist)
        self.write_row(ws_issue, 0, fields_issue)
        
        row_lobbying = 1
        row_lobbyist = 1
        row_issue = 1
        
        for record in self.data:
            
            values = [getattr(record, f) for f in fields_lobbying]
            self.write_row(ws_lobbying, row_lobbying, values)
            
            for lobbyist in record.lobbyists.all():
                values = [getattr(lobbyist, f) for f in fields_lobbyist]
                self.write_row(ws_lobbyist, row_lobbyist, values)
                row_lobbyist += 1
            
            for issue in record.issues.all():
                values = [getattr(issue, f) for f in fields_issue]
                self.write_row(ws_issue, row_issue, values)
                row_issue += 1
            
            row_lobbying += 1
        
        stats.stats['urn:fec:transaction'] = row_lobbying - 1
        stats.stats['total'] = row_lobbying - 1
        
        wb.save(output)
        xls = output.getvalue()
        output.close()
        
        yield xls
