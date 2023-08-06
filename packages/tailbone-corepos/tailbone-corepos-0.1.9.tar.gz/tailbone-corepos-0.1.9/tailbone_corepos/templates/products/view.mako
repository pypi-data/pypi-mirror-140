## -*- coding: utf-8; -*-
<%inherit file="tailbone:templates/products/view.mako" />
<%namespace name="corepos" file="/corepos-util.mako" />

<%def name="object_helpers()">
  ${parent.object_helpers()}
  ${self.render_xref_helper()}
</%def>

<%def name="render_xref_helper()">
  ${corepos.render_xref_helper()}
</%def>

<%def name="render_xref_button()">
  ${corepos.render_xref_button()}
</%def>

<%def name="extra_main_fields(form)">
  ${parent.extra_main_fields(form)}
  ${self.extra_main_fields_corepos(form)}
</%def>

<%def name="extra_main_fields_corepos(form)">
  ${form.render_field_readonly('corepos_id')}
</%def>

${parent.body()}
