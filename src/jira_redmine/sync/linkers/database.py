# coding: utf-8
from typing import Dict

from jira_redmine.base.providers.database import DBProvider
from jira_redmine.base.resources.base import BaseResource
from jira_redmine.sync.linkers.base import BaseLinker


class DBLinker(BaseLinker):
    """Класс для связи ресурсов Jira и Redmine с помощью БД."""

    _provider_class = DBProvider

    def __init__(
        self,
        driver: str,
        server: str,
        database: str,
        link_params: Dict = None,
        *args,
        **kwargs
    ):
        super().__init__(driver, server, database, *args, **kwargs)
        if not link_params:
            raise ValueError('Не указаны параметры для связи объектов в БД')

        try:
            self._table_name = self._get_not_empty_value(
                link_params, 'table_name'
            )
            self._resource_field_name = self._get_not_empty_value(
                link_params, 'resource_field_name'
            )
            self._source_field_name = self._get_not_empty_value(
                link_params, 'source_field_name'
            )
            self._target_field_name = self._get_not_empty_value(
                link_params, 'target_field_name'
            )
        except KeyError as exc:
            raise ValueError(
                f'Не указан параметр {str(exc)} для связи объектов в БД.'
            )

    @staticmethod
    def _get_not_empty_value(source: dict, key: str):
        """Получить не пустое значение или бросить ошибку KeyError."""
        def _exc(k):
            raise KeyError(k)

        value = source[key] or _exc(key)
        return value

    def get_target_key(self, source_object: BaseResource, *args, **kwargs):
        """Получить код целевого ресурса."""
        column_values = (self._target_field_name,)
        where_values = {
            self._resource_field_name: source_object.get_resource_caption(),
            self._source_field_name: source_object.key,
        }
        row = self.get(
            self._table_name,
            column_values=column_values,
            where_values=where_values,
            *args,
            **kwargs
        )
        if row:
            return getattr(row, self._target_field_name)

    def link(
        self,
        source_object: BaseResource,
        target_object: BaseResource,
        *args,
        **kwargs
    ):
        """Связать ресурсы."""
        column_values = {
            self._resource_field_name: source_object.get_resource_caption(),
            self._source_field_name: source_object.key,
            self._target_field_name: target_object.key,
        }
        where_values = {
            self._resource_field_name: source_object.get_resource_caption(),
            self._target_field_name: target_object.key,
        }
        return super().link(
            self._table_name,
            column_values=column_values,
            where_values=where_values,
            *args,
            **kwargs
        )
