function ImageMagickXBlockSettingsView(runtime, element)
{
    ImageMagickXBlockSettingsView.superclass.constructor.apply(this, [runtime, element]);

    var self = this;

    self.upload_logic = {
        url: self.runtime.handlerUrl(self.element, 'upload_instructor_image'),
        add: function (e, data) {
            var selected = self.element.find("div.ifmo-xblock-imagemagick-studio-image-selected");
            selected.html('Выбран ' + data.files[0].name);
            selected.data('status', 'selected');
            selected.data('status-name', data.files[0].name);
            self.element.find("input.ifmo-xblock-imagemagick-studio-image-upload").off('click').on('click', function () {
                self.element.find("input.ifmo-xblock-imagemagick-studio-image-upload").val('Идёт загрузка...');
                data.submit();
            });
        },
        start: function() {
            self.element.find('input').attr('disabled', 'disabled');
        },
        done: function (e, data) {
            alert('Эталонное изображение успешно загружено');
            var selected = self.element.find("div.ifmo-xblock-imagemagick-studio-image-selected");
            selected.data('status', 'uploaded');
            selected.html('Загружен ' + selected.data('status-name'));
        },
        fail: function() {
            alert('При загрузке эталонного изображения произошла ошибка');
        },
        always: function() {
            self.element.find("input.ifmo-xblock-imagemagick-studio-image-upload").val('Загрузить');
            self.element.find('input').removeAttr('disabled');
        }
    };

    self.validate = function()
    {
        // Проверим статус изображения: загружено, выбрано или пуст
        var selected = $(self.element).find('.ifmo-xblock-imagemagick-studio-image-selected');
        var stop_saving_confirm = "";

        if(selected.data('status') == 'empty') {
            stop_saving_confirm = 'Эталонное изображение не было выбрано.';
        } else if(selected.data('status') == 'selected') {
            stop_saving_confirm = 'Эталонное изображение выбрано, но не загружено.';
        }

        // Подтвердить действие
        if(stop_saving_confirm != "") {
            if (!confirm(stop_saving_confirm + " Продолжить сохранение?")) {
                return {
                    result: false,
                    message: stop_saving_confirm,
                    title: 'ImageMagick XBlock'
                }
            }
        }
        return {
            result: true
        }

    };

    self.save = function()
    {
        ImageMagickXBlockSettingsView.superclass.save.apply(self);
    };

    self.init_xblock = function($, _)
    {
        ImageMagickXBlockSettingsView.superclass.init_xblock.apply(self, [$, _]);

        var xblock = $(self.element).find('.ifmo-xblock-editor');
        var data = xblock.data('metadata');

        if (data.instructor_image != undefined && data.instructor_image.filename != undefined) {
            var selected = xblock.find('div.ifmo-xblock-imagemagick-studio-image-selected');
            selected.html('Загружен ' + data.instructor_image.filename);
            selected.data('status', 'uploaded');
        }

        xblock.find('input.ifmo-xblock-imagemagick-studio-image-file').fileupload(self.upload_logic);

    };

    self.init_xblock_ready($, _);

    return {
        save: self.save
    };

}

xblock_extend(ImageMagickXBlockSettingsView, IfmoXBlockSettingsView);
