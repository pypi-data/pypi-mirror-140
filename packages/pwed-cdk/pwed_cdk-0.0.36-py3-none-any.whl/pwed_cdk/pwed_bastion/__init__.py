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
import aws_cdk.aws_iam
import constructs


class BastionAccessPolicy(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_bastion.BastionAccessPolicy",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param security_tag: 

        :stability: experimental
        '''
        props = BastionAccessPolicyProps(security_tag=security_tag)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> aws_cdk.aws_iam.PolicyDocument:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.PolicyDocument, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: aws_cdk.aws_iam.PolicyDocument) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.BastionAccessPolicyProps",
    jsii_struct_bases=[],
    name_mapping={"security_tag": "securityTag"},
)
class BastionAccessPolicyProps:
    def __init__(self, *, security_tag: typing.Optional[aws_cdk.Tag] = None) -> None:
        '''
        :param security_tag: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if security_tag is not None:
            self._values["security_tag"] = security_tag

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BastionAccessPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


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
        *,
        permission_set_name: builtins.str,
        sso_instance_arn: builtins.str,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        session_duration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param permission_set_name: 
        :param sso_instance_arn: 
        :param security_tag: 
        :param session_duration: 

        :stability: experimental
        '''
        props = BastionPermissionSetProps(
            permission_set_name=permission_set_name,
            sso_instance_arn=sso_instance_arn,
            security_tag=security_tag,
            session_duration=session_duration,
        )

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


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.BastionPermissionSetProps",
    jsii_struct_bases=[],
    name_mapping={
        "permission_set_name": "permissionSetName",
        "sso_instance_arn": "ssoInstanceArn",
        "security_tag": "securityTag",
        "session_duration": "sessionDuration",
    },
)
class BastionPermissionSetProps:
    def __init__(
        self,
        *,
        permission_set_name: builtins.str,
        sso_instance_arn: builtins.str,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        session_duration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param permission_set_name: 
        :param sso_instance_arn: 
        :param security_tag: 
        :param session_duration: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "permission_set_name": permission_set_name,
            "sso_instance_arn": sso_instance_arn,
        }
        if security_tag is not None:
            self._values["security_tag"] = security_tag
        if session_duration is not None:
            self._values["session_duration"] = session_duration

    @builtins.property
    def permission_set_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("permission_set_name")
        assert result is not None, "Required property 'permission_set_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sso_instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("sso_instance_arn")
        assert result is not None, "Required property 'sso_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    @builtins.property
    def session_duration(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("session_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BastionPermissionSetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


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
        *,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        shutdown_schedule: typing.Optional[builtins.str] = None,
        timezone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param security_tag: 
        :param shutdown_schedule: 
        :param timezone: 

        :stability: experimental
        '''
        props = ScheduleShutdownProps(
            security_tag=security_tag,
            shutdown_schedule=shutdown_schedule,
            timezone=timezone,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.ScheduleShutdownProps",
    jsii_struct_bases=[],
    name_mapping={
        "security_tag": "securityTag",
        "shutdown_schedule": "shutdownSchedule",
        "timezone": "timezone",
    },
)
class ScheduleShutdownProps:
    def __init__(
        self,
        *,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        shutdown_schedule: typing.Optional[builtins.str] = None,
        timezone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param security_tag: 
        :param shutdown_schedule: 
        :param timezone: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if security_tag is not None:
            self._values["security_tag"] = security_tag
        if shutdown_schedule is not None:
            self._values["shutdown_schedule"] = shutdown_schedule
        if timezone is not None:
            self._values["timezone"] = timezone

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    @builtins.property
    def shutdown_schedule(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("shutdown_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScheduleShutdownProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_ec2.IInstance)
class WindowsBastion(
    aws_cdk.Resource,
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
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        vpc_subnets: aws_cdk.aws_ec2.SubnetSelection,
        create_key_pair: typing.Optional[builtins.bool] = None,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        windows_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: 
        :param vpc_subnets: 
        :param create_key_pair: 
        :param security_tag: 
        :param windows_packages: 

        :stability: experimental
        '''
        props = WindowsBastionProps(
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            create_key_pair=create_key_pair,
            security_tag=security_tag,
            windows_packages=windows_packages,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceAvailabilityZone")
    def instance_availability_zone(self) -> builtins.str:
        '''(experimental) The availability zone the instance was launched in.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceAvailabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        '''(experimental) The instance's ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePrivateDnsName")
    def instance_private_dns_name(self) -> builtins.str:
        '''(experimental) Private DNS name for this instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePrivateDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePrivateIp")
    def instance_private_ip(self) -> builtins.str:
        '''(experimental) Private IP for this instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePrivateIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePublicDnsName")
    def instance_public_dns_name(self) -> builtins.str:
        '''(experimental) Publicly-routable DNS name for this instance.

        (May be an empty string if the instance does not have a public name).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePublicDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePublicIp")
    def instance_public_ip(self) -> builtins.str:
        '''(experimental) Publicly-routable IP  address for this instance.

        (May be an empty string if the instance does not have a public IP).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePublicIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, jsii.get(self, "securityGroup"))


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.WindowsBastionProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "create_key_pair": "createKeyPair",
        "security_tag": "securityTag",
        "windows_packages": "windowsPackages",
    },
)
class WindowsBastionProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        vpc_subnets: aws_cdk.aws_ec2.SubnetSelection,
        create_key_pair: typing.Optional[builtins.bool] = None,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        windows_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param vpc: 
        :param vpc_subnets: 
        :param create_key_pair: 
        :param security_tag: 
        :param windows_packages: 

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
            "vpc_subnets": vpc_subnets,
        }
        if create_key_pair is not None:
            self._values["create_key_pair"] = create_key_pair
        if security_tag is not None:
            self._values["security_tag"] = security_tag
        if windows_packages is not None:
            self._values["windows_packages"] = windows_packages

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def vpc_subnets(self) -> aws_cdk.aws_ec2.SubnetSelection:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        assert result is not None, "Required property 'vpc_subnets' is missing"
        return typing.cast(aws_cdk.aws_ec2.SubnetSelection, result)

    @builtins.property
    def create_key_pair(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("create_key_pair")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''
        :stability: experimental
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    @builtins.property
    def windows_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("windows_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WindowsBastionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BastionAccessPolicy",
    "BastionAccessPolicyProps",
    "BastionPermissionSet",
    "BastionPermissionSetProps",
    "ScheduleShutdown",
    "ScheduleShutdownProps",
    "WindowsBastion",
    "WindowsBastionProps",
]

publication.publish()
