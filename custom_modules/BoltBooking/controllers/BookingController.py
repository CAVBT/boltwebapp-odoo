from datetime import datetime
from odoo import http
from odoo.http import request
import json

class BookingController(http.Controller):

    @http.route('/api/booking', type='json', auth='public', methods=['POST'], csrf=False)
    def create_booking(self, **post):
        data = json.loads(request.httprequest.data)

        # Extract booking data from the request body
        email = data.get('email')
        total = data.get('total')
        number_of_adults = data.get('numberOfAdults')
        number_of_children = data.get('numberOfChildren')
        booking_date = datetime.strptime(data.get('bookingDate'), "%Y-%m-%d").date()
        booking_time = data.get('bookingTime')
        payment_reference = data.get('paymentLocator')
        destination = data.get('destination')

        # Extract only IDs from the destination list
        if isinstance(destination, list):
            destination_ids = [d['id'] for d in destination if 'id' in d]
        else:
            destination_ids = []  # If destination is empty or not a list

        # Locate or create contact
        contact = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if not contact:
            return {'status': 'error', 'message': 'Contact not found'}

        # Locate payment
        payment = request.env['payments.payment'].sudo().search([('transaction_id', '=', payment_reference)], limit=1)

        # Create a new booking record in Odoo
        new_booking = request.env['booking.bookings'].sudo().create({
            'contact': contact.id,
            'total': total,
            'number_of_adults': number_of_adults,
            'number_of_children': number_of_children,
            'booking_date': booking_date,
            'booking_time': booking_time,
            'booking_status': 'pending',
            'payment': payment.id,
            'destinations': [(6, 0, destination_ids)],  # Proper Many2Many format
        })


        if not new_booking:
            return {'status': 'error', 'message': 'Booking was not created'}
        else:
            return {'status': 'success', 'bookingId': new_booking.reference}
