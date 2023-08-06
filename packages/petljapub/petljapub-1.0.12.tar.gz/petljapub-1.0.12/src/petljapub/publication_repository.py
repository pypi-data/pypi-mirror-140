import os
import pathlib

from .md_util import parse_front_matter
from . import logger

# A publication contains Markdown files, stored within a given
# directory root_dir and its subdirectories. A default setup assumes
# that each publication section is writen in the file named index.md,
# stored in a separate directory (together with tasks related to that
# section). However, other filenames are also supported. The central
# functionality of the class is reading Markdown files (the method
# "read_md_file"). Files can be specified either by their absolute paths
# (relative to the root_dir) or by their relative paths determined
# only by the section directory names (which should be unique).
# For example, if the root_dir is "/home/user/pub", then the file
# "/home/user/pub/01 datastructures/03 stack/implementation.md"
# can be accessed either as
#   read_file("01 datastructures/03 stack/implementation.md")
# or just as
#   read_file("stack/implementation.md") -- the full path is automatically resolved
# Index files can be read using the method read_index. For example,
#   read_index("stack")
# would read the file "/home/user/pub/01 datastructures/03 stack/index.md"

class PublicationRepository:
    # initialize repository stored in the given root_dir
    def __init__(self, root_dir, normalize_md=None, translit=None):
        self._root_dir = root_dir
        self._normalize_md = normalize_md
        self._translit = translit
        self._section_dir = self.__collect_section_dirs(root_dir)

    # path given relative to the root_dir is expanded to the full absolute path
    def full_path(self, path):
        return os.path.join(self._root_dir, path)

    # extracting section name (key) from the given section path
    # e.g. "00 stack/01 implementation/file.md" -> "implementation"
    # e.g. "00 stack/01 implementation" -> "implementation"
    @staticmethod
    def extract_key(path):
        # remove md filename if present
        if path.endswith(".md"):
            path = os.path.dirname(path)
        # use the last directory
        dir = os.path.basename(path)
        # remove leading numbers
        return dir.split(" ", 1)[-1]


    # enable relative section addressing, by collecting all subdirs of the given
    # publication home directory that contain index.md files, and mapping dir
    # names (keys) to their paths. Eg. if md files are the following:
    #    src/datastructures/index.md
    #    src/datastructures/stack/index.md
    #    src/datastructures/queue/index.md
    # the resulting dictionary will be
    #   {"datastructures": "src/datastructures"
    #    "stack": "src/datastructures/stack"
    #    "queue": "src/datаstructures/queue"}
    def __collect_section_dirs(self, root_dir):
        root_dir = os.path.abspath(root_dir)
        dirs = {}
        # recursive enumeration of all subdirectories
        for path in pathlib.Path(root_dir).rglob('*'):
            # check if the current path is a section specification 
            if path.name.endswith('index.md'):
                index_file = str(path)
                key = PublicationRepository.extract_key(index_file)
                dir = os.path.dirname(index_file)
                # strip root_dir from the beginning
                if dir.startswith(root_dir):
                    dir = dir[len(root_dir)+1:]
                # add dir to the result
                if key in dirs:
                    dirs[key].append(dir)
                    logger.warn("duplicate directory: ", key, " - ", dirs[key])
                else:
                    dirs[key] = [dir]
        return dirs

    # try to resolve relative section paths using collected section names (keys)
    # paths to existing resources are not changed
    # a full path is always returned
    def resolve_path(self, path):
        # absolute paths are not changed
        if os.path.isfile(path) or os.path.isdir(path):
            return path
        # absolute paths relative to the root_dir
        full_path = self.full_path(path)
        if os.path.isfile(full_path) or os.path.isdir(full_path):
            return full_path

        # if the directory exist the path is not changed
        if os.path.isdir(os.path.dirname(full_path)):
            return full_path
        
        # treating the path as relative and trying to resolve it
        key = PublicationRepository.extract_key(path)
        if key in self._section_dir:
            if len(self._section_dir[key]) > 0:
                logger.warn("multiple sections with the name", key, "- taking the first one")
            dir = self._section_dir[key][0]
            if path.endswith(".md"):
                file = os.path.basename(path)
                return self.full_path(os.path.join(dir, file))
            else:
                return self.full_path(dir)

        # path could not be resolved
        return full_path

    # read title (metadatum `title`) and the content of the given md
    # file (given either by an absolute path, or a relative path
    # containing only section name and the file name)
    def read_md_file(self, path):
        path = self.resolve_path(path)

        if not os.path.isfile(path):
            logger.error(path, "does not exist")
            return "", ""
        
        content, metadata = parse_front_matter(path)
        title = metadata.get("title", "")

        # normalize markdown dialect and transliterate if necessary
        if self._normalize_md:
            content = self._normalize_md(content)
        if self._translit:
            title = self._translit(title)
            content = self._translit(content)
            
        return title, content
        
    # full path for the index.md file of a given section (given either
    # by an absolute path, or a relative path containing only the
    # section name)
    def index_md(self, path):
        return os.path.join(self.resolve_path(path), "index.md")

    # check if the given section (given either by an absolute path, or
    # a relative path containing only the section name) contains an
    # index file
    def contains_index(self, path):
        return os.path.isfile(self.index_md(path))
  
    # title (metadatum `title`) and the content of the index file
    # `index.md` within the given section (given either by an absolute
    # path, or a relative path containing only the section name)
    def read_index(self, path):
        if self.contains_index(path):
            return self.read_md_file(self.index_md(path))
        else:
            logger.warn("index for", path, "does not exist")
            return ("[" + path + "]", "")

        
if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser(description='Publication repository')
    parser.add_argument('root_dir', type=str,
                        help='Root directory of the publication')
    args = parser.parse_args()
    repo = PublicationRepository(args.root_dir)
    for line in sys.stdin:
        line = line.strip()
        print(repo.resolve_path(line))
