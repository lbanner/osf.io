import json
import uuid
from hashlib import md5
from urllib import urlencode

import requests

from website import settings


class PiwikException(Exception):
    pass

def create_user(user):
    """ Given an OSF user, creates a Piwik user.
    """

    login = 'osf.' + user._id
    pw = str(uuid.uuid4())[:8]

    user.piwik_token = md5(login + md5(pw).hexdigest()).hexdigest()

    response = requests.post(
        url=settings.PIWIK_HOST,
        data={
            'module': 'API',
            'method': 'UsersManager.addUser',
            'format': 'json',
            'token_auth': settings.PIWIK_ADMIN_TOKEN,
            'userLogin': login,
            'password': pw,
            'email': user._id + '@osf.io',
            'alias': "OSF User: " + user._id,
        }
    )

    if json.loads(response.content)['result'] == 'error':
        raise PiwikException('Piwik user not updated')

    user.save()

def update_node(node, updated_fields=None):
    """ Given a node, provisions a Piwik site if necessary and sets
    contributors to "view".

    :param node:            Instance of ``website.models.Node`` to update or
                            provision
    :param updated_fields:  Iterator containing the names of fields that have
                            been updated on the ``node``
    """
    # If no site has been created for the node, create one.
    if not node.piwik_site_id:
        return _provision_node(node)

    # If contributors have changed
    if updated_fields is None or 'contributors' in updated_fields:
        # Hit Piwik API to get a list of users with view access
        users = _users_with_view_access(node)

        # figure out what's changed
        removed_users = users - set(('osf.' + x._id for x in node.contributors))
        added_users = set(('osf.' + x._id for x in node.contributors)) - users

        # Deal with changes appropriately
        if removed_users:
            _change_view_access(removed_users, node, 'noaccess')

        if added_users:
            _change_view_access(added_users, node, 'view')

    # If public/private setting has changed
    if updated_fields is None or 'is_public' in updated_fields:
        _change_view_access(
            users=('anonymous',),
            node=node,
            access='view' if node.is_public else 'noaccess'
        )



def _users_with_view_access(node):
    """ Given a node, calls Piwik and returns the set of users with view access.
    Filters out "anonymous".
    """
    response = requests.post(
        url=settings.PIWIK_HOST,
        data={
            'module': 'API',
            'method': 'UsersManager.getUsersWithSiteAccess',
            'format': 'json',
            'token_auth': settings.PIWIK_ADMIN_TOKEN,
            'idSite': node.piwik_site_id,
            'access': 'view',
        }
    )

    try:
        # Could also raise ValueError
        rv = json.loads(response.content)
        return set((x.get('login') for x in rv if x.get('login') != 'anonymous'))
    except (ValueError, AttributeError):
        raise PiwikException('Failed to retrieve users for {}'.format(node._id))



def _change_view_access(users, node, access):
    """ Grants view access for a Piwik site to a Piwik user

    :param users:   Iterable of (string) user IDs
    :param node:
    """
    response = requests.post(
        url=settings.PIWIK_HOST,
        data=dict(
            module='API',
            method='API.getBulkRequest',
            format='json',
            token_auth=settings.PIWIK_ADMIN_TOKEN,
            # The next line unpacks a dictionary, thereby adding the elements
            #   as key/value pairs to the dict being built. They can't just be
            #   passed as a list because Piwik uses PHP-style URL params.
            **{ # OMG... WTF?
                'urls[{}]'.format(idx): url # PHP-style params :(
                for idx, url in enumerate(
                    (   # Innermost comprehension (generator) - iterates once
                        #   for each user passed in, returns a URL query string.
                        urlencode({
                            'method': 'UsersManager.setUserAccess',
                            'userLogin': u,
                            'access': access,
                            'idSites': node.piwik_site_id
                        }) for u in users
                    )
                )
            }
        )
    )

    try:
        # Could also raise ValueError
        rv = json.loads(response.content)
        for x in rv:
            if x.get("result" != "success"): raise ValueError()
    except ValueError:
        raise PiwikException(
            'Failed to update Piwik user permissions for {}'.format(node._id)
        )


def _provision_node(node):
    response = requests.post(
            settings.PIWIK_HOST,
            data={
                'module': 'API',
                'token_auth': settings.PIWIK_ADMIN_TOKEN,
                'format': 'json',
                'method': 'SitesManager.addSite',
                'siteName': 'Node: ' + node._id,
                'urls': [
                    settings.CANONICAL_DOMAIN + node.url,
                    settings.SHORT_DOMAIN + node.url,
                ],
            }
        )

    try:
        node.piwik_site_id = json.loads(response.content)['value']
        node.save()
    except ValueError:
        raise PiwikException('Piwik site creation failed for ' + node._id)

    # contributors lists might be empty, due to a bug.
    if node.contributors:
        users = ['osf.' + user._id for user in node.contributors]
        if node.is_public:
            users.append('anonymous')
        _change_view_access(
            # contibutors lists might contain `None` due to bug
            users,
            node,
            'view'
        )