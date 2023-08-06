import os.path
from typing import List
from urllib.parse import unquote
from dataclasses import dataclass, field

from favorites_crawler.utils.text import drop_illegal_characters


@dataclass
class BaseItem:
    id: str = field(default=None)
    title: str = field(default=None)
    image_urls: List = field(default_factory=list)
    tags: List = field(default_factory=list)
    referer: str = field(default=None)

    def get_filepath(self, url):
        folder_name = self.get_folder_name()
        filename = self.get_filename(url)
        filepath = os.path.join(folder_name, filename)
        return drop_illegal_characters(filepath)

    def get_filename(self, url):
        return unquote(url.rsplit('/', maxsplit=1)[1])

    def get_folder_name(self):
        name = self.title
        prefix = self.get_folder_prefix()
        subfix = self.get_folder_subfix()
        return f'{prefix}{name}{subfix}'

    def get_folder_prefix(self):
        return f'[{self.id}] '

    def get_folder_subfix(self):
        tags = ' '.join(self.tags)
        if not tags:
            return ''
        return f' [{tags}]'


@dataclass
class PixivIllustItem(BaseItem):

    def get_folder_prefix(self):
        return ''

    def get_folder_subfix(self):
        return ''

    def get_folder_name(self):
        return 'Pixiv'



@dataclass
class YanderePostItem:
    """Yandere Post"""
    id: int = field(default=None)
    file_url: str = field(default=None)

    def get_filename(self):
        filename = self.file_url.rsplit('/', maxsplit=1)[1]
        filename = unquote(filename)
        filename = drop_illegal_characters(filename)
        return filename


@dataclass
class LemonPicPostItem(BaseItem):

    def get_folder_prefix(self):
        return ''


@dataclass
class NHentaiGalleryItem(BaseItem):
    characters: List = field(default_factory=list)

    def get_folder_name(self):
        characters = ' '.join(self.characters)
        prefix = f'[{self.id}] {self.title}'
        if characters:
            return prefix + f' [{characters}]'
        return prefix
