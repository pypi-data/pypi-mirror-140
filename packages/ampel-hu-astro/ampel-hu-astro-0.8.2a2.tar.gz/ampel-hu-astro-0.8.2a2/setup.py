# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ampel',
 'ampel.contrib.hu',
 'ampel.contrib.hu.t0',
 'ampel.contrib.hu.t2',
 'ampel.contrib.hu.t3',
 'ampel.contrib.hu.t3.complement',
 'ampel.contrib.hu.t3.tns',
 'ampel.contrib.hu.test',
 'ampel.contrib.hu.util']

package_data = \
{'': ['*'], 'ampel.contrib.hu.t2': ['data/*']}

install_requires = \
['adjustText>=0.7.3,<0.8.0',
 'ampel-plots>=0.8.0-alpha.0,<0.9.0',
 'ampel-ztf>=0.8.2-alpha.5,<0.8.3',
 'astropy>=5.0,<6.0',
 'backoff>=1.11.1,<2.0.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'numpy>=1,<2',
 'pandas>=1.3.3,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'scipy>=1.4,<2.0',
 'seaborn>=0.11.2,<0.12.0']

extras_require = \
{'extcats': ['extcats>=2.4.2,<3.0.0'],
 'sncosmo': ['sncosmo>=2.5.0,<3.0.0',
             'iminuit>=2.8.0,<3.0.0',
             'sfdmap>=0.1.1,<0.2.0']}

setup_kwargs = {
    'name': 'ampel-hu-astro',
    'version': '0.8.2a2',
    'description': 'Astronomy units for the Ampel system from HU-Berlin',
    'long_description': '\nContributed Ampel units from HU/DESY group\n==========================================\n\nContains as of Jan 2020:\n\nT0\n--\n* DecentFilter\n* LensedTransientFilter\n* NoFilter\n* RandFilter\n* SEDmTargetFilter\n* SimpleDecentFilter\n* ToOFilter\n* TransientInClusterFilter\n* TransientInEllipticalFilter\n* XShooterFilter\n\nT2\n--\n* T2CatalogMatch\n* T2LCQuality\n* T2MarshalMonitor\n* T2Observability\n* T2SNCosmo\n\nT3\n--\n* ChannelSummaryPublisher\n* CompareExternal\n* CompareUli\n* CountSncosmo\n* GrowthMarshalAnnotate\n* MarshalPublisher\n* RapidBase\n* RapidSedm\n* RejectionLogsPublisher\n* SkyPortalPublisher\n* SlackAlertPublisher\n* SlackPublisher\n* SlackSummaryPublisher\n* T3MarshalMonitor\n* TNSTalker\n* TransientInfoPrinter\n* TransientViewDumper\n* TransientWebPublisher\n* aiotns (TNSMatcher)\n',
    'author': 'Valery Brinnel',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ampelproject.github.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
