{
    "name": "Bolt Booking System",
    "author": "Omega Tech Labs",
    "depends": ["base", "mail", "snailmail", "hr", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/destination_views.xml",
        "views/payments_views.xml",
        "views/booking_views.xml",
        "views/menu.xml"
    ],
    'controllers': [
        'controllers/BookingController.py',
        'controllers/DestinationController.py',
        'controllers/PaymentsController.py',
        'controllers/RouteLogger.py'
    ],
}
