from odoo import api, fields, models

class Payments(models.Model):
    _name = 'payments.payment'
    _description = 'Payments'
    _inherit = 'mail.thread'
    _rec_name = 'reference'

    reference = fields.Char( string='Payment Reference',default="New")
    transaction_id = fields.Char(string='Transaction ID', required=True)
    cardholder_name = fields.Char(string='Cardholder Name', required=True)
    payment_method = fields.Selection([
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ], string='Payment Method', required=True)

    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], string='Payment Status', default='pending')

    annotation = fields.Text(string='Annotation')
    contact = fields.Many2one('res.partner', string='User', required=True)
    subtotal = fields.Float(string='Subtotal', required=True)
    total = fields.Float(string='Total', required=True)
    booking = fields.Many2one('booking.bookings', string='Booking')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals.get('reference') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('cavbt.payment')
        return super().create(vals_list)

    @api.depends('subtotal')
    def _compute_total(self):
        for record in self:
            record.total = record.subtotal * 1.1  # Example: 10% tax, adjust logic as needed

    _sql_constraints = [
        ('check_total', 'CHECK(total >= subtotal)', 'The total amount must be greater than or equal to the subtotal.')
    ]
