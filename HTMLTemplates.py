import config

simple_header = """
      <title>ibrouteur</title>
      <style type="text/css"><!-- @import "%s"; --></style>
""" % (config.css_url)

doctype= "<html>"
##doctype= """
##<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
##"""

header = """
      <title>ibrouteur</title>
      <style type="text/css"><!-- @import \""""+config.css_url+"""\"; --></style>
      <script src=\""""+config.static_server+"""/js/scriptaculous/prototype.js" type="text/javascript"></script>
      <script src=\""""+config.static_server+"""/js/scriptaculous/scriptaculous.js" type="text/javascript"></script>
      <script type="text/javascript">
      function toggle_choices(target, url){
        var telem = document.getElementById(target);
        if (telem.style['display'] == 'none') {
          if (telem.innerHTML== '') {
            telem.innerHTML='loading...';
            var loadlist = true;
          }
          new Effect.BlindDown(target); 
          if (loadlist) {
            list_choices(target,url); 
          }
        }
        else
        {
          hide_choices(target);
        }
      }
function hide_choices (target) {
  new Effect.SwitchOff(target);
}
function list_choices(target, url){
  var pars = '';
  var myAjax = new Ajax.Updater(target, url, {method: 'get', parameters: pars});
}
</script>
""" 

root_body_start = """
    <body>
      <div id="header">
        <div class="backlinks">
          <a href="%s">delaunay.org</a>&gt;<a href="%s/antoine">antoine</a>
          <div class="help"><a href="%s/antoine/i/help/">help</a> - <!--<a href="./help/fr" rel="help">aide</a>--><a href="%s/antoine/license" rel="copyright">license</a></div>
        </div>
        <h1>iBrouteur</h1>
      </div>
      <div id="body">""" % (config.static_server, config.static_server, config.static_server, config.static_server)

body_start = """
    <body>
      <div id="header">
        <div class="backlinks">
          <a href="%s">delaunay.org</a>&gt;<a href="%s/antoine">antoine</a>&gt;<a href="http://delaunay.org/antoine/i">iBrouteur</a>
          <div class="help"><a href="%s/antoine/i/help/">help</a> - <!--<a href="./help/fr">aide</a>--><a href="%s/antoine/license">license</a></div>
        </div>
        <h1>Browsing</h1>
      </div>
      <div id="body">""" % (config.static_server, config.static_server, config.static_server, config.static_server)

body_end = """</div>
</body></html>"""

section_start = lambda id, name, cl_name = '', extra_text = '' : \
    '<div class="ib section %s" id="%s"> <div class="title"><span>%s :</span><div class="roundingtitle">&nbsp;</div>%s</div><div class="content">'\
    % (cl_name, id,name, extra_text)

section_choices_start = lambda id, index : \
  """<div id="%s" class="ib section choices" style="display:none;">
        <div class="title">
          <div style="float:left;">
            <span>other possible %ss :</span>
          </div>
          <div style="float:right;">
            <a onclick="document.getElementById('%s').style['display'] = 'none';">close</a>
          </div>
        </div>
      <div style="clear:right;" class="content">""" % (id, index, id)

section_end = '</div></div>'

explanation = """<dl>
          <dt>Moliere:</dt>
          <dd>
          iBrouteur : i pour image et brouteur comme ma traduction personelle de "browser". Des bouts de ma vie en images, pas tous les bouts parce que j'ai pas toujours un appareil photo et pas toutes les images non plus parce que j'ai un minimum de decence. Toutes reclamations peuvent <a href="mailto:rouadec@hotmail.com">m'etre adressees</a>, elles seront traitees avec l'efficacite habituelle.<br/>
          Voir <a href="./help/fr">l'aide</a> (aussi disponible en haut a droite de cette page) pour le comment.
          </dd>
          <dt>Shakespeare:</dt>
          <dd>
          iBrouteur : i for image and brouteur as my personal traduction of "browser" (we french people like to translate every word of english into something more "bread, cheese and wine", this is a well known fact ;). Bits of my life in images, not all the bits because I did not always had a camera and not all the images either because I still retain a minimum amount of decency. Any reclamation can be done to <a href="mailto:rouadec@hotmail.com">me</a>, they will be adressed with the usual efficiency.<br/>
          See the <a href="./help/eng">help</a> (also available in the upper-right corner of this page) for the how.
          </dd>
        </dl>"""

icones = {
    'next' : '<img class="movek" src="%s/icones/ibrouteur/next.png" alt="next" />' % config.static_server,\
    'prev' : '<img class="movek" src="%s/icones/ibrouteur/prev.png" alt="previous" />' % config.static_server}
#    'remove' : "<img src='"+root_url+"/icones/ibrouteur/remove.png'/ alt='remove' title='remove this index from your selection'>",\
#    'add' : '<img src="'+root_url+'/icones/ibrouteur/add.png" alt="add" title="add this index to your selection"/>',\
#    'add_disabled' : '<img src="'+root_url+'/icones/ibrouteur/add_disabled.png" alt="useless index" title="this index is not significant anymore"/>' }

if __name__ == '__main__':
    print 'this module contains the html templates used for page rendering'
    print header
    print body_start
    print body_end
    print section_start
    print section_end

