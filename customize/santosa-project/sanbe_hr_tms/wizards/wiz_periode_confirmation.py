from odoo import models, fields, api, _

class RunningConfirmationWizard(models.TransientModel):
    _name = 'running.confirmation.wizard'
    _description = 'Konfirmasi Pembuatan Record Running'

    # Field untuk menampilkan pesan kepada pengguna
    message = fields.Text(
        string='Peringatan', 
        readonly=True
    )
    
    # Field untuk menyimpan nama record yang running (dari record lama)
    running_record_name = fields.Char(readonly=True) 
    vals_json = fields.Text(string="Data Create", required=True)
    # ====================================================================
    # FIELDS BARU (untuk menahan data yang akan di-create)
    # ====================================================================
    # area_id = fields.Many2one('res.territory', string='Area')
    # branch_id = fields.Many2one('res.branch', string='Business Unit')
    # open_periode_from = fields.Date('Opening Periode From')
    # open_periode_to = fields.Date('Opening Periode To')
    
    @api.model
    def action_show_warning(self, existing_record_name, vals_to_create):
        """Metode ini menyiapkan wizard dengan data yang akan di-create."""
        
        # # Buat instance wizard, mengisi fields dengan 'vals_to_create'
        # wizard = self.create({
        #     'running_record_name': existing_record_name,
        #     'message': _('Periode "%s" sedang Running. Lanjutkan untuk membuat periode baru? Catatan: Anda harus menutup periode lama secara manual nanti.') % (existing_record_name),
            
        #     # Transfer data dari vals_to_create
        #     'area_id': vals_to_create.get('area_id'),
        #     'branch_id': vals_to_create.get('branch_id'),
        #     'open_periode_from': vals_to_create.get('open_periode_from'),
        #     'open_periode_to': vals_to_create.get('open_periode_to'),
            
        # })
        import json # Import untuk menangani JSON
        
        # Buat instance wizard, mengisi vals_json dengan data serial
        wizard = self.create({
            'message': _('Periode "%s" sedang Running. Lanjutkan untuk membuat periode baru? Catatan: Anda harus menutup periode lama secara manual nanti.') % (existing_record_name),
            'vals_json': json.dumps(vals_to_create), # Simpan semua data di sini
        })
        
        # Kembalikan action window
        return {
            'name': 'Konfirmasi Pembuatan Record',
            'type': 'ir.actions.act_window',
            'res_model': 'running.confirmation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': wizard.id,
            'views': [(False, 'form')],
        }
        
        # Kembalikan action window
        # return {
        #     'name': 'Konfirmasi Pembuatan Record',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'running.confirmation.wizard',
        #     'view_mode': 'form',
        #     'target': 'new',
        #     'res_id': wizard.id,
        #     'views': [(False, 'form')],
        # }

    # def action_confirm_create(self):
    #     """Metode ini dipanggil saat tombol 'Lanjutkan' ditekan, dan akan melanjutkan CREATE."""
    #     self.ensure_one()
    #     vals = {
    #         'area_id': self.area_id.id,
    #         'branch_id': self.branch_id.id,
    #         'open_periode_from': self.open_periode_from,
    #         'open_periode_to': self.open_periode_to,
    #         'state_process': 'draft',
    #     }
        
    #     new_record = self.env['hr.opening.closing'].create(vals)
        
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'hr.opening.closing',
    #         'view_mode': 'form',
    #         'res_id': new_record.id,
    #         'target': 'current',
    #     }
    
    def action_confirm_create(self):
        """Metode ini dipanggil saat tombol 'Lanjutkan' ditekan, dan akan melanjutkan CREATE."""
        self.ensure_one()
        import json
        vals = json.loads(self.vals_json)
        
        new_record = self.env['hr.opening.closing'].create(vals)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.opening.closing',
            'view_mode': 'form',
            'res_id': new_record.id,
            'target': 'current',
        }