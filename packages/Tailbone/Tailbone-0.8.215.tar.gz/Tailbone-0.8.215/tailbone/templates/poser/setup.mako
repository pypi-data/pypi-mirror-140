## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Poser Setup</%def>

<%def name="page_content()">
  <br />

  <p class="block">
    Before you can use Poser features, ${app_title} must create the
    file structure for it.
  </p>

  <p class="block">
    A new folder will be created at this location:&nbsp; &nbsp;
    <span class="is-family-monospace has-text-weight-bold">
      ${poser_dir}
    </span>
  </p>

  <p class="block">
    Once set up, ${app_title} can generate code for certain features,
    in the Poser folder.&nbsp; You can then access these features from
    within ${app_title}.
  </p>

  <p class="block">
    You are free to edit most files in the Poser folder as well.&nbsp;
    When you do so ${app_title} should pick up on the changes with no
    need for app restart.
  </p>

  <p class="block">
    Proceed?
  </p>

  ${h.form(request.current_route_url(), **{'@submit': 'setupSubmitting = true'})}
  ${h.csrf_token(request)}
  <b-button type="is-primary"
            native-type="submit"
            :disabled="setupSubmitting">
    {{ setupSubmitting ? "Working, please wait..." : "Go for it!" }}
  </b-button>
  ${h.end_form()}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.setupSubmitting = false

  </script>
</%def>


${parent.body()}
