# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['weather_command', 'weather_command.models']

package_data = \
{'': ['*']}

install_requires = \
['camel-converter[pydantic]==1.0.3',
 'httpx==0.22.0',
 'pydantic==1.9.0',
 'rich==11.2.0',
 'tenacity==8.0.1',
 'typer==0.4.0']

entry_points = \
{'console_scripts': ['weather-command = weather_command.main:app']}

setup_kwargs = {
    'name': 'weather-command',
    'version': '2.1.5',
    'description': 'Command line weather app',
    'long_description': '# Weather Command\n\n[![Tests Status](https://github.com/sanders41/weather-command/workflows/Testing/badge.svg?branch=main&event=push)](https://github.com/sanders41/weather-command/actions?query=workflow%3ATesting+branch%3Amain+event%3Apush)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sanders41/weather-command/main.svg)](https://results.pre-commit.ci/latest/github/sanders41/weather-command/main)\n[![Coverage](https://codecov.io/github/sanders41/weather-command/coverage.svg?branch=main)](https://codecov.io/gh/sanders41/weather-command)\n[![PyPI version](https://badge.fury.io/py/weather-command.svg)](https://badge.fury.io/py/weather-command)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/weather-command?color=5cc141)](https://github.com/sanders41/weather-command)\n\nA command line weather app\n\n## Installation\n\nInstallation with [pipx](https://github.com/pypa/pipx) is recommended.\n\n```sh\npipx install weather-command\n```\n\nAlternatively Weather Command can be installed with pip.\n\n```sh\npip install weather-command\n```\n\n## Usage\n\nFirst an API key is needed from [OpenWeather](https://openweathermap.org/), A free account is all that\nis needed. Once you have your API key create an environment variable named `OPEN_WEATHER_API_KEY` that\nconstains your API key.\n\n```sh\nexport OPEN_WEATHER_API_KEY=your-api-key\n```\n\nEach time the shell is restarted this variable will be cleared. To avoid this it can be added to your\nprofile. For example if your shell is zsh the API key can be added to the `~/.zshenv` file. Doing this\nwill prevent the need to re-add the key each time the shell is started.\n\nTo get the weather for a city:\n\n```sh\nweather-command city seattle\n```\n\nOnce installed you can also add aliases to your shell to make it quick to get a forecast. For example\nif your shell is zsh you can add something like the following to your `~/.zshrc` file:\n\n```sh\nalias we="weather-command zip 98109 -i --am-pm"\nalias wed="weather-command zip 98109 -i --am-pm -f daily"\nalias weh="weather-command zip 98109 -i --am-pm -f hourly"\n```\n\nAfter adding this to the `~/.zshrc` you will need to restart your terminal. After that typing `we`\nwill get the current forecast, `wed` will get the daily forecast and `weh` will get the hourly forecast.\n\n### Arguments\n\n* [HOW]: How to get the weather. Accepted values are city and zip. [default: city]\n* [CITY_ZIP]: The name of the city or zip code for which the weather should be retrieved. If the\nfirst argument is \'city\' this should be the name of the city, or if \'zip\' it should be the zip\ncode. [required]\n\n### Options\n\n* -s, --state-code: The name of the state where the city is located.\n* -c, --country-code: The country code where the city is located.\n* -i, --imperial: If this flag is used the units will be imperial, otherwise units will be metric.\n* --am-pm: If this flag is set the times will be displayed in 12 hour format, otherwise times\nwill be 24 hour format.\n* -f, --forecast-type: The type of forecast to display. Accepted values are \'current\' \'daily\', and \'hourly\'. [default: current]\n* -t, --temp-only: If this flag is set only tempatures will be displayed.\n* --terminal_width INTEGER: Allows for overriding the default terminal width.\n* --help: Show this message and exit.\n\n## Contributing\n\nContributions to this project are welcome. If you are interesting in contributing please see our [contributing guide](CONTRIBUTING.md)\n',
    'author': 'Paul Sanders',
    'author_email': 'psanders1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sanders41/weather-command',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
