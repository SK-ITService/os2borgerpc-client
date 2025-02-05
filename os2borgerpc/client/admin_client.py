import os
import xmlrpc.client
import urllib.request


def get_default_admin(verbose=False):
    from os2borgerpc.client.config import OS2borgerPCConfig

    conf_data = OS2borgerPCConfig().get_data()
    admin_url = conf_data.get("admin_url", "http://os2borgerpc.magenta-aps.dk")
    xml_rpc_url = conf_data.get("xml_rpc_url", "/admin-xml/")
    return OS2borgerPCAdmin("".join([admin_url, xml_rpc_url]), verbose=verbose)


# Thanks to A. Ellerton for this
class ProxyTransport(xmlrpc.client.Transport):
    """Provides an XMl-RPC transport routing via a http proxy.

    This is done by using urllib2, which in turn uses the environment
    varable http_proxy and whatever else it is built to use (e.g. the
    windows registry).

    NOTE: the environment variable http_proxy should be set correctly.
    See checkProxySetting() below.

    Written from scratch but inspired by xmlrpc_urllib_transport.py
    file from http://starship.python.net/crew/jjkunce/ byself,  jjk.

    A. Ellerton 2006-07-06
    """

    def __init__(self, schema="http"):
        xmlrpc.client.Transport.__init__(self)
        self.schema = schema

    def request(self, host, handler, request_body, verbose):

        self.verbose = verbose
        url = self.schema + "://" + host + handler

        request = urllib.request.Request(url)
        request.add_data(request_body)

        # Note: 'Host' and 'Content-Length' are added automatically
        request.add_header("User-Agent", self.user_agent)
        request.add_header("Content-Type", "text/xml")  # Important

        proxy_handler = urllib.request.ProxyHandler()
        opener = urllib.request.build_opener(proxy_handler)
        f = opener.open(request)
        return self.parse_response(f)


class OS2borgerPCAdmin(object):
    """XML-RPC client class for communicating with admin system."""

    def __init__(self, url, verbose=False):
        """Set up server proxy."""
        # TODO: Modify to use SSL.
        self._url = url
        rpc_args = {"verbose": verbose, "allow_none": True}
        # Use proxy if present
        if "http_proxy" in os.environ:
            rpc_args["transport"] = ProxyTransport(schema=url[: url.index(":")])

        self._rpc_srv = xmlrpc.client.ServerProxy(self._url, **rpc_args)

    def register_new_computer(self, mac, name, distribution, site, configuration):
        return self._rpc_srv.register_new_computer(
            mac, name, distribution, site, configuration
        )

    def send_status_info(self, pc_uid, package_data, job_data, update_required=None):
        return self._rpc_srv.send_status_info(
            pc_uid, package_data, job_data, update_required
        )

    def get_instructions(self, pc_uid):
        return self._rpc_srv.get_instructions(pc_uid)

    def get_proxy_setup(self, pc_uid):
        return self._rpc_srv.get_proxy_setup(pc_uid)

    def push_config_keys(self, pc_uid, config_dict):
        return self._rpc_srv.push_config_keys(pc_uid, config_dict)

    def push_security_events(self, pc_uid, csv_data):
        return self._rpc_srv.push_security_events(pc_uid, csv_data)

    def citizen_login(self, username, password, site):
        return self._rpc_srv.citizen_login(username, password, site)
