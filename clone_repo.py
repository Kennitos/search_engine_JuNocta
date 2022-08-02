##########################
##### IMPORT MODULES #####
##########################
# import python modules
import requests
import re
import os
import json
import itertools
import tqdm
import datetime
import random

from bs4 import BeautifulSoup
from git import Repo    # add 'git' module through anaconda navigator +
# pip install gitpython



#########################
####### FUNCTIONS #######
#########################
def create_url(link_list,r_e,split_index):
    """Takes a list of link and cuts down each link to a valid url to a github
    repository url using regular expressions. Returns a list of new urls.
    """
    pre_string = 'https://github.com/'
    url_list = []
    for url in link_list:
        match = r_e.findall(url)
        if  match != []:
            url = pre_string + match[0][split_index:]
            url_list.append(url)
        if len(match) > 1:
            print(match)
    return url_list


def scrape_gallery(url):
    """Takes a url of a jupyter gallery page, and perform webscraping in order
    to return a list of unique url's of valid github repositories. It also
    print/returns a summary of the webscraping process.

    github pattern:
    user_name       - can exist out of letters,numbers and '-'
    repository_name - can exist out of letters,numbers and '_.-'

    regular expressions used:
    # r11   match all links the same as .....github.com/.../...$
    # r12   match all links the same as .....github/.../...$
    # r21   match all links the same as .....github.com/.../...+
    # r22   match all links the same as .....github/.../...+
    # r31   match all links the same as .....github.com/user/?$
    # r32   match all links the same as .....github/user/?$
    # rt_1  findall the links the same as github.com/.../...+
    # rt_2  findall the links the same as github/.../...+
    """
    r  = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data,features="html.parser")
    body = soup.find_all("div", {"class": "markdown-body"})[0]
    # using [0] since there is only 1 result of a div with class 'markdown-body'
    all_links_in_body = [link.get('href') for link in body.find_all('a')]
    unique_links_body = set(all_links_in_body)
    all_github_links = [link for link in unique_links_body if 'github' in link]

    total_list = []
    return_list = []

    # link to github repositories
    r11 = re.compile(".*github.com/[a-zA-Z0-9-]+/[a-zA-Z0-9_.-]+$")
    r12 = re.compile(".*github/[a-zA-Z0-9-]+/[a-zA-Z0-9_.-]+$")

    # link to files
    r21 = re.compile(".*github.com/[a-zA-Z0-9-]+/[a-zA-Z0-9_.-]+")
    r22 = re.compile(".*github/[a-zA-Z0-9-]+/[a-zA-Z0-9_.-]+")

    # link to github users
    r31 = re.compile(".*github.com/[a-zA-Z0-9_-]+/?$")
    r32 = re.compile(".*github/[a-zA-Z0-9_-]+/?$")
    #/? to include links that end with 'user/' instead of only 'user'

    # transform
    rt_1 = re.compile("github/[a-zA-Z0-9-]+/[a-zA-Z0-9_.-]+")
    rt_2 = re.compile("github.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+")

    # r1 - clean repo
    r11_list = list(filter(r11.match, all_github_links))
    r12_list = list(filter(r12.match, all_github_links))
    r12_trans_list = create_url(r12_list,rt_1,7)


    total_list.extend(r11_list)
    total_list.extend(r12_list)
    not_used = [link for link in all_github_links if link not in total_list]

    r21_list = list(filter(r21.match, not_used))
    r21_trans_list = create_url(r21_list,rt_2,11)
    r22_list = list(filter(r22.match, not_used))
    r22_trans_list = create_url(r22_list,rt_1,7)
    r31_list = list(filter(r31.match, not_used))
    # r32_list = list(filter(r32.match, not_used)) # will yield no matches

    total_list.extend(r21_list)
    total_list.extend(r22_list)
    total_list.extend(r31_list)
    not_used = [link for link in all_github_links if link not in total_list]
    used = len(r11_list)+len(r12_list)+len(r21_list)+len(r22_list)+len(r31_list)

    return_list.extend(r11_list)
    return_list.extend(r12_trans_list)
    return_list.extend(r21_trans_list)
    return_list.extend(r22_trans_list)
    return_list.sort()

    summary = """    [1] all links in body: {0}
    [2] all unique links in body: {1}
    [3] all github links in body: {2}\n
    [4] all clean github repos: {3}+{4} = {5}
    [4] all clean github users: {6}
    [4] all links to notebook files: {7}+{8} = {9}
    [4] all links with string 'github', but not used: {10}
    [4] {3} + {4} + {6} + {7} + {8} + {10} = {11}\n
    [4] {3} + {4} + {7} + {8} = {12}
    [4] all github links that are continued with [4]: {12}
    [5] when removing duplicates of those {12}, these remain: {13}
    """.format(len(all_links_in_body),len(unique_links_body),
    len(all_github_links),len(r11_list),len(r12_trans_list),
    len(r11_list)+len(r12_trans_list),len(r31_list),len(r21_trans_list),
    len(r22_trans_list),len(r21_trans_list)+len(r22_trans_list),len(not_used),
    used+len(not_used),len(return_list),len(set(return_list)))
    print(summary)
    return sorted(set(return_list))#,summary


def clone_repositories(repositories_list,folder_dir):
    """Takes a list of github repository url's and checks whether
    the repository is an repository or a blank page. If it is an actual
    repository, then it will be cloned. The repositories will be placed in the
    folder 'folder_dir'. If cloning will cause a problem, the reasons will be
    written in a text file.
    """
    f_dict = {}     # failed_dict
    s_dict = {}     # succes_dict (useful to check with duplicates)
    total = len(repositories_list)
    succes = 0

    cwd = os.getcwd()
    for url in tqdm.tqdm(list(repositories_list)):
        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data,features="html.parser")
        repo_name = "("+url.split('/')[3]+")"+url.split('/')[4]
        repo_dir = cwd+'\\'+folder_dir+'\\'+repo_name
        try:
            if 'Page not found · GitHub' in soup.title.string:
                f_dict[repo_name] = {'type': 'Page not found','url':url}
            else:
                if not os.path.exists(folder_dir+'/'+repo_name):
                    # skip already downloaded repo
                    try:
                        Repo.clone_from(url,repo_dir)
                        s_dict[repo_name] = {'path':repo_dir, 'url':url}
                        succes +=1
                    except Exception as e:
                        f_dict[repo_name] = {'type':'error: cloning failed',
                                                'message':e,
                                                'url':url}
                else:
                    f_dict[repo_name] = {'type':'duplicate',
                                            'url':url}#,
                                            #'duplicate':s_dict[repo_name]}

        except Exception as e:
            f_dict[repo_name] = {'type':'error','message':e,'url':url}

    count_pnf = len([k for k in f_dict if f_dict[k]['type'] == 'Page not found'])
    # count_error = len([k for k in f_dict if f_dict[k]['type'] == 'error'])
    count_error = len([k for k in f_dict if 'error' in f_dict[k]['type']])
    count_duplicate = len([k for k in f_dict if f_dict[k]['type'] == 'duplicate'])

    print("Cloning finished, summary:")
    print("Succesfull cloned repositories: {}/{}\n".format(succes,total))
    print("Repo's with Page not Found: {}".format(count_pnf))
    print("Repo's with error: {}".format(count_error))
    print("Repo's with duplicate: {}\n\n".format(count_duplicate))

    # save f_dict to text file
    ct = str(datetime.datetime.now()).replace(' ','_').replace(':','-')
    file_time = "failed_dict_{}.txt".format(ct)
    # ct = current time / create a unique name for the text file
    f = open(file_time, "w")
    # f = open("failed_dict.txt", "w")
    f.write("{\n")
    for k in f_dict.keys():
        f.write("'{}':'{}'\n".format(k, f_dict[k]))
    f.write("}")
    f.close()


def valid_check_samplesize(user_input,set_repositories,folder_dir):
    """Takes a sample size and checks if it is smaller than the size of the
    all the repositories. If this is true, clone [sample size] repositories,
    otherwise ask for a new sample size.
    """
    max_size = len(set_repositories)
    try:
        size = int(user_input)
        if max_size > size > 0:
            # print("Creating a error_list of 'Page not found' github "
            # "repositories url's... (approx 2 min)")
            # error_list = scan_page_not_found(set_repositories)
            print("Cloning sample size of",size)
            random_list = random.sample(set_repositories,size)
            clone_repositories(random_list,folder_dir)
            # clone_repositories(list(set_repositories)[:size],folder_dir)
        else:
            print("Choose within the delimiters of 0 and",max_size)
            print(),start_cloning(set_repositories,folder_dir)
    except Exception as e:
        print("Type a integer \n")
        start_cloning(set_repositories,folder_dir)


def start_cloning(set_repositories,folder_dir):
    """Interacts with the user via the shell, to determine the amount of
    folders to clone. This 'if-else' decisison tree is extensive to make it
    'idiot-proof'.
    """
    max_size = len(set_repositories)
    # print("A total of",max_size,"repositories have been found.")
    print("Clone all(y) or use a sample size(n)? Type (y) to clone all "
          "repos, type (n) to choose a sample size or type (q) to quit" )
    user_input1 = input()
    if user_input1 == "y":
        print("Are you sure to clone all {} repositories? Type (y) to confirm,"
              " type (n) to choose a sample size or type (q) to "
              "quit".format(max_size))
        user_input2 = input()
        if user_input2 == "y":
            print("Downloading all {} repositories..."
                  " (approx 40min/15gb)".format(max_size))
            clone_repositories(list(set_repositories),folder_dir)
        elif user_input2 == "q":
            print("Cloning aborted")
            return
        elif user_input2 == "n":
            print("Type the size of your sample size:")
            user_input3 = input()
            if user_input3 == "q":
                print("Cloning aborted")
                return
            valid_check_samplesize(user_input3,set_repositories,folder_dir)
        else:
            print("Type a 'y', 'n' or 'q'\n")
            start_cloning(set_repositories,folder_dir)

    elif user_input1 == "n":
        print("Type the size of your sample size:")
        user_input4 = input()
        if user_input4 == "q":
            print("Cloning aborted")
            return
        valid_check_samplesize(user_input4,set_repositories,folder_dir)

    elif user_input1 == "q":
        print("Cloning aborted")
        return

    else:
        print("Type a 'y', 'n' or 'q'\n")
        start_cloning(set_repositories,folder_dir)



####################
##### RUN CODE #####
####################
print("IMPORTED CLONE_REPO.PY")
