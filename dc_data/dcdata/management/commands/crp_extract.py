import os
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

def extract(src_path, dest_path):
    
    for f in os.listdir(src_path):
        
        fpath = os.path.join(src_path, f)
    
        if f.endswith('.zip'):
            cmd = 'unzip -u %s -d %s' % (fpath, dest_path)
        else:
            cmd = 'cp %s %s' % (fpath, dest_path)
            
        print cmd
        os.system(cmd)
    

class CRPExtract(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-d", "--dataroot", dest="dataroot",
                          help="path to data directory", metavar="PATH"),
        make_option("-b", "--verbose", action="store_true", dest="verbose", default=False,
                          help="noisy output"))

    def handle(self, *args, **options):
        if 'dataroot' not in options:
            raise CommandError("path to dataroot is required")
    
        
        dataroot = os.path.abspath(options['dataroot'])
        
        src_path = os.path.join(dataroot, 'download', 'crp')
        dest_path = os.path.join(dataroot, 'raw', 'crp')
    
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        else:
            os.system('rm -r %s' % os.path.join(dest_path, '*'))
            
        extract(src_path, dest_path)


Command = CRPExtract
