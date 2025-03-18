/** @odoo-module **/

/*****************************************************************************************************************/
/*  Author   => Albertus Restiyanto Pramayudha                                                                   */
/*  email    => xabre0010@gmail.com                                                                              */
/*  linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/                             */
/*  youtube  => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA                                         */
/*****************************************************************************************************************/

import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { onMounted, Component, useRef } from "@odoo/owl";
import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { WebClient } from "@web/webclient/webclient";
const actionRegistry = registry.category("actions");
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

var employee_data = [];
var emp_form_id;
var parent_id;
var oc;

export class OrgChartEmployee extends Component{
    static template = 'sanbe_org_chart.org_chart_template';
    static props = ["*"];
    setup() {
        this.dialogService = useService("dialog");
        this.action = useService("action");
        this.effect = useService("effect");
        this.user = useService("user")
        this._rpc = useService("rpc");
        this.log_in_out = useRef("log_in_out")
        this.orm = useService("orm");
        this.employee_data = [];
        this.emp_form_id = false;
        onWillStart(async () => {
            var self = this;
            const dataemp = await this.orm.call('org.chart.employee', 'get_emp_form_id', []) ;
            if(dataemp){
                this.emp_form_id = dataemp.form_id;
                if (direction === undefined){
                    direction = dataemp.direction;
                }

                verticalLevel = dataemp.vertical_level;
                self.verticalLevel = verticalLevel;
            }
            this.employee_data = await this.orm.call('org.chart.employee', 'get_employee_data', []) ;

        });
        onMounted(() => {
            this.title = 'Dashboard'
            this.show_org_chart();
             $( ".o_control_panel" ).addClass( "o_hidden" );
        });
    }
    reload() {
      window.location.href = this.href;
    }
    reload_org_chart(event) {
        location.reload();
    }
    switch_org_chart(event) {
      direction = get_direction(direction);
      this.reload_org_chart();
    }
    switch_org_chart(event) {
      direction = get_direction(direction);
      this.reload_org_chart();
    }
    show_org_chart(event) {
      var self = this;
      if (this.employee_data){
        self.href = window.location.href;
        oc = get_organization_chart(this.employee_data.values, direction, verticalLevel);
        oc.$chart.on('nodedrop.orgchart', function(event, extraParams) {
          var data = {
            "child": extraParams.draggedNode.children('.org_chart_id').text(),
            "last_parent": extraParams.dragZone.children('.org_chart_id').text(),
            "new_parent": extraParams.dropZone.children('.org_chart_id').text()
          };
          parent_id = extraParams.draggedNode.children('.org_chart_id').text();
          $.ajax({
            type: "POST",
            dataType: "json",
            url: "/orgchart/update",
            data: data,
          });
        });
        $('.o_content').addClass('o_hidden');

        if (direction != undefined && direction == 'l2r') {
          $('#org-chart-main').addClass('org-chart-scroll');
        }
        $('.add_node').on("click", function(event) {
            self.add_data(event);
        });
        $('.edit_node').on("click", function(event) {
            self.edit_data(event);
        });
        $('.delete_node').on("click", function(event) {
            self.delete_data(event);
        });

      }

    }
    export_org_chart (event) {
      $('.third-menu-icon').addClass('o_hidden');
      $('#org-chart-main').removeClass('org-chart-scroll');
      $('#chart-container').addClass('org-chart-scroll');
      $('.orgchart').removeClass('orgchartwindowsize');
      var that = oc;
      that.export(that.options.exportFilename, that.options.exportFileextension);
      $('.third-menu-icon').removeClass('o_hidden');
      if (direction == 'l2r') {
        $('#org-chart-main').addClass('org-chart-scroll');
      }
      $('#chart-container').removeClass('org-chart-scroll');
      $('.orgchart').removeClass('orgchartwindowsize');
    }
    add_data(event){
      var self = this;
      event.stopPropagation();
      event.preventDefault();
      this.action.doAction({
          name: _t("Add new Employee"),
          type: 'ir.actions.act_window',
          res_model: 'hr.employee',
          view_mode: 'form',
          view_type: 'form',
          context: {'parent_id': parseInt(event.target.id)},
          views: [[emp_form_id, 'form']],
          target: 'new'
      }, {
            onClose: () => {
                location.reload();
            },
      });
    }
    edit_data(event){
      var self = this;
      event.stopPropagation();
      event.preventDefault();
        this.action.doAction({
          name: _t("Edit Employee"),
          type: 'ir.actions.act_window',
          res_model: 'hr.employee',
          view_mode: 'form',
          view_type: 'form',
          res_id: parseInt(event.target.id),
          views: [[emp_form_id, 'form']],
          target: 'new'
        }, {
            onClose: () => {
                location.reload();
            },
        });
    }
    delete_data(event){
        var self = this;
        this.dialogService.add(ConfirmationDialog, {
            body: _t("Do you Want to Delete this Employee ?"),
            confirm: async () => {
                  console.log('emplloyee id ',event.target.id)
                  await this.orm.call('hr.employee', "unlink", [parseInt(event.target.id)]);
                  location.reload();
            },
            cancel: () => { },
        })
    }
    action_drop(event){
      var self = this;
      self._rpc({
          route: "/orgchart/ondrop",
          params: {
              employee_id: parseInt(parent_id),
          },
      })
      .then(function (result) {
          self.do_action(result);
      });
    }
}
registry.category("actions").add("org_chart_employee", OrgChartEmployee)
