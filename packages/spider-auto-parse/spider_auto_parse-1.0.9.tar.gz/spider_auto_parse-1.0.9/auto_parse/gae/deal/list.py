import itertools
import math
import operator
import re
import time
import traceback
from collections import defaultdict
from urllib.parse import urljoin

import Levenshtein
import numpy as np
from auto_parse.gae.deal.base import BaseExtractor
from auto_parse.gae.schemas.element import Element
from auto_parse.gae.utils.cluster import cluster_dict
from auto_parse.gae.utils.element import descendants_of_body
from auto_parse.gae.utils.preprocess import preprocess4list_extractor
from loguru import logger
from lxml import etree
from lxml.html import fromstring
from w3lib import html as hl

LIST_MIN_NUMBER = 5
LIST_MIN_LENGTH = 11
LIST_MAX_LENGTH = 100
SIMILARITY_THRESHOLD = 0.78
list_similarity_coefficient = 0.6
re_time = re.compile('(?:19|20|)\d{2}[/.\-年]\d{1,2}[/.\-月]\d{1,2}', re.DOTALL)


class ListExtractor(BaseExtractor):
    """
    extract list from index page
    """
    better_list = []

    def __init__(self, min_number=LIST_MIN_NUMBER, min_length=LIST_MIN_LENGTH, max_length=LIST_MAX_LENGTH,
                 similarity_threshold=SIMILARITY_THRESHOLD):
        """
        init list extractor
        """
        super(ListExtractor, self).__init__()
        self.min_number = min_number
        self.min_length = min_length
        self.max_length = max_length
        self.avg_length = (self.min_length + self.max_length) / 2
        self.similarity_threshold = similarity_threshold

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

    def _build_clusters(self, element):
        """
        build candidate clusters according to element
        :return:
        """
        descendants_tree = defaultdict(list)
        descendants = descendants_of_body(element)
        for descendant in descendants:
            # if one element does not have enough siblings, it can not become a child of candidate element
            if descendant.number_of_siblings + 1 < self.min_number:
                continue
            # if min length is larger than specified max length, it can not become a child of candidate element
            if descendant.a_descendants_group_text_min_length > self.max_length:
                continue
            # if max length is smaller than specified min length, it can not become a child of candidate element
            if descendant.a_descendants_group_text_max_length < self.min_length:
                continue
            # descendant element must have same siblings which their similarity should not below similarity_threshold
            if descendant.similarity_with_siblings < self.similarity_threshold:
                continue
            descendants_tree[descendant.parent_selector].append(descendant)
        descendants_tree = dict(descendants_tree)

        # cut tree, remove parent block
        selectors = sorted(list(descendants_tree.keys()))
        last_selector = None
        for selector in selectors[::-1]:
            # if later selector
            if last_selector and selector and last_selector.startswith(selector):
                del descendants_tree[selector]
            last_selector = selector
        clusters = cluster_dict(descendants_tree)
        return clusters

    def _evaluate_cluster(self, cluster):
        """
        calculate score of cluster using similarity, numbers, or other info
        :param cluster:
        :return:
        """
        score = dict()

        # calculate avg_similarity_with_siblings
        score['avg_similarity_with_siblings'] = np.mean(
            [element.similarity_with_siblings for element in cluster])

        # calculate number of elements
        score['number_of_elements'] = len(cluster)

        # calculate probability of it contains title
        # score['probability_of_title_with_length'] = np.mean([
        #     self._probability_of_title_with_length(len(a_descendant.text)) \
        #     for a_descendant in itertools.chain(*[element.a_descendants for element in cluster]) \
        #     ])

        # TODO: add more quota to select best cluster
        score['clusters_score'] = \
            score['avg_similarity_with_siblings'] \
            * np.log10(score['number_of_elements'] + 1) \
            # * clusters_score[cluster_id]['probability_of_title_with_length']
        return score

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
        logger.log('inspect', f'cluster after extend {cluster}')
        return cluster

    def _best_cluster(self, clusters):
        """
        use clustering algorithm to choose best cluster from candidate clusters
        :param clusters:
        :return:
        """
        if not clusters:
            logger.log('inspect', 'there is on cluster, just return empty result')
            return []
        if len(clusters) == 1:
            logger.log('inspect', 'there is only one cluster, just return first cluster')
            return clusters[0]
        # choose best cluster using score
        clusters_score = defaultdict(dict)
        clusters_score_arg_max = 0
        clusters_score_max = -1
        for cluster_id, cluster in clusters.items():
            # calculate avg_similarity_with_siblings
            clusters_score[cluster_id] = self._evaluate_cluster(cluster)
            # get max score arg index
            if clusters_score[cluster_id]['clusters_score'] > clusters_score_max:
                clusters_score_max = clusters_score[cluster_id]['clusters_score']
                clusters_score_arg_max = cluster_id
        logger.log('inspect', f'clusters_score {clusters_score}')
        best_cluster = clusters[clusters_score_arg_max]
        return best_cluster

    def _extract_cluster(self, cluster):
        """
        extract title and href from best cluster
        :param cluster:
        :return:
        """
        if not cluster:
            return None
        # get best tag path of title
        probabilities_of_title = defaultdict(list)
        for element in cluster:
            descendants = element.a_descendants
            for descendant in descendants:
                path = descendant.path
                descendant_text = descendant.text
                probability_of_title_with_length = self._probability_of_title_with_length(len(descendant_text))
                # probability_of_title_with_descendants = self.probability_of_title_with_descendants(descendant)
                # TODO: add more quota to calculate probability_of_title
                probability_of_title = probability_of_title_with_length
                probabilities_of_title[path].append(probability_of_title)

        # get most probable tag_path
        probabilities_of_title_avg = {k: np.mean(v) for k, v in probabilities_of_title.items()}
        if not probabilities_of_title_avg:
            return None
        best_path = max(probabilities_of_title_avg.items(), key=operator.itemgetter(1))[0]
        best_score = probabilities_of_title_avg[best_path]
        logger.log('inspect', f'best tag path {best_path}')
        # ==========================
        best_path = max(probabilities_of_title_avg.items(), key=operator.itemgetter(1))[0]
        second_best_path = None
        if len(probabilities_of_title_avg) > 1:
            del probabilities_of_title_avg[best_path]
            second_best_path = max(probabilities_of_title_avg.items(), key=operator.itemgetter(1))[0]
            second_score = probabilities_of_title_avg[second_best_path]
            if second_score / best_score < list_similarity_coefficient:
                second_best_path = None

        logger.log('inspect', f'best tag path {best_path}')
        # ==========================
        # extract according to best tag path
        result = []
        score = 0
        for element in cluster:
            descendants = element.a_descendants
            for descendant in descendants:
                path = descendant.path
                base = best_path if path == best_path else (second_best_path if path == second_best_path else None)
                base_url = self.kwargs.get('base_url')
                if base:
                    title = descendant.xpath('./@title')[0] if descendant.xpath('./@title') else descendant.text
                    url = descendant.attrib.get('href')
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
                        base: 'xpath',
                        'score': score
                    })
                    score += 1
        if result:
            result = self.process_result(result)
        return result

    @staticmethod
    def process_result(result: list):

        count_result = defaultdict(int)
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

    @staticmethod
    def make_basic(link):
        basic = link.split('/')[2]
        index_1 = basic.find('.') + 1
        basic = basic[index_1:]
        index_2 = basic.rfind('.')
        basic = basic[:index_2]
        return basic

    def spare(self, html=None, **kwargs):
        url = self.kwargs.get('base_url', None)
        basic = self.make_basic(url)
        dt = None
        try:
            hx = etree.HTML(html)
            dt = hx.xpath('//a')
        except Exception as e:
            pass
        result = []
        if not dt:
            url_list_old = re.findall(r'''(http[s]?://.*?)['"]''', html)
            url_list = list(set(url_list_old))
            url_list.sort(key=url_list_old.index)
            for uri in url_list:
                data = {'url': uri}
                result.append(data)
            if result:
                return result
        for i in dt:
            link = i.xpath('string(./@href)')
            if link:
                link = link.replace('\\', '').replace('"', '').replace("'", '')
                try:
                    link = urljoin(url, link)
                except ValueError:
                    continue
                if basic not in link:
                    continue
                if 'javas' in link or '\\' in link or '@' in link or '+' in link or '#' in link:
                    continue
                link = link.replace(' ', '').replace('"', '').replace("'", '').replace("\n", '').replace("\r", "")
                suffix_list = ['.htm', '.do', 'jsp', '.asp', '.xml', '.php']
                for suffix in suffix_list:
                    if suffix in link:
                        break
                else:
                    continue
                if link.endswith('/'):
                    continue
                title = i.xpath('./@title')[0] if i.xpath('./@title') else None
                if not title:
                    title = i.xpath('string(.)')
                    title = title.replace('\r', '').replace('\n', '').strip()
                link = urljoin(url, link)
                data = {'title': title, 'url': link}
                result.append(data)
        if not result:
            url_list_old = re.findall(r'''(http[s]?://.*?)['"]''', html)
            if not url_list_old:
                url_list_old = re.findall(r'"([^"]*?\.(?:htm.?|do|jsp|asp|xml|php))"', html)
            url_list = list(set(url_list_old))
            url_list.sort(key=url_list_old.index)
            for uri in url_list:
                if uri.endswith('.ico') or uri.endswith('.css') or uri.endswith('.js') or uri.endswith('.gif'):
                    continue
                uri = urljoin(url, uri)
                data = {'url': uri, 'title': None}
                result.append(data)
        return result

    def pre_processing(self, html):
        import re
        html = hl.remove_comments(html)
        # imt = re.compile(r'(<a.*?>.*?)<[^a/].*?></[^a].*?>(.*?</a>)', re.S)
        # html = imt.sub(r'\1\2', html)
        imt = re.compile(
            r'<([^>\s]+)[^>]*>(?:\s*(?:<br \/>|&nbsp;|&thinsp;|&ensp;|&emsp;|&#8201;|&#8194;|&#8195;)\s*)*<\/\1>', re.S)
        html = imt.sub(r'', html)
        html = hl.remove_tags(html, which_ones=('span', 'font', 'strong', 'img'))
        hx = etree.HTML(html)
        body = hx.xpath('/html')
        node_list = self.second_node(body)
        for r in node_list:
            try:
                r.getparent().remove(r)
            except AttributeError:
                pass
        html = etree.tostring(body[0], encoding='utf-8', pretty_print=True, method="html").decode('utf-8')
        return html

    def process(self, element: Element):

        preprocess4list_extractor(element)

        # build clusters
        clusters = self._build_clusters(element)
        logger.log('inspect', f'after build clusters {clusters}')

        # choose best cluster
        best_cluster = self._best_cluster(clusters)
        logger.log('inspect', f'best cluster {best_cluster}')

        extended_cluster = self._extend_cluster(best_cluster)
        logger.log('inspect', f'extended cluster {extended_cluster}')

        # extract result from best cluster
        result = self._extract_cluster(extended_cluster)
        if not result:
            rsp = self.spare(
                etree.tostring(element, encoding='utf-8', pretty_print=True, method="html").decode('utf-8'))
            task = []
            for r in rsp:
                task.append(r['url'])
            task = map(self.similarity, list(itertools.combinations(task, 2)))
            _ = [i for i in task if i]
            self.better_list = [list(set(r)) for r in self.better_list]
            try:
                better_array = max(self.better_list, key=len)
                point = 0
                for data in better_array:
                    dic = dict()
                    for nmb in range(point, 4):
                        element_str = ''.join(
                            element.xpath('//a[contains(@href,"{}")]'.format(data) + '/..' * nmb + '//text()'))
                        pub_time = re_time.findall(element_str)
                        dic['url'] = data
                        title = element.xpath('string(//a[contains(@href, "{}")]/@title)'.format(data))
                        dic['title'] = title if title else element.xpath(
                            'string(//a[contains(@href, "{}")])'.format(data))
                        if pub_time:
                            point = nmb
                            dic['pub_time'] = pub_time[0]
                            result.append(dic)
                            break
            except ValueError:
                pass
        return result

    def extract(self, html, **kwargs):
        """
        base extract method, firstly, it will convert html to WebElement, then it call
        process method that child class implements
        :param html:
        :return:
        """
        self.kwargs = kwargs
        html = self.pre_processing(html)
        element = fromstring(html=html)
        element.__class__ = Element
        result = self.process(element)
        return result

    def similarity(self, array):
        rsp = []
        str1, str2 = array
        ratio = Levenshtein.ratio(str1, str2)
        if ratio > 0.8:
            for r in self.better_list:
                if str1 in r or str2 in r:
                    r.append(str2)
                    break
            else:
                rsp.append(str1)
                rsp.append(str2)
            if rsp:
                self.better_list.append(rsp)


def abstract_list(html, **kwargs):
    list_extractor = ListExtractor()
    return list_extractor.extract(html, **kwargs)


def show_list(html, **kwargs):
    rsp_list = abstract_list(html, base_url=kwargs.get('base_url'))
    if isinstance(rsp_list, list) and rsp_list:
        time_list = None
        try:
            time_xp = rsp_list[0]['xpath'].replace('html', '/').replace('/a', '//a')
            hx = etree.HTML(html)
            url_num = len(rsp_list)
            for i in range(5):
                block = hx.xpath(time_xp + '/..' * i + '//text()')
                time_list_copy = re_time.findall(' '.join(block), re.DOTALL)
                if len(time_list_copy) > url_num:
                    dic = {}
                    for j in time_list_copy:
                        if dic.get(j[4]):
                            dic[j[4]] += 1
                        else:
                            dic[j[4]] = 1
                    del dic[max(dic, key=dic.get)]
                    key_list = dic.keys()
                    for key in key_list:
                        for _ in time_list_copy.copy():
                            if key in _:
                                time_list_copy.remove(_)
                time_list_copy = [
                    ('20' + t).replace('.', '-').replace('/', '-').replace('年', '-').replace('月', '-')
                    if len(re.split(r'[^\d]', t)[0]) < 4 else t.replace('.', '-').replace('/',
                                                                                          '-').replace('年',
                                                                                                       '-').replace(
                        '月', '-') for t in time_list_copy]
                if not time_list_copy:
                    continue
                better_num = len(time_list_copy)
                if better_num % url_num == 0:
                    multiple = better_num / url_num
                    time_list_copy = [
                        time.strftime("%Y-%m-%d", time.localtime(time.mktime(time.strptime(t, '%Y-%m-%d')))) for t in
                        time_list_copy]
                    start_time_list = [time_[:10] for time_ in time_list_copy[:int(multiple)]]
                    if len(start_time_list) != len(list(set(start_time_list))):
                        continue
                    min_time = time.strftime("%Y-%m-%d", time.localtime(
                        (min([time.mktime(time.strptime(time1, '%Y-%m-%d')) for time1 in start_time_list]))))
                    time_index = start_time_list.index(min_time)
                    time_list = time_list_copy[time_index::int(multiple)]
                    del time_xp
                    break
            result = []
            for rsp in rsp_list:
                rsp['pub_time'] = time_list[rsp['score']]
                if rsp['pub_time'] in rsp['title']:
                    rsp['title'] = rsp['title'].replace(rsp['pub_time'], '')
                del rsp['score']
                del rsp['xpath']
                result.append(rsp)
            return result
        except Exception as e:
            logger.warning('请注意：时间解析失败')
            pass
    return rsp_list


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    x = np.asarray(range(4, 40))
    y = ListExtractor()._probability_of_title_with_length(x)
    plt.plot(x, y, 'g', label='m=0, sig=2')
    plt.show()
    # print(re_time.findall('21.07.01'))
