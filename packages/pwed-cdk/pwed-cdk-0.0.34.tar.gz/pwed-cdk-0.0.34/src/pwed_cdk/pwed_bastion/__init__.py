'''
# bastion

A set of constructs to create and access bastion hosts using SSO or IAM. By using session manager for shell access and GUI Connect for Windows RDP access, no ports need to be exposed to the internet and all access can be managed and audited through AWS services.

## Todo

* Allow full custom userdata
* Allow choco installs
* fix aws cli not installing with winget
* tests
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import aws_cdk
import aws_cdk.aws_ec2
import constructs


class BastionPermissionSet(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_bastion.BastionPermissionSet",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: "IBastionPermissionSetProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="assign")
    def assign(
        self,
        account_id: builtins.str,
        principal_id: builtins.str,
        principal_type: builtins.str,
    ) -> None:
        '''
        :param account_id: -
        :param principal_id: -
        :param principal_type: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "assign", [account_id, principal_id, principal_type]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityTag")
    def security_tag(self) -> aws_cdk.Tag:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.Tag, jsii.get(self, "securityTag"))

    @security_tag.setter
    def security_tag(self, value: aws_cdk.Tag) -> None:
        jsii.set(self, "securityTag", value)


@jsii.interface(jsii_type="pwed-cdk.pwed_bastion.IBastionPermissionSetProps")
class IBastionPermissionSetProps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionSetName")
    def permission_set_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @permission_set_name.setter
    def permission_set_name(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssoInstanceArn")
    def sso_instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @sso_instance_arn.setter
    def sso_instance_arn(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityTag")
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        ...

    @security_tag.setter
    def security_tag(self, value: typing.Optional[aws_cdk.Tag]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionDuration")
    def session_duration(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @session_duration.setter
    def session_duration(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IBastionPermissionSetPropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "pwed-cdk.pwed_bastion.IBastionPermissionSetProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionSetName")
    def permission_set_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "permissionSetName"))

    @permission_set_name.setter
    def permission_set_name(self, value: builtins.str) -> None:
        jsii.set(self, "permissionSetName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssoInstanceArn")
    def sso_instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "ssoInstanceArn"))

    @sso_instance_arn.setter
    def sso_instance_arn(self, value: builtins.str) -> None:
        jsii.set(self, "ssoInstanceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityTag")
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.Tag], jsii.get(self, "securityTag"))

    @security_tag.setter
    def security_tag(self, value: typing.Optional[aws_cdk.Tag]) -> None:
        jsii.set(self, "securityTag", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionDuration")
    def session_duration(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionDuration"))

    @session_duration.setter
    def session_duration(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "sessionDuration", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBastionPermissionSetProps).__jsii_proxy_class__ = lambda : _IBastionPermissionSetPropsProxy


@jsii.interface(jsii_type="pwed-cdk.pwed_bastion.IScheduleShutdownProps")
class IScheduleShutdownProps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityTag")
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        ...

    @security_tag.setter
    def security_tag(self, value: typing.Optional[aws_cdk.Tag]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shutdownSchedule")
    def shutdown_schedule(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @shutdown_schedule.setter
    def shutdown_schedule(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timezone")
    def timezone(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @timezone.setter
    def timezone(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IScheduleShutdownPropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "pwed-cdk.pwed_bastion.IScheduleShutdownProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityTag")
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.Tag], jsii.get(self, "securityTag"))

    @security_tag.setter
    def security_tag(self, value: typing.Optional[aws_cdk.Tag]) -> None:
        jsii.set(self, "securityTag", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shutdownSchedule")
    def shutdown_schedule(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shutdownSchedule"))

    @shutdown_schedule.setter
    def shutdown_schedule(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "shutdownSchedule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timezone")
    def timezone(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timezone"))

    @timezone.setter
    def timezone(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "timezone", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IScheduleShutdownProps).__jsii_proxy_class__ = lambda : _IScheduleShutdownPropsProxy


@jsii.interface(jsii_type="pwed-cdk.pwed_bastion.IWindowsBastionProps")
class IWindowsBastionProps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        ...

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnets")
    def vpc_subnets(self) -> aws_cdk.aws_ec2.SubnetSelection:
        '''
        :stability: experimental
        '''
        ...

    @vpc_subnets.setter
    def vpc_subnets(self, value: aws_cdk.aws_ec2.SubnetSelection) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createKeyPair")
    def create_key_pair(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        ...

    @create_key_pair.setter
    def create_key_pair(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityTag")
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        ...

    @security_tag.setter
    def security_tag(self, value: typing.Optional[aws_cdk.Tag]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="windowsPackages")
    def windows_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        ...

    @windows_packages.setter
    def windows_packages(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        ...


class _IWindowsBastionPropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "pwed-cdk.pwed_bastion.IWindowsBastionProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        jsii.set(self, "vpc", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnets")
    def vpc_subnets(self) -> aws_cdk.aws_ec2.SubnetSelection:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.SubnetSelection, jsii.get(self, "vpcSubnets"))

    @vpc_subnets.setter
    def vpc_subnets(self, value: aws_cdk.aws_ec2.SubnetSelection) -> None:
        jsii.set(self, "vpcSubnets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createKeyPair")
    def create_key_pair(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "createKeyPair"))

    @create_key_pair.setter
    def create_key_pair(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "createKeyPair", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityTag")
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.Tag], jsii.get(self, "securityTag"))

    @security_tag.setter
    def security_tag(self, value: typing.Optional[aws_cdk.Tag]) -> None:
        jsii.set(self, "securityTag", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="windowsPackages")
    def windows_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "windowsPackages"))

    @windows_packages.setter
    def windows_packages(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "windowsPackages", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWindowsBastionProps).__jsii_proxy_class__ = lambda : _IWindowsBastionPropsProxy


class ScheduleShutdown(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_bastion.ScheduleShutdown",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: typing.Optional[IScheduleShutdownProps] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id, props])


class WindowsBastion(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_bastion.WindowsBastion",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: IWindowsBastionProps,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, jsii.get(self, "securityGroup"))

    @security_group.setter
    def security_group(self, value: aws_cdk.aws_ec2.ISecurityGroup) -> None:
        jsii.set(self, "securityGroup", value)


__all__ = [
    "BastionPermissionSet",
    "IBastionPermissionSetProps",
    "IScheduleShutdownProps",
    "IWindowsBastionProps",
    "ScheduleShutdown",
    "WindowsBastion",
]

publication.publish()
