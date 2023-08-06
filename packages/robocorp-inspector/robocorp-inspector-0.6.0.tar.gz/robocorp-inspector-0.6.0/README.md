# Robocorp Inspector

Robocorp Inspector is a tool for exploring various user interfaces
and developing ways to target elements within them. An expression
that can target specific UI elemements is called a _locator_, and
these locators can be used to automate applications typically
used by humans.

## Development

The project uses `invoke` for overall project management, `poetry` for
python dependencies and environments, and `yarn` for Javascript dependencies
and building.

Both `invoke` and `poetry` should be installed via pip: `pip install poetry invoke`

- To see all possible tasks: `invoke --list`
- To run the project: `invoke run `

All source code is hosted on [GitHub](https://github.com/robocorp/inspector/).

## Usage

Robocorp Inspector is distributed as a Python package with all front-end
components compiled and included statically.

If the package (and all required dependencies) is installed manually,
it can be run with the command: `inspector`.

---

<p align="center">
  <img height="100" src="https://cdn.robocorp.com/brand/Logo/Dark%20logo%20transparent%20with%20buffer%20space/Dark%20logo%20transparent%20with%20buffer%20space.svg">
</p>
