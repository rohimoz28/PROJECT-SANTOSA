from odoo import models, fields, api
from datetime import date, datetime, timedelta

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def _compute_message_needaction(self):
        res = dict.fromkeys(self.ids, 0)
        if self.ids:
            partner_id = self.env.user.partner_id.id
            self._cr.execute("""SELECT msg.res_id 
                                FROM mail_message msg
                                RIGHT JOIN mail_notification rel
                                ON rel.mail_message_id = msg.id 
                                AND rel.res_partner_id = %s 
                                AND (rel.is_read = %s OR rel.is_read IS NULL)
                                WHERE msg.model = %s 
                                AND msg.res_id IN %s 
                                AND msg.message_type != 'user_notification'""",
                             (partner_id, False, self._name, tuple(self.ids),))
            for result in self._cr.fetchall():
                res[result[0]] += 1

        for record in self:
            record.message_needaction_counter = res.get(record._origin.id, 0)
            record.message_needaction = bool(record.message_needaction_counter)