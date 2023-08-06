from typing import Dict, Union

from django.db.models import Model
from django.forms import model_to_dict

from .consts import DUMP_INFO, DUMP_IS_PINNED_VERSIONS, REL_MODELS_FOREIGN_KEY
from .exceptions import ObjExportException
from ..model_versions.models import VersionModel, VersionedModelMixin
from ..model_versions.models import is_instance_versioned
from ..model_versions.utils.consts import REL_VERSION_FIELD_END, REL_VERSION_PATTERN_FIELD_END
from ..utils.db import get_rel_model_fields
from ..utils.inspect import get_class_by_name

# переопределенные модели экспортеров
exporters = {}


def register(model_name):
    def register_exporter(dump_cls):
        global exporters
        exporters[model_name] = dump_cls
    return register_exporter


def get_model_export(
        models_module_name: str, instance, version: VersionModel = None, is_pinned_versions: bool = False
) -> Dict[str, any]:
    """ Вызывает функцию-сериализатор для экспорта модели """
    result = model_export(models_module_name, instance.__class__.__name__, instance, version,
                          is_pinned_versions=is_pinned_versions)
    result.update(DUMP_INFO)
    result.update({DUMP_IS_PINNED_VERSIONS: is_pinned_versions})
    return result


def model_export(models_module_name: str, class_name: str, instance: Union[dict, Model],
                 version: Union[int, str, VersionModel] = None, exclude_rel_fields: Union[tuple, list] = None,
                 is_pinned_versions: bool = False
                 ) -> Dict[str, any]:
    exporter = exporters.get(class_name, BaseExporter)
    return exporter(models_module_name, class_name, instance, version, exclude_rel_fields, is_pinned_versions).export()


class BaseExporter:
    """ Базовый класс для выгрузки json разных видов моделей """

    def __init__(self, models_module_name: str, class_name: str, instance: Union[dict, Model, VersionedModelMixin],
                 version: Union[int, str, VersionModel] = None, exclude_rel_fields=None,
                 is_pinned_versions: bool = False):
        self.models_module_name = models_module_name
        self.class_name = class_name
        self.model_class = get_class_by_name(self.models_module_name, self.class_name)
        self.is_pinned_versions = is_pinned_versions
        self.version = version
        self.rel_field_names = get_rel_model_fields(self.model_class, exclude_rel_fields)
        self.is_versioned = issubclass(self.model_class, VersionedModelMixin)
        self.result_dict = instance if isinstance(instance, dict) else self.get_json_from_instance(instance)
        self.instance_dict = self.result_dict['json'] if self.is_versioned else self.result_dict
        self.result_json = {
            'model_name': self.class_name,
            self.class_name: self.result_dict,
        }

    def get_json_from_instance(self, instance: Union[Model, VersionedModelMixin]) -> dict:
        """ Делает словарь из инстанса модели с учетом версии"""
        if self.is_versioned:
            # модель версионная - берем словарь версии
            version_instance = instance.get_version_by_pattern(self.version)
            if not version_instance:
                raise ObjExportException(f'Требуется сохранить версию для {self.class_name}:{str(instance)}')
            return model_to_dict(version_instance)
        else:
            # неверсионная - берем словарь основной модели
            model_dict = model_to_dict(instance, exclude=self.rel_field_names)
            for rel_field_name in self.rel_field_names:
                rel_field_name_id = f'{rel_field_name}_id'
                model_dict[rel_field_name_id] = getattr(instance, rel_field_name_id)
            return model_dict

    def _get_rel_instance(self, rel_field_name: str) -> Union[Model, VersionedModelMixin]:
        """ Возвращает инстанс связанной модели """
        rel_instance = None
        if rel_instance_id := self.instance_dict.get(f'{rel_field_name}_id'):
            rel_class = get_class_by_name(self.models_module_name, self._get_rel_class_name(rel_field_name))
            rel_instance = rel_class.objects.get(pk=rel_instance_id)
        return rel_instance

    @staticmethod
    def _get_rel_class_name(rel_field_name: str):
        """ Маппинг связанных моделей """
        # модели и реляции не всегда совпадают
        if rel_field_name == 'subgraph':
            return 'Graph'
        if rel_field_name == 'direction':
            return 'OrgDirection'

        return rel_field_name.capitalize()

    def add_rel_models_json(self):
        """ Добавляет jsons связанных моделей """
        rel_models = {}
        for rel_field_name in filter(lambda x: not x.endswith(REL_VERSION_FIELD_END), self.rel_field_names):
            if rel_obj := self._get_rel_instance(rel_field_name):
                if is_instance_versioned(rel_obj):
                    # если связанная модель версионная, нужно подтянуть конкретную версию
                    rel_version = self.instance_dict.get(f'{rel_field_name}{REL_VERSION_FIELD_END}')
                    rel_version_pattern = self.instance_dict.get(f'{rel_field_name}{REL_VERSION_PATTERN_FIELD_END}')
                    version = rel_obj.get_version_by_pattern(rel_version or rel_version_pattern)
                    # если закрепляем версии, то онужно прописать их в словаре явно
                    if self.is_pinned_versions:
                        self.instance_dict[f'{rel_field_name}{REL_VERSION_FIELD_END}'] = version.version
                        self.instance_dict[f'{rel_field_name}{REL_VERSION_PATTERN_FIELD_END}'] = ''
                else:
                    version = None
                # экспорт связанной модели с учетом версии
                rel_models[rel_field_name] = model_export(
                    self.models_module_name, self._get_rel_class_name(rel_field_name), rel_obj, version,
                    is_pinned_versions=self.is_pinned_versions)

        self.result_json[REL_MODELS_FOREIGN_KEY] = rel_models

    def export(self) -> Dict[str, any]:
        self.add_rel_models_json()
        return self.result_json
