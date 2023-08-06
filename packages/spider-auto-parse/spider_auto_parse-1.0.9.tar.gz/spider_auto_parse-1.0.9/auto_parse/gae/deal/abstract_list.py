import collections
import datetime
import math
import operator
import re
import time
from urllib.parse import urljoin

import numpy as np
from auto_parse.gae.deal.base import BaseExtractor
from auto_parse.gae.schemas.element import Element
from auto_parse.gae.schemas.path import longest_common_prefix, build_basic_cluster
from auto_parse.gae.utils import remove_preserve_tail
from auto_parse.gae.utils.element import parent
from auto_parse.gae.utils.preprocess import preprocess4list_extractor
from auto_parse.gae.utils.similarity import similarity
from lxml import etree
from lxml.html import fromstring
# from auto_parse.gae.utils.element import path_raw
from w3lib import html as hl

LIST_MIN_NUMBER = 5
LIST_MIN_LENGTH = 11
LIST_MAX_LENGTH = 90
MIN_NUM = 2.0861548052953718e-25
SIMILARITY_THRESHOLD = 0.78
list_similarity_coefficient = 0.6
re_time = re.compile(r'(?:19|20|)\d{2}[/.\-年][0-1]?[0-9][/.\-月]\d{1,2}', re.DOTALL)
re_hz = re.compile(r'[\u4e00-\u9fa5]')


class AbstractList(BaseExtractor):
    def __init__(self, min_number=LIST_MIN_NUMBER, min_length=LIST_MIN_LENGTH, max_length=LIST_MAX_LENGTH,
                 similarity_threshold=SIMILARITY_THRESHOLD):
        super(AbstractList, self).__init__()
        self.min_number = min_number
        self.min_length = min_length
        self.max_length = max_length
        self.avg_length = (self.min_length + self.max_length) / 2
        self.similarity_threshold = similarity_threshold

    def _build_clusters(self, element):
        a_list = element.xpath('//a')
        path_list = list(set(['/' + path_raw(a) for a in a_list]))
        # 会不会下面还有分组？ 会的
        clusters = build_basic_cluster(path_list)
        # clusters = refactoring_list(base_group)
        clusters = self.check_cluster(clusters)
        clusters = self.make_element(element, clusters)
        clusters = {v: l for v, l in enumerate(clusters)}
        return clusters

    def make_element(self, element, block_list):
        result = []
        for block in block_list:
            array = []
            for b in block:
                node = element.xpath(b)
                if node:
                    node[0].__class__ = Element
                    node[0].path = b
                    array.append(node[0])
            if array:
                result.append(array)
        return result

    def check_cluster(self, clusters: list):
        # 剔除a标签上父级不同的a路径
        # for cluster in clusters:
        #     [ for each in cluster]
        return clusters

    def _probability_of_title_with_length(self, length):
        """
        get the probability of title according to length
        import matplotlib.pyplot as plt
        x = np.asarray(range(5, 40))
        y = list_extractor.probability_of_title_with_length(x)
        plt.plot(x, y, 'g', label='m=0, sig=2')
        plt.show()
        :param length:
        :return:
        """
        sigma = 12
        return np.exp(-1 * ((length - self.avg_length) ** 2) / (2 * (sigma ** 2))) / (math.sqrt(2 * np.pi) * sigma)

    def _evaluate_cluster(self, cluster, element):
        """
        calculate score of cluster using similarity, numbers, or other info
        :param cluster:
        :return:
        """
        score = dict()

        # calculate avg_similarity_with_siblings
        score['avg_similarity_with_siblings'] = np.mean(
            [similarity_with_siblings(element, cluster) for element in cluster])

        # calculate number of elements
        score['number_of_elements'] = len(cluster)
        text_list = [text for text in
                     [get_title(element) if get_title(element) else element.text
                      for element in cluster]]
        title_list = [len(text) for text in text_list]
        score['probability_of_title_with_length'] = MIN_NUM
        # if np.mean(title_list) < LIST_MAX_LENGTH and min(title_list) > 3:
        if 5 < np.mean(title_list) < LIST_MAX_LENGTH:
            # calculate probability of it contains title
            score['probability_of_title_with_length'] = np.mean(
                [self._probability_of_title_with_length(length) for length in title_list])

        prefix = longest_common_prefix([element.path for element in cluster])
        score['probability_of_release_time'] = self._probability_of_release_time(element, prefix, len(cluster))

        ch_ratio = np.mean([chinese_ratio(text) for text in text_list])

        # TODO: add more quota to select best cluster
        score['clusters_score'] = \
            score['avg_similarity_with_siblings'] \
            * np.log2(score['number_of_elements'] + 1) \
            * score['probability_of_title_with_length'] * score['probability_of_release_time']
        score['clusters_score'] = score['clusters_score'] * MIN_NUM if ch_ratio < 0.1 or '首页' in text_list else score[
            'clusters_score']
        return score

    @staticmethod
    def _probability_of_release_time(element, prefix, num):
        prefix = prefix.rsplit('/', 1)[0]
        block = element.xpath(prefix)
        if block:
            block = block[0]
            block_text = etree.tostring(block, pretty_print=True, encoding='utf-8').decode('utf-8')
            r_count_dic = find_max_common_date_type(re_time.findall(block_text))
            r_len = r_count_dic[max(r_count_dic, key=r_count_dic.get)] if r_count_dic else 0
            if r_len >= num:
                return 1
        return 0.1 ** 10

    def _extend_cluster(self, cluster):
        """
        extend cluster's elements except for missed children
        :param cluster:
        :return:
        """
        result = [element.selector for element in cluster]
        for element in cluster:
            path_raw = element.path_raw
            siblings = list(element.siblings)
            for sibling in siblings:
                # skip invalid element
                if not isinstance(sibling, Element):
                    continue
                sibling_selector = sibling.selector
                sibling_path_raw = sibling.path_raw
                if sibling_path_raw != path_raw:
                    continue
                # add missed sibling
                if sibling_selector not in result:
                    cluster.append(sibling)
                    result.append(sibling_selector)

        cluster = sorted(cluster, key=lambda x: x.nth)
        return cluster

    def _best_cluster(self, clusters, element):
        """
        use clustering algorithm to choose best cluster from candidate clusters
        :param clusters:
        :return:
        """
        if not clusters:
            return []
        if len(clusters) == 1:
            return clusters[0]
        # choose best cluster using score
        clusters_score = collections.defaultdict(dict)
        clusters_score_arg_max = 0
        clusters_score_max = -1
        for cluster_id, cluster in clusters.items():
            # calculate avg_similarity_with_siblings
            clusters_score[cluster_id] = self._evaluate_cluster(cluster, element)
            # get max score arg index
            if clusters_score[cluster_id]['clusters_score'] > clusters_score_max:
                clusters_score_max = clusters_score[cluster_id]['clusters_score']
                clusters_score_arg_max = cluster_id
        best_cluster = clusters[clusters_score_arg_max]
        return best_cluster

    def _extract_cluster(self, cluster, **kwargs):
        """
        extract title and href from best cluster
        :param cluster:
        :return:
        """
        if not cluster:
            return None
        # get best tag path of title
        # probabilities_of_title = collections.defaultdict(list)
        # for element in cluster:
        #     path = element.path
        #     descendant_text = element.text
        #     probability_of_title_with_length = self._probability_of_title_with_length(len(descendant_text))
        #     # probability_of_title_with_descendants = self.probability_of_title_with_descendants(descendant)
        #     # TODO: add more quota to calculate probability_of_title
        #     probability_of_title = probability_of_title_with_length
        #     probabilities_of_title[path].append(probability_of_title)
        #
        # # get most probable tag_path
        # probabilities_of_title_avg = {k: np.mean(v) for k, v in probabilities_of_title.items()}
        # if not probabilities_of_title_avg:
        #     return None
        # best_path = max(probabilities_of_title_avg.items(), key=operator.itemgetter(1))[0]
        # best_score = probabilities_of_title_avg[best_path]
        # ==========================
        # best_path = max(probabilities_of_title_avg.items(), key=operator.itemgetter(1))[0]
        # second_best_path = None
        # if len(probabilities_of_title_avg) > 1:
        #     del probabilities_of_title_avg[best_path]
        #     second_best_path = max(probabilities_of_title_avg.items(), key=operator.itemgetter(1))[0]
        #     second_score = probabilities_of_title_avg[second_best_path]
        #     if second_score / best_score < list_similarity_coefficient:
        #         second_best_path = None

        # ==========================
        # extract according to best tag path
        result = []
        score = 0
        for descendant in cluster:
            path = descendant.path
            base_url = kwargs.get('base_url')
            title = get_title(descendant) if get_title(descendant) else descendant.text
            title = title if title else descendant.text
            url = descendant.attrib.get('href')
            if not url:
                url = descendant.attrib.get('url')
            if not url or 'javas' in url:
                continue
            if url.startswith('//'):
                url = 'http:' + url
            if base_url:
                url = urljoin(base_url, url)
            if not title:
                continue
            result.append({
                'title': title,
                'url': url,
                'xpath': path,
                'score': score
            })
            score += 1
        # if result:
        #     result = self.process_result(result)
        return result

    def process(self, element, **kwargs):
        preprocess4list_extractor(element)
        clusters = self._build_clusters(element)
        best_cluster = self._best_cluster(clusters, element)
        # extended_cluster = self._extend_cluster(best_cluster)

        result = self._extract_cluster(best_cluster, **kwargs)
        return result

    def extract(self, html, **kwargs):
        # self.kwargs = kwargs
        element = fromstring(html=html)
        element.__class__ = Element
        result = self.process(element, **kwargs)
        return result

    @staticmethod
    def process_result(result: list):
        count_result = collections.defaultdict(int)
        new_result = list()
        for rsp in result:
            this_result = dict()
            base = list(rsp.keys())[2]
            count_result[base] += 1
            this_result['title'] = rsp['title']
            this_result['url'] = rsp['url']
            this_result['score'] = rsp['score']
            this_result['xpath'] = base.split(':')[0]
            new_result.append(this_result)
        best_key = max(count_result, key=lambda x: count_result[x]).split(':')[0]
        new_result = [new for new in new_result if best_key in new.values()]
        return new_result


def path_raw(element: Element):
    """
    get tag path using recursive function, only contains raw tag
    for example result: html/body/div/div/ul/li
    :param element:
    :return:
    """
    if element is None:
        return ''
    p = parent(element)
    element_weights = len(element.xpath('./preceding-sibling::' + element.tag)) + 1
    if p is not None:
        return path_raw(p) + '/' + element.tag + f'[{element_weights}]'
    return element.tag


def abstract_list(html, **kwargs):
    extract = AbstractList()
    return extract.extract(html, **kwargs)


def show_list(html, **kwargs):
    html = remove_footer(html)
    html = pre_processing(html)
    rsp_list = abstract_list(html, base_url=kwargs.get('base_url'))
    if not rsp_list:
        return []
    rsp_list = sorted(rsp_list, key=lambda x: x['xpath'])
    if isinstance(rsp_list, list) and rsp_list:
        time_list = None
        try:
            time_xp = longest_common_prefix([i['xpath'] for i in rsp_list]).rsplit('/', 1)[0]
            hx = fromstring(html)
            url_num = len(rsp_list)
            for i in range(6):
                # block = [etree.tostring(b, pretty_print=True, encoding='utf-8').decode(
                #     'utf-8') for b in hx.xpath(time_xp + '/..' * i)]
                block = hx.xpath(time_xp + '/..' * i + '//text()')
                time_list_copy = re_time.findall(' '.join(block), re.DOTALL)
                if len(time_list_copy) > url_num:
                    clear_time_list(time_list_copy, url_num)
                time_list_copy = [
                    ('20' + t).replace('.', '-').replace('/', '-').replace('年', '-').replace('月', '-')
                    if len(re.split(r'[^\d]', t)[0]) < 4 else t.replace('.', '-').replace('/', '-').replace('年',
                                                                                                            '-').replace(
                        '月', '-')
                    for t in time_list_copy]
                if not time_list_copy:
                    continue
                better_num = len(time_list_copy)
                if better_num % url_num == 0:
                    data_now = datetime.datetime.now()
                    multiple = better_num / url_num
                    time_list_copy = [
                        time.strftime("%Y-%m-%d", time.localtime(time.mktime(time.strptime(t, '%Y-%m-%d')))) for t in
                        time_list_copy]
                    for k in range(url_num):
                        start_time_list = [time_[:10] for time_ in
                                           time_list_copy[k * int(multiple):(k + 1) * int(multiple)]]
                        if len(start_time_list) != len(list(set(start_time_list))):
                            continue
                    else:
                        start_time_list = time_list_copy[:int(multiple)]
                    min_time = time.strftime("%Y-%m-%d", time.localtime(
                        (min([time.mktime(time.strptime(time1, '%Y-%m-%d')) for time1 in start_time_list]))))
                    time_index = start_time_list.index(min_time)
                    time_list = time_list_copy[time_index::int(multiple)]
                    if [t for t in time_list if datetime.datetime(*([int(i) for i in t.split('-')])) > data_now]:
                        continue
                    del time_xp
                    break
            result = []
            processing_order(rsp_list)
            extract_correctly = False
            if time_list and len(time_list) == len(rsp_list):
                extract_correctly = True
            for rsp in rsp_list:
                if extract_correctly:
                    rsp['pub_time'] = time_list[rsp['score']]
                else:
                    rsp['pub_time'] = ''
                if rsp['pub_time'] and rsp['pub_time'] in rsp['title']:
                    rsp['title'] = rsp['title'].strip(rsp['pub_time'])
                del rsp['score']
                del rsp['xpath']
                result.append(rsp)
            de_duplication = len(list(set([r['url'] for r in result])))
            len_result = len(result)
            if de_duplication != len_result:
                if len_result % de_duplication == 0:
                    scale = len_result / de_duplication
                    new_title_list = [len(r['title']) if 6 < len(r['title']) < 100 else -1 for r in result[:scale]]
                    max_index = max(new_title_list)
                    index = new_title_list.index(max_index)
                    result = result[index::scale]
            result = [rsp for rsp in result if len(rsp['title']) > 3]
            return result

        except Exception as e:
            # traceback.print_exc()
            pass

    return rsp_list


def clear_time_list(time_list_copy, num):
    dic = {}
    for j in time_list_copy:
        if dic.get(j[4]):
            dic[j[4]] += 1
        else:
            dic[j[4]] = 1
    # del dic[max(dic, key=dic.get)]
    remove_list = [k for k, v in dic.items() if v % num == 0]
    for remove in remove_list:
        del dic[remove]
    key_list = dic.keys()
    for key in key_list:
        for _ in time_list_copy.copy():
            if key in _:
                time_list_copy.remove(_)


def processing_order(rsp: list):
    xp_list = [r['xpath'] for r in rsp]
    xp_manner = list(set([r['xpath'][-2] for r in rsp]))
    score_dic = {}
    if len(xp_manner) > 1:
        score_dic = {xp: xp.rsplit('[', 1)[-1].replace(']', '') for xp in xp_list}
    else:
        xp_num = {xp: re.findall(r'(\d+)', xp) for xp in xp_list}
        for num in range(len(xp_num[xp_list[0]])):
            if len(list(set([xp[num] for xp in xp_num.values()]))) > 1:
                score_dic = {xp: tup[num] for xp, tup in xp_num.items()}
                break
    for r in rsp:
        r['score'] = int(score_dic.get(r['xpath'])) - 1
    rsp = sorted(rsp, key=operator.itemgetter('score'))
    n = 0
    for r in rsp:
        r['score'] = n
        n += 1


def similarity_with_element(element1: Element, element2: Element):
    """
    get similarity between two elements
    :param element1:
    :param element2:
    :return:
    """
    alias1 = element1.alias
    alias2 = element2.alias
    # TODO: use better metrics to compare the two elements
    return similarity(alias1, alias2)


def similarity_with_siblings(element: Element, clusters: list):
    """
    get similarity with siblings
    :param element:
    :param clusters:
    :return:
    """
    scores = []
    for sibling in clusters:
        # TODO: maybe compare all children not only alias
        scores.append(similarity_with_element(element, sibling))
    if not scores:
        return 0
    return np.mean(scores)


def pre_processing(html):
    html = hl.remove_comments(html)
    # imt = re.compile(
    #     r'<([^>\s]+)[^>]*>(?:\s*(?:<br \/>|&nbsp;|&thinsp;|&ensp;|&emsp;|&#8201;|&#8194;|&#8195;)\s*)*<\/\1>', re.S)
    # html = imt.sub(r'', html)
    # TODO
    html = hl.remove_tags(html, which_ones=('span', 'strong', 'font', 'i'))  # 'img',
    # 处理xml
    if '<![CDATA[' in html:
        html = html.replace('<![CDATA[', '').replace(']]>', '').replace('<script type="text/xml">', '')
    # 处理js
    if 'javascript:urlOpen(' in html:
        html = html.replace("javascript:urlOpen('", '').replace('''')"''', '"')
    return html


def remove_footer(html):
    html = html.replace('</html>', '').replace('<body>', '').replace('</body>', '')
    doc = etree.HTML(html)
    rm_space = doc.xpath('//*[not(node()) and not(self::img)]')
    rm_doc = doc.xpath(
        '//*[(ancestor-or-self::*[contains(@id,"foot") or contains(@class,"foot")]) '
        'and not(self::script or self::style or self::title)]')
    rm_self = doc.xpath('//a[@href="./"]| //a[@href=""] |//a[@href="/"]')
    rm_doc.extend(rm_space)
    rm_doc.extend(rm_self)
    for r in rm_doc:
        remove_preserve_tail(r)
    rm_footer = doc.xpath('//footer')
    for r in rm_footer:
        remove_preserve_tail(r)
    html = etree.tostring(doc, encoding='utf-8', pretty_print=True, method="html").decode('utf-8')
    return html


def get_title(element):
    title = ''
    title_list = element.xpath('./@title')
    if title_list and len(title_list[0].strip()) > 6:
        title = title_list[0]
    return title


def chinese_ratio(text: str):
    if not text:
        return 0
    num = 0
    for em in text:
        if '\u4e00' <= em <= '\u9fa5':
            num += 1
    return num / len(text)


def find_max_common_date_type(array):
    # 统计不同时间格式的总数
    dic = collections.defaultdict(int)
    re_clear_num = re.compile(r'\d', re.DOTALL | re.IGNORECASE)
    for each in array:
        key = re_clear_num.sub('', each)
        dic[key] += 1
    return dic


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    x = np.asarray(range(5, 40))
    y = AbstractList()._probability_of_title_with_length(x)
    plt.plot(x, y, 'g', label='m=0, sig=2')
    plt.show()
