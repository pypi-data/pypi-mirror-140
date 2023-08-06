from auto_parse.gae.deal.title import show_title
from auto_parse.gae.deal.content import show_content
from auto_parse.gae.deal.abstract_list import show_list
from auto_parse.gae.deal.datetime import show_datetime


# def show_title(html):
#     pm = PageModel(html)
#     meta_title = pm.extract()['title']
#     return meta_title


def show_detail(html):
    """
    extract detail information
    :param html:
    :return:
    """
    return {
        'title': show_title(html),
        'datetime': show_datetime(html),
        # 'content': show_content(html)
    }
