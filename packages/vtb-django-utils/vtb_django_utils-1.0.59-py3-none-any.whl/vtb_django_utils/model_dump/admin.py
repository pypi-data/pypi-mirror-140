import json
import logging

from django.conf.urls import url
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from .consts import DUMP_PINNED_FILE_PREFIX, DUMP_IS_PINNED_VERSIONS
from .dump import get_model_export
from .load import dump_import
from ..model_versions.models import is_instance_versioned
from ..utils.jsons import JSONEncoder

logger = logging.getLogger('default')


class ImportExportMixin(admin.ModelAdmin):
    """ Добавляет функционал экспорта-импорта модели в админке """
    models_module_name = None
    change_list_template = 'change_list.html'  # add button 'import XXX'

    def __init__(self, *args, **kwargs):
        super(ImportExportMixin, self).__init__(*args, **kwargs)
        self.list_display += ['export_actions']
        self.readonly_fields += ('export_actions',)

    # noinspection PyProtectedMember
    def get_url_name(self, part: str):
        return '%s_%s_%s' % (self.model._meta.app_label, self.model._meta.model_name, part)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<instance_id>.+)/form_export/$',
                self.admin_site.admin_view(self.form_export),
                name=self.get_url_name('form_export'),
            ),
            url(
                r'^form_import/$',
                self.admin_site.admin_view(self.form_import),
                name=self.get_url_name('form_import'),
            ),
        ]
        return custom_urls + urls

    def export_actions(self, obj):
        """ Кнопка экспорта в строке модели """
        return format_html(
            '<a class="button" href="{}">Export</a> ',
            reverse(f'admin:{self.get_url_name("form_export")}', args=[obj.pk]),
        )

    export_actions.short_description = 'Export'
    export_actions.allow_tags = True

    def form_export(self, request, instance_id):
        """ Вызывает форму экспорта модели """
        ver_file_mask = '_ver_XXX'
        mode = request.POST.get('mode')
        instance = self.model.objects.get(pk=instance_id)
        instance_name = f'_{instance.name}' if hasattr(instance, 'name') else ''
        if not mode:
            versions = instance.versions.filter(json__id__isnull=False) if is_instance_versioned(instance) else []
            version_choice = [(v.pk, v.version) for v in versions]
            file_name = f'{self.model.__name__}{instance_name}_{instance.pk}{ver_file_mask if versions else ""}.json'
            return TemplateResponse(request, 'export_instance.html', {
                'action_name': f'Экспорт {self.model.__name__}',
                'mode': 'export',
                'file_name': file_name,
                'version_choice': version_choice,
                'version_id': version_choice[-1][0] if version_choice else None,
            })
        else:
            file_name = request.POST.get('file_name')

            if version_id := request.POST.get('version_id'):
                version = instance.versions.get(pk=version_id)
            else:
                version = None

            if ver_file_mask in file_name and version:
                file_name = file_name.replace(ver_file_mask, f'_ver_{version.version}')

            is_pinned_versions = request.POST.get('is_pinned_versions') == 'on'
            if is_pinned_versions:
                file_name = f'{DUMP_PINNED_FILE_PREFIX}{file_name}'

            try:
                is_pinned_versions = request.POST.get('is_pinned_versions') == 'on'
                data = get_model_export(
                    self.models_module_name, instance, version, is_pinned_versions=is_pinned_versions)
            except Exception as e:
                err_msg = f'Error export object {self.model.__name__} {instance_name=} {instance.pk=}. {str(e)}'
                logger.exception(err_msg)
                messages.add_message(request, messages.ERROR, err_msg)
                return HttpResponseRedirect(reverse(f'admin:products_{self.model.__name__.lower()}_changelist'))
            else:
                messages.add_message(request, messages.INFO, f'File saved - {file_name}')
                response = HttpResponse(
                    json.dumps(data, cls=JSONEncoder),
                    content_type='application/octet-stream',
                )
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response

    def form_import(self, request):
        """ Вызывает форму импорта модели """
        mode = request.POST.get('mode')
        referer = request.META.get('HTTP_REFERER')

        if not mode:
            return TemplateResponse(request, 'load_instance.html', {
                'action_name': f'Импорт {self.model.__name__}',
                'mode': 'loading',
                'file_name': '',
                'referer': referer,
            })
        elif mode == 'loading':
            referer = request.POST.get('referer')
            if 'submit_cancel' in request.POST:
                messages.add_message(request, messages.WARNING, f'Import canceled')
                return HttpResponseRedirect(referer)

            if 'file_name' in request.FILES:
                uploaded_file = request.FILES['file_name']
                uploaded_file_name = uploaded_file.name
                object_dump_str = ''.join([line.decode() for line in uploaded_file])
                object_dump = json.loads(object_dump_str)
                # дополнительное подтверждение при импорте закрепленных версий
                if object_dump.get(DUMP_IS_PINNED_VERSIONS):
                    return TemplateResponse(request, 'confirm_pinned_version.html', {
                        'action_name': f'Подтверждение импорта {self.model.__name__}',
                        'mode': 'loading',
                        'uploaded_file_name': uploaded_file_name,
                        'object_dump_str': object_dump_str,
                        'referer': referer,
                    })
            elif 'object_dump_str' in request.POST:
                object_dump_str = request.POST.get('object_dump_str')
                object_dump = json.loads(object_dump_str)
                uploaded_file_name = request.POST.get('uploaded_file_name')
            else:
                messages.add_message(request, messages.WARNING, f'File did not selected')
                return HttpResponseRedirect(referer)

            try:
                self._import_object(request, object_dump)
            except Exception as e:
                logger.exception(f'Error loading file {uploaded_file_name}')
                messages.add_message(request, messages.ERROR, f'Error loading file {uploaded_file_name}. {str(e)}')

            return HttpResponseRedirect(referer)

    @transaction.atomic
    def _import_object(self, request, object_dump: dict):
        """ Импорт модели """
        msgs = dump_import(self.models_module_name, object_dump, self.model)
        for msg_level, msg_list in msgs.items():
            for msg in msg_list:
                messages.add_message(request, msg_level, msg)
