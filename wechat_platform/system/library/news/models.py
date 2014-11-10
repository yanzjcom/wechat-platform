# -*- coding: utf-8 -*-

from django.db import models

from system.official_account.models import OfficialAccount


class LibraryNewsManager(models.Manager):
    """
    素材库 - 图文库 Manager
    """
    def get(self, official_account, root):
        """
        获取以 root 为父节点的所有图文回复 (链式)
        :param official_account: 所属公众号 (OfficialAccount)
        :param root: 父节点实例 (LibraryNews)
        :return: 一个 list 对象, 一次为所有的图文回复 (以 root 为根, 呈链状)
        """
        return [root] + self._get_without_root(official_account=official_account, root=root)

    def add(self, official_account, news):
        """
        新建一个完整的图文信息
        :param official_account: 所属公众号 (OfficialAccount)
        :param news: 一个 list 对象, 每个元素为一个 dict 对象, key 包括 'title', 'description', 'picurl',
                     'url', 'author', 'content', 'picture', 'picture_id', 'from_url', 'msgid', 对应 value 解释见
                     LibraryNews Model, 除 'title' 外所有 key 值均为可选
        :return: 第一条图文的实例 (LibraryNews)
        """
        parent = None
        first_instance = None
        for item in news:
            tmp = super(LibraryNewsManager, self).create(
                official_account=official_account,
                parent=parent,
                title=item.get('title'),
                description=item.get('description'),
                picurl=item.get('picurl'),
                url=item.get('url'),
                author=item.get('author'),
                content=item.get('content'),
                picture=item.get('picture'),
                picture_id=item.get('picture_id', 0),
                from_url=item.get('from_url'),
                msgid=item.get('msgid'),
            )
            if not first_instance:
                first_instance = tmp
            parent = tmp
        return first_instance

    def _get_without_root(self, official_account, root):
        """
        获取以 root 为父节点的所有图文回复 (链式), 注意获取到的列表不含 root 在内
        :param official_account: 所属公众号 (OfficialAccount)
        :param root: 父节点实例 (LibraryNews)
        :return: 一个 list 对象, 一次为所有的图文回复 (以 root 为根, 呈链状但不含 root)
        """
        now = super(LibraryNewsManager, self).get_queryset().filter(official_account=official_account).filter(parent=root)
        if not now:
            return None

        child = self._get_without_root(official_account, now[0])
        if not child:
            return [now[0]]
        else:
            return [now[0]] + child


class LibraryNews(models.Model):
    """
    素材库 - 图文库
    """
    official_account = models.ForeignKey(OfficialAccount, verbose_name=u'所属公众号')
    parent = models.ForeignKey('self', verbose_name=u'父ID', blank=True, null=True)
    title = models.CharField(u'图文标题', max_length=100)
    description = models.TextField(u'图文描述', blank=True, null=True)
    picurl = models.CharField(u'缩略图图片地址', max_length=1024, blank=True, null=True)
    url = models.CharField(u'跳转地址', max_length=1024, blank=True, null=True)
    author = models.CharField(u'图文作者', max_length=100, blank=True, null=True)
    content = models.TextField(u'图文内容', blank=True, null=True)
    picture = models.ImageField(u'图片存储地址', blank=True, null=True)
    picture_id = models.IntegerField(u'素材库中的图片ID', default=0)
    from_url = models.CharField(u'来源URL', max_length=1024, blank=True, null=True)
    msgid = models.BigIntegerField(u'公众平台图文ID号', blank=True, null=True)

    objects = models.Manager()
    manager = LibraryNewsManager()

    class Meta:
        verbose_name = u'素材库 - 图文库'
        verbose_name_plural = u'素材库 - 图文库'
        db_table = 'library_news'

    def __unicode__(self):
        return self.title