## -*- coding: utf-8; -*-
<%inherit file="tailbone:templates/people/view_profile_buefy.mako" />

<%def name="render_customer_panel_buttons(customer)">
  <b-button type="is-primary"
            v-if="customer.view_corepos_url"
            tag="a" :href="customer.view_corepos_url" target="_blank"
            icon-pack="fas"
            icon-left="external-link-alt">
    View in CORE Office
  </b-button>
  ${parent.render_customer_panel_buttons(customer)}
</%def>

<%def name="render_member_panel_buttons(member)">
  <b-button type="is-primary"
            v-if="member.view_corepos_url"
            tag="a" :href="member.view_corepos_url" target="_blank"
            icon-pack="fas"
            icon-left="external-link-alt">
    View in CORE Office
  </b-button>
  ${parent.render_member_panel_buttons(member)}
</%def>


${parent.body()}
