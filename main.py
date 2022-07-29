##########################
##### IMPORT MODULES #####
##########################
# import python modules
from elasticsearch import Elasticsearch
import os
import sys
import importlib

# import python files
import modules_setup # you can comment this line after ran once
import clone_repo
import local_es
import local_cell_based
import local_file_based



#####################
##### VARIABLES #####
#####################
HOST = 'http://localhost:9200/'
es_new = Elasticsearch(hosts=[HOST])
# url_old = "https://github.com/jupyter/jupyter/wiki/A-gallery-of-interesting-Jupyter-Notebooks"
url_new = "https://github.com/jupyter/jupyter/wiki"
folder_new = "repos"

choose_dataset = 2
folder_new = "dataset_{}".format(str(choose_dataset))
INDEX_CELL = "test_dataset{}_cell".format(str(choose_dataset))
INDEX_FILE = "test_dataset{}_file".format(str(choose_dataset))
TYPE = "record"

# test variables for demo
folder_new = "demo"
INDEX_CELL_TEST = "demo_cell"
INDEX_FILE_TEST = "demo_file"



#########################
####### FUNCTIONS #######
#########################
def create_folder(folder):
    """Create folder in which to put all the repositories (if it does not
    exist).
    """
    if not os.path.exists(folder):
        print("Created the folder: {}".format(folder))
        os.makedirs(folder)


def option_all(url,folder,es,es_index1,es_index2,es_type):
    """Run the functions: option_2(), option_3() and option_4(). """
    option_1(url,folder,es,es_index1,es_index2,es_type)
    option_2(url,folder,es,es_index1,es_index2,es_type)
    option_3(folder)


def option_1(url,folder,es,es_index1,es_index2,es_type):
    """Run the code in order to clone the repositories. """
    print("""Scraping...""")
    github_repositories = clone_repo.scrape_gallery(url)
    print("Scraped {} github repositories".format(len(github_repositories)))

    clone_repo.start_cloning(github_repositories,folder)

    # if cloning is aborted dont continue with option_2
    cwd = os.getcwd()
    path_d = cwd+'\\'+folder
    if len(os.listdir(path_d)) == 0:
        # check if folder is empty (not filled with cloned repos)
        what_to_do(url,folder,es,es_index1,es_index2,es_type)


def option_2(url,folder,es,es_index1,es_index2,es_type):
    """Run the code in order to setup elasticsearch. """
    print("\nSetting up elasticsearch...")
    repo_ipynb_dict,fldict = local_es.count_ipynb_fldict(folder)
    # print(repo_ipynb_dict)
    if fldict == {}:
        print("First clone the repositories, before setting up elastic "
            "search. Press (1)")
        return what_to_do(url,folder,es,es_index1,es_type)
    # gallery_es,file_id,gallery_df = local_es.create_SE_from_folder(es,folder,0,fldict,es_index,es_type)

    print("\n\nSetting up elasticsearch cell-based...")
    local_cell_based.create_cell_ES_from_folder(es,folder,0,fldict,es_index1)
    print("\n\nSetting up elasticsearch file-based...")
    local_file_based.create_file_ES_from_folder(es,folder,0,fldict,es_index2)
    print("Setup finished\n\n")
    # xx,yy,zz = local_cell_based.create_cell_ES_from_folder(es,folder,0,fldict,es_index1)
    # ab,cd = local_file_based.create_file_ES_from_folder(es,folder,0,fldict,es_index2)


def option_3(folder):
    """Run """
    modulename = "widget_new"
    if modulename in sys.modules:
        print("widget_new detected")
        importlib.reload(widget_new.py)
        # widget_new.reload(sys)
    else:
        import widget_new # startup the search Engine
    print("Application closed")


def what_to_do(url,folder,es,es_index1,es_index2,es_type):
    """Interact with the user in order to determine what to do. The options are
    to (1) lorem, (2) ipsum, (3) doler, (4) sit, (5) amet.
    """
    print("\nWhat would you like to do? First time running this code, try "
    "running all in order (1). Otherwise choose an other option.\n"
    "Press (1) to run all: (2), (3) and (4)\n"
    "Press (2) to clone the repositories,\n"
    "Press (3) to setup elasticsearch,\n"
    "Press (4) to open the search engine,\n"
    "Press (q) to quit")
    user_input_what1 = input()
    #try whether the user input can be transformed into an integer
    try:
        int_input = int(user_input_what1)
        #clone repo/setup es/start se
        if int_input == 1:
            option_all(url,folder,es,es_index1,es_index2,es_type)
            return what_to_do(url,folder,es,es_index1,es_index2,es_type)

        #only clone repo
        elif int_input == 2:
            option_1(url,folder,es,es_index1,es_index2,es_type)
            return what_to_do(url,folder,es,es_index1,es_index2,es_type)

        #only setup elasticsearch
        elif int_input == 3:
            option_2(url,folder,es,es_index1,es_index2,es_type)
            return what_to_do(url,folder,es,es_index1,es_index2,es_type)

        #only start search engine
        elif int_input == 4:
            option_3(folder)
            print("run what_to_do hierna")
            return what_to_do(url,folder,es,es_index1,es_index2,es_type)
    #except that the user input is an string
    except Exception as e:
        if user_input_what1 == "q" or user_input_what1 == "Q":
            print("working?")
            return
        print(e)
    print("Type a '1', '2', '3', '4' or 'q'\n")
    what_to_do(url,folder,es,es_index1,es_index2,es_type)



####################
##### RUN CODE #####
####################
# run demo
create_folder(folder_test)
what_to_do(url_new,folder_new,es_new,INDEX_CELL_TEST,INDEX_FILE_TEST,TYPE)

# # actual code
# create_folder(folder_new)
# what_to_do(url_new,folder_new,es_new,INDEX_CELL,INDEX_FILE,TYPE)



#################################################
##### curl commands for local elasticsearch #####
#################################################
# !curl -XDELETE "localhost:9200/ntest_cell"
# !curl -XDELETE "localhost:9200/ntest_file"
# !curl "http://localhost:9200/_cat/indices?v"
