
# system requirement

```
sudo apt update


sudo apt install nodejs
sudo apt install npm
sudo apt install python3-pip
sudo pip3 install biopython
sudo pip3 install bcbio-gff
sudo pip3 install pyyaml
pip install elasticsearch

```

# speed test 
Load features from GFF file: 13s
Insert featurs to mongodb: 4s


# design

single document 16M, 

collection: 
	organism
	analysis (in fact, this is anlaysis result)
		the pipeline can be used as field of analysis
		the organism can be the reference of organism

	feature
		type:chromosome
		type:gene (Bidirectional reference) 
		type:mRNA (protein, CDS, exon, UTR are Embedded)
		
	* the analysis, organism is reference
	* the position is reference of chrosome
	* the funcational annotation is Embedded
		
	feature_relationship : for one-to-squillions
		single gene with many AS, such as the Drosophila Down syndrome cell adhesion molecule (Dscam) gene, which can generate 38,016 isoforms by the alternative splicing of 95 variable exons.


# insert genomic data to database
