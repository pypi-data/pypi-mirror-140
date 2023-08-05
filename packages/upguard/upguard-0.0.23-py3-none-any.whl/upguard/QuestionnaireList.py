import json
from .BaseObject import BaseObject
from .Questionnaire import Questionnaire
class QuestionnaireList(BaseObject):
    
  def __init__(self, api_key):
    BaseObject.__init__(self, api_key)
    self.inner_list = []
  

    
  def __getitem__(self, key):
    return self.inner_list[key]
  

    
  def __len__(self):
    return len(self.inner_list)
  

    
  def __iter__(self):
    self.iterator_counter = 0
    return self
  
  def __next__(self):
    if self.iterator_counter < len(self):
      x = self.inner_list[self.iterator_counter]
      self.iterator_counter += 1
      return x
    else:
      raise StopIteration
  
  def next(self):
    if self.iterator_counter < len(self):
      x = self.inner_list[self.iterator_counter]
      self.iterator_counter += 1
      return x
    else:
      raise StopIteration
  

    
  def append(self, obj):
    if isinstance(obj, Questionnaire) == False:
      raise Exception("Can only append 'Questionnaire' to 'QuestionnaireList'")
    self.inner_list.append(obj)
  

    
  def to_json(self):
    ll = []
    length = len(self.inner_list)
    for i in range(length):
      if i > 0:
        ll.append(",")
      ll.append(self.inner_list[i].to_json())
    return "[" + "".join(ll) + "]"
  

