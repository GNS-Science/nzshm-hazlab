# Contributing

This project is provided by
**[GNS Science | Te Pū Ao](https://github.com/GNS-Science/)**
to support the wider seismic hazard analysis community.

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at [https://github.com/GNS-Science/nzshm-hazlab/issues](https://github.com/GNS-Science/nzshm-hazlab/issues).

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

nzshm-hazlab could always use more documentation, whether as part of the
official nzshm-hazlab docs, in docstrings, or even on the web in blog posts,
articles, and such.

The project has Markdown-based documentation, using
[MkDocs](https://www.mkdocs.org/user-guide/) with
[mkdocstrings-python](https://mkdocstrings.github.io/python/) in the
[Google](https://mkdocstrings.github.io/griffe/docstrings/) style.

### Submit Feedback

The best way to send feedback is to file an issue at [https://github.com/GNS-Science/nzshm-hazlab/issues](https://github.com/GNS-Science/nzshm-hazlab/issues).

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.

## Get Started!

* [Install nzshm-hazlab from source code](docs/installation.md#from-source-code)
* [Run the tests](docs/testing.md)
* [Fix bugs or contribute features](https://github.com/GNS-Science/nzshm-hazlab/issues)

### Enable the git hooks

This repo ships a `pre-push` hook in `.githooks/` that blocks pushing a `v*`
release tag if `CHANGELOG.md` does not yet contain a section for that version.
It is **not** active by default — git ignores any hooks directory other than
`.git/hooks/` until you opt in.

After cloning (one time per checkout):

```console
$ git config core.hooksPath .githooks
```

This setting lives in `.git/config` and is local to your checkout — it is not
shared and not committed.

To verify it is active:

```console
$ git config --get core.hooksPath
.githooks
```

You can bypass the hook with `git push --no-verify` if you need to, but the
same check runs in CI (`verify-changelog` job in
`.github/workflows/release.yml`) and will fail the release there if the
CHANGELOG section is missing.

## Releasing

Versioning uses [hatch-vcs](https://github.com/ofek/hatch-vcs) — the package
version is derived from the latest `v*` git tag at build time, so there is no
version string to bump in source. To cut a release:

1. Move the relevant entries from `## [Unreleased]` in `CHANGELOG.md` into a
   new section headed `## [X.Y.Z] - YYYY-MM-DD`. Commit on `main`.
2. Tag and push:

   ```console
   $ git tag vX.Y.Z
   $ git push --tags
   ```

3. The push triggers `.github/workflows/release.yml`, which runs the
   `verify-changelog` guard and then builds + publishes via the reusable
   `python-release-uv.yml` workflow.

If the local `pre-push` hook (or the CI guard) fails because the CHANGELOG
section is missing, fix the CHANGELOG, delete the tag (`git tag -d vX.Y.Z`),
and re-tag the new commit.
