#TODO reintegrate those links on the frontpage, maybe using /xtra/method_name in the url and a redirect
import config
import web
import uihelper
import random
import index

def last_month():
  last_month = web.query("select month(max(date)) month, year(max(date)) year from images")[0]
  web.tempredirect(config.base_url+uihelper.build_link((("year", last_month.year),("month", last_month.month))))

def random_image():
  rand_img= web.query("select id  from images order by rand() limit 0,1")[0]
  #web.tempredirect("%simage%s" % (config.base_url, rand_img.id))
  index.browser().GET("image%s" % ( rand_img.id))

def latest_images():
  last_batch= web.query("select max(batch) as value from images")[0]
  #web.tempredirect(config.base_url+uihelper.build_link((("batch", last_batch.value),)))
  index.browser().GET("batch%s" % ( last_batch.value))

def rss_latest_images():
  last_batch= web.query("select max(batch) as value from images")[0]
  index.browser().GET("batch%s/RSS" % ( last_batch.value))

