from odoo import http
from odoo.http import request
import json


class MyApiController(http.Controller):

    @http.route('/api/payment', auth='public', type='json', methods=['POST'], csrf=False)
    def create_appointment(self, **post):
        data = json.loads(request.httprequest.data)

        transaction_id = data.get('transactionId')
        cardholder_name = data.get('cardholderName')
        payment_method = data.get('paymentMethod')
        annotation = data.get('annotation')
        email = data.get('email')
        subtotal = data.get('subtotal')
        total = data.get('total')


        # Ensure all necessary data is present
        if not transaction_id or not cardholder_name  or not email or not subtotal or not total:
            return {
                'status': 'error',
                'message': 'Missing required fields',
            }

        contact = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)

        # Locate or create contact
        if not contact:
            contact = request.env['res.partner'].sudo().create({
                'email': email,
                'name': cardholder_name
            })


        # Create the record
        new_payment = request.env['payments.payment'].sudo().create({
            'transaction_id': transaction_id,
            'cardholder_name': cardholder_name,
            'payment_method': payment_method,
            'payment_status': 'pending',
            'annotation': annotation,
            'contact': contact.id,
            'subtotal': subtotal,
            'total': total
        })

        if new_payment:
            return {
                'status': 'success',
                'paymentId': transaction_id,
                'message': 'Payment created successfully',
            }
