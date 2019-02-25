#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Suffix tree implementation by
# https://github.com/tommy91/Algorithms/blob/master/suffixTree.py

import networkx as nx
from collections import defaultdict
import pydot


class TikzNode():
    def __init__(self, childs=None, text='', label='',
                 edge_from_parent=False,
                 edge_from_parent_attr=None,
                 edge_node=None, attr=None,
                 pos=''):
        self.attr = attr or []
        self.edge_from_parent_attr = edge_from_parent_attr or []
        self.childs = childs or []
        self.edge_from_parent = edge_from_parent
        self.edge_node = edge_node
        self.label = label
        self.text = text
        self.pos = pos

    def __str__(self):
        label = f'({self.label})' if self.label else ''
        attr = ','.join(self.attr)
        attr = f'[{attr}]' if attr else ''
        efp_attr = ','.join(self.edge_from_parent_attr)
        efp_attr = f'[{efp_attr}]' if efp_attr else ''
        edge_node = str(self.edge_node) if self.edge_node else ''
        efp = 'edge from parent' if self.edge_from_parent else ''
        pos = f'at ({self.pos})' if self.pos else ''
        return f'node{attr}{label}{pos} {{ {self.text} }} ' + \
            ' '.join(str(x) for x in self.childs) + \
            f'{efp}{efp_attr}' + ' ' + edge_node


class TikzChild():
    def __init__(self, node=None):
        self.node = node

    def __str__(self):
        return f'child {{ {self.node} }}'


class TikzDraw():
    def __init__(self, source_label='', target_label='', attr=None):
        self.source_label = source_label
        self.target_label = target_label
        self.attr = attr or []

    def __str__(self):
        attr = ','.join(self.attr)
        attr = f'[{attr}]' if attr else ''
        return f'\\draw{attr}' + \
            f'({self.source_label}) to ({self.target_label});'


class SuffixTreeTikzFigure():
    def __init__(self, node, draws=None):
        self.node = node
        self.draws = draws or []

    def __str__(self):
        return '\\' + str(self.node) + ';' + \
            ''.join(str(x) for x in self.draws)


def bar(s):
    return ''.join(c + '\u0305' for c in s)


class SuffixTree:

    def __init__(self, T, write_tex=False):
        self.write_tex = write_tex
        self.counter = 0
        self.graph = nx.MultiDiGraph()
        self.suffix_links = {}
        self.bottom = "bottom"
        self.root = "#"  # root state is named '#'
        self.Qp = [self.bottom, self.root]  # Q': set of states
        # self.graph.add_node(self.bottom)
        # self.graph.add_node(self.root)

        self.gp = {self.root: {}}  # g': transition function
        self.graph.add_edge(self.bottom, self.root, label='$\\Sigma$')
        self.fp = {self.root: self.bottom}  # f': suffix function
        self.suffix_links[self.root] = self.bottom
        self.T = T
        self.algorithm2()

    def write(self):
        if self.write_tex:
            with open(f'st_{self.T}_out{self.counter}.tex', 'w') as f:
                self.counter += 1
                f.write(str(self.to_tikz_figure()))

    def algorithm2(self):

        # Builds STree(T) for string T
        # one char at time
        # with one scan left to right
        s = self.root
        k = 0
        self.write()
        for i in range(len(self.T)):
            # write_dot(self.graph, f'out{i}.dot')
            # self.printST()
            if k == i:
                active_state = '[#]'
            else:
                active_state = f'{self.T[k: i]}'
                active_state = f'[{bar(active_state)}]'
            # i-th Endpoint is (i+1)-th Active Point
            (s, k) = self.update(s, *(k, i))
            (s, k) = self.canonize(s, *(k, i))

    def update(self, s, k, i):
        # Transforms STree(T(i-1)) into STree(T(i))
        # by inserting the ti-transitions in the second group:
        # from Active Point to Endpoint.
        # Returns a reference pair for sj' (the Endpoint)

        # (s,(k,i-1)) = reference pair for the Active Point

        ti = self.T[i]

        oldr = self.root

        (is_end_point, r) = self.testAndSplit(s, *(k, i-1), ti)

        while not is_end_point:
            # create new state r'
            rp = r + str(i) + ti + "_"  # '_' means a leaf
            self.Qp.append(rp)

            # add transition g'(r, (i, inf)) = r'
            self.updateGP(r, (i, len(self.T)-1), rp)
            self.write()

            if oldr != self.root:
                # XXX: suffix link might already be there due to
                # possible canonization of r
                new = False
                if oldr not in self.fp or self.fp[oldr] != r:
                    new = True
                self.fp[oldr] = r  # create suffix link
                if new:
                    self.suffix_links[oldr] = r
                    self.graph.add_edge(oldr, r, style='dashed')
                    self.write()
            oldr = r

            # fp[s] follow the suffix link
            (s, k) = self.canonize(self.fp[s], *(k, i-1))

            (is_end_point, r) = self.testAndSplit(s, *(k, i-1), ti)

        if oldr != self.root:
            self.fp[oldr] = s
            self.suffix_links[oldr] = s
            self.graph.add_edge(oldr, s, style='dashed')
            self.write()

        return (s, k)

    def updateGP(self, s, kp, r):
        if s in self.gp:
            self.gp[s][kp] = r
        else:
            self.gp[s] = {kp: r}
        self.graph.add_edge(
            s, r,
            label=f'${self.T[kp[0]:kp[1]+1]}$ \\\\ $({kp[0]+1},{kp[1]+1})$')

    def getTransition(self, s, t):
        # Return the t-transition from s assuming it exists.
        if s == self.bottom:
            return ((-1, -1), self.root)
        for (kp, pp) in self.gp[s]:
            if self.T[kp] == t:
                sp = self.gp[s][(kp, pp)]
                return ((kp, pp), sp)

    def existsTransition(self, s, t):
        # Return True if the t-transition from s exists or False.
        if s == self.bottom:
            return True
        for (kp, pp) in self.gp[s]:
            if self.T[kp] == t:
                return True
        return False

    def testAndSplit(self, s, k, p, t):
        """
        Tests whether or not a state with canonical reference pair
        (s,(k,p)) is the endpoint,
        that is, a state that in STrie(T(i-1)) would have a ti-transition.
        Symbol ti is given as input parameter t.
        The test result is returned as the first output parameter.
        If (s,(k,p)) is not the endpoint, then state (s,(k,p)) is made explicit
        (if not already so) by splitting a transition.
        The explicit state is returned as the second output parameter.
        """
        if k <= p:
            # s is implicit
            # g'(s,(k',p')) = s'
            ((kp, pp), sp) = self.getTransition(s, self.T[k])

            # p - k is length of w, the string spelled from s to r
            # r is the (im|ex)plicit state referred by (s,(k,p))
            if t == self.T[kp + (p - k) + 1]:
                # endpoint (the first s_j that has a t_i transition)
                return (True, s)
            else:
                # not endpoint
                self.graph.remove_edge(s, self.gp[s][(kp, pp)])
                del self.gp[s][(kp, pp)]
                # new explicit state r
                # XXX: why here can use kp? (kp != k)
                # kp = k
                r = s + str(kp) + self.T[kp:kp+(p-k)+1]

                self.Qp.append(r)
                self.updateGP(s, (kp, kp+(p-k)), r)
                self.updateGP(r, (kp+(p-k)+1, pp), sp)
                self.write()

                return (False, r)
        else:
            # s is explicit
            if self.existsTransition(s, t):
                return (True, s)
            else:
                return (False, s)

    def canonize(self, s, k, p):
        """ # NOQA
        Given a reference pair (s,(k,p)) for some state r,
        it finds and returns state s' and left link k'
        such that (s', (k', p)) is the canonical reference pair for r.
        State s' is the closest explicit ancestor of r
        (or r itself if r is explicit).
        Therefore the string that leads from s' to r must be
        a suffix of the string t_k...t_p that leads from s to r.
        Hence the right link p does not change but the left link k can become
        k' s.t. k' > k.
        """
        if p < k:
            # s already explicit
            return (s, k)
        else:
            # g'(s,(k',p')) = s'
            ((kp, pp), sp) = self.getTransition(s, self.T[k])

            while pp - kp <= p - k:
                # Move on closer to r
                k = k + (pp - kp) + 1
                s = sp
                if k <= p:
                    ((kp, pp), sp) = self.getTransition(s, self.T[k])
            return (s, k)

    def printST(self):
        print("Suffix Tree for '" + self.T + "'")
        print("Q': " + str(self.Qp))
        print("root: " + str(self.root))
        print("g':")
        print(self.gp)
        print("f':")
        print(self.fp)

    def get_ranks(self, use_length_as_rank=False):
        # BFS to get the depth of all nodes.
        if use_length_as_rank:
            ranks = defaultdict(list)
            q = [(self.root, 0)]
            while q:
                q_new = []
                for e, curr_len in q:
                    if self.gp.get(e):
                        for k, v in self.gp[e].items():
                            length = k[1] - k[0] + 1
                            length_new = curr_len + length
                            ranks[length_new].append(v)
                            q_new.append((v, length_new))
                q = q_new
            return ranks
        else:
            ranks = defaultdict(list)
            q = [self.root]
            rank = 1
            while q:
                for e in q:
                    if self.gp.get(e):
                        ranks[rank] += list(self.gp[e].values())
                q = ranks[rank] if rank in ranks else []
                rank += 1
            return ranks

    def to_dot(self, filename='out.dot', use_length_as_rank=False):
        self.counter += 1
        # Since networkx doesn't provide a mechanism setting the rank,
        # I have to do it manually
        ranks = self.get_ranks(use_length_as_rank)
        pdot = nx.drawing.nx_pydot.to_pydot(self.graph)
        for k, v in ranks.items():
            sg = pydot.Subgraph()
            sg.set_rank('same')
            for e in v:
                sg.add_node(pydot.Node(e))
            pdot.add_subgraph(sg)
        pdot.write(filename)

    def to_tikz_figure(self):
        def sanitize(x):
            return x.replace('#', 'q').replace('_', 'w')

        def dfs_visit(nx_node, tikz_node, no_node_text=False):
            nx_childs_info = self.graph[nx_node]
            nx_node_childs = adj_list.get(nx_node, [])
            shift_start = (len(nx_node_childs) - 1) * -5
            for i, nx_node_child in enumerate(sorted(nx_node_childs)):
                shift = shift_start + 10 * i
                new_tikz_child = TikzChild(TikzNode(
                    text='' if no_node_text else nx_node_child,
                    label=sanitize(nx_node_child),
                    edge_from_parent=True,
                    edge_node=TikzNode(
                        text=f"{nx_childs_info[nx_node_child][0]['label']}",
                        attr=['rectangle', 'draw=green', 'fill=white'] +
                        ([f'xshift={shift}pt'] if shift else[]) +
                        (['align=center']
                            if nx_node_child != '#' else []))))
                tikz_node.childs.append(new_tikz_child)
                dfs_visit(nx_node_child, new_tikz_child.node, no_node_text)
        adj_list = {x: list(y.values()) for x, y in self.gp.items()}
        adj_list['bottom'] = ['#']
        n = TikzNode(label='bottom', pos='current page.north',
                     attr=['yshift=-30pt'])
        dfs_visit('bottom', n, no_node_text=True)

        draws = []
        for x, y in self.fp.items():
            x = sanitize(x)
            y = sanitize(y)
            draws.append(TikzDraw(x, y, attr=['style=sll']))
        return SuffixTreeTikzFigure(n, draws)


if __name__ == "__main__":
    T = input()
    # ST = SuffixTree(T, write_tex=True)
    ST = SuffixTree(T)
    ST.printST()
