# -*- coding=utf-8 -*-

from django.core.files.base import File
from django.core.files.storage import default_storage
from xblock.core import XBlock
from xblock_ifmo.core import IfmoXBlock, SubmissionsMixin, XQueueMixin
from xblock_ifmo import FragmentMakoChain, deep_update
from xblock_ifmo import get_sha1, file_storage_path
from webob.response import Response

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
        fragment.add_css(self.load_css('settings_view.css'))
        fragment.add_javascript(self.load_js('settings_view.js'))
        fragment.initialize_js('ImageMagickXBlockSettingsView')
        return fragment

    @XBlock.json_handler
    def save_settings(self, data, suffix=''):
        return super(ImageMagickXBlock, self).save_settings(data)

    @XBlock.json_handler
    def save_settings(self, data, suffix):
        result = super(ImageMagickXBlock, self).save_settings(data)

        # Извлекаем информацию об оригинальном архиве и драфте
        fs_path = self.instructor_image_meta.get('fs_path')
        draft_fs_path = self.instructor_image_meta.get('draft', {}).get('fs_path')

        # Сейчас оригинального файла может не существовать, поэтому вычислим его расположение

        # Перемещать нам нужно файл только если в драфте что-то есть
        storage = default_storage
        if draft_fs_path and storage.exists(draft_fs_path):

            # Удаляем существующий оригинальный файл
            # if fs_path and storage.exists(fs_path):
            #     storage.delete(fs_path)

            # Вычисляем новый адрес архива
            new_fs_path = draft_fs_path[:-len(".~draft")]

            # Сохраняем из драфта, операции move нет, поэтому только open...
            storage.save(new_fs_path, storage.open(draft_fs_path))

            # Подчищаем draft
            storage.delete(draft_fs_path)

            # Сохраняем мета-информацию о драфте
            self.instructor_image_meta = self.instructor_image_meta['draft']
            self.instructor_image_meta['fs_path'] = new_fs_path

        return result

    @XBlock.handler
    def upload_instructor_image(self, request, suffix):
        """
        Обработчик загрузки эталонного изображения инструктора.

        Вызывается, когда в студии инструктор нажимает кнопку "Загрузить"
        напротив поля "Эталонное изображение".

        Проводит валидацию изображения и временно сохраняет его. Позднее, он может
        быт восстановлен обработчиком "save_settings". Защиты от параллельной
        загрузки несколькими инструкторами (или в нескольких окнах браузера)
        не предусмотрено.

        :param request:
        :param suffix:
        :return:
        """

        def get_image_signature(archive):
            """
            Формирует подпись изображения (файла) на основании sha1 и текущего времени

            :param archive: file-object
            :return: tuple(sha1, signature)
            """
            import hashlib
            import datetime
            sha1 = get_sha1(archive)
            md5 = hashlib.md5()
            md5.update(sha1)
            md5.update(datetime.datetime.isoformat(datetime.datetime.now()))
            return sha1, md5.hexdigest()

        upload = request.params['instructor_image']

        # self.validate_instructor_image(upload.file)

        uploaded_file = File(upload.file)

        image_sha1, image_signature = get_image_signature(uploaded_file)
        image_name = "instructor.{signature}.~draft".format(name=upload.file.name, signature=image_signature)
        fs_path = file_storage_path(self.location, image_name)

        # Сохраняем временную информацию до того как нажата кнопка "Save"
        self.instructor_image_meta['draft'] = {
            'filename': upload.file.name,
            'sha1': get_sha1(uploaded_file),
            'upload_at': None,
            'upload_by': None,
            'fs_path': fs_path,
        }

        if default_storage.exists(fs_path):
            default_storage.delete(fs_path)
        default_storage.save(fs_path, uploaded_file)

        return Response(json_body={})

    def get_settings_context(self):

        context = super(ImageMagickXBlock, self).get_settings_context()
        deep_update(context, {
            'metadata': {
                'instructor_image': self.instructor_image_meta,
            },
        })
        return context
