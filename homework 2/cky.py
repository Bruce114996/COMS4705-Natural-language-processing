"""
COMS W4705 - Natural Language Processing
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        n = len(tokens)
        pie_list = [[[] for x in range(n + 1)] for j in range(n + 1)]
        rules = list(grammar.rhs_to_rules)
        for i in range(n):
            for rule in rules:
                if rule == (tokens[i],):
                    for x in grammar.rhs_to_rules[rule]:
                        pie_list[i][i + 1].append(x[0])
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length
                for k in range(i + 1, j):
                    for rule in rules:
                        if pie_list[i][k] and pie_list[k][j]:
                            for item in pie_list[i][k]:
                                for item_ in pie_list[k][j]:
                                    if rule[0] == item and rule[1] == item_:
                                        for x in grammar.rhs_to_rules[rule]:
                                            pie_list[i][j].append(x[0])
        if 'TOP' in pie_list[0][n]:
            return True
        else:
            return False

    def parse_with_backpointers(self, tokens, grammar):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        prob = defaultdict(dict)
        pie_list = defaultdict(dict)
        rules = list(grammar.rhs_to_rules)
        n=len(tokens)
        for i in range(n):
            for rule in rules:
                if rule == (tokens[i],):
                    for x in grammar.rhs_to_rules[rule]:
                        pie_list[(i, i + 1)][x[0]] = x[1][0]
                        prob[(i, i + 1)][x[0]] = math.log(x[2])
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length
                for k in range(i + 1, j):
                    for rule in rules:
                        if pie_list[(i, k)] and pie_list[(k, j)]:
                            for item in pie_list[(i, k)].keys():
                                for item_ in pie_list[(k, j)].keys():
                                    if rule[0] == item and rule[1] == item_:
                                        for x in grammar.rhs_to_rules[rule]:
                                            data = ((item, i, k), (item_, k, j))
                                            if x[2] != 0:
                                                probability = math.log(x[2]) + prob[(i, k)][item] + prob[(k, j)][item_]
                                            else:
                                                probability = 0
                                            if (i, j) not in prob.keys() or x[0] not in prob[(i, j)]:
                                                prob[(i, j)][x[0]] = probability
                                                pie_list[(i, j)][x[0]] = data
                                            else:
                                                if probability > prob[(i, j)][x[0]]:
                                                    prob[(i, j)][x[0]] = probability
                                                    pie_list[(i, j)][x[0]] = data
                                            #print('(i,j)=(', i, ',', j, ')', 'x[0] is', x[0], prob[(i, j)][x[0]])

        return pie_list, prob
        # TODO, part 3


def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
    leaf = chart[(i, j)][nt]
    if j-i==1:
        return (nt, leaf)
    left_ = leaf[0]
    right_ = leaf[1]
    left_tree = get_tree(chart, left_[1], left_[2], left_[0])
    right_tree = get_tree(chart, right_[1], right_[2], right_[0])
    return (nt, left_tree, right_tree)

if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file)
        parser = CkyParser(grammar)
        toks =['miami', 'flights','cleveland', 'from', 'to','.']
        print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks,grammar)
        print(probs[(0,3)]['NP'])
        print(check_table_format(table))
        print(check_probs_format(probs))




