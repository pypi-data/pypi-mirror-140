# Nautobot Cable Utilities

Utilities for working with cables in Nautobot. Enables you to change cable
endpoints and work with cable templates.

Please note that this plugin uses internal Nautobot components, which is
explicitly discouraged by the documentation. We promise to keep the plugin up
to date, but the latest version might break on unsupported Nautobot version.
Your mileage may vary.

## Installation

The plugin can be found on [pypi](https://pypi.org/project/nautobot-cable-utils).
You should therefore be able to install it using `pip`:

```
pip install nautobot-cable-utils
```

Make sure to use the same version of `pip` that manages Nautobot, so if you’ve
set up a virtual environment, you will have to use `<venv>/bin/pip` instead.

After that, you should be able to install the plugin as described in [the
Nautobot documentation](https://nautobot.readthedocs.io/en/stable/plugins/). No
change to `PLUGINS_CONFIG` is necessary.

## Usage

This plugin has two main purposes: [reconnecting cables](#reconnecting-cables)
and [working with cable templates](#working-with-cable-templates).

### Reconnecting cables

If you want to reconnect a cable, just go to its detail view. There should be a
button called `Reconnect` that will send you to a form in which you can change
cable endpoints.

<img alt="Reconnect button" src="./docs/reconnect_button.png" width="150">

The form that it will send you to is fairly similar to the cable creation view,
but it will not allow you to edit the cable’s properties.

![Reconnect form](./docs/reconnect_form.png)

### Working with cable templates

Cable templates can be found under `Plugins`, where you will be able to add them
one by one or import them via CSV (both buttons next to `Cable templates`). They
have all the same properties as regular cables, plus a cable number.

<img alt="Cable template form" src="./docs/template_form.png" width="500">

Cable templates can be used in any planned cable. If you navigate to that
cable’s detail view, an additional button named `Commission` will appear.

<img alt="Commission button" src="./docs/commission_button.png" width="150">

If you click on it, you will be able to select the cable template you want to
use for it (by cable number). The cable takes on the properties of the template
(length, color, etc.) and the template will not be selectable again for future
cables.

<hr/>

Have fun!
