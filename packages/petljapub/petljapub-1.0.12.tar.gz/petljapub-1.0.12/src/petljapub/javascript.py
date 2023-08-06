# javascript support to switching languages in the HTML file
def add_switcher(md, langs):
    js_switches = "\n<ul class='language-switcher'>\n"
    for lang in langs:
        js_switches += "<li><a href='javascript:displaySolutionByLanguage(\"{}\")'>{}</a></li>\n".format(lang, lang)
    js_switches += "</ul>\n\n"
    
    js_switcher = '''
        
<script type="text/javascript">
   function displaySolutionByLanguage(lang) {{
      var sol_divs = document.getElementsByClassName("sol");
      for (var i = 0; i < sol_divs.length; i++)
             sol_divs[i].style.display = "none";
      document.getElementById("sol-" + lang).style.display = "block";
   }}
   displaySolutionByLanguage(\"{}\")
</script>

    '''.format(langs[0])
        
    return js_switches + md + js_switcher
