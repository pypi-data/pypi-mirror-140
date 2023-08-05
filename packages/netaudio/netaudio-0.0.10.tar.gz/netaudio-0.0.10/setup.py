# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netaudio',
 'netaudio.console',
 'netaudio.console.commands',
 'netaudio.console.commands.channel',
 'netaudio.console.commands.config',
 'netaudio.console.commands.device',
 'netaudio.console.commands.subscription',
 'netaudio.dante',
 'netaudio.utils']

package_data = \
{'': ['*']}

install_requires = \
['cleo>=0.8.1,<0.9.0',
 'netifaces>=0.11.0,<0.12.0',
 'twisted>=22.1.0,<23.0.0',
 'zeroconf>=0.38.3,<0.39.0']

entry_points = \
{'console_scripts': ['netaudio = netaudio:main']}

setup_kwargs = {
    'name': 'netaudio',
    'version': '0.0.10',
    'description': 'List, configure, and control Dante network audio devices without Dante Controller',
    'long_description': "\n### Description\n\nThis is a python program for controlling Dante network audio devices (and possibly others in the future). It's very early, so expect things to break or switches to change.  Use this at your own risk; it's not ready for anything other than a test environment and could make the devices behave unexpectedly. The first goal is to do everything that Dante Controller can do that would be useful for control of the devices from a command-line interface or within scripts.\n\nFor more information, check out the [gearspace discussion](https://gearspace.com/board/music-computers/1221989-dante-routing-without-dante-controller-possible.html).\n\n### Features\n\n- AVIO input/output gain control\n- Add/remove subscriptions\n- CLI\n- Display active subscriptions, Rx and Tx channels, devices names and addresses, subscription status\n- JSON output\n- Set device latency, sample rate, encoding\n- Set/reset channel names, device names\n- mDNS device discovery\n\n### In progress\n\n- Gather information from multicast traffic (make, model, lock status, subscription changes)\n\n### Planned features\n\n- AES67 device support\n- Change channel/device names without affecting existing subscriptions\n- Change/display device settings (AES67 mode)\n- Client/server modes\n- Command prompt\n- Control of Shure wireless devices ([Axient receivers](https://pubs.shure.com/view/command-strings/AD4/en-US.pdf) and [PSM transmitters](https://pubs.shure.com/view/command-strings/PSM1000/en-US.pdf))\n- Signal presence indicator\n- Stand-alone command API\n- TUI\n- Web application UI\n- XML output (such as a Dante preset file)\n\n### Installation\n\nTo install from PyPI on most systems, use pip or pipx:\n\n```bash\npipx install netaudio\n```\n\n```bash\npip install netaudio\n```\n\nTo install the package from a clone:\n```bash\npipx install --force --include-deps .\n```\n\n#### Arch Linux\n\nTo install from AUR, build the package with\n[aur/python-netaudio](https://aur.archlinux.org/packages/python-netaudio).\nFor development, install the following packages:\n\n```bash\npacman -S community/python-pipx community/python-poetry\n```\n\n#### MacOS\n\nFor development, install the following packages:\n\n```bash\nbrew install pipx poetry\nbrew link pipx poetry\n```\n\n### Usage\n\nTo run without installing:\n```bash\npoetry install\npoetry run netaudio\n```\n\nThen run `netaudio`\n\n### Documentation\n\n- [Examples](https://github.com/chris-ritsen/network-audio-controller/wiki/Examples)\n- [Technical details](https://github.com/chris-ritsen/network-audio-controller/wiki/Technical-details)\n- [Testing](https://github.com/chris-ritsen/network-audio-controller/wiki/Testing)\n",
    'author': 'Christopher Ritsen',
    'author_email': 'chris.ritsen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chris-ritsen/network-audio-controller',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
