function ImageMagickXBlockStudentView(runtime, element)
{
    ImageMagickXBlockStudentView.superclass.constructor.apply(this, [runtime, element]);

    var self = this;

    self.urls = {
        upload_logic: runtime.handlerUrl(element, 'upload_submission'),
        get_user_data: runtime.handlerUrl(element, 'get_user_data'),
        download_image: runtime.handlerUrl(element, 'download_image')
    };

    self.render = function(context)
    {
        var xblock = $(self.element).find('.ifmo-xblock-student');
        var template_content = self.template.main(context);
        xblock.find('.ifmo-xblock-content').html(template_content);

        if (context.allow_submissions) {
            xblock.find('.upload_container').html(self.template.upload_input());
            xblock.find(".file_upload").fileupload(self.upload_logic);
        }

        if (context.task_status != 'IDLE') {
            setTimeout(function(){
                $.post(self.urls.get_user_data, '{}', function(data) {
                    self.render(data);
                }).fail(function(){
                    console.log('error');
                })
            }, 5000);
        }
    };

    self.init_xblock = function($, _)
    {
        ImageMagickXBlockStudentView.superclass.init_xblock.apply(self, [$, _]);

        var xblock = $(element).find('.ifmo-xblock-base');
        var context = xblock.data('context');

        var template = _.partial(self.get_template, element);
        self.add_templates(self, {
            main: template('script.ifmo-xblock-template-base'),
            upload_input: template("script.imagemagick-template-upload-input"),
            upload_selected: template("script.imagemagick-template-upload-selected"),
            annotation: template("script.imagemagick-template-annotation")
        });

        self.render(context);
    };

    self.upload_logic = {
        url: self.urls.upload_logic,
        add: function (e, data) {
            var xblock = $(self.element).find('.ifmo-xblock-student');
            xblock.find('.upload_container').html(self.template.upload_selected({
                'filename': data.files[0].name
            }));
            xblock.find(".upload_another").on('click', function () {
                xblock.find('.upload_container').html(self.template.upload_input());
                xblock.find(".file_upload").fileupload(self.upload_logic);
            });
            xblock.find(".upload_do").on('click', function () {
                xblock.find(".upload_do").text("Uploading...");
                self.helpers.disable_controllers(self.element);
                data.submit();
            });
        },
        progressall: function (e, data) {
            var xblock = $(self.element).find('.ifmo-xblock-student');
            var percent = parseInt(data.loaded / data.total * 100, 10);
            xblock.find(".upload_do").text("Uploading... " + percent + "%");
        },
        start: function() {
            self.helpers.disable_controllers(self.element);
        },
        done: function (e, data) {
            self.render(data.result);
        },
        fail: function() {
            // Эмулируем сброс файла, потому что нам не из чего перерендерить страницу
            $(self.element).find("button.button.upload_another").click();
            alert('При загрузке архива с решением произошла ошибка');
        },
        always: function() {
            self.helpers.enable_controllers(self.element);
        }
    };

    self.add_hooks(self, {
        render_student_answer: function(data) {

            // Поскольку у нас нет доступа к идентификатору решения здесь,
            // нам нужен дополнитеьный хендлер, получающий файл по его SHA,
            // минуя обращение к submissions.api.
            var student_file_id = data.sha1;
            var instructor_file_id = /([^\/]*)$/.exec(data.instructor_real_path)[0];

            var student_url = self.urls.download_image + '/student?' + student_file_id;
            var instructor_url = self.urls.download_image + '/instructor_prev?' + instructor_file_id;

            return '<p>' +
                '<a href="' + student_url + '" class="button">Скачать решение ' + data.filename + '</a> ' +
                '<a href="' + instructor_url + '" class="button">Скачать проверяющий архив</a>' +
                '</p>';
        },
        render_annotation: function(data) {
            return self.template.annotation(data);
        }
    });

    self.init_xblock_ready($, _);
}

xblock_extend(ImageMagickXBlockStudentView, IfmoXBlockStudentView);
