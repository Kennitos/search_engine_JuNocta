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
def read_ipynb_cell(cell_id,cell_dict,file,folder,location,repo,user):
    """Takes in a jupyter notebook file and looks at it at cell level. Returns
    the existing dictionary with the added cells and their attributes:
    file_cell, file, nbformat, folder, user, repo, location, string.
    """
    with open(location,encoding="utf8") as notebook:
        try:
            data = json.load(notebook) # check if file has correct json format
        except Exception as e:
            print(e,file)
            return cell_id,cell_dict

        file_cell = 0
        nbformat = data['nbformat']
        if nbformat == 4:       # current nbformat
            data_cells =  data['cells']
        elif nbformat == 3:     # old nbformat
            data_cells = data['worksheets'][0]['cells']
        elif nbformat == 2:     # even older format
            data_cells = data['worksheets'][0]['cells']

        for i,cell in enumerate(data_cells):
            temp_dict = {}
            if cell['cell_type'] == 'code' and (nbformat == 3 or nbformat == 2):
                # cell['source'] doesn't exist within this condition,
                # use cell['input']
                text = cell['input']
            else:
                text = cell['source']
            clean_cell = list(map(lambda s: s.strip(), text))
            # remove the '\n' at the end of each string in the list with .strip
            single_string = ' '.join(clean_cell)
            lines = len(clean_cell)

            temp_dict['file_cell'] = i
            temp_dict['file'] = file
            temp_dict['nbformat'] = data['nbformat']
            temp_dict['folder'] = folder
            temp_dict['user'] = user
            temp_dict['repo'] =  repo
            temp_dict['location'] = location
            temp_dict['string'] = clean_cell
            #temp_dict['char'] = single_string
            temp_dict['lines'] = lines
            temp_dict['cell_type'] = cell['cell_type']
            if cell['cell_type'] == 'code':
                temp_dict = local_es.code_output(cell,temp_dict)

            cell_dict[cell_id] = temp_dict
            cell_id += 1
            file_cell += 1

    return cell_id,cell_dict


def cells_to_dict(file_dict):
    """Takes a dict of all the files and loop through the files, each iteration
    running the function read_ipynb_cell(). It will return a dict of all the
    cells and their attributes.
    """
    cell_id = 0     # enumerate not an option
    cell_dict = {}

    fail_count = 0
    failed_files = ""

    for file in file_dict:
        file_name = file_dict[file]['file']
        user = file_dict[file]['user']
        folder = file_dict[file]['folder']
        location = file_dict[file]['location']
        repo = file_dict[file]['repo']
        # kan ik dit niet in één regel schrijven,
        # ff controleren nog bijv a,b,c = dict.values()
        try:
            cell_id_dict = read_ipynb_cell(cell_id,cell_dict,file_name,
                                            folder,location,repo,user)
        except Exception as e:
            fail_count += 1
            failed_files += file
        cell_id = cell_id_dict[0]
        cell_dict = cell_id_dict[1]

    print('Failed files: {}/{}'.format(fail_count,len(file_dict)))
    print('Files: {}'.format(failed_files))

    return cell_id,cell_dict


def create_cell_ES_from_folder(es,folder,file_id,fl_dict,es_index):
    """Inserting the data into ElasticSearch. This starts with creating a
    file_dict that contains all the files as keys and their attributes as
    values. Followed by running the function cells_to_dict() to create a dict
    with the all the cells as keys and their content attributes as values.
    Followed by creating a DataFrame of this dict, after which this df is saved
    to csv file in case problems with es might occur. At last the df is
    inserting into elasticsearch.
    """
    cwd = os.getcwd()
    path = cwd+'\\'+folder
    file_dict = {}


    for file in fl_dict:
        location = fl_dict[file]
        # example location:
        # 'C:\\Users\\kenne\\Documents\\test_thesis\\repos_sample\\..
        # ..(herrfz)dataanalysis\\week1\\simulation.ipynb'
        folder_name = location.split(folder)[1].split('\\')[1]
        user,repo = local_es.decompose_folder_name(folder_name)
        temp_dict = {}
        temp_dict['file'] = file
        temp_dict['folder'] = location.split('\\')[-2]
        temp_dict['location'] = location
        temp_dict['user'] = user
        temp_dict['repo'] = repo

        file_dict[file_id] = temp_dict
        file_id += 1

    print("Looping through all ipynb files within the path ('{}') "
            "directory...".format(path))
    # create dict for all cells
    cell_dict = cells_to_dict(file_dict)[1]
    # create dataframe from dict
    cell_df = pd.DataFrame.from_dict(cell_dict,orient='index')
    cell_df.index = cell_df.index.set_names(['cell_id'])
    cell_df = cell_df.fillna('empty').reset_index()

    # save df to csv (in case problems with es)
    ct = str(datetime.datetime.now()).replace(' ','_').replace(':','-')
    cell_df_time = "cell_df_{}.csv".format(ct)
    cell_df.to_csv(cell_df_time)

    # put dataframe into elastic search local
    split_size = 1000
    index_in_chunk = 0
    for chuck in tqdm.tqdm(local_es.split(cell_df, split_size)):
        # r = es.bulk(rec_t o_actions(cell_df)) replaced with try/except
        try:
#             r = es.bulk(local_es.rec_to_actions(chuck,es_index))
            helpers.bulk(es,local_es.new_rec_to_actions(chuck,es_index,index_in_chunk))
            index_in_chunk += split_size
        except Exception as e:
            print("\nBulk failed at df cell_id: {}-{}"
                    .format(chuck.cell_id.iloc[0],chuck.cell_id.iloc[-1]))
            print(e)

    # return file_id,cell_df
    return es,file_id,cell_df



####################
##### RUN CODE #####
####################
print("IMPORTED LOCAL_CELL_BASED.PY")
