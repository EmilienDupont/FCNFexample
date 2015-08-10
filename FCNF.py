#!/usr/bin/env python

from gurobipy import *
import StringIO
import sys

# Flow conservation/sink/source
vertices = {0: 4, 1: 3, 2: 2, 3: 0, 4: -6, 5: -3}
# Capacities and cost. Format is key: edge, value: (capacity, cost per flow, cost to open)
edges = {(0,4): (4,1,1),
     (0,3): (2,1,1),
     (1,3): (3,1,1),
     (2,5): (2,1,1),
     (3,4): (2,1,1),
     (3,5): (1,1,1)}

def mycallback(model, where):
    if where == GRB.callback.MESSAGE:
        print >>model.__output, model.cbGet(GRB.callback.MSG_STRING),

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

    solution = optimize(newVertices, newEdges)
    return solution

def optimize(vertices, edges, output=False):

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
        m.addConstr(quicksum(edgeOut[v]) - quicksum(edgeIn[v]) == vertices[v], name="v%d" % v)

    for edge in edges:
        m.addConstr(x[edge] <= edges[edge][0]*y[edge], name=str(edge))

    # Set objective
    m.setObjective(quicksum((edges[edge][1]*x[edge] + edges[edge][2]*y[edge]) for edge in edges), GRB.MINIMIZE)

    if not output:
        m.params.OutputFlag = 0;

    output = StringIO.StringIO()
    m.__output = output

    m.optimize(mycallback)

    solEdges = []
    solWidth = []

    for edge in edges:
        if (y[edge].X > .5): # if edge was opened
            solEdges.append([edge[0], edge[1]])
            solWidth.append(x[edge].X)

    solution = [solEdges, solWidth, output.getvalue()]

    return solution

def handleoptimize(jsdict):
    if 'vertices' and 'edges' and 'params' in jsdict:
        solution = transform(jsdict['vertices'], jsdict['edges'], jsdict['params'])
        return {'solution': solution }


if __name__ == '__main__':
    import json
    jsdict = json.load(sys.stdin)
    jsdict = handleoptimize(jsdict)
    print 'Content-Type: application/json\n\n'
    print json.dumps(jsdict)
