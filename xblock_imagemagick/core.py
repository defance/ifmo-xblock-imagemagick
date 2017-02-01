from xblock.core import XBlock
from xblock_ifmo.core import IfmoXBlock, SubmissionsMixin, XQueueMixin
from xblock_ifmo import FragmentMakoChain, deep_update

from .fields import ImageMagickXBlockFields


@XBlock.wants("user")
@IfmoXBlock.register_resource_dir()
class ImageMagickXBlock(ImageMagickXBlockFields, XQueueMixin, SubmissionsMixin, IfmoXBlock):

    submission_type = "imagemagick_xblock"

    def student_view(self, context=None):

        fragment = FragmentMakoChain(base=super(ImageMagickXBlock, self).student_view(),
                                     lookup_dirs=self.get_template_dirs())
        fragment.add_content(self.load_template('xblock_imagemagick/student_view.mako'))
        fragment.add_javascript(self.load_js('student_view.js'))
        fragment.initialize_js('ImageMagickXBlockStudentView')
        return fragment

    def studio_view(self, context=None):

        if context is None:
            context = dict()

        deep_update(context, {'render_context': self.get_settings_context()})

        fragment = FragmentMakoChain(base=super(ImageMagickXBlock, self).studio_view(),
                                     lookup_dirs=self.get_template_dirs())
        fragment.add_content(self.load_template('xblock_imagemagick/settings_view.mako'))
        fragment.add_context(context)
        # fragment.add_css(self.load_css('settings_view.css'))
        fragment.add_javascript(self.load_js('settings_view.js'))
        fragment.initialize_js('ImageMagickXBlockSettingsView')
        return fragment

    @XBlock.json_handler
    def save_settings(self, data, suffix=''):
        return super(ImageMagickXBlock, self).save_settings(data)
