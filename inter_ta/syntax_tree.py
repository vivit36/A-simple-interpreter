import graphviz

graph_cnt = 1


class Node(object):
    def __init__(self, t='const', val=None,  ch=None, no=None, pos=None):
        self.type = t
        self.value = val
        self.child = ch or []
        self.lineno = no
        self.lexpos = pos

    def __repr__(self):
        return f'{self.type} {self.value}'

    def graphviz_tree(self):
        def format_string(node, label=None):
            if label is None:
                return f"<<FONT POINT-SIZE=\"10\" COLOR=\"blue\">{node.type}</FONT>" \
                       f"<br/><FONT POINT-SIZE=\"10\" COLOR=\"black\">{node.value}</FONT>" \
                       f"<br/><FONT POINT-SIZE=\"10\" COLOR=\"black\">Pos {node.lineno}</FONT>>"
            else:
                return f"<<FONT POINT-SIZE=\"10\" COLOR=\"red\">{label}</FONT>>"

        def recursive(cur_node):
            global graph_cnt
            if cur_node is None:
                return
            if isinstance(cur_node.child, list):
                n_lst = list()
                for child in cur_node.child:
                    n_lst.append(recursive(child))

                cur_sum = 'N' + str(graph_cnt)
                graph_cnt += 1
                dot.node(cur_sum, label=format_string(cur_node))
                for el in n_lst:
                    dot.edge(cur_sum, el)
                return cur_sum
            elif isinstance(cur_node.child, Node):
                v_sum = recursive(cur_node.child)
                cur_sum = 'N' + str(graph_cnt)
                graph_cnt += 1
                dot.node(cur_sum, label=format_string(cur_node))
                dot.edge(cur_sum, v_sum)
                return cur_sum
            elif isinstance(cur_node.child, dict):
                k_lst = list()
                for key, value in cur_node.child.items():
                    key_sum = 'N' + str(graph_cnt)
                    dot.node(key_sum, label=format_string(cur_node, key))
                    graph_cnt += 1
                    k_lst.append(key_sum)

                    val_sum = recursive(value)
                    dot.edge(key_sum, val_sum)

                cur_sum = 'N' + str(graph_cnt)
                graph_cnt += 1
                dot.node(cur_sum, label=format_string(cur_node))

                for el in k_lst:
                    dot.edge(cur_sum, el)

                return cur_sum

        dot = graphviz.Digraph('stree', filename='../stree',
                               node_attr={'color': 'lightblue2', 'style': 'filled'})
        recursive(self)
        dot.view()