def anc(string):
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
      if not s.isdigit():
        res += replace[s.upper()]
      else:
        raise KeyError
    except KeyError:
      res += s
    
  return res