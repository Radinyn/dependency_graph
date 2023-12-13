import re
import networkx as nx
import matplotlib.pyplot as plt
import contextlib


def parse_input(filepath="input.txt"):
    with open(filepath, "r") as f:
        data = f.read().strip().split("\n")
    data = [x.strip() for x in data]
    word = data.pop()
    instructions = data
    return instructions, word


# Map letter to number (ascii index)
def word_to_index_list(word: str):
    return list(map(lambda l: ord(l) - ord("a"), word))


# Convert into pure dependency format
# "x=2y+3z" -> ['x', 'y', 'z']
def parse_instructions(instructions):
    clean = lambda s: re.sub(r"[/\+-=\*,.;@#?!&$0-9]+\ *", " ", s).split()
    return list(map(clean, instructions))


def generate_dependence_sets(instructions):
    D = set()
    I = set()

    for i, (h0, *t0) in enumerate(instructions):
        for j, (h1, *t1) in enumerate(instructions):
            if (h0 in t1) or (h1 in t0):
                D.add((i, j))
            else:
                I.add((i, j))

    return D, I


# Get FNF using the snowball algorithm
def snowball_algorithm(word, D):
    stacks = {letter: [] for letter in word}

    for letter in reversed(word):
        for i in set(word):
            if i == letter:
                stacks[i].append(letter)
            elif (letter, i) in D:
                stacks[i].append(None)

    fnf = []
    while any(len(s) != 0 for s in stacks.values()):
        letters = set()

        for stack in stacks.values():
            if len(stack) > 0 and stack[-1] != None:
                letters.add(stack.pop())

        for letter in letters:
            for i, stack in stacks.items():
                if i == letter:
                    continue
                if (letter, i) in D:
                    stack.pop()

        fnf.append(letters)
    return fnf


def generate_graph(fnf, D):
    G = nx.DiGraph()

    for layer, group in enumerate(fnf):
        for letter in group:
            ascii = chr(letter + ord("a"))
            node = (ascii, layer)
            G.add_node(node)

    # Add dependency edges only to the nodes in further layers
    for layer0, group in enumerate(fnf):
        for letter in group:
            ascii0 = chr(letter + ord("a"))
            node = (ascii, layer)

            for ascii1, layer1 in G.nodes():
                if layer1 <= layer0:
                    continue
                if (ascii0, layer0) == (ascii1, layer1):
                    continue

                if (letter, ord(ascii1) - ord("a")) in D:
                    G.add_edge((ascii0, layer0), (ascii1, layer1))

    # Remove redundant dependency edges
    edges = list(G.edges())
    for edge in edges:
        start, end = edge
        G.remove_edge(start, end)
        if not nx.has_path(G, start, end):
            G.add_edge(start, end)

    return G


def print_twoD(twoD):
    for lst in twoD:
        print("(", end="")
        for i, letter in enumerate(lst):
            ascii = chr(letter + ord("a"))
            print(ascii, end="")
            if i != len(lst) - 1:
                print(" ", end="")
        print(")", end=" ")
    print()


if __name__ == "__main__":
    instructions, word = parse_input()
    instructions = parse_instructions(instructions)
    word = word_to_index_list(word)

    D, I = generate_dependence_sets(instructions)
    fnf = snowball_algorithm(word, D)

    G = generate_graph(fnf, D)
    G = nx.relabel_nodes(G, lambda node: node[0] + str(node[1]))

    # Silence anoying pydot stderr
    with contextlib.redirect_stderr(None):
        pos = nx.nx_pydot.graphviz_layout(G, prog="dot")

    print("D = ", end="")
    print_twoD(D)
    print()

    print("I = ", end="")
    print_twoD(I)
    print()

    print("FNF = ", end="")
    print_twoD(fnf)
    print()

    nx.draw(G, pos=pos)
    nx.draw_networkx_labels(G, pos=pos, labels={node: node[0] for node in G.nodes()})
    plt.show()
