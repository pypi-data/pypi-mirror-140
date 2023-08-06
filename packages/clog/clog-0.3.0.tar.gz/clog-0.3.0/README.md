clog
====

This project is now simply a shortcut for using [rich](https://github.com/Textualize/rich).

_If you want to save yourself a dependency, just use `rich`._


## Usage

Pass any data into clog and it'll get pretty-printed.

    >>> from clog import clog
    >>> data = {'here': 'is some data'}
    >>> clog(data)

You can also give it a title:

    >>> clog(data, title="My Data")

Or change the color:

    >>> clog(data, title="My Data", color="red")


### Colors

This library uses `rich` under the hood, so it theoretically supports
any color that `rich` supports.


## Disclaimer

The `clog` function is now simply a wrapper around:

```python
from rich.panel import Panel
from rich.pretty import Pretty
from rich import print

print(Panel(Pretty(msg), title=title, subtitle=subtitle, border_style=color))
```

So, seriously... just use `rich`.