# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['across']

package_data = \
{'': ['*'], 'across': ['abis/*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'web3>=5.28.0,<6.0.0']

setup_kwargs = {
    'name': 'across-py',
    'version': '0.1.0',
    'description': 'across sdk in python',
    'long_description': '# Across\n\nAcross is the fastest, cheapest and most secure cross-chain bridge. It is a system that uses UMA contracts to quickly move tokens across chains. This contains various utilities to support applications on across.\n\n## How to use\n\n### Get suggested fees from online API\n\nUse across official API to get suggested fees.\n\n```py\n>>> import across\n>>> a = across.AcrossAPI()\n>>> a.suggested_fees("0x7f5c764cbc14f9669b88837ca1490cca17c31607", 10, 1000000000)\n{\'slowFeePct\': \'43038790000000000\', \'instantFeePct\': \'5197246000000000\'}\n```\n\n### Fee Calculator\n\nCalculates lp fee percentages when doing a transfer.\n\n```py\nfrom across.fee_calculator import (\n    calculate_apy_from_utilization,\n    calculate_realized_lp_fee_pct,\n)\nfrom across.utils import toBNWei\n\nrate_model = {\n    "UBar": toBNWei("0.65"),\n    "R0": toBNWei("0.00"),\n    "R1": toBNWei("0.08"),\n    "R2": toBNWei("1.00"),\n}\n\ninterval = { "utilA": 0, "utilB": toBNWei(0.01), "apy": 615384615384600, "wpy": 11830749673498 }\napy_fee_pct = calculate_apy_from_utilization(rate_model, interval["utilA"], interval["utilB"])\nassert apy_fee_pct == interval["apy"]\n\nrealized_lp_fee_pct = calculate_realized_lp_fee_pct(rate_model, interval["utilA"], interval["utilB"])\nassert realized_lp_fee_pct == interval["wpy"]\n```\n\n### LP Fee Calculator\n\nGet lp fee calculations by timestamp.\n\n```py\nfrom across import LpFeeCalculator\nfrom web3 import Web3\n\nprovider = Web3.WebsocketProvider("{YOUR-PROVIDER-ADDRESS}")\ncalculator = LpFeeCalculator(provider)\ntoken_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" # WETH on mainnet\nbridge_pool_address = "0x7355Efc63Ae731f584380a9838292c7046c1e433" # WETH BridgePool on mainnet\namount = "1000000000000000000" # 1 ETH\ntimestamp = 1645000000 # timestamp in seconds\npercent = calculator.get_lp_fee_pct(\n    token_address, bridge_pool_address, amount, timestamp\n)\nprint(percent)\n```\n\n## How to build and test\n\nInstall poetry and install the dependencies:\n\n```shell\npip3 install poetry\n\npoetry install\n\n# test\npython -m unittest\n\n# local install and test\npip3 install twine\npython3 -m twine upload --repository testpypi dist/*\npip3 install --index-url https://test.pypi.org/simple/ --no-deps across\n```\n',
    'author': 'qiwihui',
    'author_email': 'qwh005007@gmail.com',
    'maintainer': 'qiwihui',
    'maintainer_email': 'qwh005007@gmail.com',
    'url': 'https://github.com/qiwihui/across-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
