import datetime

from vtb_django_utils.utils.consts import DATETIME_SHORT_FORMAT

DUMP_CURRENT_VERSION = 4.0
DUMP_INFO = {
    'dump_version': DUMP_CURRENT_VERSION,
    'dump_date': datetime.datetime.now().strftime(DATETIME_SHORT_FORMAT)
}
DUMP_IS_PINNED_VERSIONS = 'is_pinned_versions'
DUMP_PINNED_FILE_PREFIX = 'PINNED_'

REL_MODELS_FOREIGN_KEY = 'rel_foreign_models'
REL_MODELS_REVERS_KEY = 'rel_revers_models'
