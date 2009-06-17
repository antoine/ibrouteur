import os
import sys
import config
import web
import indexbuilder
try:
  from datetime import date
except:
  from mx.DateTime import Date as date
#import p23_lib.distutils.filelist as filelist


def findall (dir = os.curdir):
  """Find all files under 'dir' and return the list of full filenames
  (relative to 'dir').
  """
  #copied from the pythom2.3 libs for easier adaptation to python 2.1
  from stat import ST_MODE, S_ISREG, S_ISDIR, S_ISLNK

  list = []
  stack = [dir]
  pop = stack.pop
  push = stack.append

  while stack:
    dir = pop()
    names = os.listdir(dir)

    for name in names:
      if dir != os.curdir:        # avoid the dreaded "./" syndrome
        fullname = os.path.join(dir, name)
      else:
        fullname = name

      # Avoid excess stat calls -- just one will do, thank you!
      stat = os.stat(fullname)
      mode = stat[ST_MODE]
      if S_ISREG(mode):
        list.append(fullname)
      elif S_ISDIR(mode) and not S_ISLNK(mode):
        push(fullname)

  return list

def sync():
  #list all files from disk and DB
  disk_entries = get_files()
  db_entries = [f['filename'] for f in web.query("select filename from images")]
  extra_db_entries = []
  print "%s disk entries\n%s db entries\n" % (len(disk_entries), len(db_entries))
  for f in db_entries: 
    if f in disk_entries:
      disk_entries.remove(f)
    else:
      extra_db_entries.append(f)


  print "%s EXTRA disk entries" % (len(disk_entries))
  build_all(disk_entries, extra_db_entries)

  print "\n%s EXTRA db entries" % (len(extra_db_entries))
  for f in extra_db_entries:
    print "removing %s from DB" % f
    #remove the info from the db
    file_id = web.query('select id from images where filename = "%s"' % f)[0].id
    web.query("delete from images where id = %s" % file_id)
    for imv in config.have_many_values:
      #removing the infos from the various multiple indexes
      web.query("delete from images_%ss where image_id = %s" % (imv, file_id))
  for imv in config.have_many_values:
    print "cleaning the possibles orphan values for the index %s" % imv
    web.query("delete from %ss where id not in (select %s_id from images_%ss)" % (imv, imv, imv))


  #diff the lists : remove from each list identical entries
  #for each file on the disk but not on the DB insert it
  #for each file in the DB but not on the disk remove the entries (in images and in multiple tags tables)
  #remove the unused multiple values (just SQL)


def get_files(root_dir = config.base_dir):
  imfiles = findall(root_dir)
  return [im for im in imfiles if im[-3:].upper() in config.supported_extensions and im[-7:-3]!=".ni."]

def build_all(files = get_files(), extra_db_entries=(), batch=date.today()):
  #build the indexes for the given list of files
  idx_types = config.additional_indexes
  idx_types.extend(config.built_indexes)
  print "found %s images to index" % (len(files))
  #i = 0
  for f in files:
    infos = extract_infos(f, idx_types)
    infos["batch"] = batch
    store_infos(infos, extra_db_entries)
    #i+=1
    #if i > 100: break

def extract_infos(f, idx_types):
  file_infos = {"filename" : f}
  for idx_type in idx_types:
    try:
      value = getattr(indexbuilder, "get_%s" % idx_type)(f)
      file_infos[idx_type] = value
    except:
      print "[ERR] file %s is like a piece of dirty old cheese because \n\
          %s " % (f,sys.exc_info()[0])
      raise
  return file_infos

def store_infos(infos, extra_db_entries):
  print " %s" % (infos)
  #web.debug(" %s" % (infos))
  simple_infos = infos.copy()
  multiple_infos = {}
  for imv in config.have_many_values:
    try:
      del simple_infos[imv]
      multiple_infos[imv] = infos[imv]
    except KeyError:
      pass
  #checking for file renaming with sha
  possiblePrevFiles = web.query("select id, filename, batch from images where sha ='"+infos['sha']+"'")
  updatingFile = False
  if len(possiblePrevFiles) == 1:
    #file found in db
    print "INFO duplicate found : "+infos['filename']
    prevFile = possiblePrevFiles[0]
    file_id = prevFile.id
    simple_infos['batch'] = prevFile.batch
    try:
      extra_db_entries.remove(prevFile.filename)
      web.update('images', 'id = %s' % file_id, None, **simple_infos)
      updatingFile = True
    except ValueError:
      #raise with .remove when the filename do not match
      print "WARNING duplicate sha accross fileset, creating new entry"
  else:
    if len(possiblePrevFiles) > 1:
      #more than one file with this sha... 
      print "INFO sha present multiple time for file : "+infos["filename"]
    file_id = web.insert('images', True, **simple_infos)

  for index in multiple_infos.keys():
    #store the value in its table
    for value in multiple_infos[index]:
      try:
        value_id = web.insert(index+'s', True, **{"value" : value})
        #debuginsert(index+'s', False, **{"value" : value})
      except: 
        #TODO should be IntegrityError for mysql but not sure how best integrate that without breaking the DB abstraction...
        #but if the error wasn't an IntegrityError then the next line should fail
        value_id = web.query('select id from %ss where value = "%s"' % (index, value))[0].id
      #store the relationship between the value and the file
      try:
        web.insert("images_"+index+'s', False, **{index+"_id": value_id, "image_id" : file_id})
      except Exception, inst:
        #if we are update a file we might raise some integrity error here
        if updatingFile:
          pass
        else:
          raise inst

def debuginsert(tablename, seqname=None, **values):
  if values: 
    print("INSERT INTO %s (%s) VALUES (%s)" % (
          tablename,
          ", ".join(values.keys()),
          ', '.join([web.aparam() for x in values])
          ), values.values())
  else:   
    print("INSERT INTO %s DEFAULT VALUES" % tablename)

def __to_dict_list(dict, key, value):
  if dict.has_key(key):
    dict[key].append(value)
  else:
    dict[key] = [value, ]

def test():
  name = 'Bob'
  web.render('browse.html')
  name = None
  web.render('browse.html')
