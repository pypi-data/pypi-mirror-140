# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'EmailTranslation',
]

@pulumi.output_type
class EmailTranslation(dict):
    def __init__(__self__, *,
                 language: str,
                 subject: str,
                 template: str):
        """
        :param str language: The language to map the template to.
        :param str subject: The email subject line.
        :param str template: The email body.
        """
        pulumi.set(__self__, "language", language)
        pulumi.set(__self__, "subject", subject)
        pulumi.set(__self__, "template", template)

    @property
    @pulumi.getter
    def language(self) -> str:
        """
        The language to map the template to.
        """
        return pulumi.get(self, "language")

    @property
    @pulumi.getter
    def subject(self) -> str:
        """
        The email subject line.
        """
        return pulumi.get(self, "subject")

    @property
    @pulumi.getter
    def template(self) -> str:
        """
        The email body.
        """
        return pulumi.get(self, "template")


