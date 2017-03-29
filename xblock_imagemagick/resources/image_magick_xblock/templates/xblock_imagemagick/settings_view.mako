## -*- coding: utf-8 -*-

<%inherit file="ifmo_xblock_base"/>

<%block name="extra_settings">

    ${parent.extra_settings()}

    <li class="field comp-setting-entry">
        <div class="wrapper-comp-setting">
            <label for="input_${id}_instructor_image" class="label setting-label">Эталонное изображение</label>
            <div class="ifmo-xblock-imagemagick-studio-image-container">
                    <input id="input_${id}_instructor_image" class="setting-input ifmo-xblock-imagemagick-studio-image-file" type="file" name="instructor_image"/>
                    <div class="ifmo-xblock-imagemagick-studio-image-selected" data-status="empty">Изображение не выбрано</div>
            </div>
            <input type="button" class="upload_instructor_image ifmo-xblock-imagemagick-studio-image-upload" value="Отправить">
        </div>
        <span class="tip setting-help"></span>
    </li>

    <li class="field comp-setting-entry">
        <div class="wrapper-comp-setting">
            <label for="input_${id}_cut_off" class="label setting-label">Порог непохожести</label>
            <input id="input_${id}_cut_off" class="input setting-input" type="text" name="cut_off" value="<%text><%= cut_off %></%text>" />
        </div>
        <span class="tip setting-help">Порог различия в процентах всех пикселей, после которого изображения будут считаться непохожими. По-умолчанию 0%.</span>
    </li>

    <li class="field comp-setting-entry">
        <div class="wrapper-comp-setting">
            <label for="input_${id}_allowable_fuzz" class="label setting-label">Возможное расхождение (fuzz)</label>
            <input id="input_${id}_allowable_fuzz" class="input setting-input" type="text" name="allowable_fuzz" value="<%text><%= allowable_fuzz %></%text>" />
        </div>
        <span class="tip setting-help">Максимальное допустимое отличие пикселей пользовательского изображения от эталона в процентах. При 0 -- все пиксели должны быть идентичны. При 100 -- все пиксели считаются одинаковыми. По-умолчанию 80%.</span>
    </li>

    <li class="field comp-setting-entry">
        <div class="wrapper-comp-setting">
            <label for="input_${id}_extra_cmd_settings" class="label setting-label">Дополнительные настройки</label>
            <input id="input_${id}_extra_cmd_settings" class="input setting-input" type="text" name="extra_cmd_settings" value="<%text><%= _.escape(extra_cmd_settings) %></%text>" />
        </div>
        <span class="tip setting-help">Дополнительные настройки в формате json. Допустимые поля объекта: <i>quality_fuzz</i>, <i>report_size</i>.</span>
    </li>

</%block>