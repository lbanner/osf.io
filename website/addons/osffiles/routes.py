"""

"""

from framework.routing import Rule, json_renderer
from website.routes import OsfWebRenderer

from . import views


settings_routes = {
    'rules': [],
    'prefix': '/api/v1',
}

web_routes = {

    'rules': [

        Rule(
            [
                '/project/<pid>/osffiles/<fid>/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/',
            ],
            'get',
            views.view_file,
            OsfWebRenderer('../addons/osffiles/templates/osffiles_view_file.mako'),
        ),

        # Download file
        Rule(
            [
                '/project/<pid>/osffiles/<fid>/download/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/download/',
                # Note: Added these old URLs for backwards compatibility with
                # hard-coded links.
                '/project/<pid>/osffiles/download/<fid>/',
                '/project/<pid>/node/<nid>/osffiles/download/<fid>/',
                '/project/<pid>/files/<fid>/',
                '/project/<pid>/node/<nid>/files/<fid>/',
                '/project/<pid>/files/download/<fid>/',
                '/project/<pid>/node/<nid>/files/download/<fid>/',
                '/api/v1/project/<pid>/osffiles/<fid>/',
                '/api/v1/project/<pid>/node/<nid>/osffiles/<fid>/',
                '/api/v1/project/<pid>/files/download/<fid>/',
                '/api/v1/project/<pid>/node/<nid>/files/download/<fid>/',
            ], 'get', views.download_file, json_renderer,
        ),

        # Download file by version
        Rule(
            [
                '/project/<pid>/osffiles/<fid>/version/<vid>/download/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/version/<vid>/download/',
                # Note: Added these old URLs for backwards compatibility with
                # hard-coded links.
                '/project/<pid>/osffiles/download/<fid>/version/<vid>/',
                '/project/<pid>/node/<nid>/osffiles/download/<fid>/version/<vid>/',
                '/project/<pid>/files/<fid>/version/<vid>/',
                '/project/<pid>/node/<nid>/files/<fid>/version/<vid>/',
                '/project/<pid>/files/download/<fid>/version/<vid>/',
                '/project/<pid>/node/<nid>/files/download/<fid>/version/<vid>/',
                '/api/v1/project/<pid>/osffiles/<fid>/version/<vid>/',
                '/api/v1/project/<pid>/node/<nid>/osffiles/<fid>/version/<vid>/',
                '/api/v1/project/<pid>/files/download/<fid>/version/<vid>/',
                '/api/v1/project/<pid>/node/<nid>/files/download/<fid>/version/<vid>/',
            ], 'get', views.download_file_by_version, json_renderer,
        ),

    ]

}

api_routes = {

    'rules': [

        Rule(
            [
                '/project/<pid>/osffiles/hgrid/',
                '/project/<pid>/node/<nid>/osffiles/hgrid/',
                '/project/<pid>/osffiles/hgrid/<path:path>/',
                '/project/<pid>/node/<nid>/osffiles/hgrid/<path:path>/',
            ],
            'get',
            views.get_osffiles_public,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/file_paths/',
                '/project/<pid>/node/<nid>/file_paths/',
            ],
            'get',
            views.list_file_paths,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/osffiles/',
                '/project/<pid>/node/<nid>/osffiles/',
            ],
            'post',
            views.upload_file_public,
            json_renderer,
        ),
        Rule(
            [
                '/project/<pid>/osffiles/<fid>/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/',
            ],
            'delete',
            views.delete_file,
            json_renderer,
        ),

        ### File Render ###
        Rule(
            [
                '/project/<pid>/osffiles/<fid>/version/<vid>/render/',
                '/project/<pid>/node/<nid>/osffiles/<fid>/version/<vid>/render/',
            ],
            'get',
            views.osffiles_get_rendered_file,
            json_renderer,
        ),

    ],

    'prefix': '/api/v1',

}