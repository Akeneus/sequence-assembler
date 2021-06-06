from posixpath import dirname
from typing import List
from assemble_data import AssembleData
from igraph import Graph, plot, os
from random import randrange
from datetime import date
import math


min_weight = 2
def main(min_weight, number_of_iterations):
    """
    main ist the entrypoint of the sequence-assembler
    the method starts the initial setUp of the data and then starts the assembleing

    :param min_weight: the minimun weight, which is relevant for building an edge
    :param number_of_iterations: the umber of exectuions of the the assembler
    """ 
    path = "ressource/frag_a.dat"
    # path = "ressource/frag_b.dat"
    # path = "ressource/frag_c.dat"
    min_weight = min_weight
    for i in range(number_of_iterations):
        data = _setup_data(path)
        _save_graph(data)
        _assemble(data)

def _setup_data(path) -> AssembleData:
    """
    _setupData builds the AssembleData object, which is then used in the entiere programm

    :param path: The path, where the datafile is deposited
    :return: An AssembleData object, which holds all necessary information
    """ 
    g = _build_graph(path)
    source_data_path = _build_path(path)
    return AssembleData(source_data_path,g,[])

def _build_graph(path) -> Graph:
    """
    _build_graph generates a Graph based on the relevant Datafile

    :param path: The path, where the datafile is deposited
    :return: A graph object based on the datafile
    """ 
    frag_file = open(path, 'r')
    lines = frag_file.readlines()
    sequences = [line.strip() for line in lines] 
    graph = Graph(directed= True)
    graph = _build_vertices(graph,sequences)
    graph = _build_edges(graph,sequences)
    return graph

def _build_vertices(graph:Graph,sequences:List[str]) -> Graph:
    """
    _build_vertices generates all necessary vertices for the graph and saves them in the object
    additionally the vertices get the attributes name and label_id, to identify them better

    :param graph: the current Graph object
    :param sequences: the list of Sequences based on the input file
    :return: a Graph with added Vertices based on sequences
    """ 
    graph.add_vertices(len(sequences))
    graph.vs["name"] = sequences
    graph.vs["label_id"] = [id for id in range(len(sequences))]
    return graph

def _build_edges(graph:Graph,sequences:List[str]) -> Graph:
    """
    _build_edges generate the edges based in the current graph, and the Data file
    with the given information.
    The method iterates every Sequence in sequences against all Sequences in the sequence list but itself
    and starts a check, if it is a prefix of another

    :param graph: the current Graph object
    :param sequences: the list of Sequences based on the input file
    :return: a Graph with added Edges based on sequences
    """ 
    l_edges = []
    l_weights = []
    l_copy_sequences = sequences.copy()
    for sequence_to_check in l_copy_sequences:
        l_sequences_to_check = l_copy_sequences.copy()
        l_sequences_to_check.remove(sequence_to_check)
        for sequence_getting_checked in l_sequences_to_check:
            size_of_matching_prefix = _check_sequence_subst(sequence_to_check, sequence_getting_checked)
            if(size_of_matching_prefix >= min_weight):
                new_edge = (l_copy_sequences.index(sequence_to_check),l_copy_sequences.index(sequence_getting_checked))
                l_edges.append(new_edge)
                l_weights.append(size_of_matching_prefix)
    graph.add_edges(l_edges)
    graph.es["weight"] = l_weights
    return graph

def _assemble(data:AssembleData):
    """
    _assemble starts the sequence assemble and executes it as long as there are edges left

    :param data: the current AssembleData object, which holds the relevant information
    """ 
    # wenn noch kanten da, dann weiter machen!
    count = data.graph.ecount()
    while( count!= 0):
        data = _unify_nodes(data)
        count = data.graph.ecount()
        _save_graph(data)
    _save_substrings(data)  

def _unify_nodes(data:AssembleData) -> AssembleData:
    """
    _unify_nodes starts the methods to combine the information of two Vertices and to redirect or delte affected edges

    :param data: the current AssembleData object, which holds the relevant information
    :return: the changed graph object
    """ 
    selected_edge = _select_highest_weighted_edge(data)
    _rename_merged_vertice(data,selected_edge)
    _refactor_graph(data,selected_edge)
    return data

def _select_highest_weighted_edge(data:AssembleData):
    """
    _select_highest_weighted_edge searches all edges with the highest weight and returns one of them

    :param data: the current AssembleData object, which holds the relevant information
    :return: An Edge with the current highest weight
    """ 
    #  find highest weight
    current_highest_weight = max((value for value in data.graph.es["weight"] if isinstance(value, int)))
    # find all edges with the highest weight
    l_heighest_weighted_edges = data.graph.es.select(weight=current_highest_weight)

    #TODO
    # Randooooom
    # highestWeightedEdge = maxWeightEdgesList[randrange(len(maxWeightEdgesList))]
    # Greedy? letztes
    # highestWeightedEdge = maxWeightEdgesList[-1]
    # Greedy? erstes
    selected_edge = l_heighest_weighted_edges[0]
    return selected_edge

def _rename_merged_vertice(data,selected_edge):
    """
    _rename_merged_vertice renames the Vertices which is the Source of the an given edge

    :param data: the current AssembleData object, which holds the relevant information
    :return: An Edge with the current highest weight
    """

    # select the vertice at the source of the selected_edge
    source_vertice = data.graph.vs[selected_edge.source]

    # select the vertice at the target of the selected_edge
    target_vertice = data.graph.vs[selected_edge.target]
    
    # merges the name of the target_vertie into the source_vertiec, but only the subsequencce which is not equal
    merged_sequence_name = source_vertice["name"]+target_vertice["name"][selected_edge["weight"]:]
    source_vertice["name"] = merged_sequence_name
    #TODO
    data.sequences.append(str(selected_edge["weight"])+"|"+merged_sequence_name +" | "+ source_vertice["name"]+":"+str(source_vertice["label_id"]) +"<-"+target_vertice["name"]+":"+str(target_vertice["label_id"]))

def _refactor_graph(data,selected_edge):
    """
    _refactor_graph refactors the affected parth of the graph after the unifycation

    :param data: the current AssembleData object, which holds the relevant information
    :return: the Edge with the current highest weight
    """ 
    # select the vertice at the source of the selected_edge
    source_vertice = data.graph.vs[selected_edge.source]

    # select the vertice at the target of the selected_edge
    target_vertice = data.graph.vs[selected_edge.target]

    # select and then delete all edges which have the soure_vertice as source itself, since the Source vertice gets deleted later
    l_edges_to_delete_with_old_source = list(data.graph.es.select(_source=source_vertice))
    if(len(l_edges_to_delete_with_old_source)>0):
        data.graph.delete_edges(l_edges_to_delete_with_old_source)
    
    # select and then redirect the edges which have the target_vertice as source, 
    # since these edges have the the same word ending, and hence the edge only needs redirection
    l_edges_to_redirect = data.graph.es.select(_source=target_vertice)
    for edge in l_edges_to_redirect:
        # ignore edges on it self
        if(source_vertice.index != edge.target):
            data.graph.add_edge(source_vertice.index,edge.target)
            data.graph.es[-1]["weight"] = edge["weight"]
    data.graph.delete_edges(l_edges_to_redirect) 
    data.graph.delete_vertices(target_vertice)

def _save_graph(data:AssembleData):
    """
    _save_graph saves a snapshot of the current Graph 

    :param data: the current AssembleData object, which holds the relevant information
    """ 
    visual_style = {}
    visual_style["vertex_shape"] = 'circle'
    visual_style["vertex_size"] = 30
    # visual_style["vertex_color"] = ["rgba(255, 0, 0, 0)"]
    # visual_style["vertex_label_dist"] = 5
    visual_style["vertex_label"] = data.graph.vs["name"]
    visual_style["edge_label"] = data.graph.es["weight"]
    # visual_style["layout"] = g.layout("kk")
    visual_style["layout"] = data.graph.layout("large")
    visual_style["bbox"] = (1000, 1000)
    visual_style["margin"] = 40
    dir_name = data.data_name+"step_"+str(len(data.sequences))+".png" 
    plot(data.graph, dir_name,**visual_style)

def _save_substrings(data:AssembleData):
    """
    _save_substrings saves all build substrings into a textfile

    :param data: the current AssembleData object, which holds the relevant information
    """ 
    file = open(data.data_name+"_sequences.txt", "w")
    for sequence in data.sequences:
        file.write(sequence+"\n") 
    file.close()

def _build_path(path:str):
    """
    _build_path generates a path where the results shall be saved based on where the Datafile is located

    :param path: The path, where the datafile is deposited
    :return: the path to a directory where the results are saved
    """ 
    source_data_name = path.split("/")[-1]
    source_data_name = source_data_name.split(".")[0]
    dir_name = "log/"+source_data_name
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    num_folders  = len(os.listdir(dir_name))
    dir_name = dir_name+"/run_"+str(num_folders)+"_"+date.today().strftime("%d-%m-%Y")+"/"
    os.makedirs(dir_name)
    return dir_name

def _check_sequence_subst(sequence_to_check:str, sequence_getting_checked:str) -> int:
    """
    _checkSequenceSubst checks of a sequence is a prefix of another, considering the edit distance and the max fehler quota
    
    :param sequence_to_check: 
    :param sequence_getting_checked: 
    :return: the size of the matching prefixstring
    """ 
    sequence_to_check_len = len(sequence_to_check)
    sequence_getting_checked_len = len(sequence_getting_checked)
    v = 0
    max_error_quoat = _get_max_error_quota(max(sequence_to_check_len,sequence_getting_checked_len))
    for i in range(sequence_to_check_len):
        current_subsequence = sequence_to_check[i:sequence_to_check_len]
        edit_dist = _get_edit_distanze(sequence_getting_checked, current_subsequence)
        if(edit_dist <= max_error_quoat):
            return len(current_subsequence)
    return v

def _get_max_error_quota(stringLen:int) -> int:
    """
    _getMaxErrors calculates the max errors, which a sequence is allowed to have, 
    since it is allowed to have 1 error in every 10 chars of a sequence

    :param stringLen: the length of the sequence
    :return: the max number of errors
    """ 
    return math.ceil(stringLen / 10)

def _get_edit_distanze(sequence_getting_check, sequence_to_check):
    """
    _getEditDistanze uses a simple for loop to calculate the edit distance between two strings (only substitution!)
    
    :param sequence_getting_check:
    :param sequence_to_check:
    :return: the edit distanz between two Sequences
    """ 
    edit_dist = 0
    relevant_subsequence = sequence_getting_check[0:len(sequence_to_check)]
    for i in range(len(relevant_subsequence)):
        if(relevant_subsequence[i] != sequence_to_check[i]):
            edit_dist += 1
    return edit_dist

main(1,1)