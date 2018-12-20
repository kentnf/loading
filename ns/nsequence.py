#!/usr/bin/python3

from Bio import SeqIO

def sequence_to_attr(input_fasta):
	seq_attr = {}
	for record in SeqIO.parse(input_fasta, "fasta"):
		seq_attr[record.id] = {}
		seq_attr[record.id]['residues'] = str(record.seq)
		seq_attr[record.id]['len'] = len(str(record.seq))
	print("%d sequences have been load from %s."%(len(seq_attr), input_fasta))
	return seq_attr
