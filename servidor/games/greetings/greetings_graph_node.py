class Node:
    def __init__(self, name, NUM_INPUTS, NUM_OUTPUTS, NUM_BIDIRECTIONAL):
        self.name = name
        self.input_edges = [] # Edges that go to the node
        self.output_edges = [] # Edges that go from the node
        self.bidirectional_edges = [] # Edges that go both ways
        self.NUM_INPUTS = NUM_INPUTS # Size of the input edges list
        self.NUM_OUTPUTS = NUM_OUTPUTS # Size of the output edges list
        self.NUM_BIDIRECTIONAL = NUM_BIDIRECTIONAL # Size of the bidirectional edges list

    def get_name(self):
        return self.name

    def add_output_edge(self, target, called_from_input):
        self.output_edges.append(target)
        if not called_from_input:
            target.add_input_edge(self, True)
        if(target in self.input_edges):
            self.bidirectional_edges.append(target)

    def add_input_edge(self, source, called_from_output):
        self.input_edges.append(source)
        if not called_from_output:
            source.add_output_edge(self, True)
        if(source in self.output_edges):
            self.bidirectional_edges.append(source)
    
    def add_bidirectional_edge(self, node):
        """
            Adds a bidirectional edge between the current node and the node passed as parameter
        """
        self.add_output_edge(node, False) # Will add it to the input node
        self.add_input_edge(node, False) # Will add it to the output node
     
    def get_outputs(self):
        return self.output_edges
    
    def get_inputs(self):
        return self.input_edges
    
    def get_bidirectional_edges(self):
        return self.bidirectional_edges
    
    def get_edges_of_type(self, type):
        """
            Returns the edges of the type passed as parameter
        """
        if type == 'input':
            return self.input_edges
        elif type == 'output':
            return self.output_edges
        elif type == 'bidirectional':
            return self.bidirectional_edges
    
    def get_num_outputs(self):
        return len(self.output_edges)
    
    def get_num_inputs(self):
        return len(self.input_edges)
    
    def get_num_bidirectional_edges(self):
        return len(self.bidirectional_edges)
    
    def get_num_edges_of_type(self, type):
        if type == 'input':
            return self.get_num_inputs()
        elif type == 'output':
            return self.get_num_outputs()
        elif type == 'bidirectional':
            return self.get_num_bidirectional_edges()
        
    def is_connected_to(self, node, type):
        """
            Checks if the current node is connected to the node passed as parameter
            type: Type of edge that is checked
        """
        if type == 'input':
            return node in self.input_edges
        elif type == 'output':
            return node in self.output_edges
        elif type == 'bidirectional':
            return node in self.bidirectional_edges
    
    def is_avaliable_for_input(self, origin_node):
        """
            Checks if the current node is avaliable for a new input edge from that node
        """
        # If there already was a reverse edge and bidirectional edges are not allowed, return False
        if origin_node in self.output_edges and not self.get_num_bidirectional_edges() < self.NUM_BIDIRECTIONAL:
            return False
        elif origin_node in self.input_edges: # If there already was an input edge to that node
            return False
        return self.get_num_inputs() < self.NUM_INPUTS
    
    def is_avaliable_for_output(self, destination_node):
        """
            Checks if the current node is avaliable for a new output edge to that node
        """
        # If there already was a reverse edge and bidirectional edges are not allowed, return False
        if destination_node in self.input_edges and not self.get_num_bidirectional_edges() < self.NUM_BIDIRECTIONAL:
            return False
        elif destination_node in self.output_edges: # If there already was an output edge to that node
            return False
        return self.get_num_outputs() < self.NUM_OUTPUTS
    
    def is_avaliable_for_bidirectional(self, new_node):
        """
            Checks if the current node is avaliable for a new bidirectional edge with that node
            The node must be avaliable for both input and output to the new node
        """
        if self.get_num_bidirectional_edges() >= self.NUM_BIDIRECTIONAL:
            return False
        elif new_node in self.bidirectional_edges:
            return False
        else:
            if self.is_avaliable_for_input(new_node) and self.is_avaliable_for_output(new_node):
                return True
            else:
                return False
    
    def is_node_avaliable(self, new_node, type):
        if type == 'input':
            return self.is_avaliable_for_input(new_node)
        elif type == 'output':
            return self.is_avaliable_for_output(new_node)
        elif type == 'bidirectional':
            return self.is_avaliable_for_bidirectional(new_node)
        
    def can_connect(self, new_node, edge_type, inverse_edge_type):
        """
            Requestor: Node that is requesting a new edge
            New_node: Node that is being requested to connect
            Edge_type: Type of edge that is requested

            They can't connect if:
                They are the same node
                Any of them is not available for that kind of connection to the other node
        """
        if (new_node == self or not self.is_node_avaliable(new_node, edge_type) 
                or not new_node.is_node_avaliable(self, inverse_edge_type)):
            return False
        else:
            return True
    
    def print_edges(self):
        #print(f"El nodo {self.name} tiene {self.get_num_inputs()} aristas de entrada, {self.get_num_outputs()} aristas de salida y {self.get_num_bidirectional_edges()} aristas bidireccionales")
        # Print inputs names
        print("Inputs:")
        for node in self.input_edges:
            if node in self.bidirectional_edges:
                print(f"{node.name} (Bi), free for {self.NUM_BIDIRECTIONAL - node.get_num_bidirectional_edges()} more bidirectional edges")
            else: # Print the available output edges of this input node
                print(f"{node.name}, free for {self.NUM_OUTPUTS - node.get_num_outputs()} more output edges")
        # Print outputs names
        print("Outputs:")
        for node in self.output_edges:
            if node in self.bidirectional_edges:
                print(f"{node.name} (Bi), free for {self.NUM_BIDIRECTIONAL - node.get_num_bidirectional_edges()} more bidirectional edges")
            else:
                print(f"{node.name}, free for {self.NUM_INPUTS - node.get_num_inputs()} more input edges")