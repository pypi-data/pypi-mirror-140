# Release documentation

## How it works

GitLab CI automation will automatically upload wheels to PyPI on tagged versions.
So we need to do a Git tag.
At the same time, the wheel versions come out of `Cargo.toml` (via the [Maturin packaging tool](https://maturin.rs/)).

So we use [bump2version](https://github.com/c4urself/bump2version/) to both update `Cargo.toml` and add a matching Git tag at the same time.

## How to do it

1. `pip install bump2version`
2. Make sure you're on `main` git branch.
2. `bump2version --current-version 0.x.y minor`
3. `git push --tags`
