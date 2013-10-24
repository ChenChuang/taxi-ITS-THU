import lib
import os

import config

def read_by_cuid(from_cuid, to_cuid, proc):
	max_cuid = 8602
	#max_cuid = 1

	if callable(getattr(proc, "parser_start_callback", None)):
		proc.parser_start_callback()

	for cuid in range(max(from_cuid, 1), min(to_cuid + 1, max_cuid + 1)):
		input_dir = config.proc_input_dir + 'CUID_' + str(cuid) + '/data/'
		if not os.path.isdir(input_dir):
			continue

		print 'CUID =',str(cuid),'...',

		all_infn = sorted(os.listdir(input_dir),cmp=lib.cmp_str_by_int)

		proc.cuid_start_callback(cuid)

		for infn in all_infn:	
			if not os.path.isfile(input_dir + infn):
				continue
			inf = open(input_dir + infn, 'r')
			
			proc.file_start_callback(infn)

			while True:
				line = inf.readline()
				if len(line) == 0:
					break
				if line == '\n':
					continue
				proc.line_callback(line)
			pass

			proc.file_end_callback(infn)
	
		proc.cuid_end_callback(cuid)

		print 'completed'
	
	if callable(getattr(proc, "parser_end_callback", None)):
		proc.parser_end_callback()
