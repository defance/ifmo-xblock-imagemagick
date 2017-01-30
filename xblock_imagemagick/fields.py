from xblock_ifmo.core import XBlockFieldsMixin
from xblock.fields import Scope, String


class ImageMagickXBlockFields(XBlockFieldsMixin):

    display_name = String(
        display_name="Display name",
        default='ImageMagick Assignment',
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings
    )
