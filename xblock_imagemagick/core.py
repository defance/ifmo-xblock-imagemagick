from xblock_ifmo.core import IfmoXBlock, SubmissionsMixin, XQueueMixin
from xblock_ifmo import FragmentMakoChain

from .fields import ImageMagickXBlockFields


@IfmoXBlock.register_resource_dir()
class ImageMagickXBlock(ImageMagickXBlockFields, XQueueMixin, SubmissionsMixin, IfmoXBlock):

    def student_view(self, context=None):

        fragment = FragmentMakoChain(base=super(ImageMagickXBlock, self).student_view(),
                                     lookup_dirs=self.get_template_dirs())
        fragment.add_content(self.load_template('xblock_imagemagick/student_view.mako'))
        return fragment
