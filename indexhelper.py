#TODO update the query string to use the %(name)s instead of %s when multiple references to the same var, use the vars() function
import web
import config
import sys
try:
  from cStringIO import StringIO
except:
  from StringIO import StringIO

def get_all_values(index):
  if index in config.have_many_values:
    db_values = web.query('select value from %ss' % index)
    return [row.value for row in db_values]
  elif index in config.compound_indexes.keys():
    compound_info = config.compound_indexes[index]
    db_values = web.query('select distinct(%s) as value from images order by %s' % (compound_info['reverse_query'](), get_order(index)))
    return [str(row.value) for row in db_values]
  else:
    db_values = web.query('select distinct(%s) as value from images order by %s' % (index, get_order(index)))
    return [row.value for row in db_values]


def get_values(sel_ik, idx):
  """will print all the possible keys an index could use in order to still
  show at least one file with the current selection of i/k in mind"""

  def get_printkeys_class(i_name, module=sys.modules[__name__]):      
    """get formatter fonctions from the index name, this is for when we want to do a specific sort
    using information not available when defining the sort function in the config or a specific printing"""
    format_func = "get_%s_values" % i_name       
    return hasattr(module, format_func) and getattr(module, format_func) or get_default_values

  return get_printkeys_class(idx)(sel_ik, idx)

def get_default_values(sel_ik, index):
  """will print all the possible keys an index could use in order to still
  show at least one file with the current selection of i/k in mind"""
  value_per_index = []


  #get all the possible values from the index
  if sel_ik:

    #building the ignore clause
    for (sel_index, sel_value) in sel_ik:
      if sel_index == index:
        if value_per_index:
          value_per_index.append(sel_value)
        else:
          value_per_index = [sel_value, ]
    if value_per_index:
      ignore_clause = "and %s not in ("+", ".join(['"'+ivalue+'"' for ivalue in value_per_index])+")"
    else:
      ignore_clause = ""

    if index in config.have_many_values:
      additional_clauses = build_clauses(sel_ik, 'and ', 'images.')
      if ignore_clause:
        temp_ignore_clause = ignore_clause % "value"
      else:
        temp_ignore_clause = ""
      #web.debug('GET VALUE : select value, count(images.id) as quantity from images_%(index)ss , %(index)ss, images where %(index)s_id = %(index)ss.id and images_%(index)ss.image_id = images.id %(temp_ignore_clause)s %(additional_clauses)s group by %(index)s_id' % (vars()))
      return web.query('select value, count(images.id) as quantity from images_%ss , %ss, images where %s_id = %ss.id and images_%ss.image_id = images.id %s %s group by %s_id order by %s' % (index, index, index, index, index, temp_ignore_clause , additional_clauses, index, get_order(index)))
    else:
      additional_clauses = build_clauses(sel_ik, 'and ')
      if index in config.compound_indexes.keys():
        #need to get database specific query to match value
        db_value =  config.compound_indexes[index]['reverse_query']()
      else:
        db_value = index
      if ignore_clause:
        temp_ignore_clause = ignore_clause % db_value
      else:
        temp_ignore_clause = ""
      #web.debug('GET VALUE: select %s as value, count(id) as quantity from images where 1=1 %s %s group by value' % (db_value, temp_ignore_clause , additional_clauses))
      return web.query('select %s as value, count(id) as quantity from images where 1=1 %s %s group by value order by %s' % (db_value, temp_ignore_clause , additional_clauses, get_order(index)))
  else:
    #simpler case, left here for the sake of simplicity
    if index in config.have_many_values:
      #web.debug('select value, count(image_id) as quantity from images_%ss , %ss where %s_id = id  group by %s_id' % (index, index, index, index))
      return web.query('select value, count(image_id) as quantity from images_%ss , %ss where %s_id = id  group by %s_id order by %s' % (index, index, index, index , get_order(index)))
    else :
      if index in config.compound_indexes.keys():
        #need to get database specific query to match value
        db_value =  config.compound_indexes[index]['reverse_query']()
      else:
        db_value = index
      return web.query('select %s as value, count(id) as quantity from images group by value order by %s' % (db_value, get_order(index)))


def get_tag_values(sel_ik, index):
  """will print all the labels ordered by their quantities
  show at least one file with the current selection of i/k in mind"""
  def get_class_of_quantity(pos):
    i=0
    for classoq in config.class_of_quantity:
      if pos < classoq:
        return i
      i+=1
    return len(config.class_of_quantity)-1

  #HTML print

  #get all the possible keys from the index
  tags = [i for i in get_default_values(sel_ik, 'tag')]
  #sort them by importance
  #web.debug("%s" % tags)
  quantity_per_tag = {}
  tags_by_quantity = []
  for row in tags:
    quantity_per_tag[row.value] = int(row.quantity)
    tags_by_quantity.append(row.value) 

  tags_by_quantity.sort(lambda x,y : quantity_per_tag[y] - quantity_per_tag[x])
  
  for tag in tags:
    quantity_position = (tags_by_quantity.index(tag.value)+1)*100/len(tags)
    tag.quantity = get_class_of_quantity(quantity_position)

  return tags

def get_order(index):
  for k in config.sort_orders.keys():
    if index in k:
      return config.sort_orders[k]
  return config.default_sort_order

def build_clauses(sel_ik, start_with='', table_prefix = ''):
  w = StringIO()
  if sel_ik:
    w.write(start_with)
    clauses = []
    for (index, value) in sel_ik:
      if index in config.have_many_values:
        clauses.append(table_prefix+"id in (select image_id from images_%ss linkt, %ss valuet where value=\"%s\" and linkt.%s_id = valuet.id)" % (index, index, value, index))
      elif index in config.compound_indexes.keys():
        clauses.append("%s = \"%s\"" % (config.compound_indexes[index]['reverse_query'](table_prefix), value))
      else:
        clauses.append(table_prefix+"%s = \"%s\"" % (index, value))
    w.write(' and '.join(clauses))
  return w.getvalue()

def select_files(sel_ik):
  q = StringIO()
  q.write('select id, filename from images ')
  q.write(build_clauses(sel_ik,'where '))
  q.write(' order by date desc ')
  web.debug('file query = %s' % q.getvalue())
  return web.query(q.getvalue())

def select_clusters_of_files(sel_ik):
  q = StringIO()
  q.write('select * from images ')
  q.write(build_clauses(sel_ik,'where '))
  q.write(' order by date desc ')
  files = [f for f in web.query(q.getvalue())]
  web.debug('file query = %s' % q.getvalue())
  #clustering happens here.
  (clustered_files, cluster_pivot) = cluster_files(files, sel_ik)
  if len(clustered_files.keys()) < config.minimum_pivot_value:
    return (files, None, None)
  return (files, clustered_files, cluster_pivot)

def cluster_files(files, sel_ik):
  #we create a cluster if more than config.minimum_pivot_value values exist
  clusters = {}
  tested_pivots = []
  #we test all the pivots
  while len(tested_pivots) < len(config.cluster_pivot_order):
    clusters = {}
    pivot = get_clustering_index(sel_ik, tested_pivots)
    tested_pivots.append(pivot)
    for f in files:
      if pivot in config.compound_indexes.keys():
        pivot_value = config.compound_indexes[pivot]["method"](f[config.compound_indexes[pivot]["base_index"]])
      else:
        pivot_value = f[pivot]
      if not clusters.has_key(pivot_value): clusters[pivot_value] = []
      clusters[pivot_value].append(f)
    #if the number of cluster if enough then we stop
    if len(clusters.keys()) >= config.minimum_pivot_value :
      return (clusters, pivot)
  return (clusters, pivot)

def get_clustering_index(sel_ik, tested_pivots):
  """take the list of used index and return the index which should be used
  for clustering of the information"""
  sel_i = [i[0] for i in sel_ik]
  for index in config.cluster_pivot_order:
    if index not in sel_i and index not in tested_pivots:
      return index
  return index

