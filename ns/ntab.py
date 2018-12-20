#!/usr/bin/python3

import sys

'''
tab_to_attr -- convert tab delimit file to attr
'''
def tab_to_attr(input_file, col=0):
	feature_dict = {}

	with open(input_file, 'r+') as fh:

		first_line = fh.readline()
		first_line = first_line.strip('\n')
		title = ()
		if (first_line[0] == '#'):	
			title = first_line.split('\t')
			title.pop(col)
		else:
			m = first_line.split('\t')
			feature_name = m.pop(col)
			feature_dict[feature_name] = m

		for line in fh:
			line = line.strip('\n')
			m = line.split('\t')
			feature_name = m.pop(col)


			if (len(title) > 0):
				feature_dict[feature_name] = {}
				for n in range(len(m)):
					feature_dict[feature_name][title[n]] = m[n]
			else:
				feature_dict[feature_name] = m

	return(feature_dict)

#if __name__ == '__main__':
#	tab_to_attr('zd1')
