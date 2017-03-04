from xblock.fields import Dict
from xblock_ifmo.utils import DefaultedDescriptor
from xblock_ifmo.core import XBlockFieldsMixin
from xblock.fields import Scope, String, Integer

from .settings import *


class ImageMagickXBlockFields(XBlockFieldsMixin):

    display_name = String(
        display_name="Display name",
        default='ImageMagick Assignment',
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings
    )

    instructor_image_meta = Dict(
        default={},
        scope=Scope.settings,
    )

    report_storage = DefaultedDescriptor(
        base_class=String,
        display_name="Report storage",
        default=REPORT_STORAGE,
        help="",
        scope=Scope.settings,
    )

    latest_check = Dict(
        scope=Scope.user_state,
        default=None
    )

    allowable_fuzz = Integer(
        scope=Scope.settings,
        default=DEFAULT_FUZZ
    )

    cut_off = Integer(
        scope=Scope.settings,
        default=DEFAULT_CUT_OFF,
    )

    extra_cmd_settings = String(
        scope=Scope.settings,
        default=DEFAULT_EXTRA_CMD_SETTINGS,
    )
