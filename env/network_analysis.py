import networkx as nx
import matplotlib.pyplot as plt
import json
import csv

theme_labels = {
        1: "Leadership",
        2: "Culture",
        3: "Review",
        4: "Resources",
        5: "Process",
        6: "ShM",
        7: "People",
        8: "Other",
        9: "IP",
        10: "Impact"
}


def load_codes():
    keys = ['code', 'p_id', 'loc', 'sentiment', 'theme_id']
    data = []
    with open('../data/encoded_data.csv', encoding='utf-8') as csvf: 
        reader = csv.reader(csvf) 
        for row in reader:
            if int(row[4]) < 8:
                data.append(dict((keys[i], row[i]) for i, v in enumerate(keys)))
    return data

def initialise_graph():
    # 1. Define an undirected graph
    G = nx.Graph()

    # 2. Model the data points as nodes
    codes_array = load_codes()

    for code in codes_array:
        # start with participants...
        try:
            if not G.has_node(code['p_id']):
                G.add_node(code['p_id'], node_type="participant", label=code['p_id'])
        except:
            pass
        # next add themes...
        try:
            if not G.has_node(code['theme_id']):
                G.add_node(code['theme_id'], node_type="theme", label=theme_labels[int(code['theme_id'])])
        except:
            pass
        # now add edges, decreasing weight for every duplicate edge
        if not G.has_edge(code['p_id'], code['theme_id']):
            G.add_edge(code['p_id'], code['theme_id'], weight=15)
        else:
            if G[code['p_id']][code['theme_id']]['weight'] > 1:
                G[code['p_id']][code['theme_id']]['weight'] += -1
    return G

def draw_graph(G):
    # betweenness centraility will dictate size of nodes
    bet_cent = nx.betweenness_centrality(G, normalized=True, endpoints=True)
    # weight of edges will dictate thickness of edge lines
    n_edges = [ (15-c)*0.6 for u,v,c in G.edges.data('weight') ]
    node_size =  [v * 10000 for v in bet_cent.values()]
    project_nodes = [ node for node,attr in G.nodes(data=True) if 'participant' in attr.values() ]
    theme_nodes = [ node for node,attr in G.nodes(data=True) if 'theme' in attr.values() ]
    pos=nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, 
            nodelist=project_nodes, 
            node_color='#eeef33', 
            node_size=200, 
            with_labels=True, 
            font_weight='normal')
    nx.draw_networkx_nodes(G, pos, 
            nodelist=theme_nodes, 
            node_color='#dd99ee', 
            node_size=node_size, 
            with_labels=True, 
            font_weight='normal')
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_edges(G, pos, edge_color='#cccccc', width=n_edges)
    nx.draw_networkx_labels(G,pos,labels,font_size=16, font_weight='bold')
    plt.show()

G = initialise_graph()
draw_graph(G)
