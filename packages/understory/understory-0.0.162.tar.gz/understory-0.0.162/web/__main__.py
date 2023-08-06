"""Command line tools for the web."""

import json
import pathlib

import clicks

import web
import web.host

__all__ = ["main"]


main = clicks.application("web", web.__doc__)


@main.register()
class MF:
    """Get a resource and parse it for Microformats."""

    def setup(self, add_arg):
        add_arg("uri", help="address of the resource")

    def run(self, stdin, log):
        pprint(agent.get(self.uri).mf2json)
        return 0


@main.register()
class Apps:
    """Serve a web app."""

    def setup(self, add_arg):
        pass

    def run(self, stdin, log):
        for pkg, apps in web.get_apps().items():
            for name, _, ns, obj in apps:
                print(f"{name} {ns}:{obj[0]}")
        return 0


@main.register()
class Serve:
    """Serve a web app."""

    def setup(self, add_arg):
        add_arg("app", help="name of web application")
        add_arg("--port", help="port to serve on")
        add_arg("--socket", help="file socket to serve on")
        add_arg("--watch", default=".", help="directory to watch for changes")

    def run(self, stdin, log):
        import asyncio

        if self.port:
            asyncio.run(web.serve(self.app, port=self.port, watch_dir=self.watch))
        elif self.socket:
            asyncio.run(web.serve(self.app, socket=self.socket, watch_dir=self.watch))
        else:
            print("must provide a port or a socket")
            return 1
        return 0

        # from pprint import pprint
        # pprint(web.get_apps())
        # for pkg, apps in web.get_apps().items():
        #     for name, _, ns, obj in apps:
        #         if self.app == name:
        #             web.serve(ns, obj)
        #             return 0
        # return 1


@main.register()
class Config:
    """Config your environments."""

    def setup(self, add_arg):
        add_arg(
            "provider",
            choices=("digitalocean", "linode", "hetzner"),
            help="hosting provider",
        )
        add_arg("token", help="API access token")

    def run(self, stdin, log):
        update_config(provider=self.provider, token=self.token)
        return 0


@main.register()
class Host:
    """Host a web app."""

    def setup(self, add_arg):
        add_arg("repo", help="repository URL or GitHub path")
        add_arg("domain", help="domain name")

    def run(self, stdin, log):
        config = get_config()
        machines = config.get("machines", [])
        if len(machines) == 0:
            print("Creating machine at Digital Ocean")
            ip_address = web.host.spawn_machine("understory", config["token"])
            web.host.setup_machine(ip_address)
            machines.append(ip_address)
            update_config(machines=machines)
            web.host.setup_python(ip_address)
            web.host.setup_nginx(ip_address)
            web.host.generate_dhparam(ip_address)
            # web.host.setup_tor(ip_address)
            web.host.setup_supervisor(ip_address)
        elif len(machines) == 1:
            print("Using existing machine")
            ip_address = machines[0]
        else:
            # TODO print("Choose machine:")
            ip_address = machines[0]
        print(f"Using {ip_address}")
        return 0


config_file = pathlib.Path("~/.understory").expanduser()


def get_config():
    """Get configuration."""
    try:
        with config_file.open() as fp:
            config = json.load(fp)
    except FileNotFoundError:
        config = {}
    return config


def update_config(**items):
    """Update configuration."""
    config = get_config()
    config.update(**items)
    with config_file.open("w") as fp:
        json.dump(config, fp, indent=2, sort_keys=True)
        fp.write("\n")
    return get_config()
