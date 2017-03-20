## -*- coding: utf-8 -*-

<%inherit file="ifmo_xblock_base"/>

<%block name="block_body">

    <section class="ifmo-xblock-student">

        ${self.task_template()}
        ${self.upload_template()}
        ${self.annotation_template()}

        <div class="ifmo-xblock-content problem">
            Подождите, задание загружается...
        </div>

    </section>

</%block>

<%block name="task_template">
    <script type="text/template" class="ifmo-xblock-template-base">
        <%doc>
            Template parameter:
                {
                    allow_submissions,
                    meta: {
                        name
                    },
                    message: {
                        text,
                        type
                    },
                    task_status,
                    pregenerated,
                    student_state: {
                        score: {
                            string
                        }
                    }
                }
        </%doc>
        <h2 class="problem-header"><%text><%= meta.name %></%text></h2>
        <div class="problem-progress"><%text><%= student_state.score.string %></%text></div>
        <div class="problem-status">${ self.status() }</div>
        <div class="problem-message">${ self.message() }</div>
        <div class="problem-text">${ self.task_text() }</div>
        % if not student_state['is_studio']:
            <div class="problem-controllers">${self.controllers_box()}</div>
        % endif
    </script>
</%block>

<%block name="status">
    <%text>
        <% if (task_status == 'QUEUED') { %>
            <div class="ifmo-xblock-message ifmo-xblock-message-info">
                Ваше решение поставлено в очередь на проверку.
            </div>
        <% } %>

        <% if (task_status == 'GENERATING') { %>
            <div class="ifmo-xblock-message ifmo-xblock-message-info">
                Пожалуйста, подождите, пока генерируется ваш персональный вариант задания.
            </div>
        <% } %>
    </%text>
</%block>

<%block name="message">
    <%text>
        <% if (typeof message != 'undefined' && message.text != '' && task_status != 'GENERATING') { %>
        <div class="ifmo-xblock-message ifmo-xblock-message-<%= message.type %>"><%= message.text %></div>
        <% } %>
    </%text>
</%block>

<%block name="task_text">
    <%text><% if (need_show_interface) { %></%text>
        ${meta['text']}
    <%text><% } %></%text>


    <%text>
        <% if (task_status == 'IDLE' && latest_check != null) { %>
            <%
                // should we "earned_score = student_state.score.max.earned"?
                earned_score = latest_check.score.points_earned / latest_check.score.points_possible * student_state.score.max;
                max_score = student_state.score.max;
            %>
            <div class="ifmo-xblock-message ifmo-xblock-message-info">
                <p style="margin-bottom: 0;">Результат последней проверки: <b><%= earned_score %> / <%= max_score %></b> баллов</p>
                     <!--
                     <p>
                         <img src="<%= latest_check.report_storage %><%= latest_check.report_file %>"/>
                     </p>
                     -->
            </div>
        <% } %>
    </%text>

</%block>

<%block name="controllers_box">
    <%text>
        <% if (allow_submissions) { %>

            <% if (need_show_interface) { %>

                <% if (task_status == 'IDLE') { %>
                    <div class="controllers">
                        <div class="upload_container"></div>
                    </div>
                <% } %>

            <% } %>

        <% } else { %>
            <div class="ifmo-xblock-message ifmo-xblock-message-info">
                Решения больше не принимаются.
            </div>
        <% } %>
    </%text>
</%block>

<%block name="upload_template">
    <script type="text/template" class="imagemagick-template-upload-input">
        <div class="button upload_input">
            <span>Выберите файл</span>
            <input class="file_upload" type="file" name="submission"/>
        </div>
    </script>

    <script type="text/template" class="imagemagick-template-upload-selected">
        <button class="button upload_another">Выбрать другой файл</button>
        <button class="button button-highlighted upload_do" data-in-progress="Идёт отправка...">Отправить <%text><%= filename %></%text></button>
    </script>
</%block>

<%block name="annotation_template"><%text>
<script type="text/template" class="imagemagick-template-annotation">
<%
    try {
        annotation_details = JSON.parse(annotation.reason);
    } catch(err) {
        annotation_details = {feedback: 'Submission has annotation, but error occurred while parsing it.'};
        annotation = {annotation_type: 'annotation parse error'};
        console.error(err);
    }
    console.log(annotation_details);
%>
    <style>
        table.annotation td {text-align: left;}
        table.annotation pre {margin: 0; padding: 0; font-size: 0.8em;}
    </style>
    <table class="annotation vertical">
        <tr><th>Report Image</th><td><%= annotation_details.report_file %></td></tr>
        <tr><th>Output</th><td><pre><%= annotation_details.output %></pre></td></tr>
        <tr><th>Error Output</th><td><pre><%= annotation_details.err_output %></pre></td></tr>
    </table>
</script>
</%text></%block>