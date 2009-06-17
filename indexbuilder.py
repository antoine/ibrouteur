import os
import time
import p23_lib.exif as EXIF
import sha
#import Image
try:
  from datetime import date
except:
  from mx.DateTime import Date as date
import config



def get_etape(file):
  print "todo"

#def get_date_o(file):
  #exif_tags = EXIF.process_file(open(file, 'rb'))
  #we split the exif tag which look like 2004:10:20 10:55:24 to keep only the date info
  #sdate = exif_tags["EXIF DateTimeOriginal"].values.split()[0].split(':')
  #return date(int(sdate[0]), int(sdate[1]), int(sdate[2]))

#the split()[0] have been added as a compatibility between mx.DateTime.Date for python 2.1
# and datetime.date for python2.3
#p2.3 str(datetime.date) = 2005-06-25
#p2.1 str(mx.DateTime.Date) = 2005-06-25 00:00:00.00
#this is going to so fuck-up the urls...

def get_date(file):
  return str(__get_date(file)).split()[0]

def get_camera(file):
  """expect file to be an open file"""
  try:
    exif_tags = EXIF.process_file(open(file, 'rb'))
    #we split the exif tag which look like 2004:10:20 10:55:24 to keep only the date info
    make = str(exif_tags["Image Make"])
    model = str(exif_tags["Image Model"] )
    if make in config.redundant_model_info:
      return model
    else:
      return make + ' - ' + model
  except KeyError:
    #meaning the exif info is incorrect
    #if no correct exif then we use the file creation date
    print '[WARN] file %s has no valid exif info' % (file)
  except:
    print '[ERR] file %s is not to the taste of EXIF.py...' % (file)
  #if get_author(file) in config.default_author:
    #return config.default_camera 
  #else:
  return None

def __get_date(file):
  """expect file to be an open file"""
  date_pos = file.find('_date')
  if date_pos == -1:
    try:
      exif_tags = EXIF.process_file(open(file, 'rb'))
      #we split the exif tag which look like 2004:10:20 10:55:24 to keep only the date info
      if exif_tags.has_key("EXIF DateTimeOriginal"):
        sdate = exif_tags["EXIF DateTimeOriginal"].values.split()[0].split(':')
      else:
        print '[INFO] file %s has no exif DatetimeOriginal' % (file)
        sdate = exif_tags["Image DateTime"].values.split()[0].split(':')
      return date(int(sdate[0]), int(sdate[1]), int(sdate[2]))
    except KeyError:
      #meaning the exif info is no complete, some tinkering may have happened with the image
      print '[WARN] file %s has no valid exif info' % (file)
    except:
      print '[ERR] file %s is not to the taste of EXIF.py...' % (file)
    #if no correct exif then we use the file creation date
    d = time.localtime(os.stat(file)[os.path.stat.ST_MTIME])
    return date(d[0],d[1],d[2])
  else:
    next_pos = file.find('_',date_pos+4)
    if next_pos == -1 : next_pos = file.find('.', date_pos+4)
    file_date = file[date_pos+5:next_pos]
    return date(int(file_date[:4]), int(file_date[4:6]), int(file_date[6:]))

def get_day(file):
  return str(__get_date(file).day).split()[0]

def get_weekday(file):
  date = __get_date(file)
  try:
    return str(date.isoweekday()).split()[0]
  except:
    return str(date.day_of_week).split()[0]

def get_week(file):
  date = __get_date(file)
  try:
    return str(date.isocalendar()[1]).split()[0]
  except:
    return str(date.iso_week[1]).split()[0]

def get_month(file):
  return str(__get_date(file).month).split()[0]

def get_year(file):
  return str(__get_date(file).year).split()[0]

def get_country(file):
  return file.replace('\\','/').split('/')[-3]

def get_location(file):
  """location is the directory of the file, easy :)
  this only work in my little world of course"""
  return file.replace('\\','/').split('/')[-2]

def get_album(file):
  """album is the top level of directory, easy :)
  this only work in my little world mind you"""
  return file.replace('\\','/').split('/')[-4]

def get_sha(file):
  ofile = open(file,'rb')
  digest = sha.new()
  data = ofile.read(65536)
  while len(data) != 0:
    digest.update(data)
    data = ofile.read(65536)
  ofile.close()
  return digest.hexdigest()

def get_author(file):
  #this means the subject has to start with _ even if its the first and only item of the filename
  #this also means a filename with ____ will stall the program
  auth_pos = file.find('_auth')
  if auth_pos == -1:
    return config.default_author
  else:
    next_pos = file.find('_',auth_pos+4)
    if next_pos == -1 : next_pos = file.find('.', auth_pos+4)
    return file[auth_pos+5:next_pos]

def get_subject(file):
  """get all the tags _subjXXX in a file name
  XXX is the name of someone appearning in the picture"""
  #this means the subject has to start with _ even if its the first and only item of the filename
  #this also means a filename with ____ will stall the program
  sub_pos = file.find('_subj')
  end_pos = file.rfind('.')
  subjects = []
  #while nbsubj <= 5 and sub_pos != -1:
  while sub_pos != -1:
    next_item = file.find('_', sub_pos+4)
    if next_item == -1: next_item = end_pos
    #print 'found subject %s between %s and %s on file %s' % (file[sub_pos+5:next_item], sub_pos+5, next_item, file)
    subjects.append(file[sub_pos+5:next_item])
    sub_pos = file.find('_subj', next_item)
  return subjects

def get_tag(file):
  """get all the tags like XXX where XXX is not a subject or an author"""
  #we get the filename
  fn = os.path.split(file)[-1].split('.',1)[0].split('_')
  if file[-3:].upper() in config.extensions_tags.keys():
    fn.extend(config.extensions_tags[file[-3:].upper()])
  #we split around the _
  return [i for i in fn if i!='IMG' \
      and i \
      and not (i[:1] == 'P' and i[1:].isdigit()) \
      and i[:3] != 'DSC' \
      and i[:4] != 'subj' \
      and i[:4] != 'auth' \
      and i[:4] != 'date' \
      and not i.isdigit()]
