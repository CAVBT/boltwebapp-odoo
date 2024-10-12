from odoo import api, fields, models

class Bookings(models.Model):
    _name = 'booking.bookings'
    _description = 'Bookings from website'
    _inherit = 'mail.thread'
    _rec_name = 'reference'

    reference =fields.Char(string='Booking Record Locator', default="New")
    contact = fields.Many2one('res.partner', string='Customer', required=True,
                              domain=[('employee', '=', False)])
    employee = fields.Many2one('hr.employee',
                               string='Employee'
                               )
    destinations = fields.Many2many('destination.destination', string='Destinations')
    payment = fields.Many2one("payments.payment", string='Payment')
    number_of_children = fields.Integer(string='Children')
    number_of_adults = fields.Integer(string='Adults')
    booking_date = fields.Date(string='Booking Date')
    booking_status = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('complete', 'Complete')
    ], string='Booking Status', default='pending')
    booking_time = fields.Char(string='Time')
    subtotal = fields.Float(string='Subtotal')
    total =fields.Float(string='Total')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals.get('reference') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('cavbt.booking')
        return super().create(vals_list)