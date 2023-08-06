AWS CDK setups up a Custom Resource via Cloud Formation which sets
the AWS IAM Account Alias

# P6Namer

* [P6Namer](#p6namer)

  * [LICENSE](#license)
  * [CI/CD](#cicd)
  * [Distributions](#distributions)
  * [Summary](#summary)
  * [Contributing](#contributing)
  * [Code of Conduct](#code-of-conduct)
  * [Changes](#changes)
  * [Usage](#usage)
  * [Architecture](#architecture)
  * [Author](#author)

## LICENSE

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0) [![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/p6m7g8/p6-namer)

## CI/CD

![GitHub Build Workflow Status](https://img.shields.io/github/workflow/status/p6m7g8/p6-namer/Build) ![GitHub Release Workflow Statuss](https://github.com/p6m7g8/p6-namer/workflows/Release/badge.svg)
![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/p6m7g8/p6-namer) ![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=p6m7g8_p6-namer&metric=alert_status)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/p6m7g8/p6-namer) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/p6m7g8/p6-namer)

## Distributions

| Method | Version | Daily | Weekly | Monthly | Yearly | Total |
--------| --------| ------| -------| --------| -------|-------|
| NPM      | ![npm](https://img.shields.io/npm/v/p6-namer) |       | [![NPM Weekly Downloads](https://img.shields.io/npm/dw/p6-namer)](https://img.shields.io/npm/dw/p6-namer) | [![NPM Monthly Downloads](https://img.shields.io/npm/dm/p6-namer)](https://img.shields.io/npm/dm/p6-namer) | [![NPM Yearly Downloads](https://img.shields.io/npm/dy/p6-namer)](https://img.shields.io/npm/dy/p6-namer) | [![NPM Total Downloads](https://img.shields.io/npm/dt/p6-namer)](https://img.shields.io/npm/dt/p6-namer) |
| PYPI      | ![PyPI](https://img.shields.io/pypi/v/p6-namer) | ![PyPI - Downloads](https://img.shields.io/pypi/dd/p6-namer) | ![PyPI - Downloads](https://img.shields.io/pypi/dw/p6-namer) | ![PyPI - Downloads](https://img.shields.io/pypi/dm/p6-namer)         |       |        |
| Nuget      | ![Nuget](https://img.shields.io/nuget/v/P6m7g8.P6Namer) |       |        |         |       | ![NuGet Downloads](https://img.shields.io/nuget/dt/P6m7g8.P6Namer.svg) |
| Maven Central | ![Maven Central](https://img.shields.io/maven-central/v/com.github.p6m7g8/p6-namer) |       | ![Maven](https://jitpack.io/v/com.github.p6m7g8/p6-namer/week.svg) | ![Maven](https://jitpack.io/v/com.github.p6m7g8/p6-namer/month.svg)         |       |        |
| GoLang     |         |       |        |         |       |        |
| Kotlin     |         |       |        |         |       |        |

## Summary

Deploys Custom Resource backed by a Lambda function with `iam:CreateAccountAlias` permissions.
This function is idempotent so can be re-run with the same input.

## Contributing

* [How to Contribute](CONTRIBUTING.md)

## Code of Conduct

* [Code of Conduct](CODE_OF_CONDUCT.md)

## Changes

* [Change Log](CHANGELOG.md)

## Usage

```python
...

import { P6Namer } from 'p6-namer';

new P6Namer(this, 'AccountAlias', {
  accountAlias: 'THE-ALIAS',
});
```

## Architecture

![./assets/diagram.png](./assets/diagram.png)

## Author

Philip M. Gollucci [pgollucci@p6m7g8.com](mailto:pgollucci@p6m7g8.com)
