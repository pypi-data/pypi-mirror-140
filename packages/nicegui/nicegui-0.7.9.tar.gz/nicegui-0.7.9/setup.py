# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nicegui', 'nicegui.elements']

package_data = \
{'': ['*'],
 'nicegui': ['static/*',
             'static/templates/*',
             'static/templates/css/*',
             'static/templates/highcharts/*',
             'static/templates/js/*',
             'static/templates/local/*',
             'static/templates/local/fontawesome/css/*',
             'static/templates/local/fontawesome/webfonts/*',
             'static/templates/local/ionicons/*',
             'static/templates/local/materialdesignicons/iconfont/*',
             'static/templates/local/robotofont/*',
             'static/templates/local/tailwind/*'],
 'nicegui.elements': ['lib/*']}

install_requires = \
['Pygments>=2.9.0,<3.0.0',
 'asttokens>=2.0.5,<3.0.0',
 'docutils>=0.17.1,<0.18.0',
 'justpy==0.2.3',
 'markdown2>=2.4.0,<3.0.0',
 'matplotlib>=3.4.1,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'typing-extensions>=3.10.0,<4.0.0',
 'uvicorn[watchgodreloader]>=0.14.0,<0.15.0',
 'watchgod>=0.7,<0.8',
 'websockets>=9.1,<10.0']

setup_kwargs = {
    'name': 'nicegui',
    'version': '0.7.9',
    'description': 'Web User Interface with Buttons, Dialogs, Markdown, 3D Scences and Plots',
    'long_description': '# NiceGUI\n\n<img src="https://raw.githubusercontent.com/zauberzeug/nicegui/main/sceenshots/ui-elements.png" width="300" align="right">\n\nNiceGUI is an easy-to-use, Python-based UI framework, which renders to the web browser.\nYou can create buttons, dialogs, markdown, 3D scenes, plots and much more.\n\nIt was designed to be used for micro web apps, dashboards, robotics projects, smart home solutions and similar use cases.\nIt is also helpful for development, for example when tweaking/configuring a machine learning algorithm or tuning motor controllers.\n\n## Features\n\n- browser-based graphical user interface\n- shared state between multiple browser windows\n- implicit reload on code change\n- standard GUI elements like label, button, checkbox, switch, slider, input, file upload, ...\n- simple grouping with rows, columns, cards and dialogs\n- general-purpose HTML and markdown elements\n- powerful high-level elements to\n  - plot graphs and charts,\n  - render 3D scenes,\n  - get steering events via virtual joysticks\n  - annotate images\n- built-in timer to refresh data in intervals (even every 10 ms)\n- straight-forward data binding to write even less code\n- notifications, dialogs and menus to provide state of the art user interaction\n- ability to add custom routes and data responses\n- capture keyboard input for global shortcuts etc\n- customize look by defining primary, secondary and accent colors\n\n## Installation\n\n```bash\npython3 -m pip install nicegui\n```\n\n## Usage\n\nWrite your nice GUI in a file `main.py`:\n\n```python\nfrom nicegui import ui\n\nui.label(\'Hello NiceGUI!\')\nui.button(\'BUTTON\', on_click=lambda: print(\'button was pressed\', flush=True))\n\nui.run()\n```\n\nLaunch it with:\n\n```bash\npython3 main.py\n```\n\nThe GUI is now available through http://localhost:8080/ in your browser.\nNote: The script will automatically reload the page when you modify the code.\n\nFull documentation can be found at [https://nicegui.io](https://nicegui.io).\n\n## Configuration\n\nYou can call `ui.run()` with optional arguments for some high-level configuration:\n\n- `host` (default: `\'0.0.0.0\'`)\n- `port` (default: `8080`)\n- `title` (default: `\'NiceGUI\'`)\n- `favicon` (default: `\'favicon.ico\'`)\n- `dark`: whether to use Quasar\'s dark mode (default: `False`, use `None` for "auto" mode)\n- `reload`: automatically reload the ui on file changes (default: `True`)\n- `show`: automatically open the ui in a browser tab (default: `True`)\n- `on_connect`: default function or coroutine which is called for each new client connection; the optional `request` argument provides session infos\n- `uvicorn_logging_level`: logging level for uvicorn server (default: `\'warning\'`)\n- `main_page_classes`: configure Quasar classes of main page (default: `q-ma-md column items-start`)\n- `interactive`: used internally when run in interactive Python shell (default: `False`)\n\n## Docker\n\nYou can use our [multi-arch Docker image](https://hub.docker.com/repository/docker/zauberzeug/nicegui) for pain-free installation:\n\n```bash\ndocker run --rm -p 8888:8080 -v $(pwd):/app/ -it zauberzeug/nicegui:latest\n```\n\nThis will start the server at http://localhost:8888 with the code from your current directory.\nThe file containing your `ui.run(port=8080, ...)` command must be named `main.py`.\nCode modification triggers an automatic reload.\n\n## Why?\n\nWe like [Streamlit](https://streamlit.io/) but find it does [too much magic when it comes to state handling](https://github.com/zauberzeug/nicegui/issues/1#issuecomment-847413651).\nIn search for an alternative nice library to write simple graphical user interfaces in Python we discovered [justpy](https://justpy.io/).\nWhile too "low-level HTML" for our daily usage it provides a great basis for "NiceGUI".\n\n## API\n\nThe API reference is hosted at [https://nicegui.io](https://nicegui.io) and is [implemented with NiceGUI itself](https://github.com/zauberzeug/nicegui/blob/main/main.py).\nYou may also have a look at [examples.py](https://github.com/zauberzeug/nicegui/tree/main/examples.py) for more demonstrations of what you can do with NiceGUI.\n\n## Abstraction\n\nNiceGUI is based on [JustPy](https://justpy.io/) which is based on the ASGI framework [Starlette](https://www.starlette.io/) and the ASGI webserver [Uvicorn](https://www.uvicorn.org/).\n\n## Deployment\n\nTo deploy your NiceGUI app, you will need to execute your `main.py` (or whichever file contains your `ui.run(...)`) on your server infrastructure.\nYou can either install the [NiceGUI python package via pip](https://pypi.org/project/nicegui/) on the server or use our [pre-built Docker image](https://hub.docker.com/r/zauberzeug/nicegui) which contains all necessary dependencies and provides a much much cleaner deployment.\nFor example you can use this `docker run` command to start the script `main.py` in the current directory on port 80:\n\n```bash\ndocker run -p 80:8080 -v $(pwd)/:/app/ -d --restart always zauberzeug/nicegui:latest\n```\n\nThe example assumes `main.py` uses the port 8080 in the `ui.run` command (which is the default).\nThe `--restart always` makes sure the container is restarted on crash of the app or reboot of the server.\nOf course this can also be written in a docker compose file:\n\n```yaml\nnicegui:\n  image: zauberzeug/nicegui:latest\n  restart: always\n  ports:\n    - 80:8080\n  volumes:\n    - ./:/app/\n```\n\nWhile it is possible to provide SSL certificates directly through NiceGUI (using [JustPy config](https://justpy.io/reference/configuration/)) we suggest to use a reverse proxy like [Traefik](https://doc.traefik.io/traefik/) or [NGINX](https://www.nginx.com/).\n',
    'author': 'Zauberzeug GmbH',
    'author_email': 'info@zauberzeug.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zauberzeug/nicegui',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
