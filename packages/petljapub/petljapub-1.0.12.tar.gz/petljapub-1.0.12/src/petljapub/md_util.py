import sys
import re
import yaml
from .util import read_file
from . import logger

# split initial Metadata in Yaml format from the rest of the file in
# Markdown format
def parse_front_matter(fname):
    # Taken from Jekyll
    # https://github.com/jekyll/jekyll/blob/3.5-stable/lib/jekyll/document.rb#L13
    YAML_FRONT_MATTER_REGEXP = r"\A---\s*\n(.*?)\n?^((---|\.\.\.)\s*$\n?)"

    file = read_file(fname)
    if file is None:
        logger.error("reading file:", fname)
        return "", {}

    match = re.search(YAML_FRONT_MATTER_REGEXP, file, re.DOTALL|re.MULTILINE)
    if not match:
        logger.error("parsing file:", fname)
        return "", {}
    
    try:
        header = yaml.safe_load(match.group(1))
        content = match.string[match.end():]
        return content, header
    except:
        logger.error("parsing file:", fname)
        return "", {}

# surround the given source code in a given programming language with
# appropriate markdown formating (~~~)
def md_source_code(code, lang, title=None):
    lang_id = {"cpp": "cpp", "cs": "cs", "py": "python"}.get(lang, lang) # defaults to lang if not "cpp", "cs", "py"
    result_md = title + "\n" if title else ""
    result_md += "~~~" + lang_id + "\n" + code + "~~~\n"
    return result_md

link_re = r"\[([^])\n]*)\]\(([-a-zA-Z_0-9./]*)\)"
image_re = r"!" + link_re

# find all links in a Markdown document (returns list of pairs
# containing link title and link path)

def link(title, path):
    return "[{}]({})".format(title, path)

def links_in_md(md):
    result = []
    for link in re.finditer("(?<![!])" + link_re, md):
        result.append((link.group(1), link.group(2)))
    return result

def replace_link(md, old_title, old_path, new_title, new_path):
    old_link = link(old_title, old_path)
    new_link = link(new_title, new_path)
    return md.replace(old_link, new_link)

def remove_link(md, new_content):
    old_link = link(old_title, old_path)
    return md.replace(old_link, new_content)

# find all images in a Markdown document (returns list of pairs
# containing image title and image path)
def images_in_md(md):
    result = []
    for image in re.finditer(image_re, md):
        result.append((image.group(1), image.group(2)))
    return result

# degrade all headings so that # becomes # * level
def degrade_headings(md, level, unnumbered=False):
    result = []
    for line in md.split('\n'):
        m = re.match("^(#+)\s+(.+)$", line)
        if m:
            current_level = len(m.group(1))
            heading = "#" * (current_level + level - 1) + " " + m.group(2)
            if unnumbered:
                heading += " {.unnumbered .unlisted}"
            result.append(heading)
        else:
            result.append(line)
    return "\n".join(result)


class PandocMarkdown:
    # fix latex $ signs in accordance with Pandoc Markdown dialect
    @staticmethod
    def fix_latex_dollars(md):
        # replace $$ by $ for inline maths
        md = re.sub(r"\$\$", "$", md)
        # put $$ around displayed maths
        # single displayed line
        md = re.sub(r"\n\n[ \t]*\$(.+)\$[ \t]*(\n\n|\n\Z|\Z)", r"\n\n$$\1$$\n\n", md)
        # multiple displayed lines
        md = re.sub(r"\n\n[ \t]*\$([^$]+)\$[ \t]*(\n\n|\n\Z|\Z)", r"\n\n$$\1$$\n\n", md)
        return md

    # fix indentation of itemized lists in accordance with Pandoc
    # Markdown dialect
    @staticmethod
    def fix_itemize(md):
        return re.sub(r"^-(?!(\d|\n|[-]))", "  -", md)

    # fix Markdown content in accordance with Pandoc Markdown dialect
    @staticmethod
    def fix(md):
        md = PandocMarkdown.fix_latex_dollars(md)
        md = PandocMarkdown.fix_itemize(md)
        return md

if __name__ == '__main__':
    pass
