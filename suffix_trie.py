#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import networkx as nx
from tikz_helper import TikzDraw, TikzNode, TikzChild, TikzFigure


class SuffixTrie:
    def __init__(self, T, write_tex=False):
        self.write_tex = write_tex
        self.counter = 0
        self.T = T
        self.bottom = "bottom"
        self.root = "#"  # root state is named '#'
        self.Q = [self.bottom, self.root]  # Q: set of states
        self.g = {self.root: {}}  # g: transition function
        self.f = {self.root: self.bottom}  # f: suffix function
        self.draws = [(self.root, self.bottom, len(self.T))]

        self.graph = nx.MultiDiGraph()
        self.graph.add_edge(self.bottom, self.root, label='$\\Sigma$')
        self.graph.add_edge(self.root, self.bottom, label='0', style='dashed')

        self.top = self.root
        self.i = 0
        self.write()

        for i, t in enumerate(T):
            self.i = i
            self.algorithm1(t)

    def write(self, all_sl=False, essen=True):
        if self.write_tex:
            with open(f'strie_{self.T}_out{self.counter}.tex', 'w') as f:
                f.write(str(self.to_tikz_figure(all_sl, essen=essen)))
            self.counter += 1

    def algorithm1(self, t):
        r = self.top
        oldrp = None
        while not self.getTransition(r, t):
            rp = r + t
            self.Q.append(rp)
            self.updateG(r, t, rp)
            self.write()
            if r != self.top:
                self.f[oldrp] = rp
                self.graph.add_edge(oldrp, rp, style='dashed')
                self.draws.append((oldrp, rp, self.i))
                self.write()
            oldrp = rp
            r = self.f[r]
        self.f[oldrp] = self.getTransition(r, t)
        self.graph.add_edge(oldrp, self.getTransition(r, t), style='dashed')
        self.draws.append((oldrp, self.getTransition(r, t), self.i))
        self.write()
        self.top = self.g[self.top][t]

    def updateG(self, s, kp, r):
        if s in self.g:
            self.g[s][kp] = r
        else:
            self.g[s] = {kp: r}
        self.graph.add_edge(s, r, label=f'${kp}$')

    def getTransition(self, s, t):
        # Return s' = g(s, t)
        if s == self.bottom:
            return self.root
        if s in self.g:
            return self.g[s].get(t)

    def to_tikz_figure(self, all_sl=False, essen=True, accept=True):
        def sanitize(x):
            return x.replace('#', 'q').replace('_', 'w')

        def is_essen(node):
            tops = ['#' + self.T[:x] for x in range(len(self.T) + 1)]
            return node in tops or \
                len([y for y in self.f.values() if y == node]) > 1

        def is_accept(node):
            ends = ['#' + self.T[x:self.i + 1] for x in range(len(self.T) + 1)]
            return node in ends

        def dfs_visit(nx_node, tikz_node, no_node_text=False,
                      level=0):
            nx_childs_info = self.graph[nx_node]
            nx_node_childs = adj_list.get(nx_node, [])
            shift_start = (len(nx_node_childs) - 1) * -5
            for i, nx_node_child in enumerate(sorted(nx_node_childs)):
                shift = shift_start + 10 * i
                attr = []
                if essen and is_essen(nx_node_child):
                    attr.append('draw=red')
                if is_accept(nx_node_child):
                    attr.append('double')
                new_tikz_child = TikzChild(
                    TikzNode(
                        text='' if no_node_text else nx_node_child,
                        attr=attr,
                        label=sanitize(nx_node_child),
                        edge_from_parent=True,
                        edge_node=TikzNode(
                            text=f"{nx_childs_info[nx_node_child][0]['label']}",  # NOQA
                            attr=['rectangle', 'draw=green', 'fill=white'] +
                            ([f'xshift={shift}pt'] if shift else[]))))
                tikz_node.childs.append(new_tikz_child)
                dfs_visit(nx_node_child, new_tikz_child.node, no_node_text,
                          level+1)
        adj_list = {x: list(y.values()) for x, y in self.g.items()}
        adj_list['bottom'] = ['#']
        n = TikzNode(label='bottom', pos='current page.north',
                     attr=['yshift=-30pt'])
        dfs_visit('bottom', n, no_node_text=True)

        draws = []
        for i in range(self.i + 1):
            x = '#' + self.T[i:self.i]
            if x not in self.f:
                continue
            y = self.f[x]
            x = sanitize(x)
            y = sanitize(y)
            draws.append(TikzDraw(x, y, attr=['style=sll',
                                              'draw opacity=0.5']))

        for x, y, z in self.draws:
            x = sanitize(x)
            y = sanitize(y)
            if all_sl:
                draws.append(TikzDraw(x, y, attr=['style=sll']))
            else:
                if z == self.i:
                    # bias = 0
                    # opa = ((z + bias) / (self.i + bias))
                    draws.append(TikzDraw(x, y, attr=['style=sll']))
        return TikzFigure(n, draws)

    def printST(self):
        print("Suffix Trie for '" + self.T + "'")
        print("Q: " + str(self.Q))
        print("root: " + str(self.root))
        print("g:")
        print(self.g)
        print("f:")
        print(self.f)


if __name__ == "__main__":
    T = input()
    ST = SuffixTrie(T, write_tex=True)
    ST.write(all_sl=True)
