#!/usr/bin/env python3

class ancipher:
  
  def __init__(self):
    self.string = ''

    
  def anc(self):
    res = ''
    replace = {
      'I':'1',
      'Z':'2',
      'E':'3',
      'A':'4',
      'S':'5',
      'T':'7',
      'B':'8',
      'O':'0',
    }
  
    for s in string:
      try:
        res += replace[s.upper()]
      except KeyError:
        res += s
  
  return res