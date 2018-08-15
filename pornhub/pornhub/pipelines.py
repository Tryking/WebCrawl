# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib

import scrapy
from scrapy.http import Request
from scrapy.utils.python import to_bytes
from scrapy.pipelines.images import ImagesPipeline


class PornhubPipeline(object):
    def process_item(self, item, spider):
        return item


class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(url=image_url, meta={'item': item})

    def file_path(self, request, response=None, info=None):
        ## start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.image_key(url) and file_key(url) methods are deprecated, '
                          'please use file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from image_key or file_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        # detect if file_key() or image_key() methods have been overridden
        if not hasattr(self.file_key, '_base'):
            _warn()
            return self.file_key(url)
        elif not hasattr(self.image_key, '_base'):
            _warn()
            return self.image_key(url)
        ## end of deprecation warning block

        image_guid = hashlib.sha1(to_bytes(url)).hexdigest()  # change to request.url after deprecation

        # 重新此方法，如果 item 中含有 save_sub_dir, 则将其放入此子文件夹
        item = request.meta['item']
        if 'save_sub_dir' in item:
            path = '%s/full/%s.jpg' % (item['save_sub_dir'], image_guid)
        else:
            path = 'full/%s.jpg' % image_guid
        return path

    def thumb_path(self, request, thumb_id, response=None, info=None):
        ## start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.thumb_key(url) method is deprecated, please use '
                          'thumb_path(request, thumb_id, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from thumb_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        # detect if thumb_key() method has been overridden
        if not hasattr(self.thumb_key, '_base'):
            _warn()
            return self.thumb_key(url, thumb_id)
        ## end of deprecation warning block

        thumb_guid = hashlib.sha1(to_bytes(url)).hexdigest()  # change to request.url after deprecation

        # 重新此方法，如果 item 中含有 save_sub_dir, 则将其放入此子文件夹
        item = request.meta['item']
        if 'save_sub_dir' in item:
            path = '%s/thumbs/%s/%s.jpg' % (item['save_sub_dir'], thumb_id, thumb_guid)
        else:
            path = 'thumbs/%s/%s.jpg' % (thumb_id, thumb_guid)
        return path
