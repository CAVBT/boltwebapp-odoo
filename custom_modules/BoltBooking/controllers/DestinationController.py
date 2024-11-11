from odoo import http
from odoo.http import request
import json

class DestinationController(http.Controller):

    @http.route('/api/get_destinations', auth='public', type='http', methods=['GET'], csrf=False)
    def get_destinations(self, **kwargs):

        if request.httprequest.method == 'OPTIONS':
            headers = [
                ('Access-Control-Allow-Origin', 'https://dev.catchavibes.com'),
                ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type'),
            ]
            return request.make_response('OK', headers=headers)

        headers = [('Access-Control-Allow-Origin', 'https://dev.catchavibes.com')]
        # Fetch all destinations from the model
        destinations = request.env['destination.destination'].sudo().search([])

        # Convert the data into a format that can be returned as JSON
        destinations_list = []
        for destination in destinations:
            destinations_list.append({
                'id': destination.id,
                'name': destination.name,
                'dest_description': destination.dest_description,
                'dest_url': destination.dest_url,
                'price': destination.price
            })

        # Convert the result to JSON
        response_data = json.dumps({
            'status': 'success',
            'destinations': destinations_list,
        })

        # Create the response with CORS headers
        response = request.make_response(response_data)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = 'https://dev.catchavibes.com'  # Allow requests from any origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'  # Allow these methods
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # Allow these headers

        return response
