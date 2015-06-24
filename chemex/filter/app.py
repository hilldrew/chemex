# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import sys

_CUR_PATH = os.path.dirname(os.path.abspath(__file__)) # ./<this file>
_CLASTIC_PATH = os.path.dirname(os.path.dirname(_CUR_PATH)) # ../../
sys.path.append(_CLASTIC_PATH)

import clastic
from clastic import Application, POST, redirect
from clastic.errors import Forbidden
from clastic.static import StaticApplication
from clastic.render import AshesRenderFactory
from clastic.middleware import SimpleContextProcessor
from clastic.middleware.form import PostDataMiddleware
from clastic.middleware.cookie import SignedCookieMiddleware


from id_map import IDMap # class that manages writing results to file
_DEFAULT_DATA_FILE_PATH = os.path.join(_CUR_PATH, 'data/data.csv')
_DEFAULT_ID_FILE_PATH = os.path.join(_CUR_PATH, 'results/alignments.json')


def home(id_map, cookie):
    # cookie data used ...
    # new_entry_alias = cookie.pop('new_entry_alias', None)
    # aliases = cookie.get('aliases', [])
    human_name = cookie.get('human_name', [])
    next_id = cookie.pop('next_id')

    # placeholder for home endpoint

    return {'next_id': next_id}



def add_entry():

    # placeholder

    pass


def add_entry_render(context, cookie, link_map):
    new_entry = context.get('new_entry')
    # cookie data added...
    if new_entry:
        cookie['new_entry_alias'] = new_entry.alias
        cookie.setdefault('aliases', []).insert(0, new_entry.alias)
    return redirect('/', code=303)


def create_app(data_path=None, id_list_path=None, id_types=None, 
               local_root=None, host_url=None, secret_key=None):
    # id_types -> {'id1': id1_field, 'name1': name1,
    #              'id2': id2_field, 'display': display_field,
    #              ...} ???
    
    data_path = data_path or _DEFAULT_DATA_FILE_PATH

    data = None     # placeholder for reading data

    # placeholder for determining what ID types are being aligned, 
    # what (additional) resources need to be displayed,
    #   e.g. names, structure diagrams
    # ??

    id_list_path = id_list_path or _DEFAULT_ID_FILE_PATH
    id_map = IDMap(id_list_path)
    
    local_static_app = None  # ?
    if local_root:
        local_static_app = StaticApplication(local_root)
    host_url = (host_url or 'localhost:5000').rstrip('/') + '/'
    full_host_url = 'http://' + host_url
    
    resources = {'data': data,
                 'id_map': id_map,
                 'local_root': local_root,
                 # 'local_static_app': local_static_app,
                 'host_url': host_url,
                 'full_host_url': full_host_url}

    pdm = PostDataMiddleware({'user_name': user_name,
                              'id1': id1,
                             # placeholder for dict of info to be POSTed
                             })

    submit_route = POST('/submit', add_entry, add_entry_render,
                        middlewares=[pdm])

    routes = [('/', home, 'home.html'),
              submit_route]
    # cookie instantiated...
    scm = SignedCookieMiddleware(secret_key=secret_key)
    scp = SimpleContextProcessor('local_root', 'full_host_url')
    middlewares = [scm, scp]

    arf = AshesRenderFactory(_CUR_PATH, keep_whitespace=False)
    app = Application(routes, resources, middlewares, arf)
    return app



def main():
    secret_key = 'Philz_Coffee_secret_ingredient_is_'
    secret_key += os.getenv('CHEMEX_KEY') or 'grassfedbutter'
    app = create_app(local_root='/tmp/', secret_key=secret_key)
    app.serve(threaded=True)


if __name__ == '__main__':
    main()
