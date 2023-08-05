# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'EmailTranslationArgs',
]

@pulumi.input_type
class EmailTranslationArgs:
    def __init__(__self__, *,
                 language: pulumi.Input[str],
                 subject: pulumi.Input[str],
                 template: pulumi.Input[str]):
        """
        :param pulumi.Input[str] language: The language to map the template to.
        :param pulumi.Input[str] subject: The email subject line.
        :param pulumi.Input[str] template: The email body.
        """
        pulumi.set(__self__, "language", language)
        pulumi.set(__self__, "subject", subject)
        pulumi.set(__self__, "template", template)

    @property
    @pulumi.getter
    def language(self) -> pulumi.Input[str]:
        """
        The language to map the template to.
        """
        return pulumi.get(self, "language")

    @language.setter
    def language(self, value: pulumi.Input[str]):
        pulumi.set(self, "language", value)

    @property
    @pulumi.getter
    def subject(self) -> pulumi.Input[str]:
        """
        The email subject line.
        """
        return pulumi.get(self, "subject")

    @subject.setter
    def subject(self, value: pulumi.Input[str]):
        pulumi.set(self, "subject", value)

    @property
    @pulumi.getter
    def template(self) -> pulumi.Input[str]:
        """
        The email body.
        """
        return pulumi.get(self, "template")

    @template.setter
    def template(self, value: pulumi.Input[str]):
        pulumi.set(self, "template", value)


