from .common import *  # noqa: F401,F403

DEBUG = True
LOGGING["loggers"]["openmaps_auth"]["level"] = "DEBUG"  # noqa: F405

# Development app links with descriptions for testing
OPENMAPS_AUTH_APP_LINKS = [
    {
        "link": "/",
        "text": "MapEdit",
        "description": "Web-based mapping application that allows users to contribute and maintain vector data all over the world using high-resolution imagery.",
    },
    {
        "link": "/josm/",
        "text": "JOSM",
        "description": "Java OpenStreetMap Editor is a desktop application for editing OpenStreetMap.",
    },
    {
        "link": "/geoserver/",
        "text": "GeoServer",
        "description": "GeoServer is an open source server for sharing geospatial data.",
    },
    {
        "link": "/hootenanny/",
        "text": "Hootenanny",
        "description": "Hootenanny is a web-based application for editing OpenStreetMap data.",
    },
    {
        "link": "/certs/",
        "text": "Certificates",
        "description": "Manage your client certificates.",
    },
    {"link": "/exports/", "text": "Export Tool", "description": "Tools for exporting."},
    {
        "link": "/overpass/",
        "text": "Overpass Turbo",
        "description": "Overpass Turbo is a web-based application for querying OpenStreetMap data.",
    },
]
