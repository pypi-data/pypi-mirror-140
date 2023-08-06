import re
from functools import reduce
from time import time

from auto_parse.abstract import extract_utils
from lxml import etree
from w3lib import html as hl

# from numba import jit

content_length = 260
timeout = 120


def fast_deal(len_per_blocks, lines):
    text_list = []
    # text_begin_list = []
    # text_end_list = []
    for i, value in enumerate(len_per_blocks):
        if value > 0:
            # text_begin_list.append(i)
            s = time()
            tmp = lines[i]
            while i < len(len_per_blocks) and len_per_blocks[i] > 0:
                i += 1
                tmp += lines[i] + "\n"
                e = time()
                if e - s > timeout:
                    raise NotImplementedError
            # text_end_list.append(i)
            text_list.append(tmp)
    return text_list


class BodyExtractor(object):
    """
    url:链接地址
    body:正文内容
    depth:行块深度
    """

    def __init__(self, url=None, html=None, title=None, depth=7):
        self.url = url
        self.domain = ''
        self.body = ''  # 正文内容
        self.depth = depth  # 行块的深度
        self.html = html
        self.title = title
        self.plain_text = ''
        self.html_text = ''
        self.margin = 30  # 从text的margin长度开始去匹配text_a_p，数值越大匹配越精确，效率越差

    def execute(self):
        self._pre_process()
        self._extract()
        self._post_process()

    def _pre_process(self):
        if self.url:
            html = extract_utils.get_html(self.url)
        html = self.html
        html = hl.remove_tags_with_content(html, which_ones=('head', 'style', 'option', 'select'))
        html = hl.remove_tags(html, which_ones=('span', 'strong'))
        hx = etree.HTML(html)
        rm_li = hx.xpath('//a[contains(@href,"/")] |//a[contains(@href,".")] |//a[contains(@href,":")]')
        for r in rm_li:
            if not r.xpath(
                    ".//*[not(contains(@href, 'pdf')) and not(contains(@href, 'doc')) and not(contains(@href, 'xls'))]"):
                r.getparent().remove(r)
        self.html = etree.tostring(hx, encoding='utf-8', pretty_print=True, method="html").decode('utf-8')
        # self.html = html
        plain_text, html_text = clean_html(self.html)
        self.html_text = html_text
        self.plain_text = plain_text

    def _post_process(self):
        """
        把资源链接的相对路径改为完整路径
        清空标签的无用属性，比如class, style
        """

        def repl(match):
            s = match.group()
            return s.replace('="', '="' + self.domain)

        try:
            self.body = re.sub(r'(?:href=["\']/(.*?)["\'])|(?:src=["\']/(.*?)["\'])', repl, self.body)
            self.body = re.sub(' (?!src|href)\w*?=".*?"', '', self.body)
        except TypeError:
            pass

    def _extract(self):
        lines = tuple(self.plain_text.split('\n'))
        # lines对应每行的长度
        len_per_lines = [len(re.sub(r'\s+', '', line)) for line in lines]

        # 每个块对应的长度
        len_per_blocks = []
        for i in range(len(len_per_lines) - self.depth + 1):
            word_len = sum([len_per_lines[j] for j in range(i, i + self.depth)])
            len_per_blocks.append(word_len)

        # a = time()
        # print(a)
        text_list = fast_deal(len_per_blocks, lines)
        # b = time()
        # print(b - a)

        if not text_list:
            self.body = self.html
            return self.body
        result = reduce(lambda str1, str2: str1 if len(str1) > len(str2) else str2, text_list)
        result = result.strip()
        if self.title:
            # 去除title噪音
            self.html_text = hl.remove_tags_with_content(self.html_text, which_ones=('head',))
        i_end = self.new_end(result)
        if self.title:
            i_start = self._start(self.title)
            if i_start > i_end:
                i_start = self._start(result)
        else:
            i_start = self._start(result)

        if i_start == 0 or i_end == 0 or i_start > i_end:
            i_start = self._start(result, position=30) - 47
        if i_start > i_end:
            i_end = self.new_end(result)
            i_start = self.new_start(result)
        if i_start < i_end:
            self.body = self.html_text[i_start:i_end]
        else:
            self.body = []
        try:
            self.body = ''.join(self.body.splitlines())
        except AttributeError:
            self.body = ''
        return self.body

    def _start(self, result, position=0):
        i_start = 0
        for i in range(self.margin)[::-1]:
            start = result[position:i + position]
            p = re.compile(re.escape(start), re.IGNORECASE)
            match = p.search(self.html_text)
            if match:
                s = match.group()
                i_start = self.html_text.index(s)
                break
        return i_start

    def _end(self, result):
        i_end = 0
        for i in range(1, self.margin)[::-1]:
            end = result[-i:]
            p = re.compile(re.escape(end), re.IGNORECASE)
            match = p.search(self.html_text)
            if match:
                s = match.group()
                i_end = self.html_text.index(s) + len(s)
                break
        return i_end

    def new_end(self, result):
        i_end = 0
        for i in range(1, self.margin)[::-1]:
            end = result[-i:]
            end_index = self.html_text.rfind(end)
            if end_index != -1:
                i_end = end_index + len(end)
                break
        return i_end

    def new_start(self, result, position=0):
        i_start = 0
        for i in range(self.margin)[::-1]:
            start = result[position:i + position]
            start_index = self.html_text.find(start)
            if start_index != -1:
                i_start = start_index + len(start)
                break
        return i_start


def clean_html(html):
    """
    清洗html文本，去掉无用标签
    1. "script","style",注释标签<!-->整行用空格代替
    2. 特殊字符转义
    return:(pure_text,html_text):纯文本和包含标签的html文本
    """
    regex = re.compile(
        r'(?:<!DOCTYPE.*?>)'
        # r'|'  # doctype
        # r'(?:<head[\S\s]*?>[\S\s]*?</head>)'
        # r'|'
        # r'(?:<!--[\S\s]*?-->)|'  # comment
        # r'(?:<script[\S\s]*?>[\S\s]*?</script>)|'  # js...
        # r'(?:<style[\S\s]*?>[\S\s]*?</style>)'
        , re.IGNORECASE)  # css
    re_script = re.compile(r'(?:<script[\S\s]*?>[\S\s]*?</script>)')
    re_js_comment = re.compile(r'/\*.*?\*/', re.DOTALL)
    html = re_js_comment.sub('', html)
    html = hl.remove_comments(html)

    script_list = re_script.findall(html, re.DOTALL)
    for script in script_list:
        is_html = False
        if '&lt;div' in script or '<span' in script or '<div' in script or '&lt;span' in script or '&lt;p' in script \
                or '<p' in script:
            if deal_script(script):
                is_html = True
        if not is_html:
            html = html.replace(script, '')

    # html = hl.remove_tags(html, which_ones=('script',))
    html_text = regex.sub('', html)  # 保留html标签
    plain_text = re.sub(r"(?:</?[\s\S]*?>)", '', html_text)  # 不包含任何标签的纯html文本
    html_text = extract_utils.html_escape(html_text)
    plain_text = extract_utils.html_escape(plain_text)
    return plain_text, html_text


def deal_script(script):
    script = re.sub('//.*', '', script)
    rate = len(re.sub('[^\u4e00-\u9fa5]', '', script))
    if rate > 100:
        return True


if __name__ == "__main__":

    url = "http://gdstc.gd.gov.cn/zwgk_n/zcfg/szcfg/content/post_3248794.html"
    url = "http://ggzyjy.gxhz.gov.cn/zbgg/t8844664.shtml"
    # url = "http://gdstc.gd.gov.cn/zwgk_n/zcfg/szcfg/content/post_3248794.html"
    url = "https://www.sxbid.com.cn/f/view-6796f0c147374f85a50199b38ecb0af6-7efe28fe87604e0a90e27a35ecbc588f.html"
    url = "http://czju.suzhou.gov.cn/zfcg/html/project/c0383d4aa154433c8c9b553fabe619cf.shtml"
    URL_LIST = [
        'https://www.sxbid.com.cn/f/view-6796f0c147374f85a50199b38ecb0af6-7efe28fe87604e0a90e27a35ecbc588f.html',
        # 'http://www.miit.gov.cn/qzqd/hnstxglj/qlqd/xzcf7114/art/2020/art_6f8001312fed431a970b39f0c6ed7300.html#Beizhu',
        # 'http://www.nx.gov.cn/zwxx_11337/zwdt/202105/t20210518_2842570.html',
        # 'https://www.hainan.gov.cn/hainan/czyjs/202105/9816ec34f163461ba2c6c8f3d895e2e8.shtml',
        # 'https://www.hainan.gov.cn/hainan/wxts/202105/26112c448bbc4528a43a1364fddbefe3.shtml',
        # 'http://www.gansu.gov.cn/art/2021/5/19/art_35_481288.html',
        # 'http://www.xizang.gov.cn/xwzx_406/zwyw/202105/t20210518_202604.html',
        # 'http://news.youth.cn/gn/202105/t20210520_12956073.htm',
        # 'http://www.gov.cn/zhengce/content/2021-05/19/content_5608622.htm'
    ]
    for url in URL_LIST:
        te = BodyExtractor(url)
        te.execute()
        # doc = Document(te.body)
        # print(doc.summary(html_partial=True))

        with open('./tq.html', 'a', encoding='utf-8') as fp:
            fp.write(te.body + '<br><br>')
    # print(te.img)
    # print(te.title)
