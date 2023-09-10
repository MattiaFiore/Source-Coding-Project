from itertools import product
import math

def x_pos(elem, length):
  x_pos = 0
  for i in range(len(elem)):
    if elem[i] == '0':
      x_pos -= (2**(-i))
    else:
      x_pos += (2**(-i))
  return x_pos

def create_blocks(symbols, length):
  return list(product(symbols, repeat = length))

def gen_dict(groups, probability):
  return { j:math.prod([probability[i] for i in j]) for j in groups}


def huffman(dictionary):
  groups = [Group(j,k) for j,k in dictionary.items()]

  while len(groups) > 1:

    # sort

    groups.sort(key = lambda x: x.get_probability(), reverse = True)

    # take last two elements

    elem1 = groups.pop(-1)
    elem2 = groups.pop(-1)

    # Add bits

    if elem1.get_group() != 'MORE':
        elem1.add_bit("1")
    else:
        for i in elem1.get_more():
          i.add_bit("1")


    if elem2.get_group() != 'MORE':
        elem2.add_bit("0")
    else:
        for i in elem2.get_more():
            i.add_bit("0")

    # Combine elements and add new elements

    combined = elem1 + elem2
    groups.append(combined)

  # After the while loop we have just one element inside
  # the group list and this element will have all all the
  # groups inside the attribute more:

  dictionary = {i.get_group(): i.get_code() for i in groups[0].get_more()}
  return dictionary

class Group():

  def __init__(self, group, probability, code = "", more = []):

    self.group = group
    self.probability = probability
    self.code = code
    self.more = more

  def add_bit(self, bit):
    self.code = bit + self.code

  def __add__(self, element):

    # Probability sum of elements
    probability = self.get_probability() + element.get_probability()

    # list of elements
    more = []
    if self.get_group() == 'MORE':
      more += self.get_more()
    else:
      more.append(self)

    if element.get_group() == 'MORE':
      more += element.get_more()
    else:
      more.append(element)

    return Group(group = 'MORE', probability = probability, code = 'MORE', more = more)


  def get_probability(self):
    return self.probability

  def get_group(self):
    return self.group

  def get_code(self):
    return self.code

  def get_more(self):
    return self.more

  def __str__(self):
    return f'Group: {self.get_group()}\nProbability: {self.get_probability()}\nCode: {self.get_code()}\nMore: {self.get_more()}'


class Node():

  def __init__(self, string = '', parent = None, data = None):

    self.string = string
    self.data = data
    self.parent = parent
    self.left = None
    self.right = None

  def get_string(self):
    return self.string

  def get_left(self):
    return self.left

  def get_right(self):
    return self.right

  def get_data(self):
    return self.data

  def set_string(self, new_string):
    self.string = new_string

  def set_left(self, new_left):
    self.left = new_left

  def set_right(self, new_right):
    self.right = new_right

  def set_data(self, data):
    self.data = data

  def __str__(self):
    return self.get_string()

class Tree():

  def __init__(self):
    # Root is a node with no parent
    # no left no right child at the moment
    # No string attached

    self.root = Node('Root')
    self.node_names = [self.root.get_string()]
    self.edges = []

  def search(self, father):

    # father is a string
    node = self.get_root()

    if father == 'Root':
      return self.get_root()

    for i in father:
      if i == '0':
        node = node.get_left()
        pass
      else:
        node = node.get_right()

    return node

  def add_child(self, father, child, data=None):

    """
    Father: is the data string
    Child: is the data string

    Our logic will be 0 on the left and 1 on the right

                      Root
                   /        \
                  0          1
                /   \      /   \
               00   01    10    11


    """
    # We first search for the father
    father_node = self.search(father)

    if child[-1] == '0':
      father_node.set_left(Node(string = child, parent = father_node, data = data))

    else:
      father_node.set_right(Node(string = child, parent = father_node, data = data))

    self.node_names.append(child)
    self.edges.append((child, father))

  def is_node_present(self, node):
    return node in self.get_node_names()

  def get_node_names(self):
    return self.node_names

  def get_edges(self):
    return self.edges

  def get_root(self):
    return self.root




