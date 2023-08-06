import re

import numpy as np
from auto_parse.gae.deal.base import BaseExtractor
from auto_parse.gae.deal.title import show_title
from auto_parse.gae.schemas.element import Element
from auto_parse.gae.utils import remove_preserve_tail
from auto_parse.gae.utils.element import descendants_of_body
from auto_parse.gae.utils.lcs import lcs_of_2
from auto_parse.gae.utils.preprocess import preprocess4content_extractor
from lxml import etree
from lxml.html import fromstring
from w3lib import html as hl

min_num = 4
max_num = 13
min_word_len = 15
sy = '>首页</a>'
sy1 = '>首  页</a>'
sy2 = '登录</a>'
file_path = '//*[contains(@href,"file")]//text() | //*[contains(@href,"File")]//text()'


class ContentExtractor(BaseExtractor):
    """
    extract content from detail page
    """

    def process(self, element: Element, vessel: dict = None):
        """
        extract content from html
        :param element:
        :param vessel:
        :return:
        """
        # preprocess
        preprocess4content_extractor(element)
        has_annex = self.try_deal_annex(element, vessel)

        self.remove_a(element, vessel['new_title'])
        # start to evaluate every child element
        # element_infos = []
        descendants = descendants_of_body(element)
        html = etree.tostring(element, pretty_print=True, encoding='utf-8').decode('utf-8')
        count = html.count(vessel.get('title')) - element.xpath('string(//title)').count(vessel.get('title'))
        # sy_count = len(element.xpath('//a[contains(text(), "首") and contains(text(), "页") and not(contains(text(), "设为"))]'))
        # breadcrumb_interference = ''.join(element.xpath(
        #     '//*[contains(text(), "{}")]/ancestor::div[1]//text()'.format(vessel.get('title'))))
        # if sy[1:-1] in breadcrumb_interference or sy1[1:-1] in breadcrumb_interference:
        #     s_count = html.count(sy) + html.count(sy1)
        del html
        # a1 = time.time()
        # get std of density_of_text among all elements
        density_of_text = [descendant.density_of_text for descendant in descendants]
        density_of_text_std = np.std(density_of_text, ddof=1)
        # get density_score of every element
        for descendant in descendants:
            score = np.log(density_of_text_std) * \
                    descendant.density_of_text * \
                    np.log10(descendant.number_of_p_descendants + 2) * \
                    np.log(descendant.density_of_punctuation)
            descendant.density_score = score
        # a2 = time.time()
        # print(a2 - a1)

        # sort element info by density_score
        descendants = sorted(descendants, key=lambda x: x.density_score, reverse=True)

        text = ''

        cycles = max_num if len(descendants) > max_num else len(descendants)
        for i in range(cycles):
            descendant_first = descendants[i] if descendants else None
            if descendant_first.tag == 'a':
                continue
            if i == cycles - 1:
                descendant_sup = element.xpath('//*[contains(text(), "{}")]'.format(vessel.get('title')))
                if len(descendant_sup) >= 1:
                    descendant_first = descendant_sup[0]
            if descendant_first is None:
                return ''
            descendant_first_text = etree.tostring(descendant_first, pretty_print=True, encoding='utf-8').decode(
                'utf-8')
            if [word for word in ['网站标识码', 'ICP备', '版权所有', '邮政编码', '网站备案号'] if
                word in descendant_first_text]:
                continue

            #####################
            # # a标签数量过多认为全部被提取
            # if len(descendant_first.xpath('.//a')) > min_num:
            #     if vessel.get('word') not in etree.tostring(descendants[i], pretty_print=True,
            #                                                      encoding='utf-8').decode('utf-8'):
            #         continue
            #####################
            # if vessel.get('title') in etree.tostring(descendants[i], pretty_print=True, encoding='utf-8').decode(
            #         'utf-8'):
            #     continue

            # text = etree.tostring(descendant_first, pretty_print=True, encoding='utf-8').decode('utf-8')
            target = self.preferred_parent(descendant_first, count, has_annex, vessel)
            if max(target) < 1:
                continue
            text = self.get_better_marking(descendant_first, target, count)

            # if vessel.get('title', '') not in text or text.count(s) == s_count:
            if vessel.get('title', '') not in text:
                text = ''
                continue
            if [word for word in ['网站标识码', 'ICP备', '版权所有'] if
                word in text]:
                text = ''
                continue
            if text.split(vessel.get('title', ''), 1)[0].count('<li') > 4:
                text = ''
                continue
            break
        text = self.move_head(text, vessel)
        return text

    @staticmethod
    def try_deal_annex(element, vessel):
        has_annex = False
        if isinstance(vessel['word'], list):
            for word in vessel['word']:
                has_annex = True if [b for b in element.xpath('//*[contains(text(), "{}")]//text()'.format(word))
                                     if len(b.strip()) < min_word_len] else False
                if has_annex:
                    break
        else:
            has_annex = True if [b for b in element.xpath('//*[contains(text(), "{}")]//text()'.format(vessel['word']))
                                 if len(b.strip()) < min_word_len] else False
        return has_annex

    @staticmethod
    def remove_a(element, new_title):
        # a_list = element.xpath(
        #     '//a[not(contains(text(), "首") and  \
        #     contains(text(), "页")) and contains(@href, ".") and contains(@href, "/")]')
        try:
            a_list = element.xpath(f"//a[contains(text(), '{new_title}')]")
        except etree.XPathEvalError:
            a_list = element.xpath(f'//a[contains(text(), "{new_title}")]')
        impurity = ['上一篇：', '上一条：', '下一篇：', '下一条：', '上一篇 ：', '下一篇 ：']
        xp = ''.join(
            [
                '//li[contains(string(.), "{}")] | //p[contains(string(.), "{}")] | //a[contains(string(.), "{}")] | '.format(
                    i, i, i) for i in
                impurity]).rsplit(
            '|', 1)[0]
        a_list.extend(element.xpath(xp))
        a_list.extend(element.xpath('//*[contains(text(), "ICP备")]/parent::*'))
        a_list.extend(element.xpath('//div[contains(@class, "bottom") and contains(text(), "ICP备")]'))
        a_list.extend(element.xpath('//a[contains(text(), "登录")] | //a[contains(text(), "注册")]'))
        for a_tag in a_list:
            remove_preserve_tail(a_tag)
        li_a = element.xpath('//li/a[not(contains(text(), "."))]')
        li_a.extend(element.xpath(
            '//*[contains(text(), "上一篇")]/descendant-or-self::a | //*[contains(text(), "下一篇")]/descendant-or-self::a '
            '| //*[contains(text(), "下一条")]/descendant-or-self::a | //*[contains(text(), '
            '"上一条")]/descendant-or-self::a | //*[contains(text(), "上一")]/following-sibling::a | '
            '//*[contains(text(), "下一")]/following-sibling::a'))
        for a_tag in li_a:
            try:
                a_tag.getparent().remove(a_tag)
            except AttributeError:
                continue
        rm_style = element.xpath('//*[@style]')
        for style in rm_style:
            etree.strip_attributes(style, ["style"])

    def preferred_parent(self, element, count, has_annex, vessel):
        title = vessel.get('title', '')
        word = vessel.get('word', '')
        target = {k: -1 for k in range(count + 1)}
        for point in range(max_num):
            suspect_text = ''.join(
                [etree.tostring(e, pretty_print=True, encoding='utf-8').decode('utf-8').strip() for e in
                 element.xpath('.' + '/parent::*' * point)])
            # frequency = suspect_text.count(title) - 1 if suspect_text.count(title) != 0 else 0
            frequency = suspect_text.count(title)
            # title存在
            if frequency > max(target):
                break
            if target[suspect_text.count(title)] != -1:
                continue
            if suspect_text.count(title) <= count:
                if has_annex:
                    for block in element.xpath('.' + '/parent::*' * point):
                        for w in word:
                            if [[node for node in
                                 [b for b in block.xpath('.//*[contains(text(), "{}")]//text()'.format(w))
                                  if len(b.strip()) < min_word_len] if
                                 w in node] or [b for b in block.xpath(file_path) if b]]:
                                target[suspect_text.count(title)] = point if target[frequency] == -1 else target[
                                    suspect_text.count(title)]
                                # break
                if not has_annex:
                    # target = point
                    target[suspect_text.count(title)] = point if target[frequency] == -1 else target[
                        suspect_text.count(title)]
                    # break
                # if not target:
                #     break
                if suspect_text.count(title) == count and target[max(target.keys())] != -1:
                    break

        else:
            target = {0: 0}
        # return better_element
        return target

    @staticmethod
    def get_better_marking(element: Element, target: dict, count):
        marking_list = sorted(list(target.values()), reverse=True)
        text = ''
        for marking in marking_list:
            better_elements = element.xpath('.' + '/parent::*' * marking)
            if len(better_elements) == 1 and better_elements[0].tag == 'body' and better_elements[0].xpath(
                    '//a[contains(text(), "首") and contains(text(), "页") and not(contains(text(), "设为"))]'):
                continue
            if len(better_elements) == 1 and better_elements[0].tag == 'title':
                continue
            if len(better_elements) == 1 and better_elements[0].tag == 'table':
                better_elements = element.xpath('.' + '/parent::*' * (marking + 1))
            for better_element in better_elements:
                text += etree.tostring(better_element, pretty_print=True, encoding='utf-8').decode('utf-8')
            home_num = text.count(sy) + text.count(sy1)
            # if sy_count > 1 and sy_count == home_num:
            if home_num > 0 and count > 1:
                text = ''
                continue
            elif len(''.join(re.findall('[\u4e00-\u9fa5]', text))) < 50:
                text = ''
                continue
            else:
                break
        return text

    @staticmethod
    def pre_processing(html):
        html = hl.remove_tags(html, which_ones=('span', 'font'))
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

    def extract(self, html, **kwargs):
        """
        base extract method, firstly, it will convert html to WebElement, then it call
        process method that child class implements
        :param html:
        :return:
        """
        html = self.pre_processing(html)
        vessel = kwargs
        title = kwargs.get('title')
        substitute = '**jl**l'
        vessel['title'] = substitute
        self.make_better_title(html, title, vessel)
        html = html.replace(vessel['new_title'], substitute)
        element = fromstring(html=html)
        element.__class__ = Element
        result = self.process(element, vessel)
        result = result.replace(substitute, vessel['new_title'])

        if vessel['new_title'] not in result:
            result = ''
        return result

    @staticmethod
    def make_better_title(html, title, vessel):
        title_list = sorted([member for member in re.split(r'[^\w、（）]', title) if member],
                            key=lambda i: len(i), reverse=True)
        vessel['new_title'] = title
        if title not in html or not title:
            title_surmise = show_title(html) if show_title(html) else ''
            title_new_1 = lcs_of_2(title_surmise, title) if len(lcs_of_2(title_surmise, title)) > 6 else ''
            title_new = ''
            for t in title_list:
                title_new = t
                title_new_f = title_new
                for j in range(len(title_new), 3, -1):
                    title_new = title_new[:j]
                    title_new_f = title_new_f[len(title_new_f) - j:]
                    if title_new in html:
                        title_new = title_new
                        break
                    if title_new_f in html:
                        title_new = title_new_f
                        del title_new_f
                        break
                if title_new in html:
                    break
            title_new = max(title_new_1, title_new, key=len)
            vessel['new_title'] = title_new

    @staticmethod
    def move_head(text, vessel):
        if not text:
            return text
        title = vessel.get('title')
        if not 'table' in text[:50] or not text.count(title) < 2 or text.count(sy2) > 0:
            block = text.split(title, 1)
            new_block = block[0].rsplit('>', 1)
            text = new_block[-1] + title + block[-1]
            if [w for w in ['人', '公司', '编码', '编号'] if w in new_block[0]]:
                text = new_block[0] + text
            return text
        else:
            return text


content_extractor = ContentExtractor()


def show_content(html, **kwargs):
    """
    extract content from detail html
    :return:
    """
    return content_extractor.extract(html, **kwargs)
