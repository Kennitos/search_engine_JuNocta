##########################
##### IMPORT MODULES #####
##########################
# import python modules
import re
import os

from bs4 import BeautifulSoup



#########################
####### FUNCTIONS #######
#########################
def markdown_ref(text):
    """Remove markdowns hrefs from a string, returns the actual text and
    not the url.
    """
    refs = re.findall('\[(.*?)\]\((.*?)\)', text)
    # get match the same as [reference](url or # within page)
    for ref in refs: # small chance of multiple in a single text
        to_replace = '['+ref[0]+']'+'('+ref[1]+')' # lorem ipsum [`ref0`](`ref1`) dolor sit amet
        text = text.replace(to_replace,ref[0])
    return text


def create_ref(input_str):
    """Create a highlighted reference that works in Google Chrome, takes a
    hightlghted snippet as input and transforms that string.
    """
    if type(input_str) is list: # get the longest string from the list of strings, this works better with highlighting
        longest = max(input_str, key=len)
    else:
        longest = input_str
    if longest.startswith('#'):
        longest = longest.replace('#','').lstrip()
        # use lstrip instead of strip (only want to strip in front of string)
    longest = BeautifulSoup(longest, "html.parser").text
    # remove possible html tags, to avoid contradictory tags in display_results()
    # "BeautifulSoup(longest,"lxml") causes problems on other pc's"
    longest = longest.lstrip('-').lstrip()
    longest = markdown_ref(longest)
    start = '#:~:text='
    end = longest.replace('`','').replace(' ','%20')
    # remove html encoding for ` character (used like this ``variable``)
    # add html encoding for whitespaces between words
    output = start+end
    return output


def path_to_githuburl(path):
    """Takes location/path as input and transform this path to two github urls.
    The first url contains whitespace and will be used to display in the SERP,
    the second url does not contain whitespaces as they are removed and replaced
    by '%20' this will be used when a user actually clicks on a link in the
    SERP.
    """
    a = path.replace('\\','/') # replace backwards with forward slash
    b = a.split('(')           # split pc and file
    c = b[1].split(')')        # split user and repo
    d = c[1].split('/')        # split repo and notebook
    # c[0] = user
    # d[0] = repo
    # d[1:] = folders_file
    # d[-1] = file
    github_url = "https://github.com/"+c[0]+"/"+d[0]+"/blob/master/"+"/".join(d[1:])
    github_url_nw = github_url.replace(' ','%20')
    if len(github_url) > 100:
        github_url = "..."+github_url[-100:]
    return github_url,github_url_nw


def user_repo_href(user,repo):
    """Takes the user and repo as string inputs and returns two new strings
    that contain <a href> tags refering to the github page of the user or
    github page of the repo.
    """
    user_href = 'user: <a href="http://github.com/{0}" target="_blank">{0}</a>'.format(user)
    path = user+"/"+repo
    repo_href = 'repo: <a href="http://github.com/{}" target="_blank">{}</a>'.format(path,repo)
    return user_href,repo_href


def create_localhost_link(path):
    """Takes a location/path as input and returns three strings. It determines the 
    folder in which create_link.py resides and uses that to split the 
    given path. The localhost_path string is directory tree with the
    current_folder as its base. The localhost_path_nw is the almost the 
    same string, except whitespaces are replaced by '%20' as they will 
    indicate whitespaces. The local_url string is created to be used as 
    the actual link the user will click on in the search engine.
    """
    current_folder = os.getcwd().split('\\')[-1:][0] 
    localhost_path = path.split(current_folder)[1]
    localhost_path_nw = localhost_path.replace(' ','%20') # replace whitespaces
    
    local_url = ('<a href= http://localhost:8888/notebooks{} '
    'target="_blank">{}</a>'.format(localhost_path_nw,localhost_path))

    return localhost_path,localhost_path_nw,local_url



####################
##### RUN CODE #####
####################
print("IMPORTED CREATE_LINK.PY")
