import re

from setuptools import find_packages, setup

with open("README.rst", encoding="utf-8") as f:
    readme = f.read()


with open("certbot_dns_plugins/__init__.py", encoding="utf-8") as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

setup(
    name="certbot-dns-plugins",
    version=version,
    description="Certbot dns plugin for DNSPod",
    long_description=readme,
    author="codeif",
    author_email="me@codeif.com",
    url="https://github.com/codeif/certbot-dns-plugins",
    license="MIT",
    packages=find_packages(),
    install_requires=["certbot", "zope.interface", "dnspod-sdk"],
    entry_points={"certbot.plugins": ["dnspod = certbot_dns_plugins.dnspod:Authenticator"]},
)
