# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import pytz
from odoo.addons.base.models.ir_sequence import  _alter_sequence,_drop_sequences,_create_sequence



class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def write_inisialpt(self):
        mycomp = self._context.get('company_id')
        if mycomp:
            company_id = self.env['res.company'].sudo().browse(int(mycomp))
            print(mycomp)
            return str(company_id.inisial_pt)
        else:
            return ""

    def write_bisnis_unit(self):
        mycomp = self._context.get('bisnis_unit')
        print('bisnis unit ', mycomp)
        #sdadas
        if mycomp:
            company_id = self.env['res.company'].sudo().browse(int(mycomp))
            print(mycomp)
            return str(company_id.inisial_pt)
        else:
            return ""

    def write_year_join(self):
        mycomp = self._context.get('year_join')
        if mycomp:
            company_id = self.env['res.company'].sudo().browse(int(mycomp))
            print(mycomp)
            return str(company_id.inisial_pt)
        else:
            return ""

    def write_month_join(self):
        mycomp = self._context.get('month_join')
        if mycomp:
            company_id = self.env['res.company'].sudo().browse(int(mycomp))
            print(mycomp)
            return str(company_id.inisial_pt)
        else:
            return ""

    def _get_prefix_suffix(self, date=None, date_range=None):
        def _interpolate(s, d):
            return (s % d) if s else ''

        def _interpolation_dict():
            now = range_date = effective_date = datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
            if date or self._context.get('ir_sequence_date'):
                effective_date = fields.Datetime.from_string(date or self._context.get('ir_sequence_date'))
            if date_range or self._context.get('ir_sequence_date_range'):
                range_date = fields.Datetime.from_string(date_range or self._context.get('ir_sequence_date_range'))

            sequences = {
                'id_pt':'%id_pt','bisnis_unit': '%bisnis_unit','year_join': '%year_join','month_join': '%month_join','year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
                'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S'
            }
            res = {}
            for key, format in sequences.items():
                if 'id_pt' in key:
                    res[key] = self.write_inisialpt()
                elif 'bisnis_unit' in key:
                    res[key] = self.write_inisialpt()
                elif 'year_join' in key:
                    res[key] = self.write_inisialpt()
                elif 'month_join' in key:
                    res[key] = self.write_inisialpt()
                else:
                    res[key] = effective_date.strftime(format)
                    res['range_' + key] = range_date.strftime(format)
                    res['current_' + key] = now.strftime(format)

            return res

        self.ensure_one()
        d = _interpolation_dict()
        try:
            interpolated_prefix = _interpolate(self.prefix, d)
            interpolated_suffix = _interpolate(self.suffix, d)
        except ValueError:
            raise UserError(_('Invalid prefix or suffix for sequence %r', self.name))
        return interpolated_prefix, interpolated_suffix
