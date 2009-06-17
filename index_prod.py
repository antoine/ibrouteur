#!/usr/bin/env python
import web
import db_params
import xtralinks
import indexmanager
import browseui 
import indexhelper 
import config
import re

#web.py 2.0
#web.wsgi.runwsgi = web.wsgi.runfcgi
#web.webapi.internalerror = web.cheetah.debugerror

web.runwsgi = web.runfcgi
web.internalerror = web.debugerror
web.db_parameters = dict(dbn='mysql', user=db_params.user, pw=db_params.password, db=db_params.database)

urls = (
    '/admin/sync', 'index_synchroniser',
    '/xtra/(.*)', 'xtra_plugins',
    '/(.*)', 'browser'
    )

class xtra_plugins:
  def GET(self, url_data):
    getattr(xtralinks, url_data)()

class index_synchroniser:
  def GET(self):
    indexmanager.sync()

class browser:
  def GET(self, url_data):
    if url_data:
      #parsing the url
      filters = url_data.split('/')
      index = []
      key = []
      file_id = None
      response_format = "html"
      sizeX = config.image_preview 
      cached_values = {}
      for f in filters:
        index_unknown = True 
        no_value_for_index = False
        for i in config.indexes:
          if f[0:len(i)] == i:
            web.debug("[URL_PARSE] found index "+i+" with value "+f[len(i):])
            index.append(i)
            if f[len(i):]:
              key.append(f[len(i):])
            else:
              no_value_for_index = True 
            index_unknown = False 
            break
        if index_unknown:
          if f[0:len(config.file_url_id)] == config.file_url_id and re.match("[0-9]+$", f[len(config.file_url_id):]):
            #we have a file to show
            file_id = f[len(config.file_url_id):]
            web.debug("[URL_PARSE] file to show : "+file_id)
          elif f == "ATOM":
            #rss format
            response_format = "atom"
          elif f == "RSS":
            #rss format
            response_format = "rss"
          elif f == "AJAX":
            #ajax style request, we do not render the headers/footesr, just the main html to be included
            response_format = "ajax"
          elif re.match("[0-9]+x$", f):
            #sizing information for an image
            sizeX = f[:-1]
          else:
            web.debug("[URL_PARSE] index is unknown, testing...")
            #let's start matching
            found_in_index = False
            for iname in config.re_url_order:
              #if debug: req.write("<br/>testing against index "+iname+", with re"+config.re_url[iname])
              if re.match(config.re_url[iname], f):
                if not cached_values.has_key(iname):
                  cached_values[iname] = indexhelper.get_all_values(iname)
                all_index_values = cached_values[iname]
                #we need to test if there are values for this key/index first
                web.debug("[URL_PARSE]"+f+" compatible with index "+iname+", checking keys"+str(all_index_values))
                if f in all_index_values:
                  index.append(iname)
                  key.append(f)
                  #if debug: req.write("<br/>found index "+iname+" with value "+f)
                  found_in_index = True
                  break
            if not found_in_index:
              index.append("tag")
              key.append(f)
          if no_value_for_index: break

      browseui.print_selection(index, key, file_id, response_format, sizeX)
    else:
      browseui.print_selection()

#if __name__ == "__main__": web.run(urls, web.reloader)
if __name__ == "__main__": web.run(urls)

#web.py 2.0 
#if __name__ == "__main__": web.run(urls, globals())
