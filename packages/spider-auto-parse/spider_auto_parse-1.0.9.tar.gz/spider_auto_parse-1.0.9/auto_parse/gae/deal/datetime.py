import datetime as dt
import re

from dateparser import parse
from auto_parse.gae.deal.base import BaseExtractor
from auto_parse.gae.patterns.datetime import METAS_CONTENT, REGEXES
from auto_parse.gae.schemas.element import Element
from loguru import logger
from lxml.html import HtmlElement
from lxml.html import fromstring
from w3lib import html as hl


class DatetimeExtractor(BaseExtractor):
    """
    Datetime Extractor which auto extract datetime info.
    """

    def extract_by_regex(self, element: HtmlElement) -> str:
        """
        extract datetime according to predefined regex
        :param element:
        :return:
        """
        text = ''.join(element.xpath('.//text()'))
        for regex in REGEXES:
            result = re.search(regex, text)
            if result:
                # print(regex)
                return result.group(1)

    def extract_by_meta(self, element: HtmlElement) -> str:
        """
        extract according to meta
        :param element:
        :return: str
        """
        for xpath in METAS_CONTENT:
            datetime = element.xpath(xpath)
            if datetime:
                # print(xpath)
                return ''.join(datetime)

    def process(self, element: HtmlElement):
        """
        extract datetime
        :param html:
        :return:
        """
        return self.extract_by_regex(element) or \
               self.extract_by_meta(element)

    def extract(self, html, **kwargs):
        self.kwargs = kwargs
        html = hl.remove_tags(html, which_ones=('span',))
        element = fromstring(html=html)
        element.__class__ = Element
        result = self.process(element)

        return result


datetime_extractor = DatetimeExtractor()


def parse_datetime(datetime):
    """
    parse datetime using dateparser lib
    :param datetime:
    :return:
    """
    if not datetime:
        return None
    try:
        time = parse(datetime)
        if time and time > dt.datetime.now():
            return None
        return time
    except TypeError:
        logger.exception(f'Error Occurred while parsing datetime extracted. datetime is {datetime}')


def show_datetime(html, parse=True):
    """
    extract datetime from html
    :param parse:
    :param html:
    :return:
    """
    result = datetime_extractor.extract(html)
    if not parse:
        return result
    time = parse_datetime(result)

    return time


if __name__ == '__main__':
    print(parse_datetime('2021。9。1。。'))
