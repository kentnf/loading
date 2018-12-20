#!/usr/bin/python3

import sys
import copy

'''
ns-vcf -- read vcf and output json record

Plan: will load the vcf file bach, check the annotated vcf file and load it
'''

def vcf_to_json(vcf_file):

    vcf_json = []

    with open(vcf_file, 'r+') as fh:
        title = []
        for line in fh:
            line = line.strip('\n')
            if (line[0] == '#'):
                if (line[0:6] == '#CHROM'):
                    title = line.split('\t')
                    title[0] = 'CHROM'
                    # CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  PI_512625
                continue
            line = line.strip('\n')
            m = line.split('\t')
            
            variant = {}

            ''' save "CHROM POS ID REF ALT QUAL" to record dict '''
            for i in range(0, 5):
                variant[title[i]] = m[i]

            ''' the column 9 is format of genotype fields (gt) '''
            gf_format = m[8].split(':')

            for j in range(9, len(m)):
                ''' add accession and data '''
                record = copy.deepcopy(variant)
                record['accession'] = title[j]

                ''' add genotype info '''
                genotype_info = {}
                gt = m[j].split(':')
                if (len(gf_format) != len(gt)):
                    sys.exit('[ERR]genotype fields num is not consistant with genotype info')
                for k in (0,len(gt)-1):
                    genotype_info[gf_format[k]] = gt[k]
                record['genotype_info'] = genotype_info

                ''' add record to vcf json '''
                vcf_json.append(record)

if __name__ == '__main__':
	vcf_to_json('cucumber_SNP_miss0.5.maf0.01.vcf')


