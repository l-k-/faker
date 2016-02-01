#!/usr/bin/env python3

import copy
import multiprocessing


class Node(object):
    def __init__(self, id, parents=None, children=None):
        self.id = id
        self.parents = parents if parents else {}
        self.children = children if children else []

    def __str__(self):
        return self.id

    def add_parent(self, parameter, dependency):
        self.parents[parameter] = dependency

    def add_child(self, child_id):
        self.children.append(child_id)


class ProcessNode(Node, multiprocessing.Process):
    def __init__(self, id, worker, done_event, results):
        Node.__init__(self, id=id)

        multiprocessing.Process.__init__(self, target=worker)
        self.worker = worker
        self.done_event = done_event
        self.parent_events = []
        self.results = results

    def __str__(self):
        return self.id

    def get_node(self):
        return Node(self.id, copy.deepcopy(self.parents), copy.deepcopy(self.children))

    def add_parent(self, parameter, dependency, parent_event):
        Node.add_parent(self, parameter, dependency)
        self.parent_events.append(parent_event)

    def run(self):
        for event in self.parent_events:
            event.wait()

        dependency_values = {}
        for parameter in self.parents:
            parent = self.parents[parameter]
            dependency_values[parameter] = self.results[parent]
        self.results[self.id] = self.worker(**dependency_values)

        self.done_event.set()


def validate(nodes):
    # Validate that this set of nodes is indeed a DAG
    # by traversing the graph in topological order

    all_nodes = {}
    for id in nodes:
        all_nodes[id] = nodes[id].get_node()

    orphan_nodes = list(filter(lambda id: len(all_nodes[id].parents) == 0, all_nodes))

    while len(orphan_nodes) > 0:
        id = orphan_nodes.pop()
        node = all_nodes[id]

        for child_id in node.children:
            child = all_nodes[child_id]

            parameters = list(child.parents.keys())
            for parameter in parameters:
                if child.parents[parameter] == id:
                    del child.parents[parameter]

            if len(child.parents) == 0:
                orphan_nodes.append(child_id)

        del all_nodes[id]

    if len(all_nodes) > 0:
        raise SyntaxError('Loop(s) detected on the following nodes: '
                          + ', '.join(str(node_id) for node_id in all_nodes))
