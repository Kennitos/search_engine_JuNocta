##########################
##### IMPORT MODULES #####
##########################
#import python files in this directory
import create_query
import create_link

# import python modules
import os
import tkinter as tk
import tk_html_widgets as tk_html
from elasticsearch import Elasticsearch





#####################
##### VARIABLES #####
#####################
HOST = 'http://localhost:9200/'
es = Elasticsearch(hosts=[HOST])
path = os.getcwd()
username_pc = path.split('\\')[2] # username_pc = 'kennet'
# username is always third item, like below:
# [drive][users]['username'][folder][folder][etc]

### IMPORTANT VARIABELE ###
choose_dataset = "demo" # or "1" or "2" or "3"

folder_new = "dataset_{}".format(choose_dataset)
INDEX_CELL = "dataset_{}_cell".format(choose_dataset)
INDEX_FILE = "dataset_{}_file".format(choose_dataset)
TYPE = "record"
no_results_text = "There are no results for this query..."



#############################################
##### ESTABLISH BASIS OF TKINTER CANVAS #####
#############################################
root = tk.Tk()
root.title('Jupyter Notebook Search Engine')
# root.attributes("-fullscreen", True)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.configure(background='mintcream')
frame_main = tk.Frame(root, bg="lavender")
frame_main.grid(sticky="ns",pady=(100,100),padx=(75,75))#sticky="news")
# use sticky 'ns' instead of 'nsew' to stretch only vertically, not horizontally as well

##################
###### ROW 0 ##### (columnspan 6)
##################
widget_title = tk.Label(frame_main, text="Jupyter Notebook Search Engine",bg="ghostwhite")
widget_title.config(font=("Courier", 30))
widget_title.grid(row=0,column=0,columnspan=6,pady=(5,5),sticky='ew')

##################
###### ROW 1 ##### (columnspan 6)
##################
#ROW1 part1
e1 = tk.Entry(frame_main,width=80)
e1.grid(row=1,column=0,padx=(20,5),sticky='ew')
# e1.config(width=80)

#ROW1 part2-3
radio_v = tk.IntVar()
radio_v.set(1)
radio_cell = tk.Radiobutton(frame_main,text="Cell based",variable=radio_v,value=1)
radio_cell.grid(row=1,column=1,padx=(5,5),sticky='ew')
radio_file = tk.Radiobutton(frame_main,text="File based",variable=radio_v,value=2)
radio_file.grid(row=1,column=2,padx=(5,5),sticky='ew')

#ROW1 part4
m_btn_cell = tk.Menubutton(frame_main, text='cell_type')
m_btn_cell.grid(row=1,column=3,padx=(5,5),sticky='ew')
m_btn_cell.menu = tk.Menu(m_btn_cell,tearoff=1)
m_btn_cell["menu"] = m_btn_cell.menu
cell_code = tk.IntVar()
cell_markdown = tk.IntVar()
cell_heading = tk.IntVar()
cell_raw = tk.IntVar()
m_btn_cell.menu.add_checkbutton(label='code', variable=cell_code)
m_btn_cell.menu.add_checkbutton(label='markdown', variable=cell_markdown)
m_btn_cell.menu.add_checkbutton(label='heading', variable=cell_heading)
m_btn_cell.menu.add_checkbutton(label='raw', variable=cell_raw)

#ROW1 part5
m_btn_output = tk.Menubutton(frame_main, text='output_type')
m_btn_output.grid(row=1,column=4,padx=(5,5),sticky='ew')
m_btn_output.menu = tk.Menu(m_btn_output,tearoff=1)
m_btn_output["menu"] = m_btn_output.menu
no_output_v = tk.IntVar()
stream_v = tk.IntVar()
execute_v = tk.IntVar()
display_data_v = tk.IntVar()
pyout_v = tk.IntVar()
error_v = tk.IntVar()
pyerr_v = tk.IntVar()
m_btn_output.menu.add_checkbutton(label='stream', variable=stream_v)
m_btn_output.menu.add_checkbutton(label='execute_result', variable=execute_v)
m_btn_output.menu.add_checkbutton(label='display_data', variable=display_data_v)
m_btn_output.menu.add_checkbutton(label='pyout', variable=pyout_v)
m_btn_output.menu.add_checkbutton(label='error', variable=error_v)
m_btn_output.menu.add_checkbutton(label='pyerr', variable=pyerr_v)
m_btn_output.menu.add_checkbutton(label='no output', variable=no_output_v)

#ROW1 part6
s_btn = tk.Button(frame_main,text="SEARCH",command=lambda:search_clicked(e1.get()))
s_btn.grid(row=1, column=5,padx=(5,20),pady=(5,5),sticky="ew")
# use sticky='ew' for 'e1' and 's_btn' to make them connect

##################
###### ROW 2 ##### (columnspan 6)
##################
# Create a frame for the canvas with non-zero row&column weights
frame_result = tk.Frame(frame_main)
frame_result.grid(row=2,column=0,columnspan=6)#,sticky='nsew'
frame_result.grid_rowconfigure(0, weight=1)
frame_result.grid_columnconfigure(0, weight=1)
frame_result.configure(background='blue')
# Set grid_propagate to False to allow 5-by-5 buttons resizing later
frame_result.grid_propagate(False)
frame_result.config(width=1000,height=723)

# Add a canvas in that frame
canvas_result = tk.Canvas(frame_result, bg="ghostwhite")
canvas_result.grid(row=0, column=0, sticky="nsew")
# Link a scrollbar to the canvas
vsb = tk.Scrollbar(frame_result, orient="vertical", command=canvas_result.yview)
vsb.grid(row=0, column=1, sticky='ns')
canvas_result.configure(yscrollcommand=vsb.set)
# Link using the scrollwheel to the canvas
def on_mousewheel(event):
    canvas_result.yview_scroll(-1*int(event.delta/120), "units")

canvas_result.bind_all("<MouseWheel>", on_mousewheel)

# Create a frame to contain the labels
frame_labels = tk.Frame(canvas_result, bg="white")

root.update()
# update so that frame_main has an actual height (in pixels) instead of weight of 1
frame_result_height = int(frame_main.winfo_height())-int(widget_title.winfo_height())-int(s_btn.winfo_height())-20
# -20 because two instances a pady=(5,5) is used
frame_labels.config(width=1000,height=frame_result_height)
canvas_result.create_window((0,0),window=frame_labels,anchor='n')

# Set the canvas scrolling region
canvas_result.config(scrollregion=canvas_result.bbox("all"))



#########################
####### FUNCTIONS #######
#########################
def display_rows(result,folder):#query,max_res):
    """Loop through the results that are provided by elasticsearch and display
    them in the tk.frame 'frame_labels'. For each result add 8 rows to this
    frame.
    """
    if result['hits']['hits']==[]:
        row_0 = tk.Label(frame_labels,text=no_results_text,bg="white")
        row_0.grid(column=0,row=0,sticky='news')
    frame_labels.update_idletasks()

    ral = 0 # row at line
    for i in range(len(result['hits']['hits'])): # for all hits
        res = result['hits']['hits'][i]

        title = res['_source']['file']
        os_path = res['_source']['location']
        localhost_path = os_path.split(username_pc)[1]
        localhost_path_nw = localhost_path.replace(' ','%20')
        # in case the filename has whitespace between words / nw = no whitespace
        # (example the ipython-notebooks files of yoavram)
        local_url = ('<a href= http://localhost:8888/notebooks{} '
                        'target="_blank">{}</a>'.format(localhost_path_nw,
                                                        localhost_path))
        github_path = os_path.split(folder)[1]
        github_url,github_url_nw = create_link.path_to_githuburl(github_path)
        github_href = 'file: <a href={} target="_blank">{}</a>'.format(github_url,
                                                                title)
        # score = str(res['_score'])
        score = str(round(res['_score'], 2))
        try:
            user = res['_source']['user']
        except Exception as e:
            local_folder = str(res['_source']['folder'])
            user = local_folder.split('(')[1].split(')')[0] #temp solution
            pass
        # folder = res['_source']['folder']
        repo = res['_source']['repo']
        rank = str(i+1)
        user_href,repo_href = create_link.user_repo_href(user,repo)

        try:
            highlight_list = res['highlight']['string']
            # join them together with three dots as then it is clear when a highlight
            # stops and a new one starts
            highlight_str = ' '.join(highlight_list)
            highlight = highlight_str

            chrome_ref = create_link.create_ref(highlight_list)
            github_href = ('file: <a href={} target="_blank">{}</a>'
                            .format(github_url_nw+chrome_ref,title))
            local_url = ('<a href= http://localhost:8888/notebooks{} target="_blank">{}</a>'
                            .format(localhost_path_nw+chrome_ref,localhost_path))
        except Exception as e:
            print(e)
            highlight = "Something went wrong with the highlighted text: "+str(e)

        # ROW 1 column 0 (rank)
        row_1 = tk.Label(frame_labels,text='rank: '+rank+'.',bg="yellow")
        row_1.grid(column=0,row=ral,rowspan=1)#,sticky='w')#,sticky='news')

        # ROW 2 column 0 (score)
        row_2 = tk.Label(frame_labels,text="score: "+score,bg="white")
        row_2.grid(column=0,row=ral+1,rowspan=1)#,sticky='w')#,sticky='news')

        # ROW 1/2 column 1 (filename)
        row_12 = tk.Label(frame_labels, text=title,font='Helvetica 14',bg="white")#,anchor='w')
        row_12.grid(column=1,row=ral,columnspan=4,rowspan=2,sticky='news')#,sticky='w')

        # ROW 3 (github user link)
        row_3 = tk_html.HTMLLabel(frame_labels, html=user_href)
        row_3.grid(column=0,row=ral+2,columnspan=5,sticky='w')
        row_3.fit_height()

        # ROW 4 (github repo link)
        row_4 = tk_html.HTMLLabel(frame_labels, html=repo_href)
        row_4.grid(column=0,row=ral+3,columnspan=5,sticky='w')
        row_4.fit_height()

        # ROW 5 (github link)
        row_5 = tk_html.HTMLLabel(frame_labels, html=github_href)
        row_5.grid(column=0,row=ral+4,columnspan=5)#,sticky='news')
        row_5.fit_height()

        # ROW 6 (local link)
        row_6 = tk_html.HTMLLabel(frame_labels, html=local_url)
        row_6.grid(column=0,row=ral+5,columnspan=5)#,sticky='news')
        row_6.fit_height()

        # ROW 7 (highlight text)
        row_7 = tk_html.HTMLLabel(frame_labels, html=highlight)
        row_7.grid(column=0,row=ral+6,columnspan=5)#,sticky='w')
        row_7.fit_height()

        # ROW 8 (grey part to seperate results)
        row_8 = tk.Label(frame_labels,bg="lightgrey")
        row_8.grid(row=ral+9,columnspan=5,sticky='news')

        ral+=10
    frame_labels.update_idletasks()
    canvas_result.config(scrollregion=canvas_result.bbox("all"))


def search_clicked(entry):
    """When this function runs, four variables will be collected:
    (1) the query typed in the entry,
    (2) whether the radiobutton is set on cell or file,
    (3) the cell types that are checked in the menubutton and
    (4) the output types that are checked in the other menubutton.
    If none of the checkbuttons in the menubutton are ticked, then they will be
    ignored. These variables combined with the entry input are used in either
    the function query_string_cellbased() or query_string_filebased() as both
    will create a query. This query is used to search with elasticsearch, the
    returend results will be used in the fucntion dipslay_rows().
    """
    # remove frame_labels from previous result of query
    for label in frame_labels.grid_slaves():
        label.grid_forget()

    if entry == "":
        row_0 = tk.Label(frame_labels,text=no_results_text,bg="white")
        row_0.grid(column=0,row=0,sticky='news')
    frame_labels.update_idletasks()

    max_res = 10
    cell_types = []
    output_types = []
    # collect variables checked in both the menubuttons
    if cell_code.get() == 1:
        cell_types.append("code")
    if cell_markdown.get() == 1:
        cell_types.append("markdown")
    if cell_heading.get() == 1:
            cell_types.append("heading")
    if cell_raw.get() == 1:
        cell_types.append("raw")

    if no_output_v.get() == 1:
        output_types.append("no output")
    if stream_v.get() == 1:
        output_types.append("stream")
    if execute_v.get() == 1:
        output_types.append("execute_result")
    if display_data_v.get() == 1:
        output_types.append("display_data")
    if pyout_v.get() == 1:
        output_types.append("pyout")
    if error_v.get() == 1:
        output_types.append("error")
    if pyerr_v.get() == 1:
        output_types.append("pyerr")

    # create query and search with elasticsearch
    if radio_v.get() == 1:
        query = create_query.query_string_cellbased(entry,cell_types,
                                                    output_types,True)
        result = es.search(index=[INDEX_CELL],body=query, size=max_res)
    if radio_v.get() == 2:
        query = create_query.query_string_filebased(entry,cell_types,
                                                    output_types,True)
        result = es.search(index=[INDEX_FILE],body=query, size=max_res)
    ## FOLDER_NEW BELANGRIJKE VARIABELE ##
    # assigned in line 26 of this file
    display_rows(result,folder_new)


# Closing the tkinter application with Esc button causes problems
# def close(event):
#     root.withdraw() # if you want to bring it back
#     sys.exit() # if you want to exit the entire thing
# root.bind('<Escape>', close)

####################
##### RUN CODE #####
####################
root.bind('<Return>',lambda event:search_clicked(e1.get()))
root.state('zoomed')
root.mainloop()

print(create_error)
