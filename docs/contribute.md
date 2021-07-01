# Contribute

## Getting started

To start playing with Marion, you should build it using the `bootstrap` Make
target:

```
$ make bootstrap
```

This will build a Docker image that will run Marion in a Django sandbox, start
the `postgresql` docker compose service and run database migration.

Once finished, you can start Django's development server using:

```
$ make run
```

The REST API development server should be up and running at:
[http://localhost:8000/api/documents/requests/](http://localhost:8000/api/documents/requests/)

You can follow the web server logs using:

```
$ make logs
```

## Lint your code

To run python linters, use the `lint` Make target:

```
$ make lint
```

Linters can be run separately using the `lint-{{ linter }}` Make rule, _e.g_:

```
$ make lint-pylint
```

You can list all linters using:

```
$ make help | grep lint- | sort
```

If you need to run `pylint` with custom arguments, we provide an helper for this:

```
$ bin/pylint
```

## Run tests

Running tests with `pytest` can be achieved using:

```
$ make test
```

But we also provide an helper to add custom arguments to `pytest` calls (_e.g._
calling a specific test pattern):

```
$ bin/pytest -x -k test_foo_issuer
```

## Write documentation

Documentation sources lie in the `docs/` directory of the project. It is
generated using [MkDocs](https://www.mkdocs.org/). We provide Make rules to use
it:

```bash
# Build the documentation
$ make docs-build

# Run the documentation development server
$ make docs-serve
```

The documentation development server is then accessible on your browser at the 
following address: [http://localhost:8001](http://localhost:8001).

> Note that the documentation is automatically built by the CI platform we use,
> so you don't need to manually deploy it.

## Misc

You will find the complete list of useful commands using:

```
$ make help
```

## Git conventions

In addition to linting and tests, when creating a Pull Request, be sure to title
and format your git commit messages appropriately using the guidelines at 
[FUN with Git](https://openfun.gitbooks.io/handbook/content/git.html)

## CHANGELOG entries

Finally, be sure to add an entry to CHANGELOG with the additions, fixes, and
removals you have made in the pull request.