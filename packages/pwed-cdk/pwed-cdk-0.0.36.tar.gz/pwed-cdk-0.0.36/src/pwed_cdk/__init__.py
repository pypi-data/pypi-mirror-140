'''
# pwed-cdk

[![build](https://github.com/pwed/pwed-cdk/actions/workflows/build.yaml/badge.svg)](https://github.com/pwed/pwed-cdk/actions/workflows/build.yaml)

A library of AWS CDK constructs that I have created

## Disclaimer

This repository is in early development and can be restructured at any time.
A much higher level of stability will be targeted after 1.0.0 release

## Install

```sh
npm i pwed-cdk
```

## Constructs

1. static-site

   1. Is a simple static site that will automatically upload assets to s3 and serve them with CloudFront. Any pushed changed files will get invalidated from the CloudFront cache.
2. bastion

   1. windows-instance

      1. A windows instance that can be signed into using fleet manager for a zero surface area RDP bastion.
   2. permission-set

      1. AWS SSO permission set with the minimum permissions to give access to SSM and Fleet Manager
      2. Can be locked down with Tags if you want environment level access

## Coming soon

1. Non SSO based access for bastion
2. Hugo extension for static-site to auto build and deploy your static site
3. Auto push to NPM

   * github action for running jest
4. JSII for python

   * pip publish
5. readme badges
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

__all__: typing.List[typing.Any] = []

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import pwed_bastion
from . import pwed_static_site
