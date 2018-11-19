#!/usr/bin/python3

'''
parse large XML files which stores funtional annotations of features
infact, we do not need xml module such as SAX at here
'''

import sys
# import datetime

'''
re_match_tag -- using regexp to match tag of xml
  string: line of xml file
  tag: <tag> or </tag>
  status: 0 or 1, 0 match start, 1 match end 

 The string is much faster than regexp method, but can not ignore the upcase and lowcase
'''
def re_match_tag(string, tag, status):
	if (status):
		tag = '</' + tag + '>'
		if (tag in string):
			return(1)
		#return(re.match(r'.*</' + tag + '>.*', string, re.I))
	else:
		tag1 = '<' + tag + '>'
		tag2 = '<' + tag + ' '
		if ((tag1 in string) or (tag2 in string)):
			return(1)
		#return(re.match(r'.*<' + tag + ' .*', string, re.I) or re.match(r'.*<' + tag + '>.*', string, re.I))

	return(0)

'''
xml_get_attr -- get attr value base on key
'''
def xml_get_attr(string, key):
	string = string.strip('\n')
	member = string.split(' ')
	for m in member:
		m = m.replace('"', '')
		m = m.replace('/>', '')
		if ('=' in m):
			(k, v) = m.split('=', 2)
			if (k == key):
				return(v)
	return(0)

'''
xml_get_text -- get text in tag
'''
def xml_get_text(string):
	return(string[string.find('>')+1:string.rfind('<')])
'''
xml_get_value -- get value from xml tag, the value could be a attr of a key, or text in xml tag
if key exist, get attr value; otherwise, get text 
'''
def xml_get_value(string, key):
	if (key):
		return(xml_get_attr(string, key))
	else:
		return(xml_get_text(string))

'''
keep_hits -- keep hit_num of hits in xml_str
'''
def keep_hits(xml_str, hit_tag, hit_num):

	hit_order = 0
	out_status = 1
	new_xml_str = ''
	end_xml_str = ''

	lines = xml_str.split('\n')
	for line in lines:

		if (out_status == 1):
			new_xml_str = new_xml_str + line + '\n'
		else:
			end_xml_str = end_xml_str + line + '\n'

		if ( re_match_tag(line, hit_tag, 1) ):
			hit_order = hit_order + 1
			# print(out_status, hit_order, hit_num)
			if (hit_order >= hit_num):
				out_status = 0
			end_xml_str = ''

	new_xml_str = new_xml_str + end_xml_str
	return(new_xml_str)

'''
remove_tag -- remove tag from xml
'''
def remove_tag(xml_str, remove_tag):

	out_status = 1
	new_xml_str = ''

	lines = xml_str.split('\n')
	for line in lines:
		if ( re_match_tag(line, remove_tag, 0) ):
			out_status = 0
			continue
		if ( re_match_tag(line, remove_tag, 1) ):
			out_status = 1
			continue
		if (out_status == 1):
			new_xml_str = new_xml_str + line + '\n'
	return(new_xml_str)

'''
xml_to_attr -- save xml to dict: hits

input:
  xml_file -- file name
  branch_tag -- tag for branch wich includes multiple hits of features, sometimes includes feature info
  feature_tag -- tag for feature
    feature_key -- key for retrieve feature; blank key '' indicates feature store in text of tag

  hit_tag -- tag name of each hit
  hit_num -- number of hits (top 5 for blast, all for interproscan)

return: 
  key: feature_name
  value: xml content
'''

def xml_to_attr(xml_file, branch_tag, feature_tag, feature_key, hit_tag, hit_num):

	hits = {}
	status = 0
	value = ''
	# print(datetime.datetime.now())

	with open(xml_file, 'r+') as fh:

		for line in fh:
			if ( re_match_tag(line, feature_tag, 0) ):
				feature_name = xml_get_value(line, feature_key)
				feature_name_dict[feature_name] = 1

			if ( re_match_tag(line, branch_tag, 0) ):
				if (value and len(feature_name_dict) > 0):
					if (hit_num > 0):
						value = keep_hits(value, hit_tag, hit_num)
						value = remove_tag(value, 'Iteration_stat')
					for fname in feature_name_dict:
						hits[fname] = value
					# debug
					# if (feature_name == 'MELO3C027439.2.1'):
					#	break
				status = 1
				value = ''
				feature_name_dict = {}

			if (status == 1):
				value = value + line

			if ( re_match_tag(line, branch_tag, 1) ):
				status = 0

		# process the last record
		if (value and len(feature_name_dict) > 0):
			if (hit_num > 0):
				value = keep_hits(value, hit_tag, hit_num)
				value = remove_tag(value, 'Iteration_stat')
			for fname in feature_name_dict:
				hits[fname] = value

	print("Processing and store %d of branch xml to dict." % len(hits))
	# print(datetime.datetime.now())

	# print 1 record for debug
	# for fid in hits:
	#	if (fid == 'MELO3C027439.2.1'):
	#		print(hits[fid])
	#		sys.exit()
	return(hits)

#if __name__ == '__main__':
	#xml_to_attr("dataset/CM4.0_protein.fasta.xml", 'protein', 'xref', 'name', 'matches', -1)
    #xml_to_attr("dataset/CM4.0_protein.dia.tr.xml", 'Iteration', 'Iteration_query-def', '','Hit', 5)
