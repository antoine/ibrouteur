"""
various functions used when building a page,
mainly related to index lookup
"""
import config
import englishhelper
import web
import p23_lib.pil.Image as image
try:
  from cStringIO import StringIO
except:
  from StringIO import StringIO

def hr_tag(type, value, language = "not supported"):
  """return a human readable tag"""
  if config.human_index_keys.has_key(type):
    return config.human_index_keys[type](value)
  else:
    return value

def urlquote(s):
  return str(s).replace("'", "%27")

def build_link(sel_ik, notthis_i = None, notthis_v = None):
  """ the notthis_X vars are actually couples (index, value)!!"""
  if sel_ik:
    if notthis_v:
      link_elements = [i for i in sel_ik if i != notthis_v]
    else:
      link_elements = [i for i in sel_ik if i != notthis_i]
      
    link = '/'.join([str(index)+urlquote(str(value)) for (index,value) in link_elements])
    #web.debug(link)

    if notthis_v:
      if link:
        return  link + '/' + notthis_v[0]
      else:
        return notthis_v[0]
    else:
      return link

  else:
    return ""

def build_possible_links(sel_ik, (index, value), index_possible_values, nb_files):
  """ generate links for all possible values"""
  possible_links = []
  at_least_one_link = False
 
  for (possible_value, quantity) in [(v.value, v.quantity) for v in index_possible_values]:
    if quantity < nb_files:
      if value:
        link = build_link( sel_ik+[(index, possible_value)], (index, value))
      else:
        link = build_link(sel_ik+[(index, possible_value)])
      at_least_one_link = True
      possible_links.append('<a href="%s%s">%s</a>' % (config.base_url, link, hr_tag(index, possible_value)))
    else:
      possible_links.append(hr_tag(index, possible_value))

  return at_least_one_link, ", ".join(possible_links)

def get_thumbnail(f):
    return  resize_image(get_thumbnail_name(f), config.image_thumbnail, True)

def get_image(f, i_size= config.image_preview):
    return  resize_image(f, i_size, False)

def sort_k(keys, idx):
  if config.index_sorts.has_key(idx):
    keys.sort(config.index_sorts[idx])
  else:
    keys.sort()
  return keys

def get_thumbnail_name(filename):
  if config.extensions_thumbnails.has_key(filename[-3:].upper()):
    return filename+config.extensions_thumbnails[filename[-3:].upper()]
  else:
    return filename

def resize_image(file_path, sizeX = config.image_thumbnail, crop_to_square = False):
  """return new url for resized image"""
  #sizeX = 0 would divide by zero
  if int(sizeX) < 2 : sizeX = config.image_thumbnail
#  tn = Config.tn_base_dir+'/X'+sizeX+'Y'+sizeY+url[len(Config.web_alias)+1:].replace('/',',')
  tn = '%s/X%s_Sq%s_%s'% (config.tn_base_dir,sizeX, crop_to_square, file_path[len(config.base_dir)+1:].replace('/',','))
  #web.debug("TN :"+tn)
  #req.write('file = '+file+' </br>tn = '+tn)
  #look for a corresponding thumbmail already generated
  try:
    #if yes return correct url
    #req.write('</br>tseting tn %s</br>' % tn)
    #FIXME find better file existence test
    a=open(tn, 'rb')
    a.close()
    #req.write('tn found</br>')
  except:
    #if not generate and return url
    #req.write('</br>generating tn %s at position</br>' % sizeX)
    try:
      im = image.open(file_path)
      if crop_to_square:
        (im_x, im_y) = im.size
        if im_x < im_y:
          tn_x = sizeX
          #replace for python 2.1
          #tn_y = 1 + (im_y * sizeX)//im_x
          #px_to_cut = (tn_y - tn_x)//2
          tn_y = 1 + (im_y * sizeX)/im_x
          px_to_cut = (tn_y - tn_x)/2
          crop_box = (0,px_to_cut,sizeX,sizeX+px_to_cut)
        else:
          #replace for python 2.1
          #tn_x = 1 + (im_x * sizeX)//im_y
          #px_to_cut = (tn_x - tn_y)//2
          tn_x = 1 + (im_x * sizeX)/im_y
          tn_y = sizeX
          px_to_cut = (tn_x - tn_y)/2
          crop_box = (px_to_cut,0,sizeX+px_to_cut,sizeX)
        im.thumbnail((tn_x, tn_y), image.ANTIALIAS)
        im.crop(crop_box).save(tn, "JPEG")
      else:
        im.thumbnail((int(sizeX), int(sizeX)), image.ANTIALIAS)
        im.save(tn, "JPEG")
    except:
      return None
  wtn = config.tn_web_alias+tn[len(config.tn_base_dir):]
  #web.debug("WTN :"+wtn)
  #req.write('returning url : %s</br>' % wtn)
  return wtn

def get_nice_info(file_id):
  #TODO make it more flexible, put the strings in the config
  infos_html = StringIO()
  ddlink = lambda i, k, v : '<a href="%s%s%s">%s</a>' % (config.base_url,i,urlquote(k),v)
  fsi = web.query("select * from images where id = %s" % file_id)[0]
  fmi = {}
  for i in config.have_many_values:
    fmi[i] = web.query("select value from %(index)ss iv, images_%(index)ss ii where ii.image_id = %(file_id)s and ii.%(index)s_id = iv.id" % {"index" : i, "file_id": file_id})

  if fsi.author or fsi.date or fsi.album or fsi.location:
    infos_html.write("Taken")

    if fsi.author: infos_html.write(" by %s" % ddlink("author", fsi.author, fsi.author))
    if fsi.date: infos_html.write( " the %s" % ddlink("date", fsi.date, hr_tag("date", fsi.date)))
    if fsi.album: infos_html.write( " when doing the %s" % ddlink("album", fsi.album, fsi.album))
    if fsi.location:  infos_html.write(" at %s" % ddlink("location", fsi.location, fsi.location))
    infos_html.write(".<br/>")

  for (i, values) in fmi.items():
    if len(values) > 0:
      if i == "subject":
        infos_html.write("You can admire %s.<br/>" % englishhelper.list_nouns_as_links(i, [row.value for row in values], ddlink))
      elif i == "tag":
        infos_html.write("%s should describe this image.<br/>" % englishhelper.list_nouns_as_links(i, [row.value for row in values], ddlink))

  return infos_html.getvalue()

