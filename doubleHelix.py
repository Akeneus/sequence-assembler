from posixpath import dirname
from typing import List
from assemble_data import AssembleData
from igraph import Graph, plot, os
from random import randrange
from datetime import date
import math


min_weight = 1
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
    new_sequences = _rebuild_sequences_considering_double_helix(sequences)
    graph = Graph(directed= True)
    graph = _build_vertices(graph,new_sequences)
    graph = _build_edges(graph,new_sequences)
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
            size_of_matching_prefix = _check_sequence(sequence_to_check, sequence_getting_checked)
            if(size_of_matching_prefix >= min_weight):
                new_edge = (l_copy_sequences.index(sequence_to_check),l_copy_sequences.index(sequence_getting_checked))
                l_edges.append(new_edge)
                l_weights.append(size_of_matching_prefix)
    graph.add_edges(l_edges)
    graph.es["weight"] = l_weights
    return graph

# Boyer-Moore-Algorithmus
# Knuth-Morris-Pratt-Algorithmus
# Suffix-Tree
def _check_sequence(sequence_to_check:str, sequence_getting_checked:str) -> int:
    """
    _check_sequence verifys if a subsequence of sequence_to_check is a Prefix of sequence_getting_checked.
    If that is the case, the lenth of that subsequence is the weight of the edge between these two sequences
    and this length is returned

    :param sequence_to_check: the sequence which shall be checked to be a prefix
    :param sequence_getting_checked: the sequence which has a potential prefix
    :return: the size of the matching prefixstring
    """ 
    sequence_to_check_length = len(sequence_to_check)
    v = 0
    for start_index in range(sequence_to_check_length):
        tmp_sub_sequence = sequence_to_check[start_index:sequence_to_check_length]
        if(sequence_getting_checked.startswith(tmp_sub_sequence)):
            return len(tmp_sub_sequence)
    return v

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
    dir_name = data.data_path+"step_"+str(len(data.sequences))+".png" 
    plot(data.graph, dir_name,**visual_style)

def _save_substrings(data:AssembleData):
    """
    _save_substrings saves all build substrings into a textfile

    :param data: the current AssembleData object, which holds the relevant information
    """ 
    file = open(data.data_path+"_sequences.txt", "w")
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

def _rebuild_sequences_considering_double_helix(l_sequences:list):
    
    """
    _rebuild_sequences_considering_double_helix considers the data to be from a double helix and determins from which strand the sequences are.
    Considering this, the datalist is rebuild with potential complement sequences

    :param l_sequences: original data List
    :return: new Data list
    """ 
    l_new_sequences = []
    l_new_sequences.append(l_sequences[0])
    l_copy_sequences = l_sequences.copy()
    for sequence in l_copy_sequences[1::]:
        same = 0
        opp = 0
        for saved_sequence in l_new_sequences:
            same += _check_both_Sequences(saved_sequence, sequence)
            opp += _check_both_Sequences(_get_complement_sequence(sequence), saved_sequence)

        if(same > opp):
            l_new_sequences.append(sequence)
        else:
            l_new_sequences.append(_get_complement_sequence(sequence))
    return l_new_sequences
 

def _check_both_Sequences(sequence_one:str, sequnece_two:str) -> int:
    
    """
    _check_Sequence_left_and_right checks the weight of the two sequences to each other and adds them

    :param sequence_one: 
    :param sequnece_two:
    :return: the added weights 
    """ 
    weight_one = _check_sequence(sequence_one,sequnece_two)
    weight_two = _check_sequence(sequnece_two,sequence_one)
    return weight_one+weight_two

def _get_complement_sequence(sequence:str) -> str:
    
    """
    _get_complement_sequence builds the complement sequence to a given sequence
    the complement is defined as a reversed version where every base is changed to its complement base

    :param sequence: the sequence to build the complement of
    :return: the complement version of a sequence
    """
    res_sequence = sequence
    res_sequence = res_sequence.replace("A","t")
    res_sequence = res_sequence.replace("T","a")
    res_sequence = res_sequence.replace("G","c")
    res_sequence = res_sequence.replace("C","g")
    return (res_sequence.upper())[::-1]

main(1,1)