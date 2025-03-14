/** @odoo-module **/

import { session } from "@web/session";
import { url } from "@web/core/utils/urls";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { useService, useBus } from "@web/core/utils/hooks";
export class AppsMenu extends Dropdown {
    setup() {
    	super.setup(... arguments);
    	if (this.env.services.company.currentCompany.has_background_image) {
            this.backgroundImageUrl = url('/web/image', {
                model: 'res.company',
                field: 'background_image',
                id: this.env.services.company.currentCompany.id,
            });
    	} else {
    		this.backgroundImageUrl = '/muk_web_theme/static/img/background.png';
    	}
    	useBus(this.env.bus,"ACTION_MANAGER:UI-UPDATED",ev => this.close());
    }
}

Object.assign(AppsMenu, {
    template: 'muk_web_theme.AppsMenu',
});