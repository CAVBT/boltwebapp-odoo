from datetime import datetime
from odoo import http
from odoo.http import request, Response
import json
from odoo.exceptions import UserError

class BookingController(http.Controller):

    @http.route('/api/payment_booking', auth='public', type='json', methods=['POST', 'OPTIONS'], csrf=False)
    def create_payment_booking(self, **post):
        data = json.loads(request.httprequest.data)

        if request.httprequest.method == 'OPTIONS':
            headers = [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type'),
            ]
            return request.make_response('OK', headers=headers)

        headers = [('Access-Control-Allow-Origin', '*')]
        # Extracting payment and booking details
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        phone = data.get('phone')
        cardholder_name = data.get('cardholderName')
        email = data.get('email')
        subtotal = data.get('subtotal')
        total = data.get('total')
        tax = data.get('tax')
        destinations = data.get('destinations', [])

        booking_info = {
            'number_of_adults': data.get('numberOfAdults'),
            'number_of_children': data.get('numberOfChildren'),
            'booking_date': data.get('date'),
            'booking_time': data.get('time')
        }

        # Locate or create contact
        contact = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if not contact:
            contact = request.env['res.partner'].sudo().create({
                'email': email,
                'name': first_name + ' ' + last_name,
                'phone': phone,
            })

        # Process payment via Authorize.Net
        try:
            transaction_id = request.env['payments.payment'].sudo().create_transaction({
                'cardNumber': data.get('cardNumber'),
                'cardExpiration': data.get('cardExpiration'),

                #Commenting as card CVC is not required but may be in future
                # 'cardCVC': data.get('cardCVC'),
                'total': total
            })
        except UserError as e:
            return {
                'status': 'error',
                'message': str(e),
            }

        # Create payment record in Odoo
        new_payment = request.env['payments.payment'].sudo().create({
            'transaction_id': transaction_id,
            'cardholder_name': cardholder_name,
            'payment_method': 'credit_card',
            'payment_status': 'completed',
            'annotation': 'Payment created via BoltBooking frontend application',
            'contact': contact.id,
            'subtotal': subtotal,
            'total': total,
            'tax' : tax
        })

        # Create a new booking record in Odoo
        destination_ids = [d['id'] for d in destinations]
        new_booking = request.env['booking.bookings'].sudo().create({
            'contact': contact.id,
            'total': total,
            'number_of_adults': booking_info['number_of_adults'],
            'number_of_children': booking_info['number_of_children'],
            'booking_date': booking_info['booking_date'],
            'booking_time': booking_info['booking_time'],
            'booking_status': 'pending',
            'payment': new_payment.id,
            'destinations': [(6, 0, destination_ids)],
        })

        if not new_booking:
            return {
                'status': 'error',
                'message': 'Booking was not created',
            }

        # Correct the response format
        return {
            'status': 203,
            'message': new_booking.reference
        }