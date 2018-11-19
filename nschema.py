#!/usr/bin/python3

import sys
import glob
import yaml


'''
load_schema -- load schema for storing genomic data
'''
def load_schema(folder):

    schema_dict = {}
    uniq_type = {}
    error = 0

    required_keys = ['order', 'type', 'collection', 'fields']

    for file in glob.glob(folder + "/*.yaml"):
        with open(file) as fh:
            schema = yaml.load(fh)

            for key in required_keys:
                if (key not in schema):
                    print('[ERR] %s not exist in %s' % (key,file))
                    error = 1

            schema_dict[schema['order']] = schema

            if (schema['type'] in uniq_type):
                print('[ERR]duplicate type: %s' % schema['type'])
                error = 1
            uniq_type[schema['type']] = 1

    #print(schema_dict)
    if (error == 1):
        sys.exit()
    return(schema_dict)
    
#if __name__ == '__main__':
#    load_schema('schema')
    
