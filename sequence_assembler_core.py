from typing import List
from assemble_data import AssembleData
from igraph import Graph, plot, os

#1. Die einzelnen Fragmente als Knoten in einem Graphen darstellen (check)
#2a Gewichtete Überlappungskanten bauen, also schauen ob es Überlappungen gibt, diese dann also kante machen und gewicht anzahl der Überlappung bauen (check)
#2b Möglichkeit zu angabe einr mindest Gewichtung
#3. Verschmelzung der Knoten mit der größten Kante (check)
#3b. GIERIG die erste Kannte wenn es kannten mit gleicher gewichtung gib (check, aber eventuell random ?)
#4 bereinigen der Kanten (check)
#5 wieder bei 3 solange es kanten gibt (check)
#6 fertig (check)
# 7 Qualitätskontrolle ?
# eulerpfad ?


def main():
    path = "C:\\Users\\nlens\Documents\\sequenz-assemblerdsfasdfas\\sequence-assembler\\ressource\\frag_a.dat"
    # path = "ressource\\frag_b.dat"
    # path = "C:\\Users\\nlens\Documents\\sequenz-assemblerdsfasdfas\\sequence-assembler\\ressource\\frag_c.dat"
    data = _setupData(path)
    _saveGraph(data)
    _assemble(data)

def _setupData(path) -> AssembleData:
    g = _buildGraph(path)
    sourceDataName = path.split("\\")[-1]
    return AssembleData(sourceDataName,g,[])

def _buildGraph(path) -> Graph:
    frag_file = open(path, 'r')
    lines = frag_file.readlines()
    lines = [Lines.strip() for Lines in lines] 
    g = Graph(directed= True)
    g = _buildVertices(g,lines)
    g = _buildEdges(g,lines)
    return g

def _buildVertices(g:Graph,lines:List[str]) -> Graph:
    g.add_vertices(len(lines))
    g.vs["name"] = lines
    return g

def _buildEdges(g:Graph,lines:List[str]) -> Graph:
    edgeList = []
    weightList = []
    tmpLines = lines.copy()
    for lineToCheck in tmpLines:
        linesToCheck = tmpLines.copy()
        linesToCheck.remove(lineToCheck)
        for line in linesToCheck:
            matchingAffix = _checkSequence(lineToCheck, line)
            if(matchingAffix > 1):
                edge = (tmpLines.index(lineToCheck),tmpLines.index(line))
                edgeList.append(edge)
                weightList.append(matchingAffix)
    g.add_edges(edgeList)
    g.es["weight"] = weightList
    return g

def _checkSequence(stringA:str, stringB:str) -> int:
    stringLengA = len(stringA)
    v = 0
    for i in range(stringLengA):
        tmp = stringA[i:stringLengA]
        if(stringB.startswith(tmp)):
            return len(tmp)
    return v


def _assemble(data:AssembleData):
    # wenn noch kanten da, dann weiter machen!
    count = data.graph.ecount()
    while( count!= 0):
        data = _unifyNodes(data)
        count = data.graph.ecount()
        _saveGraph(data)
    _saveSubstrings(data)





def _unifyNodes(data:AssembleData) -> AssembleData:
    # alle höchsten kanten bestimmen
    # wenn > 1, eine zufällige auswählen
    maxWeight = max((value for value in data.graph.es["weight"] if isinstance(value, int)))
    highestWeightedEdge = data.graph.es.select(weight=maxWeight)[0]
    x = highestWeightedEdge.tuple
    source = data.graph.vs[x[0]]
    target = data.graph.vs[x[1]]

    # Neuen Sequence Bauen aus den Selektierten (zusammenführen)
    newSequenceName = source["name"]+target["name"][maxWeight:]
    source["name"] = newSequenceName
    data.sequences.append(newSequenceName)

    #Graph aufräumen
    a = data.graph.es.select(_source=target)
    for edge in a:
        if(source.index != edge.target):
            data.graph.add_edge(source.index,edge.target)
            data.graph.es[-1]["weight"] = edge["weight"]
    data.graph.delete_edges(a)
    data.graph.delete_vertices(target)
   
    return data

def _saveGraph(data:AssembleData):
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
    dirName = "log\\"+data.dataName+"\\"
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    plot(data.graph, dirName+"step_"+str(len(data.sequences))+".png" ,**visual_style)
    
def _saveSubstrings(data:AssembleData):
    dirName = "log\\"+data.dataName+"\\"
    if not os.path.exists(dirName):
        os.makedirs(dirName)

    file = open(dirName+data.dataName+"_sequences.txt", "w")
    for sequence in data.sequences:
        file.write(sequence+"\n") 
    file.close()


main()