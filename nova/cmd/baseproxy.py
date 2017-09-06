#
#    Copyright (C) 2014 Red Hat, Inc
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

"""Base proxy module used to create compatible consoles
for OpenStack Nova."""

import os
import sys

from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr
from oslo_reports import opts as gmr_opts

import nova.conf
from nova.conf import novnc
from nova.console import websocketproxy
from nova import version


CONF = nova.conf.CONF
novnc.register_cli_opts(CONF)
gmr_opts.set_defaults(CONF)


def exit_with_error(msg, errno=-1):
    sys.stderr.write(msg + '\n')
    sys.exit(errno)


def proxy(host, port):

    if CONF.ssl_only and not os.path.exists(CONF.cert):
        exit_with_error("SSL only and %s not found" % CONF.cert)

    # Check to see if tty html/js/css files are present
    if CONF.web and not os.path.exists(CONF.web):
        exit_with_error("Can not find html/js files at %s." % CONF.web)

    logging.setup(CONF, "nova")

    gmr.TextGuruMeditation.setup_autorun(version, conf=CONF)

    # Create and start the NovaWebSockets proxy
    websocketproxy.NovaWebSocketProxy(
        listen_host=host,
        listen_port=port,
        source_is_ipv6=CONF.source_is_ipv6,
        cert=CONF.cert,
        key=CONF.key,
        ssl_only=CONF.ssl_only,
        daemon=CONF.daemon,
        record=CONF.record,
        traffic=not CONF.daemon,
        web=CONF.web,
        file_only=True,
        RequestHandlerClass=websocketproxy.NovaProxyRequestHandler
    ).start_server()
