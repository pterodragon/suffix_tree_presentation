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


class TikzFigure():
    def __init__(self, node, draws=None):
        self.node = node
        self.draws = draws or []

    def __str__(self):
        return '\\' + str(self.node) + ';' + \
            ''.join(str(x) for x in self.draws)
