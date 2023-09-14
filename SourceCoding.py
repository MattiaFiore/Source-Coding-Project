from itertools import product
import math
from math import ceil, log2, prod

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

def interval(probabilites, C, seq, symbols):

    s_n = 0
    l_n = 1

    for k in seq:
        # j is the index
        #k is the symbol
        index = symbols.index(k)
        s_n = s_n + l_n*C[index]
        l_n = l_n*probabilites[index]

    return s_n, l_n

def conv_bit(x, n):

    bits = ""
    val = x
    for i in range(n):
        val *= 2
        if val<1:
            bits += '0'
        else:
            bits += '1'
            val -= 1

    return bits

def encode_shannon_type_length(probabilities, C, seq, symbols):

    s,l = interval(probabilities, C, seq, symbols)
    print(f's: {s}\nl: {s+l}')
    p = 1
    for i in seq:
        p *= probabilities[symbols.index(i)]

    L = ceil(log2(1/p))
    bits = conv_bit(s, L)
    return bits

def encode_with_sn(probabilities, C, seq, symbols):
    s,l = interval(probabilities, C, seq, symbols)
    print(f's: {s}\nl: {s+l}')
    p = 1
    for i in seq:
        p *= probabilities[symbols.index(i)]

    L = ceil(log2(1/p))
    s = s + 2**(-L)
    bits = conv_bit(s, L)
    return bits

def encode_arithmetic(probabilities, C, seq, symbols, show=False):
    s,l = interval(probabilities, C, seq, symbols)
    if show == True: 
      print(f's: {s}\nl: {s+l}')
    p = 1
    for i in seq:
        p *= probabilities[symbols.index(i)]

    L = ceil(log2(1/p)) + 1
    s = s + 2**(-L)
    bits = conv_bit(s, L)
    return bits

def compute_length(probabilities, symbol, symbols):
  # you get a simble like: x1 x2 x2
  # you compute p(x1) * p(x2) * p(x3)

  '''
  p = 1
  for i in symbol:

    p *= probabilities[symbols.index(i)]

  L = ceil(log2(1/p)) + 1
  return L

  '''
  p = prod([probabilities[symbols.index(i)] for i in symbol])
  L = ceil(log2(1/p)) + 1

  return L

def arithmetic_decode(symbols, probabilities, block_size, encoded_seq):

  prova = Interval(block_size, probabilities, symbols)
  bit_count = 0
  offset = 0


  for i in range(len(encoded_seq)):
    flag = False

    if i + offset > len(encoded_seq)-1:
        break

    prova.update(encoded_seq[i +  offset])


    bit_count += 1

    if len(prova.feasible_range) == 2:
        flag = prova.decode(i)

    if flag == True:
        # if you decode the symbol
        # you can compute how many bits you need
        # then you can add an offset to the reading

        L = compute_length(probabilities, prova.decoded_seq[prova.symbol_index-1], symbols)
        if L > bit_count:

          offset += L-bit_count


        bit_count = 0

  return "".join(prova.decoded_seq)
  
  
class Interval():

  def __init__(self, groups_len, probabilities, symbols):


    # cumulative is a modified with respect to the theoric one
    # since we need the 1 for rescaling the ranges
    self.cumulative = [sum(probabilities[:i]) for i in range(0,len(probabilities)+1)] #is fixed
    self.complete_range = self.cumulative.copy()
    # complete_range is used just to get the index positions after
    # trimming to just one possible range
    self.feasible_range = self.cumulative.copy()

    self.probabilities = probabilities
    self.symbols = symbols

    self.decoded_seq = [''] # [symbol1, symbol2, ...]
    self.symbol_index = 0 # index of the symbols

    self.range = [0,1] # computed range
    self.exponent = -1
    self.groups_len = groups_len


  def trim_ranges(self):

    indice_min = 0
    indice_max = len(self.feasible_range)

    for i in range(len(self.feasible_range)-1):
      if self.range[0] >= self.feasible_range[i+1]:
        # se l'intervallo è più piccolo dell'estremo destro dell'intervallo
        indice_min += 1

    for i in range(len(self.feasible_range), 0, -1):
      if self.range[1] <= self.feasible_range[i-1]:
        # se è più piccolo dell'estremo sinistro dell'intervalo
        indice_max -= 1

    self.feasible_range = self.feasible_range[indice_min:indice_max+1]

  def trim_ranges_opt(self, bit):

    if bit == '0':
      self.feasible_range = [i for i in self.feasible_range if i < self.range[1]]
      print(self.feasible_range)
      
    else: 
      self.feasible_range = [i for i in self.feasible_range if i > self.range[0]]
      print(self.feasible_range)
      
      

  def reset(self):

    self.symbol_index += 1
    self.decoded_seq.append('')
    self.range = [0,1]
    self.exponent = -1
    self.complete_range = self.cumulative.copy()
    self.feasible_range = self.cumulative.copy()

  def update(self, bit):

      # verify is the bit inserted is 1 or 0 a update the interval
      if bit == '0':
          self.range[1] -= 2**self.exponent
      else:
          self.range[0] += 2**self.exponent

      #update the count
      self.exponent -= 1

      # verify which intervals are feasible
      # now we need to trim the
      self.trim_ranges_opt(bit)

  def decode(self, bit):

    flag = True

    while flag:

      # we find the letter which is immediately decodable by comparing the
      # equivalence between the feasible interval and the total posssible intervals
      # If we are able to decode a letter we could be able to decode another one

      if len(self.decoded_seq[self.symbol_index]) == self.groups_len:
        # no need to keep decoding
        '''
        changes only here
        '''
        self.reset()

        return True

      flag = False
      for i in range(len(self.complete_range)-1):

        if self.feasible_range == [self.complete_range[i], self.complete_range[i+1]]:
          symbol = i
          flag = True

          self.decoded_seq[self.symbol_index] += self.symbols[symbol]
          #we recreate the list:
          var = self.feasible_range[1]
          var2 = self.feasible_range[0]
          self.feasible_range = []
          for j in range(len(self.cumulative)):
            self.feasible_range.append(var2 + (var-var2)*self.cumulative[j])

          self.complete_range = self.feasible_range.copy()
          self.trim_ranges_opt(bit)
  
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


class Interval_onesymbol():

  def __init__(self, groups_len, probabilities, symbols):


    # cumulative is a modified with respect to the theoric one
    # since we need the 1 for rescaling the ranges
    self.cumulative = [sum(probabilities[:i]) for i in range(0,len(probabilities)+1)] #is fixed
    self.complete_range = self.cumulative.copy()
    # complete_range is used just to get the index positions after
    # trimming to just one possible range
    self.feasible_range = self.cumulative.copy()

    self.probabilities = probabilities
    self.symbols = symbols

    self.decoded_seq = [''] # [symbol1, symbol2, ...]
    self.symbol_index = 0 # index of the symbols

    self.range = [0,1] # computed range
    self.exponent = -1
    self.groups_len = groups_len


  def trim_ranges(self):

    indice_min = 0
    indice_max = len(self.feasible_range)

    for i in range(len(self.feasible_range)-1):
      if self.range[0] >= self.feasible_range[i+1]:
        # se l'intervallo è più piccolo dell'estremo destro dell'intervallo
        indice_min += 1

    for i in range(len(self.feasible_range), 0, -1):
      if self.range[1] < self.feasible_range[i-1]:
        # se è più piccolo dell'estremo sinistro dell'intervalo
        indice_max -= 1

    self.feasible_range = self.feasible_range[indice_min:indice_max+1]

  def update(self, bit):

      # verify is the bit inserted is 1 or 0 a update the interval
      if bit == '0':
          self.range[1] -= 2**self.exponent
      else:
          self.range[0] += 2**self.exponent

      #update the count
      self.exponent -= 1

      # verify which intervals are feasible
      # now we need to trim the

      self.trim_ranges()

  def decode(self):

    flag = True

    while flag:

      # we find the letter which is immediately decodable by comparing the
      # equivalence between the feasible interval and the total posssible intervals
      # If we are able to decode a letter we could be able to decode another one

      if len(self.decoded_seq[self.symbol_index]) == self.groups_len:
        # no need to keep decoding
        break

      flag = False
      for i in range(len(self.complete_range)-1):

        if self.feasible_range == [self.complete_range[i], self.complete_range[i+1]]:
          symbol = i
          flag = True
          self.decoded_seq[self.symbol_index] += self.symbols[symbol]
          #we recreate the list:
          var = self.feasible_range[1]
          var2 = self.feasible_range[0]
          self.feasible_range = []
          for j in range(len(self.cumulative)):
            self.feasible_range.append(var2 + (var-var2)*self.cumulative[j])

          self.complete_range = self.feasible_range.copy()
          self.trim_ranges()




