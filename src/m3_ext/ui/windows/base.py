#coding: utf-8
"""
Created on 25.02.2010

@author: akvarats
"""
import weakref

from django.conf import settings

from m3.actions import ActionContext

from m3_ext.ui.base import ExtUIComponent, renderable
from m3_ext.ui import render_template

from m3_ext.ui.containers.base import BaseExtContainer
from m3_ext.ui.controls.base import BaseExtControl


class ExtWindowRenderer(object):
    """
    Рендерер для скрипта на показ окна
    """
    def __init__(self, common_template):
        self.common_template = common_template

    def get_script(self, window):
        return render_template(
            self.common_template, {'window': window}
        )


class BaseExtWindow(ExtUIComponent):
    """
    Базовый класс для всех окон
    """
    __metaclass__ = renderable

    #deprecated: Использовать атрибуты с верхним регистром
    ALIGN_LEFT = align_left = 'left'
    ALIGN_CENTER = align_center = 'center'
    ALIGN_RIGHT = align_right = 'right'

    _xtype = 'window'

    _js_attrs = ExtUIComponent._js_attrs + (
        'title',
        'modal', 'maximizable', 'maximized', 'closable',
        'border', 'resizable', 'draggable', 'keys',
        'items', 'buttons', 'layout',
        ('body_style', 'bodyStyle'),
        ('icon_cls', 'iconCls'),
        ('top_bar', 'tbar'),
        ('bottom_bar' 'bbar'),
        ('footer_bar', 'fbar'),
        ('button_align', 'buttonAlign'),
        ('label_width', 'labelWidth'),
        ('label_align', 'labelAlign'),
        ('label_pad', 'labelPad'),
        ('help_topic', 'helpTopic'),
        ('context_json', 'contextJson'),
    )

    def __init__(self, *args, **kwargs):
        super(BaseExtWindow, self).__init__(*args, **kwargs)
        self._init_attr('items', [])
        self._init_attr('buttons', [])
        self._init_attr('keys', [])

        self._init_attr('width', 400)
        self._init_attr('height', 300)

        self._init_attr('body_style', 'padding:5px;')

        self._init_attr('border', True)
        self._init_attr('draggable', True)
        self._init_attr('resizable', True)

    # def _help_topic_full_path(self):
    #     """
    #     Возвращает квалицифирующее имя топика помощи
    #     """
    #     if not self.help_topic:
    #         return ''
    #     assert isinstance(self.help_topic, tuple)
    #     assert len(self.help_topic) > 0
    #     return self.help_topic[0] + '.html' + (
    #         '#' + self.help_topic[1] if len(self.help_topic) > 1 else ''
    #     )

    def _make_read_only(
            self, access_off=True, exclude_list=None, *args, **kwargs):
        exclude_list = exclude_list or []
        self.read_only = access_off
        # Перебираем итемы.
        for item in self.__items:
            item.make_read_only(
                self.read_only, exclude_list, *args, **kwargs)
        # Перебираем бары.
        bar_typle = (self.footer_bar, self.bottom_bar, self.top_bar)
        for bar in bar_typle:
            if bar and bar._items:
                # Обязательно проверяем, что пришел контейнер.
                assert isinstance(bar, BaseExtContainer)
                for item in bar._items:
                    if hasattr(item, 'make_read_only'):
                        item.make_read_only(
                            self.read_only, exclude_list, *args, **kwargs)
        # Перебираем кнопки.
        if self.__buttons and self.__buttons:
            for button in self.__buttons:
                assert isinstance(button, BaseExtControl)
                button.make_read_only(
                    self.read_only, exclude_list, *args, **kwargs)

    def get_script(self):
        return self.renderer.get_script(self)
