from itertools import groupby
from operator import itemgetter


def sort_by_depth(block_list):
    deep_list = [{'key': k, 'count': k.count('/')} for k in block_list]
    deep_list.sort(key=itemgetter('count'))
    result = []
    for date, items in groupby(deep_list, key=itemgetter('count')):
        new = []
        for i in items:
            new.append(i['key'])
        result.append(new)
    return result


def longest_common_prefix(strs: list) -> str:
    len_list = [len(i) for i in strs]
    min_len = min(len_list)
    if min_len == 0:
        return ''
    res = strs[0][0]
    for i in strs:
        if i[0] != res:
            return ''
    initial = strs[0][0:1]
    for i in range(1, min_len):
        initial = strs[0][0:i + 1]
        for j in strs:
            if initial != j[0:i + 1]:
                return strs[0][0:i]
    return initial


def basic_grouping(block_list):
    new_result = []
    result = sort_by_depth(block_list)
    for r in result:
        # 处理前缀
        rsp = []
        # suffix_rsp = []
        rsp.append(prefix_classify(r))
        rsp = refactoring_list(rsp)
        rsp = [r for r in rsp if r]
        # 处理后缀
        min_len_list = [i for i in rsp if len(i) < 4]
        min_len = len(min_len_list)
        if min_len > 3:
            min_len_dic = {1: [], 2: [], 3: []}
            for k, v in min_len_dic.items():
                for ml in min_len_list:
                    if len(ml) == k:
                        v.append(ml)
            for k, min_len_list in min_len_dic.items():
                [rsp.remove(i) for i in min_len_list]
                min_len_list = [i for j in min_len_list for i in j]
                if min_len_list:
                    suffix_rsp = []
                    suffix_list = detection_suffix(min_len_list)
                    if len(suffix_list) == len(min_len_list):
                        suffix_rsp = min_len_list
                    else:
                        for suffix in suffix_list:
                            array = [i for i in r if suffix in i]
                            suffix_rsp.append(array)
                    rsp.append(suffix_rsp)
        else:
            for em in range(len(rsp)):
                suffix_list = detection_suffix(rsp[em])
                suffix_rsp = []
                if len(suffix_list) < 4:
                    for suffix in suffix_list:
                        array = [i for i in rsp[em] if suffix in i]
                        suffix_rsp.append(array)
                    rsp[em] = suffix_rsp
        new_result.append(rsp)
    return new_result


def prefix_classify(r):
    rsp = []
    common_prefix, prefix_list = classify_prefix(r)
    if len(prefix_list) == len(r):
        return r
    else:
        for prefix in prefix_list:
            prefix = common_prefix + prefix
            array = [i for i in r if prefix in i]
            rsp.append(prefix_classify(array))
    return rsp


def classify_prefix(r):
    common_prefix = longest_common_prefix(r).rsplit('/', 1)[0] + '/'
    prefix_list = list(set([xp.replace(common_prefix, '').split('/', 1)[0] for xp in r]))
    return common_prefix, prefix_list


def detection_suffix(min_len_list):
    suffix_list = None
    for i in range(len(min_len_list[0].split('/'))):
        suffix_list = list(set([xp.split('/', xp.count('/') - i)[-1] for xp in min_len_list]))
        if len(suffix_list) > 1:
            break
    return suffix_list


def build_basic_cluster(path_list):
    base_group = basic_grouping(path_list)
    base_group = refactoring_list(base_group)
    # for i in range(2):
    # for index in range(len(base_group)):
    #     if len(base_group[index]) < 2:
    #         continue
    #     base_group[index] = basic_grouping(base_group[index])
    # base_group = refactoring_list(base_group)
    base_group = [base for base in base_group if base]

    recycling_link(base_group)
    base_group = [base for base in base_group if base]

    return base_group


def recycling_link(base_group):
    min_len_list = [i for i in base_group if len(i) < 2]
    [base_group.remove(i) for i in min_len_list]
    min_len_list = [i for base in min_len_list if base for i in base]
    min_len_list = basic_grouping(min_len_list)
    min_len_list = refactoring_list(min_len_list)
    base_group.extend(min_len_list)


def diff(list1, list2):
    target = 0
    for point in range(len(list1)):
        if list1[point] != list2[point]:
            target += 1
        if target > 1:
            return False
    return True


def refactoring_list(target_list):
    queue = []
    better_list = []
    for target in target_list:
        if not isinstance(target, list):
            better_list.append(target)
        else:
            queue.extend(refactoring_list(target))
    queue.append(better_list)
    return queue


if __name__ == '__main__':
    a = ['/html/body[1]/div[4]/div[1]/ul[1]/li[12]/a[1]', '/html/body[1]/div[5]/div[1]/dl[3]/dd[5]/a[1]',
         '/html/body[1]/div[5]/div[1]/dl[3]/dd[2]/a[1]', '/html/body[1]/div[4]/div[1]/ul[1]/li[2]/a[1]',
         '/html/body[1]/div[4]/div[1]/ul[1]/li[11]/a[1]', '/html/body[1]/div[5]/div[1]/dl[2]/dd[2]/a[1]',
         '/html/body[1]/div[5]/div[1]/dl[3]/dd[3]/a[1]', '/html/body[1]/div[3]/div[1]/ul[1]/li[2]/a[1]',
         '/html/body[1]/div[4]/div[1]/ul[1]/li[7]/a[1]', '/html/body[1]/div[5]/div[1]/dl[1]/dd[2]/a[1]',
         '/html/body[1]/div[5]/div[1]/dl[3]/dd[7]/a[1]', '/html/body[1]/div[6]/div[1]/ul[1]/li[2]/a[1]',
         '/html/body[1]/div[5]/div[1]/dl[3]/dd[8]/a[1]', '/html/body[1]/div[5]/div[1]/dl[3]/dd[4]/a[1]',
         '/html/body[1]/div[4]/div[1]/ul[1]/li[14]/a[1]', '/html/body[1]/div[4]/div[1]/ul[1]/li[10]/a[1]',
         '/html/body[1]/div[6]/div[1]/ul[1]/li[3]/a[1]', '/html/body[1]/div[5]/div[1]/dl[3]/dd[9]/a[1]',
         '/html/body[1]/div[5]/div[1]/dl[1]/dd[4]/a[1]', '/html/body[1]/div[4]/div[1]/ul[1]/li[9]/a[1]',
         '/html/body[1]/div[5]/div[1]/dl[3]/dd[1]/a[1]', '/html/body[1]/div[4]/div[1]/ul[1]/li[3]/a[1]',
         '/html/body[1]/div[6]/div[1]/ul[1]/li[1]/a[1]', '/html/body[1]/div[5]/div[1]/dl[1]/dd[3]/a[1]',
         '/html/body[1]/div[4]/div[1]/ul[1]/li[15]/a[1]', '/html/body[1]/div[4]/div[1]/ul[1]/li[4]/a[1]',
         '/html/body[1]/div[5]/div[1]/dl[3]/dd[6]/a[1]', '/html/body[1]/div[4]/div[1]/ul[1]/li[6]/a[1]',
         '/html/body[1]/div[5]/div[1]/dl[2]/dd[1]/a[1]', '/html/body[1]/div[4]/div[1]/ul[1]/li[13]/a[1]',
         '/html/body[1]/div[3]/div[1]/ul[1]/li[1]/a[1]', '/html/body[1]/div[4]/div[1]/div[1]/div[1]/a[1]',
         '/html/body[1]/div[4]/div[1]/ul[1]/li[1]/a[1]', '/html/body[1]/div[5]/div[1]/dl[1]/dd[1]/a[1]',
         '/html/body[1]/div[4]/div[1]/ul[1]/li[8]/a[1]', '/html/body[1]/div[4]/div[1]/ul[1]/li[5]/a[1]']
    b = basic_grouping(a)
    print(b)
