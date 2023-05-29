# encoding: utf-8
import json
import re
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin


DEFAULT_SCHEME = "https"


class OpenGraph(dict):
    """
    """
    YT_PATTERN = re.compile(r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))"
                            r"(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$")
    YT_API_URL = 'https://youtube.com/oembed?url={video_url}&format=json'

    required_attrs = ['title', 'type', 'image']

    def __init__(self, url=None, html=None, **kwargs):

        for k in list(kwargs.keys()):
            self[k] = kwargs[k]

        dict.__init__(self)

        _url = self.provide_url_scheme(url)

        if _url is not None:
            self.fetch(_url)

        if html is not None:
            self.html_parser(html)

        if not self.get('url'):
            self.url = _url

        if not self.get('title') and self.get('html_title'):
            self.title = self.get('html_title')

        if self.get('html_title'):
            self.pop('html_title')

    def __setattr__(self, name, val):
        self[name] = val

    def __getattr__(self, name):
        return self[name]

    def fetch(self, url, is_youtube=False):
        """
        """
        _url = self.YT_API_URL.format(video_url=url) if is_youtube else url
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                 ' Chrome/106.0.0.0 Safari/537.36 facebookexternalhit/1.1', 'Accept': '*/*'}
        http = urllib3.PoolManager(headers=headers)
        try:
            response = http.request('GET', _url, preload_content=False)
            data = response.read(1024*300)
            response.drain_conn()
            response.release_conn()
        except Exception:
            return

        if is_youtube:
            self.yt_parser(data)
        else:
            self.html_parser(data, url)

        if not self.is_valid() and not is_youtube and re.match(self.YT_PATTERN, url):
            self.fetch(url, is_youtube=True)
        return

    def html_parser(self, html, url=None):
        """
        """
        if not isinstance(html, BeautifulSoup):
            doc = BeautifulSoup(html, 'html.parser')
        else:
            doc = html
        ogs = doc.findAll(property=re.compile(r'^og'))

        for og in ogs:
            if og.has_attr('content'):
                self[og['property'][3:]] = og['content']
        if not ogs:
            if doc.title:
                self['title'] = doc.title.string
            desc_tag = doc.find("meta", {'name': "description"})
            if desc_tag:
                self['description'] = desc_tag.get('content')
            img = self.find_image(url, doc)
            if img:
                self['image'] = img

        if not self.get('title') and doc.title:
            self['html_title'] = doc.title.string

    def yt_parser(self, data):
        """
        """
        try:
            ogs = json.loads(data.decode('utf-8'))
        except:
            return
        self['title'] = ogs.get('title')
        self['type'] = 'video.other'
        self['image'] = ogs.get('thumbnail_url')
        self['image:width'] = ogs.get('thumbnail_width')
        self['image:height'] = ogs.get('thumbnail_height')
        self['site_name'] = ogs.get('provider_name')
        try:
            self['video:url'] = BeautifulSoup(ogs['html'], 'html.parser').iframe.attrs['src']
        except:
            pass

    def valid_attr(self, attr):
        return self.get(attr) and len(self[attr]) > 0

    def is_valid(self):
        return any([self.valid_attr(attr) for attr in self.required_attrs])

    def to_html(self):
        if not self.is_valid():
            return "<meta property=\"og:error\" content=\"og metadata is not valid\" />"

        meta = ""
        for key, value in self.items():
            meta += "<meta property=\"og:%s\" content=\"%s\" />" % (key, value)

        return meta

    def provide_url_scheme(self, url,  default_scheme=DEFAULT_SCHEME):
        """Make sure we have valid url scheme.
        Params:
            url : string : the URL
            default_scheme : string : default scheme to use, e.g. 'https'
        Returns:
            string : updated url with validated/attached scheme
        """
        has_scheme = ":" in url[:7]
        is_universal_scheme = url.startswith("//")
        is_file_path = url == "-" or (url.startswith("/") and not is_universal_scheme)
        if not url or has_scheme or is_file_path:
            return url
        if is_universal_scheme:
            return default_scheme + ":" + url
        return default_scheme + "://" + url

    def find_image(self, url, doc):
        if not doc.body:
            return
        images = doc.body.findAll('img')
        sources = [i.get('src') for i in images if i.get('src')]
        for src in sources:
            img_type = src.split('/')[-1].split('.')[-1]
            if img_type in ['png', 'jpg', 'jpeg']:
                return urljoin(url, src)
        return None
