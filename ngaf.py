#!/usr/bin/python3

import sys

'''
tab_to_attr -- convert tab delimit file to attr
'''
def gaf_to_attr(input_file):
	feature_dict = {}

	with open(input_file, 'r+') as fh:

		''' no title of GAF file '''
		'''
		first_line = fh.readline()
		first_line = first_line.strip('\n')
		title = ()
		if (first_line[0] == '#'):	
			title = first_line.split('\t')
			title.pop(0)
		else:
			m = first_line.split('\t')
			feature_name = m.pop(0)
			feature_dict[feature_name] = m
		'''

		for line in fh:
			line = line.strip('\n')
			m = line.split('\t')
			feature_name = m[1]
			go = m[4]

			if feature_name in feature_dict:
				feature_dict[feature_name].append(go)
			else:
				feature_dict[feature_name] = []
				feature_dict[feature_name].append(go)

	return(feature_dict)

#if __name__ == '__main__':
#	tab_to_attr('zd1')
