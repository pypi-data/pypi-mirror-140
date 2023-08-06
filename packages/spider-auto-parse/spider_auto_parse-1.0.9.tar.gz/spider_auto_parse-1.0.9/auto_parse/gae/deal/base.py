from auto_parse.gae.schemas.element import Element
from loguru import logger
from lxml.html import etree
from lxml.html import fromstring


class BaseExtractor(object):
    """
    Base Extractor which provide common methods
    """

    kwargs = None

    def to_string(self, element: Element, limit: int = None):
        """
        convert element to string
        :param element:
        :param limit:
        :return:
        """
        result = etree.tostring(element, pretty_print=True, encoding="utf-8", method='html').decode('utf-8')
        if limit:
            return result[:limit]
        return result

    def process(self, element: Element, vessel=None):
        """
        process method that you should implement
        :param element:
        :param vessel:
        :return:
        """
        logger.error('You must implement process method in your extractor.')
        raise NotImplementedError

    def second_node(self, elements):
        node_list = []
        for element in elements:
            if not element.getchildren():
                # if element.xpath('name()') != 'a' and not element.xpath('ancestor::a'):
                if not element.xpath('ancestor-or-self::a'):
                    node_list.append(element)
            for child in element.getchildren():
                if not len(child):
                    if not child.xpath('ancestor-or-self::a') and not element.xpath('descendant-or-self::a'):
                        node_list.append(child.getparent())
                new_list = self.second_node(child)
                if new_list:
                    node_list.extend(new_list)
        # if '<div>2021-06-23</div>&#13;\n\t\t\t\t\t\t\t\t\n' in [etree.tostring(i, pretty_print=True, encoding='utf-8').decode('utf-8') for i in node_list]:
        #     print(1)
        return node_list

    def spare(self, html, url=None):
        logger.error('You must implement process method in your extractor.')
        raise NotImplementedError

    def extract(self, html, **kwargs):
        """
        base extract method, firstly, it will convert html to WebElement, then it call
        process method that child class implements
        :param html:
        :return:
        """
        self.kwargs = kwargs
        element = fromstring(html=html)
        element.__class__ = Element
        result = self.process(element)
        return result
