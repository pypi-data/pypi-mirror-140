# %% Libraries
import networkx as nx
import pandas as pd
import numpy as np
from d3graph import d3graph, vec2adjmat

# %%
from d3graph import d3graph, vec2adjmat

source = ['node A','node F','node B','node B','node B','node A','node C','node Z']
target = ['node F','node B','node J','node F','node F','node M','node M','node A']
weight = [5.56, 0.5, 0.64, 0.23, 0.9, 3.28, 0.5, 0.45]

adjmat = vec2adjmat(source, target, weight=weight)
d3 = d3graph()
d3.graph(adjmat)
d3.show()

d3.set_node_properties(color=adjmat.columns.values, label=['node AA','node BB','node FF','node JJ','node MM','node CC','node ZZ'])
d3.show(filepath='c://temp/')



# %%
G = nx.karate_club_graph()
adjmat = nx.adjacency_matrix(G).todense()
adjmat=pd.DataFrame(index=range(0,adjmat.shape[0]), data=adjmat, columns=range(0,adjmat.shape[0]))
adjmat.columns=adjmat.columns.astype(str)
adjmat.index=adjmat.index.astype(str)
adjmat.iloc[3,4]=5
adjmat.iloc[4,5]=6
adjmat.iloc[5,6]=7

df = pd.DataFrame(index=adjmat.index)
df['degree']=np.array([*G.degree()])[:,1]
df['other info']=np.array([*G.degree()])[:,1]
node_size=df.degree.values*2
node_color=[]

for i in range(0,len(G.nodes)):
    node_color.append(G.nodes[i]['club'])
    node_name=node_color
df['name']=node_name

# Make some graphs
d3 = d3graph()
d3.graph(adjmat)
d3.set_node_properties(color=node_color, cmap='Set1')
d3.show()
d3.set_node_properties(label=node_name, color=node_color, cmap='Set1')
d3.show()


# %%
from d3graph import d3graph, vec2adjmat

source = ['node A', 'node F', 'node B', 'node B', 'node B', 'node A', 'node C', 'node Z']
target = ['node F', 'node B', 'node J', 'node F', 'node F', 'node M', 'node M', 'node A']
weight = [5.56, 0.5, 0.64, 0.23, 0.9, 3.28, 0.5, 0.45]

# Convert to adjacency matrix
adjmat = vec2adjmat(source, target, weight=weight)
# print(adjmat)

# Example A: simple interactive network
d3 = d3graph()
d3.graph(adjmat)
d3.show()


d3.node_properties['node_A']['size']=20
d3.node_properties['node_A']['color']='#FF00FF'
d3.show()

# Example B: Color nodes
# d3 = d3graph()
d3.graph(adjmat)
# Set node properties
d3.set_node_properties(color=adjmat.columns.values)
d3.show()


size = [10, 20, 10, 10, 15, 10, 5]

# Example C: include node size
d3.set_node_properties(color=adjmat.columns.values, size=size)
d3.show()

# Example D: include node-edge-size
d3.set_node_properties(color=adjmat.columns.values, size=size, edge_size=size[::-1])
d3.show()

# Example E: include node-edge color
d3.set_node_properties(color=adjmat.columns.values, size=size, edge_size=size[::-1], edge_color='#000000')
d3.show()

# Example F: Change colormap
d3.set_node_properties(color=adjmat.columns.values, size=size, edge_size=size[::-1], edge_color='#00FFFF', cmap='Set2')
d3.show()

# Example H: Include directed links. Arrows are set from source -> target
d3.set_edge_properties(directed=True)
d3.set_node_properties(color=adjmat.columns.values, size=size, edge_size=size, edge_color='#000FFF', cmap='Set1')
d3.show(filepath='D://REPOS//erdogant.github.io//docs//d3graph//d3graph//example_2.html')


# %%
from d3graph import d3graph, vec2adjmat
d3 = d3graph()

source = ['node A','node F','node B','node B','node B','node A','node C','node Z']
target = ['node F','node B','node J','node F','node F','node M','node M','node A']
weight = [5.56, 0.5, 0.64, 0.23, 0.9, 3.28, 0.5, 0.45]

adjmat = vec2adjmat(source, target, weight=weight)
d3.graph(adjmat)
d3.set_node_properties(color=adjmat.columns.values)
d3.show()

# %% Extended example
import networkx as nx
import pandas as pd
from d3graph import d3graph

G = nx.karate_club_graph()
adjmat = nx.adjacency_matrix(G).todense()
adjmat=pd.DataFrame(index=range(0,adjmat.shape[0]), data=adjmat, columns=range(0,adjmat.shape[0]))
adjmat.columns=adjmat.columns.astype(str)
adjmat.index=adjmat.index.astype(str)
adjmat.iloc[3,4]=5
adjmat.iloc[4,5]=6
adjmat.iloc[5,6]=7

from tabulate import tabulate
print(tabulate(adjmat.head(), tablefmt="grid", headers="keys"))

df = pd.DataFrame(index=adjmat.index)
df['degree']=np.array([*G.degree()])[:,1]
df['other info']=np.array([*G.degree()])[:,1]
node_size=df.degree.values*2
node_color=[]
for i in range(0,len(G.nodes)):
    node_color.append(G.nodes[i]['club'])
    node_name=node_color

# Make some graphs
d3 = d3graph()

d3.graph(adjmat)
d3.set_node_properties(color=node_color, cmap='Set1')
d3.show()

d3.set_node_properties(label=node_name, color=node_color, cmap='Set1')
d3.show()

d3.set_node_properties(adjmat, size=node_size)
d3.show()

d3.set_node_properties(color=node_size, size=node_size)
d3.show()

d3.set_edge_properties(edge_distance=100)
d3.set_node_properties(color=node_size, size=node_size)
d3.show()

d3 = d3graph(charge=1000)
d3.graph(adjmat)
d3.set_node_properties(color=node_size, size=node_size)
d3.show()

d3 = d3graph(collision=1, charge=250)
d3.graph(adjmat)
d3.set_node_properties(color=node_name, size=node_size, edge_size=node_size, cmap='Set1')
d3.show()

d3 = d3graph(collision=1, charge=250)
d3.graph(adjmat)
d3.set_node_properties(color=node_name, size=node_size, edge_size=node_size, edge_color='#00FFFF', cmap='Set1')
d3.show()


# %%
