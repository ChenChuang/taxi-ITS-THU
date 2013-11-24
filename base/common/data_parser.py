import lib
import os

import config

def read_by_cuid(from_cuid, to_cuid, proc):
    max_cuid = 8602

    callbacks = {
            "parser_start" : "parser_start_callback",
            "parser_end"   : "parser_end_callback"  ,
            "cuid_start"   : "cuid_start_callback"  ,
            "cuid_end"     : "cuid_end_callback"    ,
            "file_start"   : "file_start_callback"  ,
            "file_end"     : "file_end_callback"    ,
            "line_proc"    : "line_callback"}

    def empty_func(*args):
        pass

    for k,v in callbacks.items():
        callbacks[k] = getattr(proc, v, empty_func)


    callbacks["parser_start"]()

    for cuid in range(max(from_cuid, 1), min(to_cuid + 1, max_cuid + 1)):
        input_dir = config.proc_input_dir + 'CUID_' + str(cuid) + '/data/'
        if not os.path.isdir(input_dir):
            continue
        print 'CUID =',str(cuid),'...',
        all_infn = lib.sort_filenames_by_ints(os.listdir(input_dir))

        callbacks["cuid_start"](cuid)
        for infn in all_infn:    
            if not os.path.isfile(input_dir + infn):
                continue
            inf = open(input_dir + infn, 'r')
            
            callbacks["file_start"](infn)
            while True:
                line = inf.readline()
                if len(line) == 0:
                    break
                if line == '\n':
                    continue
                callbacks["line_proc"](line)
            pass
            callbacks["file_end"](infn)
        callbacks["cuid_end"](cuid)

        print 'completed'
    
    callbacks["parser_end"]()
