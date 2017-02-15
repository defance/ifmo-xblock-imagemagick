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
            <label for="input_${id}_allowable_fuzz" class="label setting-label">Возможное расхождение (fuzz)</label>
            <input id="input_${id}_allowable_fuzz" class="input setting-input" type="text" name="allowable_fuzz" value="<%text><%= allowable_fuzz %></%text>" />
        </div>
        <span class="tip setting-help">Максимальное допустимое отличие от исходного изображения в процентах. По умолчанию 80%.</span>
    </li>

</%block>