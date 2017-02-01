function ImageMagickXBlockStudentView(runtime, element)
{
    ImageMagickXBlockStudentView.superclass.constructor.apply(this, [runtime, element]);

    var self = this;

    self.init_xblock_ready($, _);
}

xblock_extend(ImageMagickXBlockStudentView, IfmoXBlockStudentView);
