import re
from urllib.parse import urljoin

import re
from html import unescape
from urllib.parse import urljoin

import lxml.html
from auto_parse.abstract.extractor_block import BodyExtractor, content_length
from auto_parse.gae import show_content
from auto_parse.gae.utils import remove_preserve_tail
from auto_parse.gae.utils.html_parser import elt, cleaning_properties, md5
from lxml import etree
from readability import Document as _Document
from w3lib import html as hl


def base_extraction(html, title=None, url=None, word=None, printf=None):
    if isinstance(html, bytes):
        code = cchardet.detect(html)['encoding']
        html = html.decode(encoding=code, errors='replace')
    is_title = True
    if title is None:
        is_title = False
        title = ''
    if not word:
        word = ['附件', '文件']
    title = title.strip()
    try:
        new_title = title[title.index(re.findall('[\u4e00-\u9fa5]', title)[0]):]
        if new_title.endswith('...'):
            new_title = new_title.replace('...', '')
    except IndexError:
        new_title = title
    html = remove_footer(html)
    # ===================
    # imt = re.compile(
    #     r'<([^>\s]+)[^>]*>(?:\s*(?:<br \/>|&nbsp;|&thinsp;|&ensp;|&emsp;|&#8201;|&#8194;|&#8195;)\s*)*<\/\1>',
    #     re.DOTALL)
    # html = imt.sub(r'', html)
    # ===================

    # print(show_datetime(html))
    text = show_content(html, title=new_title, word=word)
    if not text:
        text, title = old_func(html, title, new_title, is_title, url)
        if [i for i in ['首页', 'img', '登陆'] if i in text]:
            text = move_head(text, title)
            if text.count('input') > 1:
                text = text.split('<input>', 1)[0]
            text = cleaning_properties(text)
            text = elt(text)
            return text, title
    if title.replace('…', '...').endswith('...'):
        new_title = title.replace('...', '')
        re_title = re.escape(new_title)
        new_title = re.findall(f'({re_title}.*?)<', text, re.DOTALL)
        if new_title:
            title = new_title[0].strip()
    text = cleaning_properties(text)
    text = move_head(text, title)
    text = elt(text)
    return text, title


def extraction(html, title=None, url=None, has_annex=False, base_path='', printf=None):
    text, title = base_extraction(html, title, url, printf=printf)
    if not text:
        return text, title
    new_hx = etree.HTML(text)
    remove_null_a(new_hx)
    if has_annex:
        annex_list = []
        if '附件' in text or '文件' in text:
            if new_hx is None:
                new_hx = etree.HTML(text)
            annex_queue = new_hx.xpath('//a/@href')
            for annex in annex_queue:
                if not annex:
                    continue
                suffix_list = ['.docx', '.pdf', '.xlsx', '.zip', '.doc', 'xls']
                for suffix in suffix_list:
                    if suffix in annex:
                        file_name = base_path + md5(annex) + suffix
                        annex_list.append({'url': annex, 'file_name': file_name})
                        text = text.replace(annex, file_name)
                        break
                else:
                    continue
            if url:
                get_domain_urls(new_hx, url)
            text = etree.tostring(new_hx, pretty_print=True, encoding='utf-8', method='html').decode('utf-8')
            text = unescape(text).replace(' ; ;', '')
            return text, title, annex_list
    if url:
        get_domain_urls(new_hx, url)
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
    except:
        return hx


def old_func(html, title, new_title, is_title, url=''):
    doc_text = _Document(html).summary(html_partial=True)
    block_text = ''
    if len(html) < 1000000:
        block_text = __block_extractor(html=html, title=new_title, url=url, depth=7)
    else:
        title = '文本过大+' + title
    if title.replace('…', '...').endswith('...'):
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
    a_list = element.xpath('//a[not(@href)]')
    for a in a_list:
        a.tag = 'span'


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


def remove_footer(html):
    html = html.replace('</html>', '').replace('<body>', '').replace('</body>', '')
    doc = etree.HTML(html)
    rm_doc = doc.xpath(
        '//*[(ancestor-or-self::*[contains(@id,"foot") or contains(@class,"foot") or @class="dibu"]) '
        'and not(self::script or self::style or self::title)]')
    for r in rm_doc:
        remove_preserve_tail(r)
    rm_footer = doc.xpath('//footer')
    rm_space = doc.xpath('//*[name(.) != "td" and name(.) != "tr" and not(*) and text()[not(normalize-space())]]')
    rm_footer.extend(rm_space)
    for r in rm_footer:
        remove_preserve_tail(r)
    html = etree.tostring(doc, encoding='utf-8', pretty_print=True, method="html").decode('utf-8')
    return html


if __name__ == '__main__':
    import requests
    import cchardet

    url = 'http://www.nbzfcg.cn/project/zcyNotice_view.aspx?Id=eebfb55b-c0a5-4725-8945-4246e8eacb25'
    url = 'http://ggzy.xjbt.gov.cn/TPFront/infodetail/?infoid=fe533a44-a941-4132-a894-8d315df3db43&categoryNum=004001002'
    url = 'http://ggzyjy.sc.gov.cn/jyxx/002001/002001006/20210512/444ef57b-4c2e-46ed-937e-13c075fbd106.html'
    url = 'http://ggzyjy.dl.gov.cn/TPFront/InfoDetail/?InfoID=f3abf49b-3073-4375-961a-c12eae9195dc&CategoryNum=071002004'
    url = 'https://www.ynggzy.com/jyxx/jsgcpbjggsDetail?guid=516b9318-32b0-4c85-8adb-35f8541611ea'
    url = 'https://common.dzzb.ciesco.com.cn/xunjia-zb/gonggaoxinxi/jieGuo_view.html?guid=45dc6016-0e0d-4767-99c3-d769ba706e69&callBackUrl=https://dzzb.ciesco.com.cn/html/crossDomainForFeiZhaoBiao.html'
    url = 'http://ggzyjy.gxhz.gov.cn/zbgg/t8855135.shtml'  # !!!!
    url = 'https://ggzyfw.beijing.gov.cn/jyxxzbhxrgs/20210720/1879936.html'  # !!!!
    url = 'http://www.szfy120.com/xw/tzgg/7422.htm'  # !!!!
    # url = ''
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/77.0.3865.120 Safari/537.36",
    }
    import time
    import threading

    THREAD_NUM = 100


    def thread_crawl_main(fun):
        """多线程"""
        html_thread = []
        for i in range(THREAD_NUM):
            thread = threading.Thread(target=fun)
            html_thread.append(thread)
        for i in range(THREAD_NUM):
            time.sleep(0.01)
            html_thread[i].start()
        # 等待所有线程结束，thread.join()函数代表子线程完成之前，其父进程一直处于阻塞状态。
        for i in range(THREAD_NUM):
            html_thread[i].join()


    k = 'https://gdgpo.czt.gd.gov.cn/freecms//site/gd/ggxx/info/2021/8a7efa5d7d8e6809017d996cbd834890.html?noticeType=001054'
    v = '珠海市公路事务中心珠海市公路事务中心复印纸直接订购采购合同的合同公告'


    def run(ul, tit):
        res = requests.get(url=ul, headers=headers, verify=False, timeout=29).content
        # with open('./cs.html', 'rb') as fp:
        #     res = fp.read()
        tic = time.time()
        result = extraction(res, title=tit, has_annex=True, url=ul,
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
