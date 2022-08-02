##########################
##### IMPORT MODULES #####
##########################
# import python modules
import os
import json
import re

import numpy as np



#########################
####### FUNCTIONS #######
#########################
def count_ipynb_fldict(folder):
    """Takes a folder name that is stored within the same directory as this file
    and counts the amount of ipynb files for all the folders that are in the
    given folder. Also returns a dictionary with the filename as key and
    location as value.
    """
    path = os.getcwd()+'\\'+folder
    try:
        dir_list = os.listdir(path)
    except Exception as e:
        print("The '{}' folder doesn't exist (yet)".format(folder))
        return 0,{}

    repo_ipynb_dict = {}
    file_location_dict= {}

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".ipynb"):
                splitted_root = root.split('\\')
                index_folder = splitted_root.index(folder)
                index_repo = index_folder + 1
                repo = splitted_root[index_repo]
                if not repo in repo_ipynb_dict:
                    repo_ipynb_dict[repo] = 1
                else:
                    repo_ipynb_dict[repo] += 1
                location = os.path.join(root,file)
                file_location_dict[file] = location
                # what about duplicate filenames (not from same repo)?
    return repo_ipynb_dict,file_location_dict


def code_output(cell,temp_dict):
    """Takes an ipynb cell and returns the dict with new keys/values for the
    'output_type' and 'output'. The structure of the cell depends on the
    output_type, therefore this extensive 'if-else' decisison tree.
    """
    if cell['outputs']==[]:
        temp_dict['output_type'] = 'no_output'
        temp_dict['output'] = 'no_output'
    else:
        if type(cell['outputs']) is list and len(cell['outputs'])>2:
            # print(len(cell['outputs']),temp_dict['location'],
            # temp_dict['file_cell'],cell['outputs'])
            pass
        output_type = cell['outputs'][0]['output_type']
        temp_dict['output_type'] = output_type

        if output_type == 'stream':
            temp_dict['output'] = cell['outputs'][0]['text']

        elif output_type == 'error':
            temp_dict['output'] = cell['outputs'][0]['traceback']

        elif temp_dict['output_type'] == 'display_data':
            temp_dict['output'] = 'displayed data'

        elif temp_dict['output_type'] == 'pyout': # this is 'old' execute cell
            temp_dict['output'] = 'pyout'
            #temp_dict['output'] = cell['outputs'][0]['html']

        elif 'data' in cell['outputs'][0]: # this is an display or execute cell
            temp_dict['output'] = list(cell['outputs'][0]['data'].values())

        elif 'text' in cell['outputs'][0]: # this is an stream cell
            temp_dict['output'] = cell['outputs'][0]['text']

        elif 'ename' in cell['outputs'][0]: # this is an error cell
            ename = cell['outputs'][0]['ename'] # Exception name, as a string
            evalue = cell['outputs'][0]['evalue'] # Exception value,as a string
            temp_dict['output'] = ename + evalue
        else:
            temp_dict['output'] = 'unknown'
            # print(temp_dict['location'],temp_dict['file_cell'],cell)

    return temp_dict


def decompose_folder_name(folder_name):
    """Takes a folder name and decomposes it and returns an username and
    repository.
    """
    r1 = re.compile("([a-zA-Z0-9_-]+)")
    decompose = r1.findall(folder_name)
    user,repo = decompose[0],decompose[1]
    return user,repo


def rec_to_actions(df,es_index):
    """Lorem ipsum """
    for record in df.to_dict(orient="records"):
        yield ('{ "index" : { "_index" : "%s" }}'% (es_index))
        yield (json.dumps(record, default=int))
# old yield in which es_type was needed
# yield ('{ "index" : { "_index" : "%s", "_type" : "%s" }}'% (es_index, es_type))
# rec_to_actions(chuck,index,type) > leave 'type' out
# ElasticSearch: Specifying types in bulk requests is deprecated


def new_rec_to_actions(df,es_index):
    """New version of rec_to_actions as the old version """
    actions = [
      {
        "_index": es_index,
        "_id": i,
        "_source": row
      }
      for i,row in enumerate(df.to_dict(orient="records"))
    ]
    return actions


def index_marks(nrows, chunk_size):
    """Lorem ipsum"""
    return range(1 * chunk_size,
            (nrows // chunk_size + 1) * chunk_size,
            chunk_size)


def split(dfm, chunk_size):
    """Lorem ipsum. """
    indices = index_marks(dfm.shape[0], chunk_size)
    return np.split(dfm, indices)



####################
##### RUN CODE #####
####################
print("IMPORTED LOCAL_ES.PY")

# fldict = count_ipynb_fldict('repos_sample')[1]
# # print(fldict)
