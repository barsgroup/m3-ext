# coding: utf-8
"""
Модуль с преднастроенными панелями-гридами

Created on 26.05.2010

@author: akvarats
"""
import json

from m3_ext.ui import containers, controls, menus, misc, render_component
from m3_ext.ui.base import ExtUIComponent, BaseExtComponent
from m3.actions.urls import get_url
from m3_ext.ui.containers.grids import ExtGridCheckBoxSelModel


class ExtObjectGrid(containers.ExtGrid):

    """
    Панель с гqридом для управления списком объектов.
    """
    #==========================================================================
    # Внутренние классы для ExtObjectGrid
    #=========================================================================
    class GridContextMenu(menus.ExtContextMenu):
        """
        Внутренний класс для удобной работы с контекстным меню грида
        """
        def __init__(self, *args, **kwargs):
            super(ExtObjectGrid.GridContextMenu, self).__init__(
                *args, **kwargs)
            self.menuitem_new = menus.ExtContextMenuItem(
                text=u'Добавить',
                icon_cls='add_item',
                handler='contextMenuNew'
            )
            self.menuitem_edit = menus.ExtContextMenuItem(
                text=u'Изменить',
                icon_cls='edit_item',
                handler='contextMenuEdit'
            )
            self.menuitem_delete = menus.ExtContextMenuItem(
                text=u'Удалить',
                icon_cls='delete_item',
                handler='contextMenuDelete'
            )
            self.menuitem_separator = menus.ExtContextMenuSeparator()

            self.items.extend([
                self.menuitem_new,
                self.menuitem_edit,
                self.menuitem_delete,
                self.menuitem_separator,
            ])


    class GridTopBar(containers.ExtToolBar):
        """
        Внутренний класс для удобной работы топбаром грида
        """
        def __init__(self, *args, **kwargs):
            super(ExtObjectGrid.GridTopBar, self).__init__(*args, **kwargs)
            self.button_new = controls.ExtButton(
                text=u'Добавить',
                icon_cls='add_item',
                handler='topBarNew'
            )
            self.button_edit = controls.ExtButton(
                text=u'Изменить',
                icon_cls='edit_item',
                handler='topBarEdit'
            )
            self.button_delete = controls.ExtButton(
                text=u'Удалить',
                icon_cls='delete_item',
                handler='topBarDelete'
            )
            self.button_refresh = controls.ExtButton(
                text=u'Обновить',
                icon_cls='x-tbar-loading',
                handler='topBarRefresh'
            )

            self.items.extend([
                self.button_new,
                self.button_edit,
                self.button_delete,
                self.button_refresh,
            ])


    #==========================================================================
    # Собственно определение класса ExtObjectGrid
    #=========================================================================

    _xtype = 'm3-object-grid'

    js_attrs = containers.ExtGrid.js_attrs.extend(
        allow_paging='params.allowPaging',  # Использовать постраничную навигацию
        row_id_name='params.rowIdName',  # Поля для id записи
        column_param_name='params.columnParamName',  # Имя параметра, через который передается имя выделенной колонки
        local_edit='params.localEdit',  # Признак редактирования на клиенте - особенным образом обрабатываются данные при редактировании
        url_new='params.actions.newUrl',  # Адрес для новой записи.
        url_edit='params.actions.editUrl',  # Адрес для изменения
        url_delete='params.actions.deleteUrl',  # Адрес для удаления
        url_data='params.actions.dataUrl',  # Адрес для данных
    )

    deprecated_attrs = containers.ExtGrid.deprecated_attrs + (
        'handler_beforenew',
        'handler_beforeedit',
    )

    def __init__(self, *args, **kwargs):
        super(ExtObjectGrid, self).__init__(*args, **kwargs)

        #======================================================================
        # Действия, выполняемые изнутри грида
        #======================================================================

        # Экшен для новой записи
        self.setdefault('action_new', None)

        # Экшен для  изменения
        self.setdefault('action_edit', None)

        # Экшен для удаления
        self.setdefault('action_delete', None)

        # Экшен для данных
        self.setdefault('action_data', None)

        #======================================================================
        # Источник данных для грида
        #======================================================================

        # Стор для загрузки данных
        self.setdefault('store', misc.ExtJsonStore(
            auto_load=True, root='rows', id_property='id'
        ))
        self.setdefault('load_mask', True)
        self.setdefault('row_id_name', 'row_id')
        self.setdefault('column_param_name', 'column')
        self.setdefault('allow_paging', True)

        #======================================================================
        # Контекстное меню и бары грида
        #======================================================================

        # Контекстное меню для строки грида
        self.setdefault('handler_rowcontextmenu',
                        ExtObjectGrid.GridContextMenu())

        # Контекстное меню для грида, если произошел счелчок не на строке
        self.setdefault('handler_contextmenu',
                        ExtObjectGrid.GridContextMenu())

        # Топ бар для грида
        self.setdefault('top_bar', ExtObjectGrid.GridTopBar())

        # Paging бар для постраничной навигации
        self.setdefault('paging_bar', containers.ExtPagingBar())

        # Признак локального редактирования
        self.setdefault('local_edit', False)

        # Атрибут store из store baseParams вынесен,
        # для одновременного изменения с атрибутом page_size paging_bar-а
        self.setdefault('limit', 25)

    # FIXME: перенести make_read_only в js-код
    def _make_read_only(
            self, access_off=True, exclude_list=(), *args, **kwargs):
        self.read_only = access_off
        # Выключаем\включаем компоненты.
        for item in (
            self.context_menu_grid.menuitem_new,
            self.context_menu_grid.menuitem_edit,
            self.context_menu_grid.menuitem_delete,
            self.context_menu_row.menuitem_new,
            self.context_menu_row.menuitem_edit,
            self.context_menu_row.menuitem_delete,
            self.context_menu_row,
        ):
            item.make_read_only(
                access_off, exclude_list, *args, **kwargs
            )
        if hasattr(self.top_bar, 'items') and self.top_bar.items:
            for item in self.top_bar.items:
                if hasattr(item, 'make_read_only') and callable(
                        item.make_read_only):
                    item.make_read_only(
                        access_off, exclude_list, *args, **kwargs)


class ExtMultiGroupinGrid(containers.ExtGrid):
    """
    Грид с возможностью множественной группировки колонок.
    Обработка группировки происходит на сервере
    .. seealso::
        m3.helpers.datagrouping
    """

    class GridExportMenu(menus.ExtContextMenu):
        """
        Внутренний класс для удобной работы с контекстным меню грида
        """

        def __init__(self, *args, **kwargs):
            super(ExtMultiGroupinGrid.GridExportMenu, self).__init__(
                *args, **kwargs)
            self.xls = menus.ExtContextMenuItem(
                text=u'XLS (Excel2003 до 65000 строк)',
                handler='function(){exportData("xls");}')
            self.csv = menus.ExtContextMenuItem(
                text=u'CSV (разделитель ";")',
                handler='function(){exportData("csv");}')

            self.items.extend([
                self.xls,
                self.csv,
            ])


    class LiveGridTopBar(containers.ExtToolBar):
        """
        Внутренний класс для удобной работы топбаром грида
        """
        def __init__(self, *args, **kwargs):
            super(ExtMultiGroupinGrid.LiveGridTopBar, self).__init__(
                *args, **kwargs)
            self._ext_name = "Ext.ux.grid.livegrid.Toolbar"
            self.button_new = controls.ExtButton(
                text=u'Добавить',
                icon_cls='add_item',
                handler='topBarNew'
            )
            self.button_edit = controls.ExtButton(
                text=u'Изменить',
                icon_cls='edit_item',
                handler='topBarEdit'
            )
            self.button_delete = controls.ExtButton(
                text=u'Удалить',
                icon_cls='delete_item',
                handler='topBarDelete'
            )
            self.button_export = controls.ExtButton(
                text=u'Экспорт',
                icon_cls='icon-table-go',
                menu=ExtMultiGroupinGrid.GridExportMenu(
                )
            )

            self.items.extend([
                self.button_new,
                self.button_edit,
                self.button_delete,
                self.button_export,
            ])


    # Поле в котором будет содержаться значение ключа группировки
    # должно отличаться от ключевого поля Store,
    # т.к. должно содержать совсем другие данные
    data_id_field = 'id'

    # Поле отображаемое вместо идентификатора группировки
    # (по-умолчанию отображается сам идентификатор)
    data_display_field = 'id'

    # Поля группировки по-умолчанию (список имен полей)
    grouped = None

    def __init__(self, *args, **kwargs):
        super(ExtMultiGroupinGrid, self).__init__(*args, **kwargs)
        self.template = 'ext-grids/ext-multigrouping-grid.js'
        # Для данных
        self.action_data = None

        self.action_new = None  # Экшен для новой записи
        self.action_edit = None  # Экшен для  изменения
        self.action_delete = None  # Экшен для удаления
        self.action_export = None  # Экшен для экспорта

        # Поля для id записи
        self.row_id_name = 'row_id'

        # Обработчик двойного клика
        self.dblclick_handler = 'onEditRecord'

        # Топ бар для грида
        self._top_bar = ExtMultiGroupinGrid.LiveGridTopBar()

        # Признак того, маскировать ли грид при загрузки
        self.load_mask = True

        # Стор для загрузки данных
        self.store = misc.store.ExtMultiGroupingStore(
            auto_load=True, root='rows', id_property='index')

        # Начальный перечень сгруппированных колонок
        self.grouped = []

        # Признак редактирования на клиенте
        # - особенным образом обрабатываются данные при редактировании
        self.local_edit = False

        # Признак возможности группировки (показывает панель)
        self.groupable = True

        # Признак отображения информации о записях
        self.display_info = True

        # Формат отображения информации о записях
        self.display_message = u'Показано {0}-{1} из {2}'

        # Объем буфера записей - должен быть больше,
        # чем число соседних элементов + число видимых строк
        self.buffer_size = 200

        # Число соседних элементов сверху и снизу от видимой области,
        # для предотвращения запросов.
        # Обычно 1/4 или 1/2 от объема буфера
        self.near_limit = 100

        # Стиль заголовка колонки.
        # Применяется ко всем колонкам. Например: 'text-align: center;'
        self.header_style = ''

        # Url для пака
        self.url_data = self.url_new = self.url_edit = self.url_delete = None

    def render(self):
        self.store.url = self.store.url or self.url_data

        assert self.store.url or self.action_data, 'Action data is not defined'
        # тонкая настройка self.store
        if not self.store.url and self.action_data:
            self.store.url = get_url(self.action_data)

        self.render_base_config()
        self.render_params()
        return render_component(self)

    def render_base_config(self):
        # Добавление происходит перед вызовом родителя,
        # т.к. в нём _view_config уже будет сериализован
        if self.header_style:
            self._view_config['headerStyle'] = self.header_style
        super(ExtMultiGroupinGrid, self).render_base_config()

    def render_params(self):
        super(ExtMultiGroupinGrid, self).render_params()

        data_url = self.url_data or (get_url(
            self.action_data) if self.action_data else None)

        def remove(this):
            if this in self._top_bar.items:
                self._top_bar.items.remove(this)

        new_url = self.url_new or (get_url(
            self.action_new) if self.action_new else None)
        if not new_url:
            remove(self._top_bar.button_new)

        edit_url = self.url_edit or (get_url(
            self.action_edit) if self.action_edit else None)
        if not edit_url:
            remove(self._top_bar.button_edit)
        else:
            self.handler_dblclick = self.dblclick_handler

        delete_url = self.url_delete or (get_url(
            self.action_delete) if self.action_delete else None)
        if not delete_url:
            remove(self._top_bar.button_delete)

        export_url = get_url(
            self.action_export) if self.action_export else None
        if not self.action_export:
            remove(self._top_bar.button_export)
        context_json = (
            self.action_context.json if self.action_context else None)

        for args in (
            (
                'actions',
                {
                    'dataUrl': data_url,
                    'newUrl': new_url,
                    'editUrl': edit_url,
                    'deleteUrl': delete_url,
                    'exportUrl': export_url,
                    'contextJson': context_json
                }
            ),
            (
                'groupedColumns',
                lambda: '[%s]' % ','.join(
                    ["'%s'" % col for col in self.grouped]
                )
            ),
            ('dataIdField', self.data_id_field),
            ('dataDisplayField', self.data_display_field),
            ('toolbar', self._top_bar.t_render_items),
            ('rowIdName', self.row_id_name),
            ('localEdit', self.local_edit),
            ('groupable', self.groupable),
            ('displayInfo', self.display_info),
            ('displayMsg', self.display_message),
            ('bufferSize', self.buffer_size),
            ('nearLimit', self.near_limit),
        ):
            self._put_params_value(*args)

    def t_render_base_config(self):
        return self._get_config_str()

    def t_render_params(self):
        return self._get_params_str()

    @property
    def handler_beforenew(self):
        return self._listeners.get('beforenewrequest')

    @handler_beforenew.setter
    def handler_beforenew(self, function):
        self._listeners['beforenewrequest'] = function

    @property
    def handler_beforeedit(self):
        return self._listeners.get('beforeeditrequest')

    @handler_beforeedit.setter
    def handler_beforeedit(self, function):
        self._listeners['beforeeditrequest'] = function

    def _make_read_only(
            self, access_off=True, exclude_list=(), *args, **kwargs):

        super(ExtMultiGroupinGrid, self)._make_read_only(
            access_off, exclude_list, *args, **kwargs)

        if (self._top_bar and hasattr(self._top_bar, 'items')
            and self._top_bar.items and hasattr(
                self._top_bar.items, '__iter__')):
            for item in self._top_bar.items:
                if isinstance(item, ExtUIComponent):
                    item.make_read_only(
                        self.read_only,
                        exclude_list,
                        *args, **kwargs
                    )


class ExtObjectSelectionPanel(containers.ExtContainer):
    """
    Класс, совмещающий возможность ObjectGrid'a
    и возможности выбора и запоминания значений в случае Paging'a
    """

    def __init__(self,
                 grid=None,
                 selection_columns=None,
                 selection_grid_conf=None,
                 *args,
                 **kwargs):
        super(ExtObjectSelectionPanel, self).__init__(*args, **kwargs)

        #self.xtype = 'object-selection-panel'
        self.layout = 'border'
        self.grid = grid
        self.selection_grid_conf = selection_grid_conf or {}
        self.selection_columns = selection_columns or []

        self._ext_name = 'Ext.m3.ObjectSelectionPanel'

    def render_base_config(self):
        super(ExtObjectSelectionPanel, self).render_base_config()
        assert self.grid, 'Grid should be define'

        if not isinstance(self.grid.sm, ExtGridCheckBoxSelModel):
            self.grid.sm = ExtGridCheckBoxSelModel()

        self._put_config_value('grid', self.grid.render)
        self._put_config_value('selectionColumns', lambda: json.dumps(self.selection_columns))
        self._put_config_value('selectionGridConf', self._render_selection_conf)

    def _render_selection_conf(self):
        """
        Рендеринг параметров грида для выделения записей
        :return: str
        """
        res = []
        for k, v in self.selection_grid_conf.items():
            if isinstance(v, BaseExtComponent):
                res.append('%s:%s' % (k, v.render()))
            else:
                res.append('%s:%s' % (k, json.dumps(v)))

        return '{%s}' % ','.join(res)
