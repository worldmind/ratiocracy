import re
from pathlib import Path
from lxml import etree as ET


result = ''


def convert_epigraph(element):
    author = ''
    if element.find(db('attribution')) is not None:  # Elements with no subelements will test as False.
        author = convert_paragraph(element.find(db('attribution')))
    text = ''
    paragraphs = list(element.findall(db('para')))
    for i, para in enumerate(paragraphs):
        text += convert_paragraph(para)
        # crutch for compatibility with old latex file
        if i != len(paragraphs)-1:
            text += '\epar\n\spar'
    if author:
        result = '\epigraph{%s}{%s}\n' % (text, author)
    else:
        result = '\epigraph{%s}\n' % text
    return result
    

def convert_section_header(latex_type, element):
    result = '\n\\%s{' % latex_type
    result += convert_paragraph(element.find(db('info')).find(db('title'))) + '}\n'
    result += r'\label{' + element.attrib[xml('id')] + '}\n'
    return result


def parse(parent):
    global result
    for e in parent:
        if e.tag == db('info'):
            pass  # will be converted together with header
        elif e.tag == db('chapter'):
            result += convert_section_header('part', e)
            parse(e)
            result += '\\myendpart{}\n'
        elif e.tag == db('sect1'):
            result += convert_section_header('chapter', e)
            parse(e)
            result += '\\myendchapter{}\n'
        elif e.tag == db('sect2'):
            result += convert_section_header('section', e)
            parse(e)
            result += '\\myendsection{}\n'
        elif e.tag == db('sect3'):
            result += convert_section_header('subsection', e)
            parse(e)
            result += '\\myendsubsection{}\n'
        elif e.tag == db('sect4'):
            result += convert_section_header('subsubsection', e)
            parse(e)
            result += '\\myendsubsubsection{}\n'
        elif e.tag == db('epigraph'):
            result += convert_epigraph(e)
        elif e.tag == db('indexterm'):
            result += '\index{%s}\n' % e.find(db('primary')).text
        elif e.tag == db('note'):
            result += '\\note{%s}{%s}\n' % (
                e.find(db('title')).text,
                convert_paragraph(e.find(db('para')))
            )
            pass
        elif e.tag == db('para'):
            result += '\\spar\n' + convert_paragraph(e) + '\\epar\n'
        elif e.tag == db('index'):
            pass
        elif e.tag == db('glossary'):
            pass
        elif e.tag == db('bibliography'):
            pass
        elif e.tag == db('colophon'):
            pass
        else:
            print(f'Unknown child: {child.tag}')


def convert_paragraph(para):
    result = ''
    if para.text:
        result = para.text

    for e in para:
        if e.tag == db('glossterm'):
            result += '\\gl{%s}{%s}' % (e.attrib['linkend'], e.text)
        elif e.tag in (db('itemizedlist'), db('orderedlist')):
            if e.get('role') == 'seealso':
                list_type = 'seealsolist'
            elif e.get('role') == 'numpar':
                list_type = 'numparlist'
            elif e.get('role') == 'fromzero':
                list_type = 'fromzerolist'
            elif e.tag == db('orderedlist'):
                list_type = 'enumerate'
            elif e.tag == db('itemizedlist'):
                list_type = 'itemizedlist'
            else:
                raise AssertionError('Unknown list type %s %s' % (e.tag, e.get('role')))

            result += '\\begin{%s}\n' % list_type
            for item in e.findall(db('listitem')):
                result += r'  \item '
                paragraphs = list(item.findall(db('para')))
                for i, para in enumerate(paragraphs):
                    result += convert_paragraph(para)
                    # crutch for compatibility with old latex file
                    if i != len(paragraphs)-1:
                        result += '\epar\n\spar'
                result += '\n'
            result += '\\end{%s}\n' % list_type
        elif e.tag == db('blockquote'):
            result += '\\begin{ruquotation}\n'
            assert len(e.findall(db('para'))) == 1
            result += convert_paragraph(e.find(db('para')))
            result += '\n\\end{ruquotation}\n'
        elif e.tag == db('quote'):
            parent = e.getparent()
            if 'quote' in parent.tag or 'quote' in parent.getparent().tag:
                result += r'„%s“' % convert_paragraph(e)
            else:
                result += r'«%s»' % convert_paragraph(e)
        elif e.tag == db('xref'):
            if e.get('role') == 'simple':
                result += '\\simplefullref{%s}' % e.attrib['linkend']
            else:
                result += '\\fullref{%s}' % e.attrib['linkend']
        elif e.tag == db('link'):
            link = e.attrib[xlink('href')]
            result += '\\href{%s}{%s}' % (link, convert_paragraph(e))
        elif e.tag == db('citation'):
            result += r'\cite{%s}' % e.text
        elif e.tag == db('footnote'):
            assert len(e.findall(db('para'))) == 1
            result += r'\footnote{%s}' % convert_paragraph(e.find(db('para')))
        elif e.tag == db('emphasis'):
            if e.get('role') == 'bold':
                result += r'\parheader{%s}' % convert_paragraph(e)
            elif e.get('role') == 'strong':
                result += r'\emphasis{%s}' % convert_paragraph(e)
            else:
                result += r'\emphasis{%s}' % e.text
        elif e.tag == db('indexterm'):
            result += '\index{%s}' % e.find(db('primary')).text
        else:
            AssertionError(f'Unknonw tag: {e.tag}')
        if e.tail:
            result += e.tail

    return result


def db(tag_name):
    return '{' + ns['db'] + '}' + tag_name


def xml(tag_name):
    return '{' + ns['xml'] + '}' + tag_name


def xlink(tag_name):
    return '{' + ns['xlink'] + '}' + tag_name


def latex_post_process(text):
    text = text.replace("\u00A0", '~')
    text = re.sub(r'\(см.~(\\fullref{[^}]+})\)', r'\1', text)
    text = text.replace(r'×', r'\times')
    text = text.replace(r'%', r'\%')
    text = re.sub('\s+\n', '\n', text)
    text = re.sub(r'(.)\u0301', r"\\'{\1}", text, flags=re.DOTALL)

    return text


if __name__ == '__main__':
    ns = {
        'db': 'http://docbook.org/ns/docbook',
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'xlink': 'http://www.w3.org/1999/xlink',
    }

    root = ET.fromstring(Path('ratiocracy.docbook').read_bytes())
    parse(root)
    result = latex_post_process(result)
    result = re.sub('\n+', '\n', result, flags=re.DOTALL)
    result = result.replace(r'\part{Предисловие}', r'\part*{Предисловие}')
    result = result.replace(r'\label{intro}', r'\label{intro}'+'\n'+r'\addcontentsline{toc}{part}{Предисловие}')
    result = result.replace(r'\chapter{Инструментопоклонничество}', r'\chapter{Инструменто\-поклонничество}')
    result = result.replace(r'κράτος', r'\textgreek{κράτος}')

    cites_match = re.search(r'(\\cite{[^}]+}){2,}', result)
    if cites_match:
        cites = cites_match.group().split(r'\cite')
        cites = [cite[1:-1] for cite in cites if cite]
        joined_cites = r'\cite{' + ','.join(cites) + '}'
        result = result.replace(cites_match.group(), joined_cites)

    Path('book.tex').write_text(result.strip())

    
    # Create main.tex, latex markup conflicts with mako templates
    # so, handmade template "engine" used
    info = root.find(f"./db:info", ns)
    data = Path('scripts/main.tex.template').read_text()
    author_name = (
        info.find("./db:author/db:personname/db:firstname", ns).text + ' '
         + info.find("./db:author/db:personname/db:surname", ns).text
    )
    data = data.replace('AUTHOR_TAG', author_name)
    data = data.replace('SITE_TAG', info.find("./db:author/db:uri", ns).text)
    data = data.replace('EMAIL_TAG', info.find("./db:author/db:email", ns).text)
    # replace subtitle before title
    data = data.replace('SUBTITLE_TAG', info.find("./db:subtitle", ns).text)
    data = data.replace('TITLE_TAG', info.find("./db:title", ns).text)
    data = data.replace('COPYRIGHT_TAG', author_name)
#    data = data.replace('ABSTRACT_TAG', info.find("./db:abstract/db:para", ns).text)
#    data = data.replace('LICENSE_TAG', info.find("./db:legalnotice/db:para", ns).text)
    # PUBLISHER_TAG
    # CITY_TAG
    # ISBN_TAG
    editors, illustrator = '', ''
    for othercredit in info.findall("./db:othercredit", ns):
        name = (othercredit.find("./db:personname/db:firstname", ns).text + ' '
                + othercredit.find("./db:personname/db:surname", ns).text)
        if othercredit.get('role') == 'copyeditor':
            editors += name + ', '
        elif othercredit.get('role') == 'graphicdesigner':
            illustrator += name
        else:
            raise AssertionError(othercredit.get('role'))
    data = data.replace('EDITOR_TAG', editors[:-2])
    data = data.replace('COVER_ILLUSTRATOR_TAG', illustrator)
    data = data.replace('INDEX_NAME_TAG', 'Предметный указатель')  # FIXME, check what docbook use
    data = data.replace('COLOPHON_TEXT_TAG', root.find("./db:colophon/db:para", ns).text)

    Path('main.tex').write_text(data)

    # Conver glossary
    glossary = ''
    for entry in root.find(db('glossary')).findall(db('glossentry')):
        term = entry.find(db('glossterm')).text
        definition = convert_paragraph(entry.find(db('glossdef')).find(db('para')))
        xml_id = entry.get(xml('id'))
        glossary += r"""\newglossaryentry{%s}{
    name=%s,
    description={%s}
}

""" % (xml_id, term, definition)

    glossary = latex_post_process(glossary)
    Path('glossary.tex').write_text(glossary)
    

    # Covert bibliography
    bibliography= ''
    for entry in root.find(db('bibliography')).findall(db('biblioentry')):
        abbrev = entry.find(db('abbrev')).text
        author = entry.find('./db:author/db:personname', ns).text
        author = author.replace(',', r'{,}')
        title = entry.find(db('title')).text
        if entry.find(db('bibliosource')) is not None:
            link = entry.find('./db:bibliosource/db:link', ns).get(xlink('href'))
            bibliography += """@misc{%s,
\tauthor    = "%s",
\ttitle     = "%s",
\turl       = {%s},
}
""" % (abbrev, author, title, link)
        else:
            bibliography += """@book{%s,
\tauthor    = "%s",
\ttitle     = "%s",
}
""" % (abbrev, author, title)

    Path('bibliography.bib').write_text(bibliography)

    # Create files for different formats

    Path('ratiocracy-a4.tex').write_text(r"""\documentclass[oneside]{book}
\usepackage[a4paper]{geometry}
\input{main}
""")

    Path('ratiocracy-a5.tex').write_text(r"""\documentclass[11pt,oneside]{book}
\usepackage[
  paperheight=205mm,
  paperwidth=145mm,
  left=20mm,
  right=14mm,
  top=14mm,
  bottom=14mm,
  nomarginpar,
  nohead,
  footskip=\baselineskip,
  includefoot
]{geometry}
\input{main}
""")

    Path('ratiocracy-a6.tex').write_text(r"""\documentclass[oneside]{book}
\usepackage[a6paper]{geometry}
\input{main}
""")

    # Don't remember why mst files needed
    data = '''delim_0 " "
delim_1 " "
delim_2 " "''';
    Path('ratiocracy-a4.mst').write_text(data)
    Path('ratiocracy-a5.mst').write_text(data)
    Path('ratiocracy-a6.mst').write_text(data)
