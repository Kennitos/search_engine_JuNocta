##########################
##### IMPORT MODULES #####
##########################
import re



#########################
####### FUNCTIONS #######
#########################
def multi_match_query(string,highlight):
    ### This function is not used anymore, as I switch to use query_string ###
    """Create a dictionary for a query based on the multi_match. Takes the
    a string that is typed in the entry box as input. If highlight is set on
    False, no highlighted snippets that can show where the query matches are
    returned.
    """
    fields = ['string']
    query_str = string
    q = {}
    query_dict = {}
    multi_match = {}
    multi_match['fields'] = fields
    multi_match['query'] = query_str
    query_dict['multi_match'] = multi_match
    q['query'] = query_dict

    if highlight != None:
        highlight = {"pre_tags":["<u><i><b>"],
            "post_tags":["</b></i></u>"],
            "fields":{'string':{}}}
        q['highlight'] = highlight
    return q


################################
## CELL-BASED QUERY FUNCTIONS ##
################################
def adding_string_cellbased(current_str,type_,types_list):
    """This functions works with query_string_cellbased, it takes a incomplete
    string as input and adds operators and the chosen cell_types/output_types as
    variables to complete the string in order to use for the query_str. This
    adding_string works specifically when searching cell based.
    """
    if len(types_list)>1:
        types_str = " AND ("
        for item in types_list:
            if types_str != " AND (":
                types_str += " OR "
            types_str += "({}:{})".format(type_,item)
        current_str += types_str+')'
    else:
        current_str += " AND ({}:{})".format(type_,types_list[0])
    return current_str


def query_string_cellbased(string,cell_types,output_types,highlight):
    """Create a dictionary for a query based on the query_string. Takes the
    a string that is typed in the entry box and which boxes are checked in the
    cell_types and output_types menub as input. If highlight is set on
    True, highlighted snippets that can show where the query matches are
    returned. This query_string works specifically when searching on cell based.
    """
    # string
    query_str = "({})".format(string)
    #cell_type
    if cell_types != []:
        query_str = adding_string_cellbased(query_str,'cell_type',cell_types)
    #output_type
    if output_types != []:
        query_str = adding_string_cellbased(query_str,'output_type',output_types)
    #creating dict
    q = {}
    query_dict = {}
    query_string = {}

    query_string['query'] = query_str
    query_string['default_field'] = "string"
    query_dict['query_string'] = query_string
    q['query'] = query_dict
    #highlight
    if highlight == True:
        highlight = {"pre_tags": ["<b>"],
                     "post_tags": ["</b>"],
                     "order": "score",
                     "fields": {
                                "string": {}#, "cell_type": {}
                                }
                    }
        q['highlight'] = highlight
    return q


################################
## FILE-BASED QUERY FUNCTIONS ##
################################
def adding_string_filebased(current_str,cell_types,output_types):
    """This functions works with query_string_filebased, it takes a incomplete
    string as input and adds operators and the chosen cell_types/output_types as
    variables to complete the string in order to use for the query_str. This
    adding_string works specifically when searching file based.
    """
    types_list = cell_types+output_types
    if len(types_list)>1:
        types_str = " AND ("
        for item in types_list:
            if types_str != " AND (":
                types_str += " AND "
            types_str += "({}:1.0)".format(item)
        current_str += types_str+')'
    elif len(types_list) == 1:
        current_str += " AND ({}:1.0)".format(types_list[0])
    #if types_list is empty, add nothing to current_str and return it
    return current_str


def query_string_filebased(string,cell_types,output_types,highlight):
    """Create a dictionary for a query based on the query_string. Takes the
    a string that is typed in the entry box and which boxes are checked in the
    cell_types and output_types menub as input. If highlight is set on
    True, highlighted snippets that can show where the query matches are
    returned. This query_string works specifically when searching on file based.
    """
    #string
    query_str = "({})".format(string)

    #cell_type&output_type
    query_str = adding_string_filebased(query_str,cell_types,output_types)

    #creating dict
    q = {}
    query_dict = {}
    query_string = {}

    query_string['query'] = query_str
    query_string['default_field'] = "string"
    query_dict['query_string'] = query_string
    q['query'] = query_dict
    #highlight
    if highlight == True:
        highlight = {"pre_tags": ["<b>"],
                     "post_tags": ["</b>"],
                     "order": "score",
                     "fields": {"string": {}}} #, "cell_type": {}
        q['highlight'] = highlight
    return q



####################
##### RUN CODE #####
####################
print("IMPORTED CREATE_QUERY.PY")
