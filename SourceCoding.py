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

