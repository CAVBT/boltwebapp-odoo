from odoo import http
import logging

_logger = logging.getLogger(__name__)

class RouteLogger(http.Controller):
    @http.route('/log_routes', auth='public')
    def log_routes(self):
        # Fetch all route data from ir.http model
        routes = http.request.env['ir.http'].sudo()._get_routes()

        # Create a list of routes to log
        route_list = []
        for route in routes:
            route_list.append({
                'route': route[0],
                'controller': route[1].__name__
            })

        # Log the route list
        _logger.info("All registered routes: %s", route_list)

        return "Routes logged successfully!"
