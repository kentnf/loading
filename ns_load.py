#!/usr/bin/python3

import os
import sys
import getopt
import yaml
import re
import copy
import pathlib

import pprint

import time

import json
import pymongo
from elasticsearch import Elasticsearch

from nschema import load_schema
from nschema import format_schema

# import modules for processing features, and functional annotation of features
from ndocument import Document

from nfeature import gff3_to_feature
from nsequence import sequence_to_attr
from nxml import xml_to_attr
from ntab import tab_to_attr
from ngaf import gaf_to_attr

'''
search_data -- traversing the value and retrieve the files

  The data from gdata.yaml file contains many key:value's stored in dict (like json). Some values 
are just string to descrbie the attribute of organism, assembly, and annotation. Other values are 
file names which contains pipelines (cwl), features (gff3), and attributes of features.
  This function get all files in the key:value's 
'''
def search_data(data, file_ftype):

    d = [copy.deepcopy(data)]
    n = 0 # prevent infinite loops
    queue = []
    while(d):
        for c in d:
            if (isinstance(c,dict)):
                for item in c.items():
                    if (isinstance(item[1], dict) or isinstance(item[1], list)):
                        queue.append(item[1])
                    else:
                        ftype = get_file_format(item[1])
                        if (ftype):
                            file_ftype[item[1]] = ftype
            elif (isinstance(c, list)):
                for item in c:
                    if (isinstance(item, dict) or isinstance(item, list)):
                        queue.append(item)
                    else:
                        ftype = get_file_format(item)
                        if (ftype):
                            file_ftype[item[1]] = ftype
        d = queue
        queue = []
        
        # prevent infinite loops
        # n = n + 1
        # if (n > 10):
        #	sys.exit()

'''
file_to_list -- convert file to list
'''
def file_to_list(file, mapid_data, feature_type=''):
    ftype = get_file_format(file)
    if (ftype == '.gff' or ftype == '.gff3'):
        # get feature by different feature type
        feature_list = gff3_to_feature(file, mapid_data, feature_type)
        return(feature_list)

    # below data need to band to feature 
    # (think about how to banding data to feature)
    elif (ftype == '.xml'):
        if (file == 'dataset/test_interpro.xml'):
            xml_dict = xml_to_attr(file, 'protein', 'xref', 'name', 'matches', -1)
        else:
            xml_dict = xml_to_attr(file, 'Iteration', 'Iteration_query-def', '','Hit', 5)
        return(xml_dict)

    elif (ftype == '.tab'):
        tab_dict = tab_to_attr(file)
        # print(tab_dict)
        return(tab_dict)

    elif (ftype == '.gaf'):
        gaf_dict = gaf_to_attr(file)
        # print(gaf_dict)
        return(gaf_dict)

    elif (ftype == '.fa' or ftype == '.fasta'):
        seq_dict = sequence_to_attr(file)
        return(seq_dict)

    else:
        print('[ERR]unsupported file type: %s' % file)
        sys.exit()

'''
get_file_format -- check if the data value is file, and get file format
   the file type is determined by suffix
'''
def get_file_format(file):
    
    if (isinstance(file, str)):
        path = pathlib.Path(file)
        if (path.is_file()):
            #print(file)
            ftype = os.path.splitext(file)[1]
            if (ftype):
                return(ftype.lower())
    sys.exit('[ERR] cant not get file type')

'''
map_data : add data from yaml to schema according to rules: 

The fields are separeted in 2 or 3 part by ':::'
Part 1: method used to mapping the data
Part 2: the position of data files stored in gdata schema
Part 3: the fields of data after parsing the the data files
        (only the fileds defined in this part can be insert to database) 

The position of data, or the field of data is separated by '::'
eg: annotation::output_gff3 -- the data file name is in annotation::output_gff3 of gdata
eg: location::srcfeature_id::name -- the location::srcfeature_id::name in one member of parse file

1. traversing all the field members defined in schema
2. mapping the data from gdata.yaml to the schema
3. the mapping includes methods in below:
    A. map: direct use the value from gdata
    B: file: the content of the file from gdata
    C: self: from store data, create the reference of current document
    D: list: corresponding to an file with specific format, such as gff, fasta, xml or tab

Plan. splie this function to two, 1 for traversing, 2 for mapping
     then think about mapping of list datasets
     the stored dataset will be used to build and update index later
'''

def map_data_parse_fields(fields, gdata, store_data):

    for k in fields:
        if (isinstance(fields[k], dict) or isinstance(fields[k], list)):
            map_data_parse_fields(fields[k], gdata, store_data)
            continue
        else:
            if (isinstance(fields[k], str) and re.match('^(map|file|self|list):::', fields[k])):
                m = fields[k].split(':::')
                if (len(m) < 2):
                    print('[ERR]schema fields %s' % k)
                    error = 1
                method = m[0]
                dspath = m[1]
            
                # === put variable in gdata to data value ===
                if (method == 'map'):
                    value = data_map_field(dspath, gdata)
                    fields[k] = value

                # === put file content to data value ===
                elif (method == 'file'):
                    file = data_map_field(dspath, gdata)
                    value = ''
                    with open(file, 'r+') as fh:
                        for line in fh:
                            value += line
                    fields[k] = value

                # === put stored value (most of time is _id assigned by mongodb) to data value ===
                elif (method == 'self'):
                    value = data_map_field(dspath, store_data)
                    p = dspath.split('::')
                    fields[k] = value

                # === mapping list of features ===
                # the list corresponding to an file with specific format, such as gff, fasta, xml or tab
                # the file will be processed then the feature will be load to list
                elif (method == 'list'):
                    pass
                else:
                    print('[ERR]method: %s of field %s' % (method, k))
                    error = 1


'''
map_data_parse_list --- create document using list value in item and structure of fields
'''
def map_data_parse_list(fields, item, document):

    # document is blank dict before the first round of mapping   
    for k in fields:

        if (isinstance(fields[k], dict)):
            document[k] = {}
            map_data_parse_list(fields[k], item, document[k])
        elif(isinstance(fields[k], list)):
            document[k] = []
            map_data_parse_list(fields[k], item, document[k])
        elif (isinstance(fields[k], str)):
            if (fields[k][0:7] == 'list:::'):
                document[k] = data_map_field(fields[k][7:], item)
            else:
                document[k] = fields[k]
        else:
            document[k] = fields[k]

'''
map_data -- map variable and list(gdata), document(store_data), document_id(mapid_data) according schema to generate document
'''
def map_data(schema, gdata, store_data, mapid_data):
    
    error = 0
    map_data_parse_fields(schema['fields'], gdata, store_data)

    # code for generating the list of documents
    list_label = 1 # no use, update it later
    if (list_label):
        if ('list_file' in schema):
            file = data_map_field(schema['list_file'], gdata)
            flist = file_to_list(file, mapid_data, feature_type=schema['feature_type'])

            # append attribute in other files to flist
            if ('other_files' in schema):
                for fkey, fpath in schema['other_files'].items():
                    fname = data_map_field(fpath, gdata)
                    fdict = file_to_list(fname, mapid_data)
                    nn = 0
                    for item in flist:
                        if item['name'] in fdict:
                            item[fkey] = fdict[item['name']]
                            nn = nn + 1
                        #print(item)
                        #sys.exit()
                    print('%d attributes from %s are append to %s' % (nn, fname, schema['feature_type']))
                #sys.exit()

            ''' mapping the content in flist according to the structure of schema[fields] '''
            dlist = [] # create the blank list of documents
            for item in flist:

                ''' create document according to item(content) and fields(structure) '''
                document = {}
                map_data_parse_list(schema['fields'], item, document)
                dlist.append(document)

                ''' mapping the previous stored info to current document '''
                '''
                if ('mapping' in schema):
                    for mi in schema['mapping']:
                        path = mi['mapping_dec']
                        ps = path.split('::')

                        mi_key = data_map_field(path, item)
                        mi_value = mapid_data[mi['mapping_src']][mi_key]
                        
                        item_doc = Document(item)
                        item_doc.update(ps, mi_value)
                        item = item_doc.doc
                '''

                ''' code for debug and check the mapping result '''
                '''
                if (schema['type'] == 'gene'):
                    print('--item--')
                    pprint.pprint(item)
                    print('--schema--')
                    pprint.pprint(schema['fields'])
                    print('--document--')
                    pprint.pprint(document)
                    sys.exit()
                '''

            schema['fields'] = dlist

    if (error):
        sys.exit()

def data_map_field(dspath, gdata):
    p = dspath.split('::')
    temp = copy.deepcopy(gdata)
    for v in p:
        if (isinstance(temp, dict)):
            if (v in temp):
                temp = temp[v]
            else:
                print('[ERR] %s in path: %s' % (v, dspath))
                print(temp)
                sys.exit()
        elif (isinstance(temp, list)):
            temp = temp[int(v)-1]

    return(temp)

'''
generate_query -- generate query dict for searching the collection
'''
def generate_query(data, query_keys):
    
    query = {}

    if (isinstance(data,dict)):
        for search_key in data:
            if search_key in query_keys:
                if (isinstance(query_keys[search_key], int)):
                    query[search_key] = data[search_key]
                else:
                    query[search_key] = generate_query(data[search_key], query_keys[search_key])
    elif (isinstance(data, list)):
        query = generate_query(data[0], query_keys)
    else:
        pass

    return(query)

'''
convert_nest_query --- convert nest query from dict format to mongdb format: eg
input  : {a: { b : { c: value } } } 
output : {a.b.c : value }
'''
def convert_nest_query(query, query_format, char):

    for k, v in query.items():
        newkey = k
        if (char):
            newkey = char + '.' + newkey
            
        if ( isinstance(v, dict)):
            convert_nest_query(v, query_format, newkey)
        elif ( isinstance(v, list)):
            pass
            ''' the query usually not have list '''
        else:
            query_format[newkey] = v

'''
sort_list --- sort list with nested dict
'''
#def sort_list()


'''
compare_list --- compare two list dataset
'''
#def compare_list(list1, list2):



'''
insert_update -- insert/update mapped data to database 
'''
def insert_update(db_name, collection_name, data, query_keys):

    collection = db_name[collection_name]
    
    if (isinstance(data, dict)):
        ''' generate query data base on search keys, then find the document '''
        query = generate_query(data, query_keys)
        query_format = {}
        convert_nest_query(query, query_format, '')
        old_data = collection.find_one(query_format)

        if (old_data):
            _id = old_data['_id']
            del old_data['_id']

            ''' old data is same as new data, pass '''
            if (old_data == data):
                data['_id'] = _id
                return 1

            ''' update method: replace '''
            collection.update_one(query_format, { "$set": data } )
            print("[INFO]replace single: %s" % str(data))

            ''' update method: append '''
            # print("[INFO]append single: %s" % str(data))

            ''' add _id to document '''
            data['_id'] = _id
            
        else:
            _id = collection.insert_one(data)
            # add _id to document
            data['_id'] = _id
            print("[INFO]Insert single: %s" % str(data))

    elif (isinstance(data, list)):
        ''' generate query data base on search keys, then find the document '''
        query = generate_query(data, query_keys)
        query_format = {}
        convert_nest_query(query, query_format, '')

        ''' compare the old_data with data '''
        old_data = []
        result = collection.find(query_format)
        for item in result:
            old_data.append(item)
        
        if (len(old_data)):

            ''' convert feature list to dict using feature name as key. For single organism, the feature name is unique '''
            old_dict = {}
            for odata in old_data:
                old_dict[odata['name']] = odata
            new_dict = {}
            for ndata in data:
                new_dict[ndata['name']] = ndata

            data_with_id = []

            num_rep = 0
            num_del = 0
            num_ins = 0
            num_sam = 0

            for name in old_dict:
                odoc = old_dict[name]
                doc_id = odoc['_id']

                if name in new_dict:
                    ''' 
                    the old and new doc have same name: 
                    1. keep the old if the content of doc are same
                    2. replace the old with new doc if content are diff 
                    '''
                    ndoc = new_dict[name]
                    ndoc['_id'] = doc_id
                    data_with_id.append(ndoc)

                    if (odoc == ndoc):
                        ''' 1. delete new doc in dict if same as old '''
                        num_sam = num_sam + 1
                    else:
                        ''' 2. replace old doc with new doc '''
                        collection.find_one_and_replace( {'_id': doc_id }, ndoc)
                        num_rep = num_rep + 1
                    del new_dict[name]
                else:
                    ''' delete old document if not exist in new '''
                    collection.delete_one( {'_id': doc_id } )
                    num_del = num_del + 1

            ''' insert the new data in list '''
            for name in new_dict:
                ndoc = new_dict[name]
                _id = collection.insert_one(ndoc)
                ndoc['_id'] = _id
                data_with_id.append(ndoc)
                num_ins = num_ins + 1

            ''' report the update(replace) info '''
            print("[INFO]%s -- Same: %d; Replace: %d; Insert: %d; Delete: %d." % (collection_name, num_sam, num_rep, num_ins, num_del))
        else:
            ''' insert data list'''
            _id = collection.insert(data)
            for i in range(len(data)):
                data[i]['_id'] = _id[i]
                # print(data[i]['name'],_id[i])
            print("[INFO]Insert %d documents" % len(data))
    else:
        pass

'''
noschema_insert -- insert/update dataset to mongodb according to noschema schema
'''
def noschema_insert(tdb, data_yaml, schema_folder):
    
    # === parse data.yaml ===
    with open(data_yaml) as fd:
        gdata = yaml.load(fd)
        # print(gdata)

    # file_type = {}
    # search_data(gdata, file_type)
    # print(file_type)

    # === kentnf: insert transaction start code here ===
    # with client.start_session() as s:
    #   s.start_transaction()
    #    collection_one.insert_one(doc_one, session=s)
    #    collection_two.insert_one(doc_two, session=s)
    #   s.commit_transaction()

    '''
    === process schema ====
    1. load schema for each type of content
    2. map data to schema 
    3. insert/update data to database according to the schema
    ''' 
    store_data = {}
    mapid_data = {}

    # all schemas locate in schema folder are loading to dict, the key is the order of schema
    # next, the schemas are sorted and processed by it's order 
    schemas = load_schema(schema_folder)
    schema_order = sorted(schemas)

    for so in schema_order:

        # get schema by it's order
        schema = schemas[so]
        schema_keys = format_schema(schema['fields'])        

        # map the datasets defined in gdata to the schema
        # the data need to insert to database are mapping to the 'fields' of schema
        map_data(schema, gdata, store_data, mapid_data)

        # exit the program if the mapping process can not get mapping data from gdata
        if (not schema['fields']):
            sys.exit("[ERR]can not retrieve info for %s" % schema['collection'])

        # === kentnf: build check schema ===
        # check schema is used to check dupliate document store in database, 
        # if not duplicate, the dataset will be insert to database
        # otherwise, the datasets will be update
        #    so, the check schema is subset of schema, need to be defined later

        # insert the mapping data to mongodb
        insert_update(tdb, schema['collection'], schema['fields'], schema_keys)

        #if (schema['type'] == 'gene'):
        #    sys.exit()

        # After insert, the schema['fields'] will contain objectID for each doc, that ID will be 
        # used in other document for creating relationshp. Because the schema will be updated in 
        # next loop. So, all the inserted document will be stored in store_data  
        store_data[schema['type']] = schema['fields']

        # create mapping dict using mapping_key for create relationship between documents
        if ('mapping_key' in schema):
            if (not isinstance(schema['fields'], list)):
                print(schema['fields'])
                print('[ERR] the data is not stored as list %s' % schema['type'])
                sys.exit()

            mapid_data[schema['type']] = {}
            for i in range(len(schema['fields'])):
                # pprint.pprint(schema['fields'][i])
                k = schema['fields'][i][schema['mapping_key']]
                v = schema['fields'][i]['_id']
                mapid_data[schema['type']][k] = v

        # code for exit the loop and debug
        # print(store_data[schema['type']])
        if (schema['type'] == 'mRNA'):
           sys.exit()

    
    '''

    # create search index for features 
    print('Start build search index')
    es = Elasticsearch()

    for i in range(len(feature_raw)):
    	feature_doc = feature_raw[i]
    	fid = _id[i]
    	res = es.index(index="feature", doc_type='mRNA', id=fid, body=feature_doc)
    	#print(res['result'])
    	#res = es.get(index="test-index", doc_type='tweet', id=1)
    	#print(res['_source'])
    	#es.indices.refresh(index="test-index")
    	#res = es.search(index="test-index", body={"query": {"match_all": {}}})
    	#print("Got %d Hits:" % res['hits']['total'])
    	#for hit in res['hits']['hits']:
    	  #print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
    	#print(fid)
    	#print(feature_doc)
    	#break

    #es.indices.refresh(index="feature")
    print(time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) ))
    '''

'''
noschema_delete -- delete dataset from database
'''
def noschema_delete(tdb):
	print("111")


'''
usage -- print usage information
'''
def usage():
    print ("USAGE: %s data.yaml" % (sys.argv[0]))
    sys.exit()


if __name__ == '__main__':

    '''set default parameters'''
    db_ip = '127.0.0.1'
    db_port = 27017
    db_name = 'noshcema'
    mode = 'i'

    data_yaml = 'gdata.yaml'
    schema_folder = 'schema'
    
    try:
        options,args = getopt.getopt(sys.argv[1:],"hp:i:m:d:y:s:", ["help","ip=","port=", "mode=", "database=", "yaml=", "schema="])
    except getopt.GetoptError:
        sys.exit()

    ''' check required parameter '''
    for name,value in options:
        if name in ("-h","--help"):
            usage()
        if name in ("-i","--ip"):
            db_op = value
        if name in ("-p","--port"):
            db_port = value
        if name in ('-m', "--mode"):
            mode = value
        if name in ('-d', "--database"):
            db_name = value
        if name in ('-y', "--yaml"):
            data_yaml = value
        if name in ('-s', "--schema"):
            schema_folder = value

    ''' connect to database '''
    connection = pymongo.MongoClient(db_ip, db_port, maxPoolSize=50)
    tdb = connection[db_name]

    '''manage the database according to the mode'''
    if (mode == 'i'):
        noschema_insert(tdb, data_yaml, schema_folder)
    elif (mode == 'd'):
    	dtype = 'organism'
    	dname = 'feature'
        # noschema_delete(tdb, dtype, dname)
        # delete by organism name/id
        # delete by analysis name/id
            # delete by assembly/annotation
            # delete by func annotation analysis id
    else:
        print("[ERR]Mode: %s" % mode)
        sys.exit()

    tdb.logout()