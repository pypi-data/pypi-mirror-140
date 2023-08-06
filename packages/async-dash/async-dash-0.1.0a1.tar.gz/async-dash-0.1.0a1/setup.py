# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['async_dash']

package_data = \
{'': ['*']}

install_requires = \
['dash>=2.2.0,<3.0.0', 'quart>=0.16.3,<0.17.0']

setup_kwargs = {
    'name': 'async-dash',
    'version': '0.1.0a1',
    'description': 'Async port of the official Plotly Dash library',
    'long_description': '## Async Dash\n\n`async-dash` is an async port of [Plotly Dash](https://github.com/plotly/dash) library, created by replacing its flask\nbackend with its async counterpart [quart](https://pgjones.gitlab.io/quart/index.html).\n\nIt started with my need to be able to create realtime dashboards with `dash`, specifically with event-driven\narchitecture. Using `async-dash` with components from [dash-extensions](https://github.com/thedirtyfew/dash-extensions)\nsuch as WebSocket, EventSource, etc. you can create truly events based or realtime dashboards.\n\n#### Table Of Contents\n\n- [Installation](#installation)\n- [Usage](#usage)\n- [Motivation](#motivation)\n- [Caveats](#caveats)\n- [Alternatives](#alternatives)\n- [Known Issues](#known-issues)\n- [TODO](#todo)\n\n### Installation\n\n```bash\npip install async-dash\n```\n\n### Usage\n\n```python\nfrom async_dash import Dash\nfrom dash import html, dcc\n```\n\nSimple Example\n\n```python\nimport asyncio\nimport random\n\nfrom async_dash import Dash\nfrom dash import html, Output, Input, dcc\nfrom dash_extensions import WebSocket\nfrom quart import websocket, json\n\napp = Dash(__name__)\n\napp.layout = html.Div([WebSocket(id="ws"), dcc.Graph(id="graph")])\n\napp.clientside_callback(\n    """\nfunction(msg) {\n    if (msg) {\n        const data = JSON.parse(msg.data);\n        return {data: [{y: data, type: "scatter"}]};\n    } else {\n        return {};\n    }\n}""",\n    Output("graph", "figure"),\n    [Input("ws", "message")],\n)\n\n\n@app.server.websocket("/ws")\nasync def ws():\n    while True:\n        output = json.dumps([random.randint(200, 1000) for _ in range(6)])\n        await websocket.send(output)\n        await asyncio.sleep(1)\n\n\nif __name__ == "__main__":\n    app.run_server()\n```\n\n### Motivation\n\nIn addition to all the advantages of writing async code, `async-dash` enables you to:\n\n1. run truly asynchronous callbacks\n2. use websockets, server sent events, etc. without needing to monkey patch the Python standard library\n3. use `quart` / [`fastapi`](https://fastapi.tiangolo.com) / [`starlette`](https://www.starlette.io) frameworks with\n   your dash apps side by side\n4. use HTTP/2 (especially server push) if you use it HTTP/2 enabled server such\n   as [`hypercorn`](https://pgjones.gitlab.io/hypercorn/).\n\n### Caveats\n\nI\'m maintaining this library as a proof of concept for now. It should not be used for production. You can see the\ndeviation from `dash` [here](https://github.com/snehilvj/async-dash/compare/dev...snehilvj:async-dash).\n\nIf you do decide to use it, I\'d love to hear your feedback.\n\n### Alternatives\n\n#### [dash-devices](https://github.com/richlegrand/dash_devices)\n\n`dash-devices` is another async port based on `quart`. It\'s capable of using websockets even for callbacks, which makes\nit way faster than either of `dash` or `async-dash`. However, the library stands outdated at the time this document was\nlast updated.\n\n**PS:** `async-dash` is highly inspired by the `dash-devices`. Difference being that `async-dash` tries to follow `dash`\nas close as possible.\n\n### Known Issues\n\n1. Exception handling in callbacks in **debug mode** is broken. So its disabled internally.\n\n### TODO\n\n1. Write examples/articles showcasing the use cases for asynchronous `dash`.\n2. Gather reviews and feedback from the Dash Community.\n',
    'author': 'Snehil Vijay',
    'author_email': 'snehilvj@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/snehilvj/async-dash',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
