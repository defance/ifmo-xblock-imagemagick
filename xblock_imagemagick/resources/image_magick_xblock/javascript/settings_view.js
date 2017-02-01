function ImageMagickXBlockSettingsView(runtime, element)
{
    ImageMagickXBlockSettingsView.superclass.constructor.apply(this, [runtime, element]);

    var self = this;

    self.save = function()
    {
        ImageMagickXBlockSettingsView.superclass.save.apply(self);
    };

    self.init_xblock_ready($, _);

    return {
        save: self.save
    };

}

xblock_extend(ImageMagickXBlockSettingsView, IfmoXBlockSettingsView);
