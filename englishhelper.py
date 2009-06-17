import config 

def english_a(word):
  """will decide wether or not the english 'article' a should be a or an 
  this based on the first letter and I'm sure exceptions are lurking in the dark but
  I've got plenty of light"""
  if not word : return ''
  #trying the and-or trick worth (bool)? a : b
  return word[0] in ('a','e','i','o','u','A','E','I','O','U') and 'n' or ''

def list_nouns_as_links(index, list_of_nouns, make_link):
  if list_of_nouns is None: 
    return ''
  elif len(list_of_nouns)==1:
    return make_link(index, list_of_nouns[0], list_of_nouns[0])
  else:
    return ", ".join([make_link(index, i, i) for i in list_of_nouns[:-1]])+" and "+make_link(index, list_of_nouns[-1], list_of_nouns[-1])

def list_nouns(list_of_nouns):
  if list_of_nouns is None: 
    return ''
  elif len(list_of_nouns)==1:
    return list_of_nouns[0]
  else:
    return ", ".join([i for i in list_of_nouns[:-1]])+" and "+list_of_nouns[-1]

