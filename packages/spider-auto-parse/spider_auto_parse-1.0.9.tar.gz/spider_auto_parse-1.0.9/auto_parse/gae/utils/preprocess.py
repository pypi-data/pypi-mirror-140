from itertools import chain

from auto_parse.gae.schemas.element import Element
from auto_parse.gae.utils import remove_preserve_tail
from auto_parse.gae.utils.element import children, remove_element, remove_children
from lxml.html import HtmlElement, etree

CONTENT_EXTRACTOR_USELESS_TAGS = ['meta', 'style', 'script', 'link', 'video', 'audio', 'iframe', 'source',
                                  'svg',
                                  'path',
                                  'symbol', 'footer', 'header', 'button']  # 'img',
CONTENT_EXTRACTOR_STRIP_TAGS = ['span', 'blockquote', 'font']  # ??strong
CONTENT_EXTRACTOR_NOISE_XPATHS = [
    '//div[contains(@class, "comment")]',
    '//div[contains(@class, "advertisement")]',
    '//div[contains(@class, "advert")]',
    '//*[contains(@style, "display: none") and not(contains(@class, "content"))]',
    '//*[contains(@style, "display:none") and not(contains(@class, "content"))]',
]


def preprocess4content_extractor(element: HtmlElement):
    """
    preprocess element for content extraction
    :param element:
    :return:
    """
    # remove tag and its content
    etree.strip_elements(element, *CONTENT_EXTRACTOR_USELESS_TAGS)
    # only move tag pair
    etree.strip_tags(element, *CONTENT_EXTRACTOR_STRIP_TAGS)

    remove_children(element, CONTENT_EXTRACTOR_NOISE_XPATHS)

    for child in children(element):
        # 将input 标签内容提取
        for textarea in child.xpath('.//textarea'):
            textarea.tag = 'span'

        for input_tag in chain(child.xpath('.//input[@readonly]'), child.xpath('.//input[contains(@value, "&lt;")]'),
                               child.xpath('.//input[contains(@value, "&#60;")]'),
                               child.xpath('.//input[@type="text"]')):
            input_tag.tag = 'span'
            # TODO input标签内容提炼
            text = input_tag.xpath('string(./@value)')
            # if len(text) < 5000 and input_tag.xpath('./@type') != 'hidden' and not re.match(r'[^\u4e00-\u9fa5]', text):
            input_tag.text = text
            # etree.strip_attributes(input_tag, ["type", "value", "id", "placeholder"])
        # merge text in span or strong to parent p tag
        if child.tag.lower() == 'p':
            etree.strip_tags(child, 'span')
            etree.strip_tags(child, 'strong')

            if not (child.text and child.text.strip()):
                remove_element(child)

        # if a div tag does not contain any sub node, it could be converted to p node.
        if child.tag.lower() == 'div' and not child.getchildren():
            child.tag = 'p'


LIST_EXTRACTOR_USELESS_TAGS = ['meta', 'style', 'script', 'link', 'video', 'audio', 'iframe', 'source',
                               'path',
                               'symbol', 'footer', 'header', 'button']
LIST_EXTRACTOR_STRIP_TAGS = CONTENT_EXTRACTOR_STRIP_TAGS
LIST_EXTRACTOR_NOISE_XPATHS = CONTENT_EXTRACTOR_NOISE_XPATHS.copy()
LIST_EXTRACTOR_NOISE_XPATHS[
    3] = '//a[@href=""]'
del LIST_EXTRACTOR_NOISE_XPATHS[4]


def preprocess4list_extractor(element: Element):
    """
    preprocess element for list extraction
    :param element:
    :return:
    """

    etree.strip_elements(element, *LIST_EXTRACTOR_USELESS_TAGS)
    # only move tag pair
    etree.strip_tags(element, *CONTENT_EXTRACTOR_STRIP_TAGS)

    remove_children(element, LIST_EXTRACTOR_NOISE_XPATHS)

    for child in children(element):
        # merge text in span or strong to parent p tag
        if child.tag.lower() == 'a':
            etree.strip_tags(child, 'span')
        if child.tag.lower() == 'p':
            etree.strip_tags(child, 'span')
            etree.strip_tags(child, 'strong')

            if not (child.text and child.text.strip()):
                remove_element(child)

        # if a div tag does not contain any sub node, it could be converted to p node.
        if child.tag.lower() == 'div' and len([i for i in child.children if i.tag == 'ul']) > 2:
            etree.strip_tags(child, 'ul')
        if child.tag.lower() == 'div' and not child.getchildren():
            child.tag = 'p'
    # 合并ul
    ul_list = [i.getparent() for i in element.xpath('//*/ul')]
    if len(ul_list) > 0:
        for ul in set(ul_list):
            etree.strip_tags(ul, 'ul')
    # 清除空a列表
    for each in chain(element.xpath('//a[string(.)=""]'), element.xpath('//a[string(.)="首页"]'),
                      element.xpath('//div[string(.)=""]')):
        if not each.xpath('./@title') or each.xpath('string(.)') == '首页':
            remove_preserve_tail(each)


LIST_CLASSIFIER_USELESS_TAGS = ['style', 'script', 'link', 'video', 'audio', 'iframe', 'source', 'svg', 'path',
                                'symbol', 'footer', 'header']
LIST_CLASSIFIER_STRIP_TAGS = ['span', 'blockquote']
LIST_CLASSIFIER_NOISE_XPATHS = [
    '//div[contains(@class, "comment")]',
    '//div[contains(@class, "advertisement")]',
    '//div[contains(@class, "advert")]',
    '//div[contains(@style, "display: none")]',
]


def preprocess4list_classifier(element: HtmlElement):
    """
    preprocess element for list classifier
    :param element:
    :return:
    """
    # remove tag and its content
    etree.strip_elements(element, *LIST_CLASSIFIER_USELESS_TAGS)
    # only move tag pair
    etree.strip_tags(element, *LIST_CLASSIFIER_STRIP_TAGS)

    remove_children(element, LIST_CLASSIFIER_NOISE_XPATHS)

    for child in children(element):
        # merge text in span or strong to parent p tag
        if child.tag.lower() == 'p':
            etree.strip_tags(child, 'span')
            etree.strip_tags(child, 'strong')

            if not (child.text and child.text.strip()):
                remove_element(child)

        # if a div tag does not contain any sub node, it could be converted to p node.
        if child.tag.lower() == 'div' and not child.getchildren():
            child.tag = 'p'
