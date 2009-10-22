import logging
import os

def extract(src_path, dest_path):
    
    for f in os.listdir(src_path):
        
        fpath = os.path.join(src_path, f)
    
        if f.endswith('.zip'):
            cmd = 'unzip -u %s -d %s' % (fpath, dest_path)
        else:
            cmd = 'cp %s %s' % (fpath, dest_path)
            
        print cmd
        os.system(cmd)
    
def main():

    from optparse import OptionParser
    import sys

    usage = "usage: %prog [options]"

    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dataroot", dest="dataroot",
                      help="path to data directory", metavar="PATH")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="noisy output")

    (options, args) = parser.parse_args()

    if not options.dataroot:
        parser.error("path to dataroot is required")

    
    dataroot = os.path.abspath(options.dataroot)
    
    src_path = os.path.join(dataroot, 'download', 'crp')
    dest_path = os.path.join(dataroot, 'raw', 'crp')

    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    else:
        os.system('rm -r %s' % os.path.join(dest_path, '*'))
        
    extract(src_path, dest_path)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    main()