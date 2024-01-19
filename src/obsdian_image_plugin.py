from markdown_it import MarkdownIt
import os
import os.path as path
import re


def obsdian_image_plugin(md: MarkdownIt, options):
  def find_file(name: str):
    for dir in options["obsdian_image_find_paths"]:
      for file in os.listdir(dir):
        if file == name:
          return path.abspath(path.join(dir, file))
    
  def ruler(state, silent):
    matched = re.match(r"!\[\[(?P<path>[^\]]*)\]\]", state.src[state.pos:])
    if not matched:
      return False
    path_group = matched.group("path").split("#")
    path = path_group[0]
    desc = path_group[1] if path_group.__len__() > 1 else ""
    if not path:
      return False
    img_path = find_file(path)
    
    if not silent:
      token = state.push("image", "img", 0)
      token.attrs = {"src": img_path, "alt": ""}
      token.content = desc

    state.pos = state.pos + len(matched.group())
    return True

  md.inline.ruler.push("obsdian_image", ruler)