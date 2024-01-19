import socket

from docx.oxml import CT_Inline, OxmlElement, ns, xmlchemy
from docx.oxml.ns import qn

from myenums import CNFontFaces, bcolors


# 工具函数
def list_number(doc, par, prev=None, level=None, num=True):
  """
  Makes a paragraph into a list item with a specific level and
  optional restart.

  An attempt will be made to retreive an abstract numbering style that
  corresponds to the style of the paragraph. If that is not possible,
  the default numbering or bullet style will be used based on the
  ``num`` parameter.

  Parameters
  ----------
  doc : docx.document.Document
      The document to add the list into.
  par : docx.paragraph.Paragraph
      The paragraph to turn into a list item.
  prev : docx.paragraph.Paragraph or None
      The previous paragraph in the list. If specified, the numbering
      and styles will be taken as a continuation of this paragraph.
      If omitted, a new numbering scheme will be started.
  level : int or None
      The level of the paragraph within the outline. If ``prev`` is
      set, defaults to the same level as in ``prev``. Otherwise,
      defaults to zero.
  num : bool
      If ``prev`` is :py:obj:`None` and the style of the paragraph
      does not correspond to an existing numbering style, this will
      determine wether or not the list will be numbered or bulleted.
      The result is not guaranteed, but is fairly safe for most Word
      templates.
  """
  xpath_options = {
      True: {'single': 'count(w:lvl)=1 and ', 'level': 0},
      False: {'single': '', 'level': level},
  }

  def style_xpath(prefer_single=True):
      """
      The style comes from the outer-scope variable ``par.style.name``.
      """
      style = par.style.style_id
      return (
          'w:abstractNum['
              '{single}w:lvl[@w:ilvl="{level}"]/w:pStyle[@w:val="{style}"]'
          ']/@w:abstractNumId'
      ).format(style=style, **xpath_options[prefer_single])

  def type_xpath(prefer_single=True):
      """
      The type is from the outer-scope variable ``num``.
      """
      type = 'decimal' if num else 'bullet'
      return (
          'w:abstractNum['
              '{single}w:lvl[@w:ilvl="{level}"]/w:numFmt[@w:val="{type}"]'
          ']/@w:abstractNumId'
      ).format(type=type, **xpath_options[prefer_single])

  def get_abstract_id():
      """
      Select as follows:

          1. Match single-level by style (get min ID)
          2. Match exact style and level (get min ID)
          3. Match single-level decimal/bullet types (get min ID)
          4. Match decimal/bullet in requested level (get min ID)
          3. 0
      """
      for fn in (style_xpath, type_xpath):
          for prefer_single in (True, False):
              xpath = fn(prefer_single)
              ids = numbering.xpath(xpath)
              if ids:
                  return min(int(x) for x in ids)
      return 0

  if (prev is None or
          prev._p.pPr is None or
          prev._p.pPr.numPr is None or
          prev._p.pPr.numPr.numId is None):
      if level is None:
          level = 0
      numbering = doc.part.numbering_part.numbering_definitions._numbering
      # Compute the abstract ID first by style, then by num
      anum = get_abstract_id()
      # Set the concrete numbering based on the abstract numbering ID
      num = numbering.add_num(anum)
      # Make sure to override the abstract continuation property
      num.add_lvlOverride(ilvl=level).add_startOverride(1)
      # Extract the newly-allocated concrete numbering ID
      num = num.numId
  else:
      if level is None:
          level = prev._p.pPr.numPr.ilvl.val
      # Get the previous concrete numbering ID
      num = prev._p.pPr.numPr.numId.val
  par._p.get_or_add_pPr().get_or_add_numPr().get_or_add_numId().val = num
  par._p.get_or_add_pPr().get_or_add_numPr().get_or_add_ilvl().val = level

# 不应该使用这个函数，应该使用Word的自动生成目录。
def add_toc(doc, ):
  paragraph = doc.add_paragraph()
  run = paragraph.add_run()
  fldChar = OxmlElement('w:fldChar')  # creates a new element
  fldChar.set(qn('w:fldCharType'), 'begin')  # sets attribute on element
  instrText = OxmlElement('w:instrText')
  instrText.set(qn('xml:space'), 'preserve')  # sets attribute on element
  instrText.text = 'TOC \\o "1-3" \\h \\z \\u' # type: ignore # change 1-3 depending on heading levels you need

  fldChar2 = OxmlElement('w:fldChar')
  fldChar2.set(qn('w:fldCharType'), 'separate')
  # fldChar3 = OxmlElement('w:t')
  # fldChar3.text = "Right-click to update field."
  fldChar3 = OxmlElement('w:updateFields')
  fldChar3.set(qn('w:val'), 'true')
  fldChar2.append(fldChar3)

  fldChar4 = OxmlElement('w:fldChar')
  fldChar4.set(qn('w:fldCharType'), 'end')

  r_element = run._r
  r_element.append(fldChar)
  r_element.append(instrText)
  r_element.append(fldChar2)
  r_element.append(fldChar4)
  # p_element = paragraph._p

def create_element(name):
  return OxmlElement(name)

def create_attribute(element, name, value):
  element.set(ns.qn(name), value)

def add_page_number(run):
  fldChar1 = create_element('w:fldChar')
  create_attribute(fldChar1, 'w:fldCharType', 'begin')

  instrText = create_element('w:instrText')
  create_attribute(instrText, 'xml:space', 'preserve')
  instrText.text = "PAGE" # type: ignore

  fldChar2 = create_element('w:fldChar')
  create_attribute(fldChar2, 'w:fldCharType', 'end')

  run._r.append(fldChar1)
  run._r.append(instrText)
  run._r.append(fldChar2)

def set_bold(style):
  style.font.bold = True
  style.font.cs_bold = True
  style.font.italic = False
  style.font.cs_italic = False

# 快捷设置中英文字体
def set_font_face(style, zh: str, not_zh: str):
  style.font.name = not_zh
  rFonts = style.element.rPr.rFonts
  rFonts.set(qn('w:eastAsia'), zh)
  rFonts.set(qn('w:eastAsiaTheme'), zh)
  rFonts.set(qn('w:asciiTheme'), not_zh)
  rFonts.set(qn('w:hAnsi'), not_zh)

# 快捷设置中英文字体
def set_font_face_en(style, en: str):
  style.font.name = en
  rFonts = style.element.rPr.rFonts
  rFonts.set(qn('w:eastAsia'), CNFontFaces.宋体)
  rFonts.set(qn('w:eastAsiaTheme'), CNFontFaces.宋体)
  rFonts.set(qn('w:asciiTheme'), en)
  rFonts.set(qn('w:hAnsi'), en)

def delete_paragraph(paragraph):
  p = paragraph._element
  p.getparent().remove(p)
  p._p = p._element = None


def count_char_map(src: str):
  char_map = {
    "space": 0,
    "alpha": 0,
    "number": 0,
    "other": 0,
  }

  for char in src:
    if char.isspace():
      char_map["space"] += 1
    elif char.isascii() and char.isalpha():
      char_map["alpha"] += 1
    elif char.isdigit():
      char_map["number"] += 1
    else:
      char_map["other"] += 1

  return char_map

# 汉字和空格比例大约是4.4:1，数字和空格比例大约是2:1
# 一行最好容纳有67个空格
def calculate_char_map_space_sum(char_map):
  weighted_sum = char_map["space"] * 1 + char_map["alpha"] * 2 + char_map["number"] * 2.04 + char_map["other"] * 4.1
  return weighted_sum

def get_count_char_space_width(src: str):
  char_widths = []
  
  for char in src:
    if char.isspace():
      char_widths.append(1)
    elif char.isascii() and char.isalpha():
      char_widths.append(2)
    elif char.isdigit():
      char_widths.append(2.04)
    else:
      char_widths.append(4.1)
  
  return char_widths

def get_free_port():
  sock = socket.socket()
  sock.bind(('', 0))
  port = sock.getsockname()[1]
  sock.close()
  return port

# 打印警告的函数
def preprint_content_in_map(src_lines, map):
  result = ""
  if map == None:
    return ""

  for i in range(map[0], map[1]):
    if i % 2 == 1:
      continue
    result += f"{bcolors.OKCYAN}行{str(int(i/2)).ljust(5)}{bcolors.ENDC}|{src_lines[int(i / 2)]}\n"
  return result

def print_faild(msg, e):
  print(f"\n\n{bcolors.FAIL}----发生错误----{bcolors.ENDC}\n")
  print(f"{bcolors.FAIL}[错误] {msg}。{bcolors.ENDC}")
  print("原始报错信息：", e)