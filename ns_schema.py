#!/usr/bin/python3

import sys
import glob
import copy
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

            ''' 
            the type in here is data type, not the collection name
            eg1: mRNA and gene are different data type which corresponding to different cvterm
            eg2: assembly and annotation are different type of analysis
            '''
            if (schema['type'] in uniq_type):
                print('[ERR]duplicate type: %s' % schema['type'])
                error = 1
            uniq_type[schema['type']] = 1

    #print(schema_dict)
    if (error == 1):
        sys.exit()
    return(schema_dict)

'''
format_schema -- remove * lable in fields of require, then create the key_dict for these required fields
'''
def format_schema(schema_dict):

    keys = copy.deepcopy(schema_dict)

    keys_dict = {}

    for key, value in keys.items():
        if (key[-1] == '*'):
            if (isinstance(value, str)):
                schema_dict[key[:-1]] = value
                keys_dict[key[:-1]] = 1
                del schema_dict[key]
            elif (isinstance(value, dict)):
                schema_dict[key[:-1]] = value
                keys_dict[key[:-1]] = format_schema(value)
                del schema_dict[key]
            elif (isinstance(value, list)):
                ''' will think about it later '''
                pass

    return(keys_dict)

    
#if __name__ == '__main__':
#    load_schema('schema')
    
