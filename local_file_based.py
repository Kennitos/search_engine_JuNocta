##########################
##### IMPORT MODULES #####
##########################
# import python files in this directory
import local_es

# import python modules
import json
import tqdm
import pandas as pd
import os
import datetime

from elasticsearch import helpers



#########################
####### FUNCTIONS #######
#########################
def code_output_custom(cell):
    """Similar to the function code_output(). However this functions takes an
    ipynb cell and returns two strings instead of a dict with keys/values for the
    'output_type' and 'output'. The first strings represents the output and
    the second strings represents the output_type.
    """
    if cell['outputs']!=[]:
        output_type = cell['outputs'][0]['output_type']
        if output_type == 'stream':
            return str(cell['outputs'][0]['text']),output_type

        elif output_type == 'error':
            return str(cell['outputs'][0]['traceback']),output_type

        elif output_type == 'display_data':
            return 'displayed data',output_type

        elif output_type == 'execute_result':
            return 'displayed data',output_type

        elif 'data' in cell['outputs'][0].keys():
            return str(list(cell['outputs'][0]['data'].values())),output_type

        elif 'text' in cell['outputs'][0].keys():
            return str(cell['outputs'][0]['text']),output_type

        elif 'ename' in cell['outputs'][0].keys():
            return str(cell['outputs'][0]['ename']+cell['outputs'][0]['evalue']),output_type
    else:
#         return '',''
        return 'no_output','no_output'


def read_ipynb_file(file_id,file_dict,file,folder,location,repo,user):
    """Takes in a jupyter notebook file and looks at it at cell level. Returns
    the existing dictionary with the added files and their attributes:
    file, nbformat, folder, user, repo, location, string, cell_type,
    code_cells, code_lines, markdown_cells, markdown_lines
    """
#     file_dict = {} # gets created in the function 'create_SE_from_folder'
    temp_dict = {}
    temp_dict['cell_types'] = {}
    temp_dict['output_types'] = {}
    # cell_types/output_types used to be list,
    # but changed to dict to use json_normalize in a later stage.

    with open(location,encoding="utf8") as notebook:
        data = json.load(notebook)
        nbformat = data['nbformat']
        file_text = ""
        file_lines = 0

        code_lines = 0
        markdown_lines = 0

        code_cells = 0
        markdown_cells= 0

        # current nbformat
        if nbformat == 4:
            data_cells =  data['cells']
        # old nbformat (older files)
        elif nbformat == 3:
            data_cells =  data['worksheets'][0]['cells']
        # older nbformat, minimal differences with nbformat 3 at json level
        elif nbformat == 2:
            data_cells =  data['worksheets'][0]['cells']
        else:
            print(nbformat,file)

        for cell in data_cells:
            cell_type = cell['cell_type']
            #cell['source'] doesn't exist in nbformat 3/2, use cell['input']
            if cell_type == 'code' and (nbformat == 3 or nbformat == 2):
                text = cell['input']
            else:
                text = cell['source']
            #remove the '\n' at the end of each string in the list
            clean_cell = list(map(lambda s: s.strip(), text))
            lines = len(clean_cell)
            single_string = ' '.join(clean_cell)
            file_text += single_string
            file_lines += lines

            # CELL TYPE
            if cell_type == 'code':
                # output, output_type = local_es.code_output(cell,{}).values()
                output, output_type = code_output_custom(cell)
                file_text += output
                code_lines += lines
                code_cells += 1
                if output_type not in temp_dict['output_types'].keys():
                    temp_dict['output_types'][output_type] = 1
            if cell_type == 'markdown':
                markdown_lines += lines
                markdown_cells += 1
            if cell_type not in temp_dict['cell_types'].keys():
                temp_dict['cell_types'][cell_type] = 1

        temp_dict['file'] = file
        temp_dict['nbformat'] = data['nbformat']
        temp_dict['folder'] = folder
        temp_dict['repo'] =  repo
        temp_dict['user'] = user
        temp_dict['location'] = location
        temp_dict['string'] = file_text
        temp_dict['lines'] = file_lines
        temp_dict['code_cells'] = code_cells
        temp_dict['code_lines'] = code_lines
        temp_dict['markdown_cells'] = markdown_cells
        temp_dict['markdown_lines'] = markdown_lines
        file_dict[file_id] = temp_dict

    return file_dict


def create_file_ES_from_folder(es,folder,file_id,fl_dict,es_index):
    """Inserting the data into ElasticSearch. This starts with creating a
    file_dict that contains all the files as keys and their attributes as
    values. Followed by running the function read_ipynb_file() to create a dict
    with the all the files as keys and their content attributes as values.
    Followed by creating a DataFrame of this dict, after which this df is saved
    to csv file in case problems with es might occur. At last the df is
    inserting into elasticsearch.
    """
    cwd = os.getcwd()
    path = cwd+'\\'+folder
    file_dict = {} #create dict for all 'ipynb' files
    file_id = 0

    fail_count = 0
    failed_files = ""

    print("Looping through all ipynb files within the path ({}) directory..."
            .format(path))
    for file in fl_dict:
        location = fl_dict[file]
        # example location:
        # 'C:\\Users\\kenne\\Documents\\test_thesis\\dataset_2\\..
        # ..(herrfz)dataanalysis\\week1\\simulation.ipynb'
        folder_name = location.split(folder)[1].split('\\')[1]
        user,repo = local_es.decompose_folder_name(folder_name)

        try:
            file_dict = read_ipynb_file(file_id,file_dict,file,folder_name,location,repo,user)
        except Exception as e:
            # print("failed for file:",file)
            print(e)
            fail_count += 1
            failed_files += file
        file_id += 1

    print('Failed files: {}/{}'.format(fail_count,len(fl_dict)))
    print('Files: {}'.format(failed_files))

    # CREATE DATAFRAME FROM DICT
    file_df = pd.DataFrame.from_dict(file_dict,orient='index')
#     file_df = file_df.fillna('empty').reset_index()
    file_df_extra = pd.concat([file_df.drop(['cell_types','output_types'], axis=1),
                            pd.json_normalize(file_df['cell_types']),
                            pd.json_normalize(file_df['output_types'])],
                           axis=1).fillna(0)#.drop([""],axis=1)

    # save df to csv (in case problems with es)
    file_df_extra.to_csv('file_df.csv')
    # save df to csv (in case problems with es)
    ct = str(datetime.datetime.now()).replace(' ','_').replace(':','-')
    file_df_time = "file_df_extra{}.csv".format(ct)
    file_df_extra.to_csv(file_df_time)

    # PUT DATAFRAME INTO ELASTIC SEARCH
    split_size = 500
    for chuck in tqdm.tqdm(local_es.split(file_df_extra, split_size)):
        try:
#             r = es.bulk(local_es.rec_to_actions(chuck,es_index))
            helpers.bulk(es,local_es.new_rec_to_actions(chuck,es_index))
        except:
            print('mini_split')
            try:
                for mini_chuck in tqdm.tqdm(local_es.split(chuck, int(split_size/10))):
#                     r = es.bulk(local_es.rec_to_actions(mini_chuck,es_index))
                    helpers.bulk(es,local_es.new_rec_to_actions(mini_chuck,es_index))
            except Exception as e:
                print('failed, skip this df',e)
    return es,file_df_extra



####################
##### RUN CODE #####
####################
print("IMPORTED LOCAL_FILE_BASED.PY")
