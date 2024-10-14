import json
import os
import requests
from odoo import api, fields, models
from odoo.exceptions import UserError


class Payments(models.Model):
    _name = 'payments.payment'
    _description = 'Payments'
    _inherit = 'mail.thread'
    _rec_name = 'reference'

    reference = fields.Char(string='Payment Reference', default="New")
    transaction_id = fields.Char(string='Transaction ID', required=True)
    cardholder_name = fields.Char(string='Cardholder Name', required=True)
    payment_method = fields.Selection([
        ('credit_card', 'Credit Card'),
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
    tax = fields.Float(string='Tax', required=True)
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

    def create_transaction(self, payment_data):
        """
        Process the payment via Authorize.Net by making a POST request
        """
        api_login_id = os.getenv('AUTH_NET_API_LOGIN_ID')
        transaction_key = os.getenv('AUTH_NET_TRANSACTION_KEY')

        # Create the payload for the API request
        payload = {
            "createTransactionRequest": {
                "merchantAuthentication": {
                    "name": api_login_id,
                    "transactionKey": transaction_key
                },
                "transactionRequest": {
                    "transactionType": "authCaptureTransaction",
                    "amount": payment_data['total'],
                    "payment": {
                        "creditCard": {
                            "cardNumber": payment_data['cardNumber'],
                            "expirationDate": payment_data['cardExpiration'],
                            # "cardCode": payment_data['cardCVC']
                        }
                    }
                }
            }
        }

        # Define the URL for the sandbox environment
        url = "https://apitest.authorize.net/xml/v1/request.api"

        # Send the POST request
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)

        # Clean the BOM from the response, if present
        response_text = response.content.decode('utf-8-sig')  # Removes the BOM

        # Parse the response as JSON
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError:
            raise UserError("Error parsing JSON response from Authorize.Net.")

        if response_data['messages']['resultCode'] == "Ok":
            if response_data['transactionResponse']['responseCode'] == "1":
                return response_data['transactionResponse']['transId']
            else:
                raise UserError(
                    "Transaction failed: " + response_data['transactionResponse']['errors']['error'][0]['errorText'])
        else:
            raise UserError("Payment error: " + response_data['messages']['message'][0]['text'])

    _sql_constraints = [
        ('check_total', 'CHECK(total >= subtotal)', 'The total amount must be greater than or equal to the subtotal.')
    ]
