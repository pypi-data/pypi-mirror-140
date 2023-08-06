import itertools
import re
from html import unescape
from itertools import chain
from urllib.parse import urljoin

import lxml.html
import cchardet
from auto_parse.abstract.extractor_block import BodyExtractor, content_length
from auto_parse.gae.deal import show_content
from auto_parse.gae.deal.abstract_list import path_raw
from auto_parse.gae.utils import remove_preserve_tail
from auto_parse.gae.utils.html_parser import elt, cleaning_properties, md5, remove_footer
from lxml import etree
from readability import Document as _Document
from w3lib import html as hl

base_file_word_list = ['附件', '文件']
suffix_list = ['.docx', '.pdf', '.xlsx', '.zip', '.doc', '.xls']


def base_extraction(html, title='', url=None, word=None, printf=None, **kwargs):
    html, is_title, title, word = initialization_parameter(html, title, word)
    try:
        # 从第一个中文开始计算
        new_title = title[title.index(re.findall('[\u4e00-\u9fa5]', title)[0]):]
        new_title = new_title if len(new_title) > 4 else title  # title 过短会导致提取精度出现问题
        new_title = new_title.replace('...', '') if new_title.endswith('...') else new_title
    except IndexError:
        new_title = title

    # print(show_datetime(html))
    text = show_content(html, title=new_title, word=word)
    if not text:
        # 如果新版无法兼容，解析失败，走旧逻辑算法
        text, title = old_func(html, title, new_title, is_title, url)
        return text, title
    if title.endswith('...'):
        # 局部title补全
        title = get_full_title(text, title)
    text = cleaning_properties(text)
    text = move_head(text, title)
    text = elt(text, title=title)
    return text, title


def get_full_title(text, title):
    new_title = title.replace('...', '')
    re_title = re.escape(new_title)
    new_title = re.findall(f'({re_title}.*?)<', text, re.DOTALL)
    if new_title:
        title = new_title[0].strip()
    return title


def initialization_parameter(html, title, word):
    # 参数预处理
    if isinstance(html, bytes):
        # html 可以是 二进制类型
        code = cchardet.detect(html)['encoding']
        html = html.decode(encoding=code, errors='replace')
    html = html.replace('</html>', '').replace('<body>', '').replace('</body>', '')  # 处理不合规网页
    html = hl.remove_tags_with_content(html, which_ones=('style',))

    doc = etree.HTML(html)
    if '来源' or '打印' in html:
        rm_middle_column(doc)
    html = remove_footer(html, doc)

    # title
    is_title = False if title is None else True
    title = '' if not title else title
    title = title.replace('…', '...').strip()

    if not word:
        word = base_file_word_list
    return html, is_title, title, word


def extraction(html, title=None, url=None, has_annex=False, base_path='', printf=None, **kwargs):
    text, title = base_extraction(html, title, url, printf=printf, **kwargs)
    annex_list = []
    if not text:
        if has_annex:
            return text, title, annex_list
        return text, title
    new_hx = get_domain_urls(etree.HTML(text), url) if url else etree.HTML(text)
    remove_null_a(new_hx)
    if has_annex:
        if [word for word in chain(base_file_word_list, suffix_list) if word in text]:
            annex_queue = new_hx.xpath('//a/@href')
            annex_text_queue = new_hx.xpath('//a/text()')
            for annex, annex_text in zip(annex_queue, annex_text_queue):
                if not annex or not annex_text:
                    continue
                for suffix in suffix_list:
                    if suffix in annex or suffix in annex_text:
                        file_name = base_path + md5(annex) + suffix
                        annex = annex if not url else urljoin(url, annex)
                        annex_list.append({'url': annex, 'file_name': file_name,
                                           'title': annex_text})
                        if kwargs.get('move_file', ''):
                            rm_list = new_hx.xpath('//a[contains(@href, "{}")]'.format(annex))
                            for rm in rm_list:
                                remove_preserve_tail(rm)
                        else:
                            if not base_path:
                                raise AttributeError('请提供base_path参数 或 move_file=True')
                            target_list = new_hx.xpath('//a[text()="{}"]'.format(annex_text))
                            for target in target_list:
                                target.attrib['href'] = file_name
                        break
        text = etree.tostring(new_hx, pretty_print=True, encoding='utf-8', method='html').decode('utf-8')
        text = unescape(text).replace(' ; ;', '')
        return text, title, annex_list
    text = etree.tostring(new_hx, pretty_print=True, encoding='utf-8', method='html').decode('utf-8')
    text = unescape(text).replace(' ; ;', '')
    return text, title


def get_domain_urls(hx, base_url, is_element=True):
    try:
        if not isinstance(hx, lxml.etree._Element):
            is_element = False
            hx = etree.HTML(hx)
        if base_url:
            a_list = hx.xpath('//a[@href]')
            for a in a_list:
                a.attrib['href'] = urljoin(base_url, a.attrib['href'])
            img_list = hx.xpath('//img[@src]')
            for img in img_list:
                img.attrib['src'] = urljoin(base_url, img.attrib['src'])
        if not is_element:
            return etree.tostring(hx, pretty_print=True, encoding='utf-8', method='html').decode('utf-8')
        else:
            return hx
    except:
        return hx


def old_func(html, title, new_title, is_title, url=''):
    html = hl.remove_comments(html)
    doc_text = _Document(html).summary(html_partial=True)
    block_text = ''
    if len(html) < 400000:
        block_text = __block_extractor(html=html, title=new_title, url=url, depth=7)
    else:
        title = '文本过大+' + title
    if title.endswith('...'):
        title = __get_title(block_text, title=new_title).strip()
    if len(doc_text) < content_length:
        text = block_text
    else:
        text = choose_better_results(doc_text, block_text, title)
    start_len = len(sanitize_string(text))
    if len(sanitize_string(text)) < 100:
        new_text = __block_extractor(html=html, title=new_title, url=url, depth=3)
        if len(sanitize_string(new_text)) > start_len:
            text = new_text
    if len(text) < content_length:
        text = hl.remove_tags_with_content(html, which_ones=('title', 'script', 'head', 'button'))
        text = text.split(title, 1)[-1]
        text = unescape(text)
    if not is_title:
        return text
    if [i for i in ['首页', 'img', '登陆'] if i in text]:
        text = move_head(text, title)  # 删除文前杂质
        text = text.split('<input>', 1)[0] if text.count('input') > 1 else text
        text = cleaning_properties(text)
        text = elt(text, title=title)
    if len(sanitize_string(text)) < len(title) + 20:
        text = ''
    return text, title


def sanitize_string(data):
    data = hl.remove_tags(data)
    p = re.compile('[^\u4e00-\u9fa5]')
    _ = p.sub("", data)
    return _


def choose_better_results(doc_text, block_text, title):
    if [i for i in ['>首页', '>友情链接<', 'icp备', '>版权所有'] if i in block_text]:
        return doc_text
    re_doc_text = sanitize_string(2 * title + doc_text)
    re_block_text = sanitize_string(block_text)
    result = {len(re_doc_text): doc_text, len(re_block_text): block_text}
    better = max(len(re_doc_text), len(re_block_text))
    return result[better]


def __block_extractor(**kwargs):
    html = kwargs.get('html')
    title = kwargs.get('title')
    uri = kwargs.get('url')
    depth = kwargs.get('depth')
    te = BodyExtractor(html=html, title=title, depth=depth)
    te.execute()
    text = te.body
    return text


def __get_title(html: str, title=None):
    try:
        new_title = html.split('<')[0]
    except KeyError:
        new_title = title
    return new_title


def remove_null_a(element):
    # 转换标签
    a_list = element.xpath('//a[not(@href)]')
    for a in a_list:
        a.tag = 'span'
    li_list = element.xpath('//li')
    for li in li_list:
        li.tag = 'p'
    # 删除h标签
    etree.strip_elements(element, *['h1', 'h2', 'h3'])
    rm_space = element.xpath('//li[text()[not(normalize-space())]]')
    for r in rm_space:
        remove_preserve_tail(r)


def move_head(text, title):
    if not text:
        return text
    if title in text and 'table' not in text[:50] or not text.count(title) < 2 or text.count('登录</a>') > 0:
        block = text.split(title, 1)
        new_block = block[0].rsplit('>', 1)
        text = new_block[-1] + title + block[-1]
        if [w for w in ['公司', '编码', '编号', '项目'] if w in new_block[0]]:
            text = new_block[0] + text
        return text
    else:
        return text


def rm_middle_column(doc):
    # 删除标题与正文中间部分
    if not isinstance(doc, etree._Element):
        doc = etree.HTML(doc)
    ns = {"re": "http://exslt.org/regular-expressions"}
    xpath_list = [r"//*[re:match(string(.), '20\d{2}[-/年.]\d{1,2}[-/月.]\d{1,2}') and contains(string(.), '来源')]",
                  r"//*[contains(string(.), '字号') and contains(string(.), '打印')]",
                  r"//*[re:match(string(.), '20\d{2}[-/年.]\d{1,2}[-/月.]\d{1,2}') and contains(string(.), '打印')]",
                  r"//*[contains(string(.), '作者') and contains(string(.), '分享')]",
                  r"//*[re:match(string(.), '20\d{2}[-/年.]\d{1,2}[-/月.]\d{1,2}') and contains(string(.), '作者')]",
                  ]
    xml_list = []
    for xp in xpath_list:
        target = rm_pub_xml(doc.xpath(xp, namespaces=ns)) if '\\' in xp else rm_pub_xml(doc.xpath(xp))
        xml_list.append(target) if isinstance(target, etree._Element) else None
    if len(xml_list) > 1:
        xml_list_new = list(itertools.combinations(xml_list, 2))
        for xml1, xml2 in xml_list_new:
            if len({xml1, xml2}) < 2:
                continue
            if xml1.getparent() == xml2.getparent():
                target = get_max_target(xml1.getparent())
                if len(target.xpath('string(.)')):
                    remove_preserve_tail(target)
                break
        else:
            for rm_target in xml_list:
                remove_preserve_tail(rm_target)
    else:
        for rm_target in xml_list:
            remove_preserve_tail(rm_target)


def rm_pub_xml(xml_list):
    if len(xml_list) < 3:
        return
    xml_path_dic = {path_raw(path).count('/'): path for path in xml_list}
    rm_target = xml_path_dic[max(xml_path_dic)]
    rm_target = get_max_target(rm_target)
    if len(sanitize_string(rm_target.xpath('string(.)'))) < 50:
        return rm_target


def get_max_target(rm_target):
    for i in range(5):
        parent_element = rm_target.getparent()
        if parent_element is not None and rm_target.xpath('string(.)').strip() == parent_element.xpath(
                'string(.)').strip():
            rm_target = rm_target.getparent()
        else:
            break
    return rm_target


if __name__ == '__main__':
    import requests
    import cchardet
    import time

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/77.0.3865.120 Safari/537.36",
    }

    k = 'https://api.jszbtb.com/DataSyncApi/QulifyBulletin/id/2343'
    v = '徐州矿务集团有限公司防爆电动葫芦采购招标公告（第二次）'


    def pub_xml(xml_list):
        if not xml_list:
            return
        xml_path_dic = [path.getparent().getparent() for path in xml_list]
        if len(xml_list) > 1 and len(set(xml_path_dic)) == 1:
            return xml_path_dic[0]


    def run(ul, tit):
        res = requests.get(url=ul, headers=headers, verify=False, timeout=29)
        # with open('./cs.html', 'rb') as fp:
        #     res = fp.read()
        tic = time.time()
        result = extraction(res.content, title=tit, url=ul,
                            # has_annex=True, move_file=True,
                            printf='a')

        a = '''<head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            </head><style type="text/css">
                table.gridtable {
                    font-family: verdana,arial,sans-serif;
                    font-size:11px;
                    color:#333333;
                    border-width: 1px;
                    border-color: #666666;
                    border-collapse: collapse;
                }
                table.gridtable th {
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #666666;
                    background-color: #dedede;
                }
                table.gridtable td {
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #666666;
                    background-color: #ffffff;
                }
            </style>'''

        with open('cs.html', 'w', encoding='utf-8') as fp:
            fp.write(a + '\n' + result[0])
        toc = time.time()
        shijian = toc - tic
        print(shijian)
        print(result)


    run(k, v)
