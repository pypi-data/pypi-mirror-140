# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minecraftstatus']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.2,<4.0.0']

setup_kwargs = {
    'name': 'minecraftstatus',
    'version': '0.0.6',
    'description': 'minecraftstatus is an asynchronous wrapper for https://api.iapetus11.me.',
    'long_description': '\n\nAn async API wrapper around [api.iapetus.me](https://github.com/Iapetus-11/api.iapetus11.me)\n\n\n### Get started\n\n#### to get started, type this in your terminal\n```\npip install -U minecraftstatus\n```\n\n#### or to install the main branch\n```\npip install -U git+https://github.com/Infernum1/minecraftstatus\n```\n###### (make sure you have git installed)\n### Examples\n\n#### For examples, checkout the [examples directory](https://github.com/Infernum1/minecraftstatus/tree/main/examples)\n##### If you plan to use the lib in a discord bot\n\n```py\nimport discord\nimport minecraftstatus\n\nclient = minecraftstatus.MCStatus()\nbot = discord.ext.commands.Bot()\n\n@bot.command()\nasync def achievement(achievement: str):\n  image = await client.achievement(achievement)\n  file = discord.File(image, "achievement.png")\n  await ctx.send(file=file)\n```\n\n###### these are just examples! it\'s upto you how you want to use this lib.\n\n### Join the [discord server](https://discord.gg/jJqJ3rjgqg) for support.',
    'author': 'Infernum1',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Infernum1/minecraftstatus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.6',
}


setup(**setup_kwargs)
