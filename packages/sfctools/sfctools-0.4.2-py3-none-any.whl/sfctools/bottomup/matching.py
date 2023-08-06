__version__ = "0.3"
__author__ = "Thomas Baldauf"
__email__ = "thomas.baldauf@dlr.de"
__license__ = "MIT"
__birthdate__ = '15.11.2021'
__status__ = 'dev' # options are: dev, test, prod


from abc import ABCMeta,abstractmethod
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from ..core.singleton import Singleton
import warnings

class MarketMatching(metaclass=ABCMeta):
    """
    Meta class for market matching. This is a basic framework for a list of demanders and suppliers who are matched decentrally and 
    registered centrally. This can be thought of as a graph (nodes and edges) of agents.
    """

    def __init__(self):
        """
        constructor for market matching

        :param demand_list: list of demand agents
        :param supply_list: list of supply agents
        """

        super().__init__()

        # matching map between demanders and suppliers
        self.graph = nx.MultiDiGraph()
        self._demand_list = []
        self._supply_list = []

    @property
    def supply_list(self):
        """
        Get list of supply agents. Filters suppliers who are not bankrupt
        
        :return: list of agents
        """

        my_list = []

        for agent in self._supply_list:
            if not agent.bankrupt:
                my_list.append(agent)

        return my_list

    @property
    def demand_list(self):
        """
        Get list of demand agents. Filters demanders who are not bankrupt
        
        :return: list of agents
        """

        my_list = []
        for agent in self._demand_list:
            if not agent.bankrupt:
                my_list.append(agent)

        return my_list

    def add_demander(self,agent):
        """
        Add demand agent as node in the graph

        :param agent: instance to add on demand side
        """
        self.graph.add_node(agent)
        self._demand_list.append(agent)

    def add_supplier(self, agent):
        """
        Add supply agent as node in the graph

        :param agent: instance to add on demand side
        """
        self.graph.add_node(agent)
        self._supply_list.append(agent)

    @abstractmethod
    def rematch(self):
        """
        rematch the supply and demand agents, i.e.
        update the matching map. Has to be overridden as it is abstract.
        """
        pass

    def clear(self):
        """
        Removes all edges from the current graph.
        """

        e = list(self.graph.edges())
        self.graph.remove_edges_from(e)

    def get_supply_data(self,agent):
        """
        get all suppliers  + info for agent

        :param agent: reference agent
        :return: dict containing data
        """
        in_edges = self.graph.in_edges(agent)
        supply_data = {}
        for edge in in_edges:
            supply_data[edge[0]] = next(iter(self.graph.get_edge_data(*edge).keys()))
        return supply_data

    def get_demand_data(self,agent):
        """
        get all demanders + info for agent

        :param agent: reference agent
        :return: dict containing data
        """
        in_edges = self.graph.out_edges(agent)
        supply_data = {}
        for edge in in_edges:
            supply_data[edge[1]] = next(iter(self.graph.get_edge_data(*edge).keys()))
        return supply_data

    def get_suppliers_of(self,agent) -> list:
        """
        get list of agents supplying to agent

        :param agent: reference agent
        :return: list of agents
        """
        return list(self.graph.pred[agent].keys())

    def get_demanders_from(self,agent) -> list:
        """
        get list of agents demanding from agent

        :param agent: reference agent
        :return: list of agents
        """
        return list(self.graph[agent].keys())

    def link_agents(self,supply_agent,demand_agent,val):
        """
        link a connection between demand and supply with weight val

        :param supply_agent: agent instance, supply 
        :param demand_agent: agent instance, demand
        :param val: a value that is stored in the data dict for this link
        """
        self.graph.add_edge(supply_agent,demand_agent,weight=val)

    def unlink_agents(self,supply_agent,demand_agent):
        """
        unlink a connection 

        :param supply_agent: agent instance, supply 
        :param demand_agent: agent instance, demand
        """
        try:
            self.graph.remove_edge(supply_agent,demand_agent)
        except Exception as e:
            warnings.warn(str(e))

    def get_value(self,agent_from,agent_to):
        try:
            return self.graph[agent_from][agent_to]["weight"]
        except:
            return None
        
    def plot(self):
        """
        plot the current matching situation as a network graph
        """
        
        plt.figure()
        nx.draw(self.graph,node_size=20,node_color='#ff4271')
        plt.show()
    
    def plot_weighted(self,my_layout=None,arrows=False):
        """
        plot the current matching situation as a network graph, with edge thickness matching the weights
        Suppliers re plotted in red, demanders in blue. 
        
        :param my_layout: networkx graph layout
        :param arrows: show the arrows
        """
        widths = nx.get_edge_attributes(self.graph, 'weight')
        nodelist = self.graph.nodes()
        
        colors = []
        for node in nodelist:
            # print("node",node)
            if node in self._demand_list:
                colors.append("blue")
                
            else:
                colors.append("red")
        
        plt.figure(figsize=(5,5))
        if my_layout is None:
            my_layout = nx.drawing.layout.spring_layout
        pos = my_layout(self.graph) # ,weights="weight")
        nx.draw_networkx_nodes(self.graph,pos,
                       nodelist=nodelist,
                       node_size=20,
                       node_color=colors,
                       alpha=1.0)
        nx.draw_networkx_edges(self.graph,pos,
                       edgelist = widths.keys(),
                       width=list(widths.values()),
                       edge_color='black',
                       alpha=1.0,
                       arrows=arrows)
        plt.box(False)
        plt.show()