# How to publish a release

Releases are automated by [`.github/workflows/release.yml`](.github/workflows/release.yml).
Publishing to PyPI uses [trusted publishing](https://docs.pypi.org/trusted-publishers/), so no
API token is needed, but the repository must have a `release` environment configured.

## 1. Start the release

From the [Actions tab](https://github.com/MODFLOW-ORG/modflowapi/actions/workflows/release.yml),
select **Run workflow** and fill in the form:

| Input | Description |
|:--|:--|
| `branch` | Branch to release from. Defaults to `develop`. |
| `bump` | Version increment relative to the latest release tag: `minor` (default), `patch`, `major`, or `dev` to release the current development version as-is. |
| `version` | Explicit version number, e.g. `0.3.0`. Overrides `bump`. |
| `run_tests` | Run the test suite before drafting the release. Defaults to true. |

This can also be done from the command line, for instance:

```shell
gh workflow run release.yml -f branch=develop -f bump=minor
```

The workflow creates a `v<version>` release branch, updates the version number, regenerates the
changelog with [git-cliff](https://git-cliff.org/), runs the tests, and opens a draft pull request
into `main`.

A release can alternatively be started by pushing a release branch named `v<major>.<minor>.<patch>`.

## 2. Review and approve

Review the release pull request, in particular `HISTORY.md`. Mark it ready for review and merge it
into `main`. Merge rather than squash, to preserve the commit history.

## 3. Automatic steps

Merging the release pull request into `main` triggers jobs that:

1. tag the release and create a GitHub release, with notes taken from `HISTORY.md`
2. build the package and publish it to [PyPI](https://pypi.org/project/modflowapi)
3. open a follow-up pull request resetting `develop` from `main`, with the version number
   incremented to the next development version

Merge the reset pull request to finish the release.

## Changelog conventions

Release notes are generated from commit messages, so commits merged to `develop` should follow the
[conventional commits](https://www.conventionalcommits.org/) format (`feat:`, `fix:`, `refactor:`,
etc.). Commits that do not follow the convention are omitted from the changelog. See
[`cliff.toml`](cliff.toml) for the commit groups and which ones are skipped.
