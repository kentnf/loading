#!/usr/bin/python3

# import time
import sys
from BCBio.GFF import GFFExaminer
from BCBio import GFF
import pprint

'''
parse_feature_location -- put featureLocation object to dict
'''
def parse_feature_location(src, src_id, location, phase=-1):
	loc_dict = { 'srcfeature_id': {'_id': src_id, 'name': src}, 'fmin': int(location.start), 'fmax': int(location.end), 'strand':int(location.strand) }
	if (phase>=0):
		loc_dict['phase'] = phase
	return(loc_dict)

'''
gff3_to_feature -- load gene, mRNA, or refseq features from gff3

support feature type: gene, mRNA, refseq (including chromosome, scaffold, contigs ...)
the exon and CDS features were merged into mRNA  
'''
def gff3_to_feature(gff3, mapid_data, ftype):

	feature = [] 
	
	examiner = GFFExaminer()
	
	fh = open(gff3, 'r+')
	for refseq_feature in GFF.parse(fh):
		# print(refseq_feature)
		refseq_id = refseq_feature.id
		refseq_obj_id = refseq_id
		if ('chromosome' in mapid_data and refseq_id in mapid_data['chromosome']):
			refseq_obj_id = mapid_data['chromosome'][refseq_id]

		if (ftype == 'chromosome'):
			feature.append({'name': refseq_feature.id, 'type': ftype})
			continue
		
		if (ftype == 'gene' or ftype == 'mRNA'):
			for gene_feature in refseq_feature.features:
			# skip the chromosome feature for tripal
				if ((ftype == 'gene') and (gene_feature.type == 'gene')):
					feature_loc = parse_feature_location(refseq_id, refseq_obj_id, gene_feature.location)
					feature.append({'name': gene_feature.id, 'type': gene_feature.type, 'loc': feature_loc})
					continue

				if (ftype == 'mRNA'):
					for mrna_feature in gene_feature.sub_features:
						feature_loc = parse_feature_location(refseq_id, refseq_obj_id, mrna_feature.location)
						sub_feature_list = []

						gene_obj_id = gene_feature.id
						if ('gene' in mapid_data and gene_feature.id in mapid_data['gene']):
							gene_obj_id = mapid_data['gene'][gene_feature.id]

						for sub_feature in mrna_feature.sub_features:
							if (sub_feature.type == 'CDS'):
								sub_feature_loc = parse_feature_location(refseq_id, refseq_obj_id, sub_feature.location, phase=int(sub_feature.qualifiers['phase'][0]))
								sub_feature_list.append({'name': sub_feature.id, 'type': sub_feature.type, 'loc': sub_feature_loc})
							else:
								sub_feature_loc = parse_feature_location(refseq_id, refseq_obj_id, sub_feature.location)
								sub_feature_list.append({'name': sub_feature.id, 'type': sub_feature.type, 'loc': sub_feature_loc})
						
						feature.append({'name': mrna_feature.id, 'type': mrna_feature.type, 'loc': feature_loc, 'sub_features': sub_feature_list, 'parent': { '_id': gene_obj_id, 'name': gene_feature.id} })
						#pprint.pprint(feature)
						#sys.exit()

	fh.close()
	return(feature)


#if __name__ == '__main__':
#	feature = []
#	gff3_to_feature('dataset/chr00.gff3','chromosome', feature)
#	print(len(feature))
#   gff3_to_feature('dataset/CM4.0.gff3', feature)
#   gff3_to_feature('dataset/tripal.CM4.0.rename.gff3', 'mRNA', feature)

