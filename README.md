<div id="top"></div>

# Jupyter Notebook cell-type aware search engine (JuNocta)

<!-- TABLE OF CONTENTS -->
<ol>
  <li>
    <a href="#about-the-project">About The Project</a>
    <ul>
      <li><a href="#built-with">Built With</a></li>
    </ul>
  </li>
  <li>
    <a href="#getting-started">Getting Started</a>
    <ul>
      <li><a href="#prerequisites">Prerequisites</a></li>
      <li><a href="#installation">Installation</a></li>
    </ul>
  </li>
  <li><a href="#usage">Usage</a></li>
  <li><a href="#roadmap">Roadmap</a></li>
  <li><a href="#contributing">Contributing</a></li>
  <li><a href="#license">License</a></li>
  <li><a href="#contact">Contact</a></li>
  <li><a href="#acknowledgments">Acknowledgments</a></li>
</ol>

<!-- ABOUT THE PROJECT -->
## About The Project
This search engine, called JuNocta, is designed to work with (large) datasets of Jupyter Notebooks. Jupyter Notebook is a web-based interactive platform, that provides the option to combine code snippets, computational output, explanatory text, visualations and multimedia. A notebook is divided into cells that are displayed below each other, where each cell can run separately. There exist 4 types of cells: `code`, `markdown`, `heading` and `raw`. Notebooks are saved in the JSON structure. This structure represents structured data in the form of attribute-value pairs (key-value pairs) and arrays. The two images below show the same notebook in its web-based platform and in its json structure.

This is how a notebook is displayed in its JSON structure:
![img](img/screenshot_notebook_webbased.jpg?raw=true "Image 1 - web-based")
<br/><i>Image 1</i>

This is how the same notebook is displayed on the web-based platform:
![img](img/screenshot_notebook_json.jpg?raw=true "Image 2 - json")
<br/><i>Image 2</i>

But how do you search for a specific notebook within a collection. If a collection of notebooks is stored offline, for example your own laptop, you could use the default file explorer on your operating system. In the file explorer it is possible to search for a filename. In windows 10 it is possible advanced options to search within the content of a file, however this is not 'toepasbaar' op Jupyter Notebook files. If a collection of notebooks is stored on online, for example GitHub, you could use the advanced search provided by GitHub. This does provide the option to search for a filename or within the content, but that is a far as it gets. Most of the advanced filters are related to GitHub characteristics, like amount of stars, repository name, file size or date. 

The solution to these limited search options, is to create our own search engine. JuNocta has a good understanding of the JSON sturcture when indexing the notebooks. It knows which key-value pairs can be of great value for the search engine and which pairs are abundant. It does not index the notebooks as a whole as text, but is aware of the different cell types. If we look at image 2, this means that not the notebook as a whole (line 1-53) gets indexed as text, but only certain key-value pairs are stored.  The following capabilities/functionalities of JuNocta are developed:
1. Filter on cell type (choosing between `markdown`, `code`, `raw` or `heading`)
2. Filter on code output type (choosing between `display_data`, `execute_result`, `stream`, etc.)
3. Split a query (using Boolean operators)
4. Match exact phrases (using double quotes)
5. Specifying fields (stating the field followed by a colon)
6. Search for a single cell or  whole file

Three datasets that differ in size and tidiness are used to test JuNocta:
1. Jake Vanderplas notebooks
     - These notebooks are regarding the two books written by Jake Vanderplas about Python. Jake Vanderplas has published those two entire books on GitHub in the form of Jupyter notebooks. 
     - 86 notebooks / 4.000 cells 
     - The notebooks must be downloaded **manually**, by cloning both [Python DataScience Handbook](https://github.com/jakevdp/PythonDataScienceHandbook) and [Python Whirlwind Tour](https://github.com/jakevdp/WhirlwindTourOfPython)

2. Gallery interesting notebooks (wiki page of Jupyter/Jupyter reposorityr)
     - [This GitHub wiki page](https://github.com/jupyter/jupyter/wiki) is a curated collection of links to Jupyter notebooks that are notable published on by Jupyter itself.
     - 3.000 notebooks / 100.000 cells
     - The notebooks will be downloaded **automatically**. The code will create a list containing links to GitHub repositories mentioned the wiki page, using webscraping after which they are cloned to your own laptop.
3. EECN notebooks
     - The Exploration and Explanation in Computational Notebooks (EECN) is a paper that has webscraped 1.25 million notebooks on GitHub and analyzed those notebooks. The collections of notebooks are split into six 6 zip files, I used "Notebooks files - part 1" for this search engine.
     - 200.000 notebooks / 5.000.000 cells
     - The notebooks must be downloaded **manually**, on [this page](https://library.ucsd.edu/dc/object/bb2733859v)
   


### Built With

* `bs4` / `BeautifoulSoup` for webscraping for github repositories
* `git` for cloning those repositories
* `pandas` for indexing those repositories by creating DataFrames
* `elasticsearch` for inserting those DataFrames into Elasticsearch
* `tktiner` for creating a SERP
* `tk_html_widgets` for creating clickable links in the SERP


<p align="right">(<a href="#top">back to top</a>)</p>

## Getting started


### prerequisites
* [Anaconda](https://www.anaconda.com/products/individual)
  * python+jupyter notebook installer
   * don't forget to add `python` to the path variables
* [Java](https://www.java.com/en/download/)
* [Elastic Search msi installer](https://www.elastic.co/guide/en/elasticsearch/reference/current/windows.html)
  * There are two options during the installation of elasticsearch, regarding starting elasticsearch
       1. always have elasticsearch running in the background
       2. only run elasticsearch after opening it as an admin (**I advise this option**)
* [git bash](https://git-scm.com/downloads):
     * don't forget to add `git` to the path variables, [extra information](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup) regarding installation
* manually install the "git" package in the Anaconda Navigator:
  1. In the Anaconda Navigator select the "Enviroments" tab in the left panel
  2. In the dropdown menu in the top panel change "Installed" to "All"
  3. Search for "git" in the "search packages" entry box
  4. Check the box for "git" and press "apply" in the bottom panel to install this package

### installation
#### Before running the main.py file
Before you can run the ```main.py``` file, two actions need to be performed:
1. Have the elasticsearch enviroment run in the background
2. Have the jupyter notebook enviroment run in the background
   * IT IS IMPORTANT to open jupyter notebook in the same directory in which this folder is cloned to. This is necessary as it not possible to determine 

There are two ways to navigate to the right directory:
1. Navigate in the file explorer to where this directory is cloned, when in the right directory type "cmd" in the address bar and press enter. This causes a command prompt to be opened in the right directory.
2. Navigate in the command promt manually to where this directory is cloned, by using the `cd` command. For example, if you want to go to the folder `search_engine`:
```
cd desktop/search_engine_junocta
```
After either of the 2 options is used to open the command promt in the right directory, open the jupyter notebook enviroment by using the following command:
```
jupyter notebook
```
![gif](img/navigate_option1.gif)

#### Running the main.py file
Now open a second command promt and navigate again to the right directory (by using either of the two options just described) and run the `main.py` file by using the following command:
```
python main.py
```

## Usage


After the user has run the `main.py` command, the user is met with an interactive shell in which 5 options presented:
1. Press (1) to run all the following options consecutively: (2), (3), (4)
2. Press (2) to clone the repositories,
3. Press (3) to setup elasticsearch,
4. Press (4) to open the search engine,
5. Press (q) to quit


![gif](img/example_startup.gif)

An important variable is `choose_dataset` on line 23 in the file `widget_new.py`


<p align="right">(<a href="#top">back to top</a>)</p>
