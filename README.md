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
This search engine, called JuNocta, is designed to work with (large) datasets of Jupyter Notebooks. Jupyter Notebook is a web-based interactive platform, that provides the option to combine code snippets, computational output, explanatory text, visualations and multimedia. A notebook is divided into cells that are displayed below each other, where each cell can run separately. There exist 4 types of cells: `code`, `markdown`, `heading` and `raw`. Notebooks are saved in the JSON structure. This structure represents structured data in the form of attribute-value pairs (key-value pairs) and arrays. 

This is how a notebook is displayed in its JSON structure:
img

This is how a notebook is displayed on the web-based platform:
img

But how do you search for a specific notebook within a collection. If a collection of notebooks is stored offline, for example your own laptop, you could use the default file explorer on your operating system. In the file explorer it is possible to search for a filename. In windows 10 it is possible advanced options to search within the content of a file, however this is not 'toepasbaar' op Jupyter Notebook files. If a collection of notebooks is stored on online, for example GitHub, you could use the advanced search provided by GitHub. This does provide the option to search for a filename or within the content, but that is a far as it gets. Most of the advanced filters are related to GitHub characteristics, like amount of stars, repository name, file size or date. 

The solution to these limited search options, is to create our own search engine. JuNocta has a good understanding of the JSON sturcture when indexing the notebooks. It does not index the notebooks as a whole as text, but is aware of the different cell types. The following capabilities of JuNocta are developed:
1. Filter on cell type (choosing between `markdown`, `code`, `raw` or `heading`)
2. Filter on code output type (choosing between `display_data`, `execute_result`, `stream`, etc.)
3. Split a query (using Boolean operators)
4. Match exact phrases (using double quotes)
5. Specifying fields (stating the field followed by a colon)
6. Search for a cell of file (..)

Three datasets that differ in size and tidiness are used to test JuNocta:
1. Jake Vanderplas notebooks
     - summary one line
     - 86 notebooks / 4.000 cells 
     - [Python DataScience Handbook]() and [Python Whirlwind Tour]()
2. Gallery interesting notebooks (wiki page of Jupyter/Jupyter reposorityr)
     - summary one line
     - 3.000 notebooks / 100.000 cells
     - the notebooks mentioned on this [wiki page](https://github.com/jupyter/juypter/wiki) are collected into a list, using webscraping after which they are cloned to your own laptop.
     - 
3. Exploration and Explanation in Computational Notebooks Paper
     - summary one line
     - 200.000 notebooks / 5.000.000 cells
     - 


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
* [Anaconda](https://www.anaconda.com/products/individual): python+jupyter notebook installer
     * don't forget to add `python` to the path variables
* [Java](https://www.java.com/en/download/)
* [Elastic Search msi installer](https://www.elastic.co/guide/en/elasticsearch/reference/current/windows.html)
     * 2 options to install elasticsearch, regarding using elasticsearch
     1. always have elasticsearch running in the background
     2. only run elasticsearch after opening it as an admin
* [git bash](https://git-scm.com/downloads):
     * don't forget to add `git` to the path variables, [extra information](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup) regarding installation
* manually download the following package in the anaconda navigator:
Anaconda navigator / Enviroments / All / search "git" and install



### installation
Only two command must be run in the command promt, start with navigating to the right directory where this repository is cloned to. For exmpale `search_engine`
```
cd documents/search_engine
```
Now run the `main.py` file
```
main.py
```

## usage
After the user has run the `main.py` command, the user is met with an interactive shell in which 5 options presented:
1. Press (1) to run all the following options consecutively: (2), (3), (4)
2. Press (2) to clone the repositories,
3. Press (3) to setup elasticsearch,
4. Press (4) to open the search engine,
5. Press (q) to quit

An important variable is `choose_dataset` on line 23 in the file `widget_new.py`


<p align="right">(<a href="#top">back to top</a>)</p>
