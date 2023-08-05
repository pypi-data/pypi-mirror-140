# cz-github-linear-conventional

**cz-github-linear-conventional** is a plugin for the [**commitizen tools**](https://github.com/commitizen-tools/commitizen), a toolset that helps you to create [**conventional commit messages**](https://www.conventionalcommits.org/en/v1.0.0/). Since the structure of conventional commits messages is standardized they are machine readable and allow commitizen to automaticially calculate and tag [**semantic version numbers**](https://semver.org/) as well as create **CHANGELOG.md** files for your releases.

This plugin extends the commitizen tools by:
- **require a Linear issue id** in the commit message
- **create links to GitHub** commits in the CHANGELOG.md
- **create links to Linear** issues in the CHANGELOG.md

When you call commitizen `commit` the scope is assumed from the current active branch. The Linear issue id should be available in the branch name for this. (See example below for automatically parsed issue id)
```
> cz commit
? Select the type of change you are committing fix: A bug fix. Correlates with PATCH in SemVer
? Linear issue number: cae-123
...
```

The changelog created by cz (`cz bump --changelog`)will contain links to the commits in Github and the Linear issues.
```markdown
## 1.1.0 (2022-02-15)

### Feat

- **[cae-62](https://linear.app/caesari/issue/cae-62)**: adding support for linear issue ids because it is nice [8adc3](https://github.com/ThimDeveloper/cz-github-linear-conventional/commit/8adc39bc0cb35fff07f5c9c4b906b1b3eefd3f56)

``` 


## Installation

Install with pip
`python -m pip install cz-github-linear-conventional` 

You need to use a cz config file that has the **required** additional values `linear_base_url` and `github_repo`. The scope or prefix for your linear issues will automatically be parsed from the current active branch and added to the commit message. This allows for automatic linking by the linear.app bot if that is set up for your linear project.

Example `.cz.yaml` config for this repository
```yaml
commitizen:
  name: cz_github_linear_conventional
  tag_format: $version
  version: 1.0.0
  linear_base_url: https://linear.app/caesari
  github_repo: ThimDeveloper/cz-github-linear-conventional

```

### pre-commit
Add this plugin to the dependencies of your commit message linting with `pre-commit`. 

Example `.pre-commit-config.yaml` file.
```yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v2.17.13
    hooks:
      - id: commitizen
        stages: [commit-msg]
        additional_dependencies: [cz-github-linear-conventional]
```
Install the hook with 
```bash
pre-commit install --hook-type commit-msg
```

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
This plugin would not have been possible without the fantastic work from:
* [commitizen tools](https://github.com/commitizen-tools/commitizen)
* [conventional_JIRA](https://github.com/Crystalix007/conventional_jira)
* [conventional_GITHUB_JIRA](https://github.com/apheris/cz-github-jira-conventional)
