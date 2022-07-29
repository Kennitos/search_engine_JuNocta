##########################
##### IMPORT MODULES #####
##########################
# import python modules
import subprocess
import sys
import os



#########################
####### FUNCTIONS #######
#########################
def install(package):
    """Pip install a single module/package. Pip install modules to avoid
    'ModuleNotFoundError: No module found named ...'.
     """
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def install_list(package_list):
    """Pip install the packages in the package_list, which is a list of strings.
    This is an improved version of the install() function as it takes in a list
    opposed to a single package. Pip install module to avoid
    'ModuleNotFoundError: No module found named ...'.
    """
    for package in package_list:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            print(e)



####################
##### RUN CODE #####
####################
p_list = ["pandas",
            "elasticsearch",
            "bs4",
            "tqdm",
            "requests",
            "gitpython",
            "tk_html_widgets",
            "gitpython",
            "git"]
            # "git" wont solve problemm, gitpython will!

install_list(p_list)
# maybe pipinstall these modules
# install("platform")
# platform can be used to acces the underlying platfarm's data such as,
# hardware, operating system, and interpreter version information
# > can be used to find out whether it Windows or Mac

print("IMPORTED MODULES_SETUP.PY")
