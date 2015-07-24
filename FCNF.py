#!/usr/bin/env python

from gurobipy import *

# Flow conservation/sink/source
vertices = {0: 4, 1: 3, 2: 2, 3: 0, 4: -6, 5: -2}
# Capacities and cost. Format is key: edge, value: (capacity, cost per flow, cost to open)
edges = {(0,4): (4,1,1),
     (0,3): (2,1,1),
     (1,3): (3,1,1),
     (2,5): (2,1,1),
     (3,4): (2,1,1),
     (3,5): (1,1,1)}

def transform(vertices, edges, params):
    newEdges = {}
    i = 0
    for edge in edges:
        newEdges[(edge[0], edge[1])] = params[i]
        i += 1

     # Fix javascript format
    newVertices = {}
    for v in vertices:
        newVertices[int(v)] = vertices[v]

    print 'In transform!'
    print newEdges
    print newVertices
    solution = optimize(newVertices, newEdges)
    return solution

def optimize(vertices, edges):

    m = Model()

    x = {} # Flow on each edge
    y = {} # Binary variable for each edge
    edgeIn   = { v:[] for v in vertices }
    edgeOut  = { v:[] for v in vertices }

    # Add variables
    for edge in edges:
        u = edge[0]
        v = edge[1]
        y[edge] = m.addVar(vtype=GRB.BINARY, name="y" + str(edge))
        x[edge] = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="x" + str(edge) )
        edgeIn[v] = edgeIn[v] + [x[edge]]
        edgeOut[u] = edgeOut[u] + [x[edge]]

    m.update()

    # Add constraints
    for v in vertices:
        if (vertices[v] <= 0):
            m.addConstr(quicksum(edgeOut[v]) - quicksum(edgeIn[v]) == vertices[v], name="v%d" % v)
        else:
            m.addConstr(quicksum(edgeOut[v]) - quicksum(edgeIn[v]) <= vertices[v], name="v%d" % v)
            m.addConstr(quicksum(edgeOut[v]) - quicksum(edgeIn[v]) >= 0, name="vlb%d" % v)

    for edge in edges:
        m.addConstr(x[edge] <= edges[edge][0]*y[edge], name=str(edge))

    # Set objective
    m.setObjective(quicksum((edges[edge][1]*x[edge] + edges[edge][2]*y[edge]) for edge in edges), GRB.MINIMIZE)

    m.optimize()

    solution = {}

    for edge in edges:
        solution[str(edge)] = x[edge].X

    return solution

print optimize(vertices,edges)
