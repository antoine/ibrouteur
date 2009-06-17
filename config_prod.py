"""sed to store various configuration data about the specific environnement of the application
think about reduilding the indexes once this file is modified, specially for base_dir and web_alias"""

#from how many possible key will we show them next to the label
maximum_key_quantity = 4
maximum_key_quantity_per_index = {
  'date' : 2,
  'album':2,
  'tag': 6
}
#size of the preview
image_preview = 640
#size of the square thumbnail
image_thumbnail = 128
#quantity of thumbnail to show in prev/next
tn_prev_q = 1
tn_next_q = 1
#simple_url is a parameter since it dependent on apache config
simple_url = 0
#server_name : name of the server on which the application is running
server_name = "http://delaunay.org"
#static_server : name of the machine serving the static files
static_server = "http://delaunay.org"
root_url = ''
base_url = root_url+'/antoine/i/'
home_url = base_url+''
css_url = root_url+'/css/modern.css'
#directory in which the pictures can be found, this is only used at indexing time
base_dir = "/home/rouadec/srv/www.delaunay.org/antoine/photos" 
#extension list, the value is what we append to get the thumbnail
supported_extensions = ('JPG', 'AVI' , 'WMV', 'OGG')
extensions_thumbnails = {'AVI':'.thm', 'WMV':'.thm', 'OGG':'.thm'}
extensions_tags = { 'AVI':('video',), 'WMV':('video',), 'OGG':('video',)}
video_objects = ('AVI', 'WMV', 'OGG')
#directory in which the thumbnails are going to be created and found
tn_base_dir = "/home/rouadec/cache/delaunay.org/thumbnails" 
html_base_dir = "/home/rouadec/cache/delaunay.org/html" 
#base_url of the pictures
web_alias = root_url+"/antoine/photos" 
#base_url of the thumbnails
tn_web_alias = root_url+"/antoine/thumbnails" 
#name of the anchor tag given to the thumbnail of the currently selected image
tn_anchor_name = "curr_img"
#list of index we wish to show, the order matters
#witrh dates indexes 
indexes= ('album', 'country', 'location', 'tag', 'year', 'date',  'author', 'subject', 'month', 'batch')
root_indexes= ('album', 'country', 'location', 'tag', 'year', 'subject')
built_indexes= ('album', 'location', 'date',  'author', 'subject', 'tag', 'country', 'sha')
compound_indexes = {
'year' : {
  'base_index' : 'date', 
  'method' : lambda d: d.year, 
  'reverse_query' : lambda table_prefix='': 'year(%sdate)' % table_prefix},
'month' : {
  'base_index' : 'date', 
  'method' : lambda d: d.month,
  'reverse_query' : lambda table_prefix='': 'month(%sdate)' % table_prefix} }
have_many_values = ('subject', 'tag')
default_sort_order = 'value'
sort_orders = {
  ('year', 'date', 'batch') : 'value desc'
}
#indexes= ('trip', 'location',  'subject', 'tag', 'author')
#list of additional indexes we wish to load but not let the user select, they will
#therefore only be visible in the image information. Need to be a list for extend()
#ro remove when the dates are being compiled 
#additional_indexes= ['camera',]
additional_indexes= []
#importance order for the clustering of images
cluster_pivot_order= ('album', 'location', 'year', 'month', 'date', 'author')
#cluster_pivot_order= ('trip', 'location', 'author')
minimum_pivot_value = 2
#define the order, not used anymore but the method still exists so...
order_infos = ('date', 'album', 'location', 'author',  'subject', 'tag', 'camera')
#directory in which the index are stored and read from
index_dir = "/srv/www.delaunay.org/antoine/ibrouteur/indexes"
#name of the file used for reverse indexing
reverse_idx_file = "reverse.idx"
#default author for the pictures, only used at indexing time
default_author = "me"
default_camera = "Canon DIGITAL IXUS 400"
redundant_model_info = ('Canon', 'EASTMAN KODAK COMPANY')
#put here the names of the xtra links you wish to show on the screen
xtralinks = (
('latest_images', 'new images</a>, <a href="'+base_url+'xtra/rss_latest_images"><img src="http://delaunay.org/icones/feed-icon16x16.png" alt="RSS feed of the newest images" title="RSS feed of the newest images"/> RSS feed'),
('last_month', 'latest month'), 
('random_image', 'random image'))
#meaning the first 10% have a class of quant4, the first 33% have a class of 3, etc.
class_of_quantity = (10, 33, 50, 100) 
file_url_id = "image"
  
m = ['January','February','March','April','May','June',\
    'July','August','September','October','November','December']
d = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
human_index_keys = {'month' : lambda v : m[int(v)-1], \
    'date' : lambda v : str(v).split('-')[2]+' '+m[int(str(v).split('-')[1])-1]+' '+str(v).split('-')[0],\
    'weekday' : lambda v : d[int(v)-1]}
index_sorts = {'week': lambda x, y : int(x) - int(y) ,\
    'month':lambda x, y : int(x) - int(y),\
    'tag' : lambda x,y : x.upper() == y.upper() and 0 or (x.upper() > y.upper() and 1 or -1)}

#regular expressions used in url decoding
re_url_order = ("year", "subject", "month", "date", "location", "country", "week")
re_url = { 
"month": "1?[0-9]$",\
"year": "20[10][0-9]$",\
"date": "20[10][0-9]-[01][0-9]-[0-3][0-9]$",\
"country": "[A-Z][A-Za-z\-\ ]*$",\
"subject": "[A-Z][A-Za-z\-\ ]*$",\
"album": "[\w\ \-]*$",\
"location": "[\w\ \-]*$",\
"week": "[1-5]?[0-9]$"}

format_http_header = {
"rss": "application/rss+xml",
"atom": "text/xml"}
