from urllib.parse import urlparse
from typing import List, Dict, Union, Type

from mext import providers


DATACALL = {
    'manga': 'get_manga',
    'chapter': 'read_chapter',
    'chapters': 'get_manga_chapters',
    'cover': 'get_cover',
}


class Mext:

    def __init__(self, type_list: list, url: str):
        self.url = url
        self.type_list = type_list

        self.parsed_url = urlparse(url)
        self.provider_classes = self.all_providers()

    def all_providers(self):
        return providers.__all__

    def get(self):
        data = {}
        for ProviderSite in self.provider_classes:
            provider_instance = ProviderSite(url=self.url)
            if self.parsed_url.netloc == provider_instance.domain:
                for data_type in self.type_list:
                    data[data_type] = getattr(provider_instance, DATACALL[data_type])()
        return data
