import config
import web
import indexhelper
import uihelper

def print_selection(mindex=[], mkey=[], file_id = None, response_format = "html", sizeX = config.image_preview):
  """prints a browsing page including the selected indexes, the index which are
  still selectable and the result of the current selection as thumbnails"""

  selection = None
  indexes = None
  file_url = None

  if file_id:
    #we need to request the filename
    db_file = web.query("select filename from images where id = %s" % file_id)
    if len(db_file) == 1:
      file_path = db_file[0].filename
      file_url = config.web_alias + file_path[len(config.base_dir):]

  #first let's see if anything was choosen
  if mindex:

    #choosing the kind of situation we have to handle
    if len(mindex) == len(mkey):
      #we have the same number of indexes and key so we can print image list
      sel_ik = build_sel_ik(mindex, mkey, len(mkey))

      #selecting files from the given index values
      #files = indexhelper.select_files (sel_ik)
      files, clustered_files, cluster_pivot = indexhelper.select_clusters_of_files(sel_ik)
      
      if files:
        
        cache_key = uihelper.build_link(sel_ik)
        #get the index possible values
        index_othervalues = {}
        for index in config.indexes:
          index_othervalues[index] = [i for i in indexhelper.get_values(sel_ik, index)]

        #now also get the selected index possible values without them (changing stuff)

        sel_index_othervalues = {}
        for (index, value) in sel_ik:
          temp_sel_ik = sel_ik[:]
          temp_sel_ik.remove((index,value))
          sel_index_othervalues[index] = len(indexhelper.get_values(temp_sel_ik, index))

      if len(files) == 1 and not file_id:
        #TODO have the redirect be a temporary one, or check how long the browser retain the redirect
        web.found('%s%s/%s%s' % (config.base_url, uihelper.build_link(sel_ik), config.file_url_id, files[0].id))
      else:
        if response_format in config.format_http_header.keys():
          web.header("Content-Type", config.format_http_header[response_format])
        web.render('browse.'+response_format)

    elif len(mindex)-len(mkey) == 1:
      #there is a different process if len(mindex) and len(mkey) are differents, 
      #it means an index was selected but no key for it we have to print the 
      #keys for which the current selection of indexes/keys has left some images to view
      sel_ik = build_sel_ik(mindex, mkey, len(mkey))
      current_index = mindex[-1]

      index_possible_values = indexhelper.get_values(sel_ik, current_index)
      
      #if for_ajax:
      #  web.render('browsechoosevalue.ajax')
      #else:
      web.render('browsechoosevalue.'+response_format)
    else:
      #complaining about the uneven (more than usual at least) numbers of index and keys provided
      print("you have selected %s index but only %s keys where given\
          , stop messing around with things you don't understand please ;)<br/>"\
          % (len(mindex), len(mkey)))

  elif file_url:
    web.render('browse.html')
  else:
    indexes = [idx for idx in config.root_indexes if idx != 'tag'] 
    all_tags = indexhelper.get_values(None, "tag")
    web.render('browseroot.html')


def build_sel_ik(mindex, mkey, max_range):
  """return a list of (index,key) tuples from the url attributes"""
  #we use a given range because the number of values for mindex and mkey can be uneven
  return [(mindex[i], mkey[i]) for i in range(max_range)]
