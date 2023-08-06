import os
from distutils.command.build import build

from django.core import management
from setuptools import find_packages, setup

from pretix_simple_test_results import __version__


try:
    with open(
        os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except Exception:
    long_description = ""


class CustomBuild(build):
    def run(self):
        management.call_command("compilemessages", verbosity=1)
        build.run(self)


cmdclass = {"build": CustomBuild}


setup(
    name="pretix-simple-test-results",
    version=__version__,
    description="Simple test result sending",
    long_description=long_description,
    url="https://github.com/pretix-unofficial/pretix-simple-test-results",
    author="pretix",
    author_email="support@pretix.eu",
    license="Apache",
    install_requires=[],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_simple_test_results=pretix_simple_test_results:PretixPluginMeta
""",
)
