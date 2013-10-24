import os

import common.lib as lib
import common.config

#max_cuid = 8602
max_cuid = 1

output_dir = proc_output_dir
f_count = 1
l_count = 0
f = open(output_dir + str(f_count) + '.txt', 'w')
#print 'new file:',f.name

curr_t = ""
curr_t_len = 0

for cuid in range(1, max_cuid + 1):
	#input_dir
	input_dir = proc_input_dir + 'CUID_' + str(cuid) + '/data/'
	if not os.path.isdir(input_dir):
		continue

	print 'CUID =',str(cuid),'...',

	all_infn = sorted(os.listdir(input_dir),cmp=lib.cmp_str_by_int)

	pre_occupied = -1
	pre_line = ""

	for infn in all_infn:	
		if not os.path.isfile(input_dir + infn):
			continue

		inf = open(input_dir + infn, 'r')
		while True:
			line = inf.readline()
			if len(line) == 0:
				break
			if line == '\n':
				continue

			curr_occupied = line.split(', ')[6]
			if pre_line == "":
				pass				
			elif curr_occupied == "1" and pre_occupied == "0":
				curr_t = pre_line + line
				curr_t_len = 2
			elif curr_occupied == "0" and pre_occupied == "1":
				#destination is current line, check here
				if lib.is_record_in_area(line, 3994135-2000, 3994135+2000, 11630571-2000, 11630571+2000):
					curr_t += line
					curr_t_len += 1
					f.write(curr_t)
					f.write('\n')
					l_count += curr_t_len	
			elif curr_occupied == "1":
				curr_t += line
				curr_t_len += 1

			pre_occupied = curr_occupied
			pre_line = line

			if l_count >= query_output_lines:
				f.close()
				f_count += 1
				f = open(output_dir + str(f_count) + '.txt', 'w')
				#print 'new file:',f.name
				l_count = 0
		pass
	
	print 'completed'

f.close()


