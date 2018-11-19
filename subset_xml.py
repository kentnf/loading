#!/usr/bin/python3

import sys
from nxml import xml_to_attr

if __name__ == '__main__':

	# hits = xml_to_attr("dataset/CM4.0_protein.fasta.xml", 'protein', 'xref', 'name', 'matches', -1)
	# hits = xml_to_attr("dataset/CM4.0_protein.dia.tr.xml", 'Iteration', 'Iteration_query-def', '','Hit', 5)
	# hits = xml_to_attr("dataset/CM4.0_protein.dia.sp.xml", 'Iteration', 'Iteration_query-def', '','Hit', 5)
	# hits = xml_to_attr("dataset/CM4.0_protein.dia.at.xml", 'Iteration', 'Iteration_query-def', '','Hit', 5)
	# hits = xml_to_attr("dataset/CM4.0_protein.dia.xml", 'Iteration', 'Iteration_query-def', '','Hit', 5)

	#for g in hits:
		# print(g)
	# sys.exit()

	with open('dataset/test.tid', 'r+') as fh:
		for line in fh:
			line = line.strip('\n')
			if (hits[line]):
				print(hits[line])  
