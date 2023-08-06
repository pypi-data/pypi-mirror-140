# Django serve SPA

Serve SPAs with Django

## Quick start

```shell
pip install dj-kaos-spa
```

Build your SPA and copy the contents of the build into `SPA_ROOT` (e.g. `path/to/django/spa/`).

```python
# settings.py
SPA_ROOT = BASE_DIR / 'spa'  # where the built SPA code will live
SPA_URL = ''  # To serve from /

# urls.py
from kaos_spa import settings as spa_settings

urlpatterns += [
    path(spa_settings.SPA_URL, include('kaos_spa.urls')),
]
```

Runserver, and visit `SPA_URL` (`/` by default). Your SPA will show up.

## Notes

`dj-kaos-spa` is meant to be used for development and isn't recommended for production use. For production, serve the
SPA on its own using tools like [npm serve](https://www.npmjs.com/package/serve).

`dj-kaos-spa` is mostly tested with create-react-app apps, but in theory should work with any SPA.

## Utility scripts

`dj-kaos-spa` comes bundled with some utility scripts that makes building and copying your SPA project much more
convenient.

### `build-spa`

Build your SPA and put it in your django project.

Set the following environment variables

```shell
# required
SPA_SRC_DIR=/path/to/your/spa/
SPA_IN_DJANGO_DIR=/path/to/your/django/project/spa/  # what the SPA_ROOT django setting refers to

# optional
SPA_URL  # If you are not serving on /
SPA_BUILD_CMD="npm run build"
SPA_BUILD_DIR_PATH='build/'  # Where the build command builds the app in its src directory
```

run

```shell
build-spa
```

It'll build your SPA and put it in the right folder in your django project.

### `cm-spa-build`

Commits the new build into Git with commit message from arg. If no arg is supplied, commit message defaults to "New SPA
build".

Set the following environment variables

```shell
# required
SPA_IN_DJANGO_DIR=/path/to/your/django/project/spa/  # what the SPA_ROOT django setting refers to
```

run

```shell
cm-spa-build
```

## Development and Testing

### IDE Setup

Add the `example` directory to the `PYTHONPATH` in your IDE to avoid seeing import warnings in the `tests` modules. If
you are using PyCharm, this is already set up.

### Running the Tests

Install requirements

```
pip install -r requirements.txt
```

For local environment

```
pytest
```

For all supported environments

```
tox
```
