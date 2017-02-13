# -*- coding=utf-8 -*-

import base64
import json
import mimetypes
import re

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from submissions import api as submissions_api
from xblock.core import XBlock
from xblock_ifmo.core import IfmoXBlock, SubmissionsMixin, XQueueMixin
from xblock_ifmo import FragmentMakoChain, deep_update
from xblock_ifmo import get_sha1, file_storage_path, now, reify_f
from xmodule.util.duedate import get_extended_due_date
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
        fragment.add_css(self.load_css('student_view.css'))
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

    @reify_f
    def get_student_context(self, user=None):

        parent = super(ImageMagickXBlock, self)
        if hasattr(parent, 'get_student_context'):
            context = parent.get_student_context(user)
        else:
            context = {}

        context.update({
            'allow_submissions': True if (self.due is None) or (now() < get_extended_due_date(self)) else False,
            'task_status': self.queue_details.get('state', 'IDLE'),
            'need_show_interface': True or self._is_studio(),
        })

        return context

    @XBlock.handler
    def upload_submission(self, request, suffix):

        def _return_response(response_update=None):
            if response_update is None:
                response_update = {}
            response = self.get_student_context()
            response.update(response_update)
            return self.get_response_user_state(response)

        if self.queue_details:
            return _return_response({
                'message': {
                    'text': 'Проверка другого решения уже запущена.',
                    'type': 'error',
                }
            })

        try:

            self.message = None

            # Извлечение данных о загруженном файле
            upload = request.params['submission']
            uploaded_file = File(upload.file)
            uploaded_filename = upload.file.name
            uploaded_sha1 = get_sha1(upload.file)
            uploaded_mimetype = mimetypes.guess_type(upload.file.name)[0]

            # Реальные названия файлов в ФС
            fs_path = file_storage_path(self.location, uploaded_sha1)
            instructor_fs_path = self.get_instructor_path()

            # Сохраняем данные о решении
            student_id = self.student_submission_dict()
            student_answer = {
                "sha1": uploaded_sha1,
                "filename": uploaded_filename,
                "mimetype": uploaded_mimetype,
                "real_path": fs_path,
                "instructor_real_path": instructor_fs_path,
            }
            submission = submissions_api.create_submission(student_id, student_answer)

            # Сохраняем файл с решением
            if default_storage.exists(fs_path):
                default_storage.delete(fs_path)
            default_storage.save(fs_path, uploaded_file)

            payload = {
                'method': 'check',
                'student_info': self.queue_student_info,
                'grader_payload': json.dumps({
                }),
                'student_response': self.get_queue_student_response(submission),
            }

            self.send_to_queue(
                header=self.get_submission_header(
                    access_key_prefix=submission.get('uuid'),
                ),
                body=json.dumps(payload)
            )

        except Exception as e:
            return _return_response({
                'message': {
                    'text': 'Ошибка при попытке поставить проверку решения в очередь: ' + e.message,
                    'type': 'error',
                }
            })

        return _return_response()

    @reify_f
    def get_instructor_path(self):
        return self.instructor_image_meta.get('fs_path')

    def get_queue_student_response(self, submission=None, dump=True):
        # TODO: Protect this with hash
        # TODO: Вынести формирование адреса для xqueue в обобщенный интерфейс

        # В некоторых случаях грейдер должен обратиться к LMS за дополнительными данными, при этом адрес LMS для
        # грейдера может отличаться от того, который предназначен для пользователя. Например, для внешних соединений
        # адрес представляет доменное имя с https, а грейдер внутри сети может обратиться к LMS по http/ip.

        # Полный адрес обработчика с указанием протокола
        base_url = self.runtime.handler_url(self, 'get_submitted_images', thirdparty=True)

        # Получаем из настроет callback_url для xqueue
        callback_url = settings.XQUEUE_INTERFACE.get("callback_url")

        # Если он задан, перезаписываем полный адрес обработчика
        if callback_url:

            # SITENAME содержит исключительно доменное имя или ip без указания протокола
            # Заменяем найденный в полном адресе обработчике SITENAME на callback_url
            # TODO: Корректно обрабатывать https, если он указан в настройках
            base_url = re.sub("http.?//%s" % settings.SITE_NAME, callback_url, base_url)

        if submission is None:
            submission = {}
        result = {
            'image_64_url': base_url + '/' + submission.get('uuid', ''),
        }
        if dump:
            result = json.dumps(result)
        return result

    @XBlock.handler
    def get_submitted_images(self, request, suffix):

        def get_64_contents(filename):
            with default_storage.open(filename, 'r') as f:
                return base64.b64encode(f.read())

        instructor_fs_path = self.get_instructor_path()

        response = {
            'instructor_image_name': instructor_fs_path,
            'instructor_image': get_64_contents(instructor_fs_path),
        }

        if suffix:
            user_id = self.student_submission_dict(anon_student_id=suffix)
            submission = submissions_api.get_submission(user_id.get('student_id'))
            answer = submission['answer']
            response.update({
                'user_image_name': answer.get('real_path'),
                'user_image': get_64_contents(answer.get('real_path')),
            })

        return Response(json_body=response)
