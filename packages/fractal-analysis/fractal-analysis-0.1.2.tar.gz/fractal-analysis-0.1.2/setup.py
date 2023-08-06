# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fractal_analysis', 'fractal_analysis.tester']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.0,<2.0.0', 'scipy>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'fractal-analysis',
    'version': '0.1.2',
    'description': '',
    'long_description': '# Fractal Analysis\nFractal and multifractal methods, including\n\n- fractional Brownian motion (FBM) tester\n- multifractional Brownian motion (MBM) tester\n\n## To install\nTo get started, simply do:\n```\npip install fractal-analysis\n```\nor check out the code from out GitHub repository.\n\nYou can now use the package in Python with:\n```\nfrom fractal_analysis import tester\n```\n\n## Examples\nImport:\n```\nfrom fractal_analysis.tester.series_tester import MBMSeriesTester, FBMSeriesTester\nfrom fractal_analysis.tester.critical_surface import CriticalSurfaceFBM, CriticalSurfaceMFBM\n```\nTo test if a series ```series``` is FBM, one needs to use ```CriticalSurfaceFBM``` with length of the series ```N```\nand the significance level ```alpha``` (look at quantiles of order ```alpha/2``` and ```1 − alpha/2```) \n```\nfbm_tester = FBMSeriesTester(critical_surface=CriticalSurfaceFBM(N=N, alpha=0.05))\n```\n\nTo test if the series is FBM with holder exponent 0.3 and use auto estimated sigma square (set ```sig2=None```):\n\n```\nis_fbm, sig2 = fbm_tester.test(h=0.3, x=series, sig2=None)\n```\nIf the output contains, for example:\n> Bad auto sigma square calculated with error 6.239236333681868. Suggest to give sigma square and rerun.\n\nThe auto sigma square estimated is not accurate. One may want to manually choose a sigma square and rerun. For example:\n```\nis_fbm, sig2 = fbm_tester.test(h=0.3, x=series, sig2=1)\n```\nTo test if the series is MBM, one needs to use ```CriticalSurfaceMFBM``` with length of the series ```N```\nand the significance level ```alpha``` (look at quantiles of order ```alpha/2``` and ```1 − alpha/2```) \n```\nmbm_tester = MBMSeriesTester(critical_surface=CriticalSurfaceMFBM(N=N, alpha=0.05))\n```\nTo test if the series is MBM with a given holder exponent series ```h_mbm_series``` and use auto estimated sigma square:\n```\nis_mbm, sig2 = mbm_tester.test(h=h_mbm_series, x=series, sig2=None)\n```\nBe aware that ```MBMSeriesTester``` requires ```len(h_mbm_series)==len(series)```.\n\n## Use of cache\nUse caching to speed up the testing process. If the series ```x``` for testing is unchanged and multiple ```h``` \nand/or ```sig2``` are used, one may want to set \n```is_cache_stat=True``` to allow cache variable ```stat```. If ```h``` and ```sig2``` are unchanged and multiple ```x```\nare used, one may want to set ```is_cache_quantile=True``` to allow cache variable ```quantile```.\n\n',
    'author': 'yujiading',
    'author_email': 'yujia.ding@cgu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yujiading/fractals',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
