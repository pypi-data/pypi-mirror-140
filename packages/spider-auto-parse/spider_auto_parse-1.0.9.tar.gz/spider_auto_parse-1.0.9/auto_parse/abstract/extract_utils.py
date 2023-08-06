import re

import cchardet
import requests

# 正则表达式元字符
meta_chars = [
    '+', '*', '?', '[', ']', '.', '{', '}', '(', ')'
]
meta_regex = '([' + '\\'.join(meta_chars) + '])'


# def escape_regex_meta(text):
#     """
#      text中正则表达式元字符替换成普通成字符
#     """
#     return re.sub(meta_regex, lambda matchobj: '\\' + matchobj.group(), text)


def url_validate(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return regex.match(url) is not None


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
            .replace("&#169;", "@").replace("♂", "").replace("\r\n|\r", "\n").replace("&#13;", ""))
    return text


def get_html(url):
    assert url_validate(url), "invalid url"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        raise e
    code = cchardet.detect(resp.content)['encoding']
    resp.encoding = code
    html = resp.text

    # if resp.headers.get("Content-Encoding") == 'gzip':
    #     buf = StringIO(html)
    #     f = gzip.GzipFile(fileobj=buf)
    #     html = f.read()
    #     f.close()
    #     buf.close()
    html = html_escape(html)
    return html


if __name__ == '__main__':
    print(get_html("http://www.ccgp.gov.cn/cggg/dfgg/zbgg/202105/t20210513_16276812.htm"))
