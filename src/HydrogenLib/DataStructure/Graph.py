class UndirectedGraph:
    def __init__(self, graph_dict=None):
        """ initializes a graph object
            If no dictionary or None is given,
            an empty dictionary will be used
        """
        if graph_dict is None:
            graph_dict = {}
        self.graph_dict = graph_dict

    def vertices(self):
        """ returns the vertices of a graph """
        return list(self.graph_dict.keys())

    def edges(self):
        """ returns the edges of a graph """
        return self.__generate_edges()

    def add_vertex(self, vertex):
        """ If the vertex "vertex" is not in
            self.__graph_dict, a key "vertex" with an empty
            list as a value is added to the dictionary.
            Otherwise, nothing has to be done.
        """
        if vertex not in self.graph_dict:
            self.graph_dict[vertex] = []
            return True
        return False

    def add_edge(self, left, right):
        """ assumes that edge is of type set, tuple or list;
            between two vertices can be multiple edges!
        """
        (vertex1, vertex2) = left, right

        # Add vertex1 if it does not exist
        if vertex1 not in self.graph_dict:
            self.graph_dict[vertex1] = []

        # Add vertex2 if it does not exist
        if vertex2 not in self.graph_dict:
            self.graph_dict[vertex2] = []

        # Add vertex2 to vertex1's adjacency list if not already present
        if vertex2 not in self.graph_dict[vertex1]:
            self.graph_dict[vertex1].append(vertex2)

        # Add vertex1 to vertex2's adjacency list if not already present
        if vertex1 not in self.graph_dict[vertex2]:
            self.graph_dict[vertex2].append(vertex1)

    def __generate_edges(self):
        """ A static method generating the edges of the
            graph "graph". Edges are represented as sets
            with one (a loop back to the vertex) or two
            vertices
        """
        edges = []
        for vertex in self.graph_dict:
            for neighbour in self.graph_dict[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append({vertex, neighbour})
        return edges

    def __str__(self):
        res = "vertices: "
        for k in self.graph_dict:
            res += str(k) + " "
        res += "\nedges: "
        for edge in self.__generate_edges():
            res += str(edge) + " "
        return res


class DirectedGraph:
    def __init__(self, graph_dict=None):
        """ initializes a directed graph object
            If no dictionary or None is given,
            an empty dictionary will be used
        """
        if graph_dict is None:
            graph_dict = {}
        self.graph_dict = graph_dict

    def vertices(self):
        """ returns the vertices of a graph """
        return list(self.graph_dict.keys())

    def edges(self):
        """ returns the edges of a graph """
        return self.__generate_edges()

    def add_vertex(self, vertex):
        """ If the vertex "vertex" is not in
            self.graph_dict, a key "vertex" with an empty
            list as a value is added to the dictionary.
        """
        if vertex not in self.graph_dict:
            self.graph_dict[vertex] = []

    def add_edge(self, left, right):
        """ assumes that edge is of type tuple (vertex1, vertex2);
            adds a directed edge from vertex1 to vertex2.
        """
        (vertex1, vertex2) = left, right
        if vertex1 in self.graph_dict:
            self.graph_dict[vertex1].append(vertex2)
        else:
            self.graph_dict[vertex1] = [vertex2]

    def __generate_edges(self):
        """ A static method generating the edges of the
            directed graph "graph". Edges are represented as lists
            with two vertices
        """
        edges = []
        for vertex in self.graph_dict:
            for neighbour in self.graph_dict[vertex]:
                if [vertex, neighbour] not in edges:
                    edges.append([vertex, neighbour])
        return edges

    def __str__(self):
        res = "vertices: "
        for k in self.graph_dict:
            res += str(k) + " "
        res += "\nedges: "
        for edge in self.__generate_edges():
            res += str(edge) + " "
        return res


class WeightedGraph:
    def __init__(self):
        self.graph_dict = {}

    def add_vertex(self, vertex):
        """ Adds a new vertex to the graph """
        if vertex not in self.graph_dict:
            self.graph_dict[vertex] = {}

    def add_edge(self, vertex1, vertex2, weight):
        """ Adds a weighted edge between vertex1 and vertex2 """
        if vertex1 in self.graph_dict and vertex2 in self.graph_dict:
            self.graph_dict[vertex1][vertex2] = weight
            self.graph_dict[vertex2][vertex1] = weight  # For undirected graph

    def get_weight(self, vertex1, vertex2):
        """ Returns the weight of the edge between vertex1 and vertex2 """
        if vertex2 in self.graph_dict[vertex1]:
            return self.graph_dict[vertex1][vertex2]
        return None

    def __str__(self):
        res = "vertices: "
        for k in self.graph_dict:
            res += str(k) + " "
        res += "\nedges: "
        for vertex in self.graph_dict:
            for neighbour in self.graph_dict[vertex]:
                res += f"{vertex} -> {neighbour}, weight={self.graph_dict[vertex][neighbour]} "
        return res


class LabeledGraph:
    def __init__(self):
        self.vertices = {}
        self.edges = {}

    def add_vertex(self, vertex, label=None):
        """ Adds a new vertex with an optional label """
        self.vertices[vertex] = label

    def add_edge(self, vertex1, vertex2, label=None):
        """ Adds an edge between vertex1 and vertex2 with an optional label """
        if vertex1 in self.vertices and vertex2 in self.vertices:
            self.edges[(vertex1, vertex2)] = label

    def get_vertex_label(self, vertex):
        """ Returns the label of a vertex """
        return self.vertices.get(vertex)

    def get_edge_label(self, vertex1, vertex2):
        """ Returns the label of the edge between vertex1 and vertex2 """
        return self.edges.get((vertex1, vertex2))

    def __str__(self):
        res = "vertices: "
        for vertex, label in self.vertices.items():
            res += f"{vertex}({label}) "
        res += "\nedges: "
        for (vertex1, vertex2), label in self.edges.items():
            res += f"{vertex1} -> {vertex2}({label}) "
        return res
