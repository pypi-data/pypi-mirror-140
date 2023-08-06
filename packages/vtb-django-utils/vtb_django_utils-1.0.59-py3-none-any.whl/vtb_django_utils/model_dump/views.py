import json
import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .consts import DUMP_PINNED_FILE_PREFIX
from .dump import get_model_export
from .exceptions import ObjImportException
from .load import dump_import
from ..model_versions.models import is_instance_versioned
from ..utils.jsons import JSONEncoder

logger = logging.getLogger('')


class ImportExportMixin(GenericAPIView):
    models_module_name = None

    # noinspection PyUnusedLocal
    @action(methods=['GET'], detail=True)
    def obj_export(self, request, *args, **kwargs):
        instance = self.get_object()
        err = ''
        data = {}
        version_instance = None
        as_file = request.query_params.get('as_file', '').lower() == 'true'

        if is_instance_versioned(instance):
            try:
                if version := request.query_params.get('version'):
                    version_instance = instance.get_version_by_pattern(version)
                else:
                    version_instance = instance.last_version
            except Exception as e:
                err = str(e)

        if not err:
            try:
                is_pinned_versions = request.query_params.get('is_pinned_versions', '').lower() == 'true'
                data = get_model_export(
                    self.models_module_name, instance, version_instance, is_pinned_versions=is_pinned_versions)
            except Exception as e:
                err = f'Error export object {instance.__class__.__name__} {instance.name=} {kwargs}, {str(e)}'

        if err:
            logger.error(err)

        if not err and as_file:
            response = HttpResponse(json.dumps(data, cls=JSONEncoder).encode(),
                                    content_type='application/octet-stream')
            file_name = f'{DUMP_PINNED_FILE_PREFIX}{instance.__class__.__name__}.json'
            response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
            return response

        return Response({'err': err, 'data': json.dumps(data, cls=JSONEncoder)})

    @action(methods=['POST'], detail=False)
    def obj_import(self, request, *args, **kwargs):
        if file_obj := request.FILES.get('file', None):
            object_dump = json.loads(file_obj.read())
        else:
            object_dump = request.data.get('object_dump')
        model = self.get_queryset().model
        try:
            msgs = dump_import(self.models_module_name, object_dump, model)
        except (ValidationError, ObjImportException) as e:
            errors = [str(e)]
            resp_status = status.HTTP_400_BAD_REQUEST
        else:
            errors = msgs.get(messages.ERROR, [])
            resp_status = status.HTTP_200_OK
        return Response({'errors': errors}, status=resp_status)
