"""
This is a boilerplate pipeline 'mdp'
generated using Kedro 0.17.6
"""


import pandas as pd
from thefuzz import fuzz
from typing import List, Dict, Type


def tratamento(data: pd.DataFrame) -> pd.DataFrame:
    """
    tratamento
    """
    cores = {
        "azul": "darkblue",
        "verde": "green",
        "vermelha": "red",
        "amarela": "beige",
        "lilas": "purple",
        "prata": "lightgray",
    }

    data["cor"] = data["line"].apply(
        lambda x: cores[
            sorted(x.strip("[]").replace("'", "").replace(" ", "").split(","))[0]
        ]
    )

    return data


def fuzz_string(estacao:str, serie:pd.Series) -> str:
    """
    fuzz_string
    """
    ord_serie = serie.apply(
        lambda x: (x, fuzz.token_sort_ratio(x, estacao))
    ).values
    return sorted(ord_serie, key=lambda t: t[1], reverse=True)[0][0]


def grafo(data: pd.DataFrame) -> Dict:
    """
    grafo
    """
    g = {
        r["station"]: {
            "neigh": r["neigh"].strip("[]").replace("'", "").replace(" ", "").split(","),
            "pos": (r["lat"], r["lon"]),
        }
        for _, r in data.iterrows()
    }
    return g


def funcao_custo(s:List, S:List) -> float:
    """
    funcao_custo
    """
    sy, sx = s[0], s[1]
    Sy, Sx = S[0], S[1]
    return ((sx - Sx) ** 2 + (sy - Sy) ** 2) ** (0.5)


def custo(mdp_grafo: Dict) -> Dict:
    """
    custo
    """
    c = dict()
    for s in mdp_grafo:
        for S in mdp_grafo[s]["neigh"]:
            pos_s = mdp_grafo[s]["pos"]
            pos_S = mdp_grafo[S]["pos"]
            c[(s, S)] = funcao_custo(pos_s, pos_S)
    return c


class Node:
    """
    class Node
    """

    def __init__(self, state, cost, parent=None, action=None):
        self.state = state
        self.cost = cost
        self.parent = parent
        self.action = action

        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    def __repr__(self):
        return "<Node {}>".format(self.state)


class Stack:
    """
    class Stack
    """

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def __len__(self):
        return len(self.items)


class Problem(object):
    """
    class Problem
    """

    def __init__(self, data, s0="luz", s="luz"):
        self.states = grafo(data)
        self.costs = custo(self.states)
        self.goal = s
        self.start = s0

    def start(self):
        return self.start

    def is_state(self, state):
        return state in self.states

    def actions(self, state):
        if state in self.states:
            return self.states[state]["neigh"]
        else:
            return None

    def next_state(self, state, action):
        if action in self.actions(state):
            return action
        else:
            return None

    def is_goal_state(self, state):
        return state == self.goal

    def cost(self, state, action):
        return self.costs[(state, action)]


def depthFirstSearch(problem):
    """
    depthFirstSearch
    """
    node = Node(problem.start, 0)
    frontier = Stack()
    frontier.push(node)
    explored = set()
    while len(frontier) > 0:
        node = frontier.pop()
        explored.add(node.state)

        if problem.is_goal_state(node.state):
            return node

        for act in problem.actions(node.state):
            next_state = problem.next_state(node.state, act)
            if next_state not in explored:
                cost = problem.cost(node.state, act) + node.cost
                frontier.push(Node(next_state, cost, node, act))
    return None


def carrega_mdp(data:pd.DataFrame, metro_from:str, metro_to:str) -> Type:
    """
    carrega_mdp
    """
    return Problem(data, metro_from, metro_to)


def resolve_mdp(mdp:Type) -> Dict:
    """
    resolve_mdp
    """
    parent = depthFirstSearch(mdp)
    estacoes = list()

    while parent != None:
        estacoes.append( parent.state )
        parent = parent.parent

    return {"estacoes": estacoes[::-1]}