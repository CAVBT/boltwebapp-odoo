from odoo import fields, models

class Destinations(models.Model):
    _name = 'destination.destination'
    _description = 'Destinations'
    _inherit = 'mail.thread'
    _rec_name = 'name'

    name = fields.Char(string='Destination')
    dest_description = fields.Text(string='Description')
    dest_url = fields.Char(string='URL')
    price = fields.Float(string='Price')
    bookings = fields.Many2many('booking.bookings', string='Bookings')
