# -*- coding: utf-8 -*-
import logging
import os
from mako.template import Template

from framework import request

from website.project.decorators import must_be_contributor_or_public
from website.project.decorators import must_have_addon

from ..api import GitHub, _build_github_urls, ref_to_params
from .util import _get_refs, _check_permissions
from website.util import rubeus


logger = logging.getLogger(__name__)

# TODO: Probably should just take a node object instead of having to pass
# in both url and api_url
def to_hgrid(data, node_url, node_api_url=None, branch=None, sha=None,
             can_edit=True, parent=None, **kwargs):
    """
    :param list data: The return value of Github's `contents` endpoint.
    """
    grid = []
    folders = {}

    for datum in data:
        if data[datum].type in ['file', 'blob']:
            item = {
                rubeus.KIND: rubeus.FILE,
                'urls': _build_github_urls(
                    data[datum], node_url, node_api_url, branch, sha
                )
            }
        elif data[datum].type in ['tree', 'dir']:
            item = {
                rubeus.KIND: rubeus.FOLDER,
                'children': [],
            }
        else:
            continue

        item.update({
            'addon': 'github',
            'permissions': {
                'view': True,
                'edit': can_edit,
            },
            'urls': _build_github_urls(
                data[datum], node_url, node_api_url, branch, sha
            ),
            'accept': {
                'maxSize': kwargs.get('max_size', 128),
                'acceptedFiles': kwargs.get('accepted_files', None)
            }
        })

        head, item['name'] = os.path.split(data[datum].path)
        if parent:
            head = head.split(parent)[-1]
        if head:
            folders[head]['children'].append(item)
        else:
            grid.append(item)

        # Update cursor
        if item[rubeus.KIND] == rubeus.FOLDER:
            key = data[datum].path
            if parent:
                key = key.split(parent)[-1]
            folders[key] = item

    return grid


github_branch_template = Template('''
    % if len(branches) > 1:
            <select class="github-branch-select">
                % for each in branches:
                    <option value="${each}" ${"selected" if each == branch else ""}>${each}</option>
                % endfor
            </select>
    % else:
        <span>${branch}</span>
    % endif
    % if sha:
        <a href="https://github.com/${owner}/${repo}/commit/${sha}" class="github-sha text-muted">${sha[:10]}</a>
    % endif
''')

def github_branch_widget(branches, owner, repo, branch, sha):
    """Render branch selection widget for GitHub add-on. Displayed in the
    name field of HGrid file trees.

    """
    rendered = github_branch_template.render(
        branches=[each.name for each in branches],
        branch=branch,
        sha=sha,
        owner=owner,
        repo=repo
    )
    return rendered


def github_hgrid_data(node_settings, auth, **kwargs):

    # Quit if no repo linked
    if not node_settings.complete:
        return

    connection = GitHub.from_settings(node_settings.user_settings)

    # Initialize repo here in the event that it is set in the privacy check
    # below. This potentially saves an API call in _check_permissions, below.
    repo = None

    # Quit if privacy mismatch and not contributor
    if node_settings.owner.is_public:
        repo = connection.repo(node_settings.user, node_settings.repo)
        if repo.private:
            return

    branch, sha, branches = _get_refs(
        node_settings,
        branch=kwargs.get('branch'),
        sha=kwargs.get('sha'),
        connection=connection,
    )

    if branch is not None:
        ref = ref_to_params(branch, sha)
        can_edit = _check_permissions(
            node_settings, auth, connection, branch, sha, repo=repo,
        )
        name_append = github_branch_widget(branches, owner=node_settings.user,
            repo=node_settings.repo, branch=branch, sha=sha)
    else:

        ref = None
        can_edit = False
        name_append = None

    name_tpl = '{user}/{repo}'.format(
        user=node_settings.user, repo=node_settings.repo
    )

    permissions = {
        'edit': can_edit,
        'view': True
    }
    urls = {
        'upload': node_settings.owner.api_url + 'github/file/' + (ref or ''),
        'fetch': node_settings.owner.api_url + 'github/hgrid/' + (ref or ''),
        'branch': node_settings.owner.api_url + 'github/hgrid/root/',
    }
    return [rubeus.build_addon_root(
        node_settings,
        name_tpl,
        urls=urls,
        permissions=permissions,
        extra=name_append
    )]


@must_be_contributor_or_public
@must_have_addon('github', 'node')
def github_root_folder_public(*args, **kwargs):
    """View function returning the root container for a GitHub repo. In
    contrast to other add-ons, this is exposed via the API for GitHub to
    accommodate switching between branches and commits.

    """
    node_settings = kwargs['node_addon']
    auth = kwargs['auth']
    data = request.args.to_dict()

    return github_hgrid_data(node_settings, auth=auth, **data)


@must_be_contributor_or_public
@must_have_addon('github', 'node')
def github_hgrid_data_contents(**kwargs):
    """Return a repo's file tree as a dict formatted for HGrid.

    """
    auth = kwargs['auth']
    node = kwargs['node'] or kwargs['project']
    node_addon = kwargs['node_addon']
    path = kwargs.get('path', '')

    connection = GitHub.from_settings(node_addon.user_settings)
    # The requested branch and sha
    req_branch, req_sha = request.args.get('branch'), request.args.get('sha')
    # The actual branch and sha to use, given the addon settings
    branch, sha, branches = _get_refs(
        node_addon, req_branch, req_sha, connection=connection
    )
    # Get file tree
    contents = connection.contents(
        user=node_addon.user, repo=node_addon.repo, path=path,
        ref=sha or branch,
    )

    can_edit = _check_permissions(node_addon, auth, connection, branch, sha)

    if contents:
        hgrid_tree = to_hgrid(
            contents, node_url=node.url, node_api_url=node.api_url,
            branch=branch, sha=sha, can_edit=can_edit, parent=path,
            max_size=node_addon.config.max_file_size,
            accepted_files=node_addon.config.accept_extensions
        )
    else:
        hgrid_tree = []
    return hgrid_tree