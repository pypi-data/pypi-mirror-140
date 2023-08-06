# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skillmap']

package_data = \
{'': ['*'], 'skillmap': ['themes/*']}

install_requires = \
['toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['skillmap = skillmap.main:main']}

setup_kwargs = {
    'name': 'skillmap',
    'version': '0.2.3',
    'description': 'Skillmap generates a skill tree from a toml file',
    'long_description': '# skillmap\nA tool for generating skill map/tree like diagram.\n\n# What is a skill map/tree?\nSkill tree is a term used in video games, and it can be used for describing roadmaps for software project development as well.\n\nThis project borrows inspiration and ideas from two sources:\n1. https://hacks.mozilla.org/2018/10/webassemblys-post-mvp-future/\n2. https://github.com/nikomatsakis/skill-tree\n\n# Installation\n```\npip install skillmap\n```\nAfter installation, a `skillmap` command is available.\n\n# Usage\n1. Create a toml format skill map descriptor file. You can find more details about this descriptor format [here](docs/skillmap_descriptor.md). For a minimal example, see [`docs/examples/hello_world.toml`](docs/examples/hello_world.toml)\n```\n[skillmap]\nname = "hello world"\nicon = "bicycle"\n\n[groups.learn_python]\nname = "learn python"\nicon = "rocket"\n    [groups.learn_python.skills.print]\n    name = "print statement"\n    icon = "printer"\n    [groups.learn_python.skills.string]\n    name = "string literal"\n    icon = "book"\n```\n\n2. Run `skillmap path/to/your/skillmap.toml`\n   1. For example, `skillmap docs/examples/hello_world.toml`\n3. Copy the generated skill map diagram to your clipboard.\n4. Paste the diagram to a mermaid diagram editor, for example, [`https://mermaid-js.github.io/mermaid-live-editor`](https://mermaid-js.github.io/mermaid-live-editor).\n\n# Examples\n![ocean_theme_example](docs/images/ocean_theme_example.png)\n![orientation_example](docs/images/orientation_example.png)\n\n* Each node can have a string label and an fontawsome icon.\n* Skills with different statuses will be shown with different colors.\n* Unnamed skill will be shown as a locked skill.\n* Pre-requisite skills will be connected with an directed edge.\n* You can embed the generated mermaid diagram into github markdown directly, but the fontawesome icons in the diagrams are not shown by github so far.\n\n# License\n[MIT License](LICENSE)\n\n# More details\n* Skillmap toml descriptor format can be found [here](docs/skillmap_descriptor.md)\n* hot reloading when authoring a skillmap toml file\n    * install several tools to make hot reloading to work\n        * [`entr`](https://github.com/eradman/entr), run arbitrary commands when files change\n        * [Visual Studio Code](https://code.visualstudio.com) + [Markdown Preview Enhanced Visual Studio Code Extension](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)\n        * Basically, use `entr` to watch toml file changes, and generate a `md` makrdown file using `skillmap` every time when toml file changes. And use `vscode` + `Markdown Preview Enhanced` extension to open this generated markdown file. Check out `build_sample` and `dev_sample` in [justfile](justfile) to see how to make hot reloading work',
    'author': 'Yue Ni',
    'author_email': 'niyue.com@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/niyue/skillmap',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
