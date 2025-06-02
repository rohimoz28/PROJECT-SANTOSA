/** @odoo-module */

import { calendarView } from '@web/views/calendar/calendar_view';
import { registry } from '@web/core/registry';
import { CalendarController } from '@web/views/calendar/calendar_controller';

export class PublicHolidayCalendarController extends CalendarController {
    setup() {
        super.setup();
    }

    newPublicHoliday() {
        const context = {};
        if (this.employeeId) {
            context["default_employee_id"] = this.employeeId;
        }
        this.displayDialog(FormViewDialog, {
            resModel: "resource.calendar.leaves",
            title: _t("New Time Off"),
            viewId: this.model.formViewId,
            onRecordSaved: () => {
                this.model.load();
                //this.env.timeOffBus.trigger("update_dashboard");
            },
            context: context,
        });
    }

}
PublicHolidayCalendarController.components = {
    ...TimeOffCalendarController.components,
    Dropdown,
    DropdownItem,
    FilterPanel: TimeOffCalendarFilterPanel,
};

PublicHolidayCalendarController.template = "hr_holidays.CalendarController";
const PublicHolidayCalendarView = {
    ...calendarView,
//    Renderer: ServiceTicketRenderer,
    Controller: PublicHolidayCalendarController,
//    Model: ServiceTicketCalendarModel,
}

registry.category('views').add('publicholiday_callendar', PublicHolidayCalendarView);

