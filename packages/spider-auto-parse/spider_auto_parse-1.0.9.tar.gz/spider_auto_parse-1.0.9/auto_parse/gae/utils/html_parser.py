import hashlib
import re
from itertools import chain

from auto_parse.gae.utils import remove_preserve_tail
from lxml import etree
from w3lib import html as hl


def remove_footer(html, doc=''):
    """
    清除页脚
    :param html:
    :param doc:
    :return: html
    """
    doc = etree.HTML(html) if isinstance(doc, str) else doc
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


def remove_xml(xml, doc):
    """
    :param xml: xpath路径
    :param doc: etree对象
    :return:
    """
    if isinstance(xml, str):
        rm_xml_list = doc.xpath(xml)
    elif isinstance(xml, list):
        rm_xml_list = chain(*[doc.xpath(xl) for xl in xml])
    else:
        return
    for r in rm_xml_list:
        remove_preserve_tail(r)


def html_escape(text):
    """
    html转义
    """
    text = (text.replace("&quot;", "\"").replace("&ldquo;", "“").replace("&rdquo;", "”")
            .replace("&middot;", "·").replace("&#8217;", "’").replace("&#8220;", "“").replace('&amp;nbsp', ' ')
            .replace("&#8221;", "\”").replace("&#8212;", "——").replace("&hellip;", "…")
            .replace("&#8226;", "·").replace("&#40;", "(").replace("&#41;", ")")
            .replace("&#183;", "·").replace("&amp;", "&").replace("&bull;", "·")
            .replace("&lt;", "<").replace("&#60;", "<").replace("&gt;", ">")
            .replace("&#62;", ">").replace("&nbsp;", " ").replace("&#160;", " ").replace(' ', " ")
            .replace("&tilde;", "~").replace("&mdash;", "—").replace("&copy;", "@")
            .replace("&#169;", "@").replace("♂", "").replace("\r\n|\r", "\n").replace("&#13;", "")).replace('\\n', '')
    return text


def cleaning_properties(text):
    """去除无用属性"""
    try:
        text = re.sub(r' (style|class|id)\w*?=".*?"', '', text)
        return text
    except TypeError:
        pass


def elt(text, title=''):
    """
    杂质处理
    """
    text = text.rsplit('版权声明', 1)[0]
    text = text.rsplit('>相关信息<', 1)[0]
    text = text.rsplit('>相关链接', 1)[0]
    text = text.rsplit('免责声明:', 1)[0]
    text = text.rsplit('免责声明：', 1)[0]
    if [i for i in ['联系我们', '网站信息'] if i in text.rsplit('友情链接', 1)[-1]]:
        text = text.rsplit('友情链接', 1)[0]
    text = text.replace('来源： 【打印】', '').replace('公告概要：', '').replace('>首页<', '').replace('>打印<', '><') \
        .replace('>打印本页<', '').replace('>您所在的位置：<', '><').replace('>打印文章<', '><').replace('>添加收藏<', '><') \
        .replace('>【打印此页】<', '><').replace('>【关闭窗口】<', '><').replace('>QQ好友<', '><'). \
        replace('>QQ空间<', '><').replace('>腾讯微博<', '><').replace('>新浪微博<', '><').replace('>人民微博<', '><'). \
        replace('>有道云笔记<', '><').replace('>复制网址<', '><').replace('>【新闻链接】<', '><').replace('>收藏<', '')
    text = text.replace('当前位置：', '').replace('>首页 <', '').replace('阅读次数：', '').replace('浏览次数：', '').replace('访问次数：', '')
    text = text.replace('【显示公告正文】', '').replace('【显示公告概要】', '').replace('>我要打印<', '><').replace('>关闭<', '><')
    text = text.replace('【打印本页】', '').replace('【关闭本页】', '').replace('>微信<', '><').replace('>分享<', '><')
    text = text.replace('【字体：大 中 小】打印', '').replace('>qq<', '><').replace('>qq<', '><').replace('>微博<', '><')
    text = text.replace('<title>', '').replace('<title/>', '').replace('【我要打印】', '').replace('【关闭】', '') \
        .replace('分享到：', '').replace('>打印本稿<', '><').replace('>本项目仅供正式会员及查看<', '><').replace(">admin<", '><')
    text = text.replace('扫一扫在手机打开当前页面', '').replace('扫一扫在手机打开当前页', '').replace('>关闭窗口<', '><') \
        .replace('【发送网址给好友】', '').replace('>分享到<', '><')
    text = text.replace('>返回列表<', '><').replace('>查看原公告<', '><').replace('>[打印文章]<', '><').replace('>[添加收藏]<', '><')
    text = text.replace('>更多<', '><').replace('>投诉<', '><').replace('>我要报名<', '').replace('>[ 打 印 ]<', '><').replace(
        ">报名<", '><').replace(">报名倒计时<", '><').replace(">报名倒计时<", '><').replace('>< 返回<', '><') \
        .replace("扫一扫 手机端浏览", '><').replace('>设为首页<', '><').replace('>网站地图<', '><').replace('>相关新闻<', '><') \
        .replace('>加入收藏<', '><').replace('null', '').replace('>距离报名结束还剩<', '><').replace('>去报名<', '><') \
        .replace('>上一：<', '><').replace('>下一：<', '><').replace('>网站纠错<', '><').replace('>我要纠错<', '><')
    text = text.replace('>查看操作说明<', '><').replace('>交易主体登录<', '><').replace('>—分享—<', '><').replace('【发送网址给好友】', '')
    text = text.replace('>原文链接地址<', "><").replace("<a></a>", '').replace("【】", '').replace(
        '上一篇：', '').replace('下一篇：', '').replace('<input/>', '').replace('<h2/>', '').replace('上一篇:', '') \
        .replace('下一篇:', '').replace("VIP会员可查看", '').replace('扫一扫手机打开当前页', '')
    # 去除开头title
    text = text.replace(title, '', 1) if text.strip(' ').startswith(title) else text
    return text


def md5(_):
    m = hashlib.md5()
    m.update(_.encode(encoding='utf-8'))
    return m.hexdigest()


def pre_processing(html):
    html = hl.remove_comments(html)
    re_js_comment = re.compile(r'/\*.*?\*/', re.DOTALL)
    re_jsp_comment = re.compile(r'(href="javascript:.*?")', re.DOTALL)
    re_href_comment = re.compile(r'(href="[^ ]*?")', re.DOTALL)
    href_list = re_href_comment.findall(html)
    for href in href_list:
        if [i for i in ['pdf', 'xls', 'file', 'doc', 'zip'] if i in href]:
            continue
        else:
            html = html.replace(href, '')
    html = re_js_comment.sub('', html)
    html = re_jsp_comment.sub('', html)
    return html
