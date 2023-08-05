# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from . import _utilities
import typing
# Export this package's modules as members:
from .admin_role_custom import *
from .admin_role_custom_assignments import *
from .admin_role_targets import *
from .app_group_assignments import *
from .app_oauth_api_scope import *
from .app_saml_app_settings import *
from .app_shared_credentials import *
from .app_signon_policy_rule import *
from .app_user_base_schema_property import *
from .app_user_schema_property import *
from .auth_server_claim_default import *
from .auth_server_default import *
from .authenticator import *
from .behaviour import *
from .captcha import *
from .captcha_org_wide_settings import *
from .domain import *
from .domain_certificate import *
from .domain_verification import *
from .email_sender import *
from .email_sender_verification import *
from .event_hook import *
from .event_hook_verification import *
from .factor_totp import *
from .get_app_group_assignments import *
from .get_app_signon_policy import *
from .get_app_user_assignments import *
from .get_auth_server_claim import *
from .get_auth_server_claims import *
from .get_authenticator import *
from .get_behaviour import *
from .get_behaviours import *
from .get_groups import *
from .get_network_zone import *
from .get_role_subscription import *
from .get_trusted_origins import *
from .get_user_security_questions import *
from .group_memberships import *
from .group_schema_property import *
from .link_definition import *
from .link_value import *
from .org_configuration import *
from .org_support import *
from .policy_mfa_default import *
from .policy_password_default import *
from .policy_profile_enrollment import *
from .policy_rule_profile_enrollment import *
from .provider import *
from .rate_limiting import *
from .resource_set import *
from .role_subscription import *
from .security_notification_emails import *
from .template_sms import *
from .threat_insight_settings import *
from .user_admin_roles import *
from .user_base_schema_property import *
from .user_factor_question import *
from .user_group_memberships import *
from .user_schema_property import *
from ._inputs import *
from . import outputs

# Make subpackages available:
if typing.TYPE_CHECKING:
    import pulumi_okta.app as __app
    app = __app
    import pulumi_okta.auth as __auth
    auth = __auth
    import pulumi_okta.config as __config
    config = __config
    import pulumi_okta.deprecated as __deprecated
    deprecated = __deprecated
    import pulumi_okta.factor as __factor
    factor = __factor
    import pulumi_okta.group as __group
    group = __group
    import pulumi_okta.idp as __idp
    idp = __idp
    import pulumi_okta.inline as __inline
    inline = __inline
    import pulumi_okta.network as __network
    network = __network
    import pulumi_okta.policy as __policy
    policy = __policy
    import pulumi_okta.profile as __profile
    profile = __profile
    import pulumi_okta.template as __template
    template = __template
    import pulumi_okta.trustedorigin as __trustedorigin
    trustedorigin = __trustedorigin
    import pulumi_okta.user as __user
    user = __user
else:
    app = _utilities.lazy_import('pulumi_okta.app')
    auth = _utilities.lazy_import('pulumi_okta.auth')
    config = _utilities.lazy_import('pulumi_okta.config')
    deprecated = _utilities.lazy_import('pulumi_okta.deprecated')
    factor = _utilities.lazy_import('pulumi_okta.factor')
    group = _utilities.lazy_import('pulumi_okta.group')
    idp = _utilities.lazy_import('pulumi_okta.idp')
    inline = _utilities.lazy_import('pulumi_okta.inline')
    network = _utilities.lazy_import('pulumi_okta.network')
    policy = _utilities.lazy_import('pulumi_okta.policy')
    profile = _utilities.lazy_import('pulumi_okta.profile')
    template = _utilities.lazy_import('pulumi_okta.template')
    trustedorigin = _utilities.lazy_import('pulumi_okta.trustedorigin')
    user = _utilities.lazy_import('pulumi_okta.user')

_utilities.register(
    resource_modules="""
[
 {
  "pkg": "okta",
  "mod": "app/autoLogin",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/autoLogin:AutoLogin": "AutoLogin"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/basicAuth",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/basicAuth:BasicAuth": "BasicAuth"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/bookmark",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/bookmark:Bookmark": "Bookmark"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/groupAssignment",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/groupAssignment:GroupAssignment": "GroupAssignment"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/oAuth",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/oAuth:OAuth": "OAuth"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/oAuthPostLogoutRedirectUri",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/oAuthPostLogoutRedirectUri:OAuthPostLogoutRedirectUri": "OAuthPostLogoutRedirectUri"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/oAuthRedirectUri",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/oAuthRedirectUri:OAuthRedirectUri": "OAuthRedirectUri"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/saml",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/saml:Saml": "Saml"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/securePasswordStore",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/securePasswordStore:SecurePasswordStore": "SecurePasswordStore"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/swa",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/swa:Swa": "Swa"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/threeField",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/threeField:ThreeField": "ThreeField"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/user",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/user:User": "User"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/userBaseSchema",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/userBaseSchema:UserBaseSchema": "UserBaseSchema"
  }
 },
 {
  "pkg": "okta",
  "mod": "app/userSchema",
  "fqn": "pulumi_okta.app",
  "classes": {
   "okta:app/userSchema:UserSchema": "UserSchema"
  }
 },
 {
  "pkg": "okta",
  "mod": "auth/server",
  "fqn": "pulumi_okta.auth",
  "classes": {
   "okta:auth/server:Server": "Server"
  }
 },
 {
  "pkg": "okta",
  "mod": "auth/serverClaim",
  "fqn": "pulumi_okta.auth",
  "classes": {
   "okta:auth/serverClaim:ServerClaim": "ServerClaim"
  }
 },
 {
  "pkg": "okta",
  "mod": "auth/serverPolicy",
  "fqn": "pulumi_okta.auth",
  "classes": {
   "okta:auth/serverPolicy:ServerPolicy": "ServerPolicy"
  }
 },
 {
  "pkg": "okta",
  "mod": "auth/serverPolicyClaim",
  "fqn": "pulumi_okta.auth",
  "classes": {
   "okta:auth/serverPolicyClaim:ServerPolicyClaim": "ServerPolicyClaim"
  }
 },
 {
  "pkg": "okta",
  "mod": "auth/serverPolicyRule",
  "fqn": "pulumi_okta.auth",
  "classes": {
   "okta:auth/serverPolicyRule:ServerPolicyRule": "ServerPolicyRule"
  }
 },
 {
  "pkg": "okta",
  "mod": "auth/serverScope",
  "fqn": "pulumi_okta.auth",
  "classes": {
   "okta:auth/serverScope:ServerScope": "ServerScope"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/authLoginApp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/authLoginApp:AuthLoginApp": "AuthLoginApp"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/bookmarkApp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/bookmarkApp:BookmarkApp": "BookmarkApp"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/idp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/idp:Idp": "Idp"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/mfaPolicy",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/mfaPolicy:MfaPolicy": "MfaPolicy"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/mfaPolicyRule",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/mfaPolicyRule:MfaPolicyRule": "MfaPolicyRule"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/oauthApp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/oauthApp:OauthApp": "OauthApp"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/oauthAppRedirectUri",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/oauthAppRedirectUri:OauthAppRedirectUri": "OauthAppRedirectUri"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/passwordPolicy",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/passwordPolicy:PasswordPolicy": "PasswordPolicy"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/passwordPolicyRule",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/passwordPolicyRule:PasswordPolicyRule": "PasswordPolicyRule"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/samlApp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/samlApp:SamlApp": "SamlApp"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/samlIdp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/samlIdp:SamlIdp": "SamlIdp"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/samlIdpSigningKey",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/samlIdpSigningKey:SamlIdpSigningKey": "SamlIdpSigningKey"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/securePasswordStoreApp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/securePasswordStoreApp:SecurePasswordStoreApp": "SecurePasswordStoreApp"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/signonPolicy",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/signonPolicy:SignonPolicy": "SignonPolicy"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/signonPolicyRule",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/signonPolicyRule:SignonPolicyRule": "SignonPolicyRule"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/socialIdp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/socialIdp:SocialIdp": "SocialIdp"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/swaApp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/swaApp:SwaApp": "SwaApp"
  }
 },
 {
  "pkg": "okta",
  "mod": "deprecated/threeFieldApp",
  "fqn": "pulumi_okta.deprecated",
  "classes": {
   "okta:deprecated/threeFieldApp:ThreeFieldApp": "ThreeFieldApp"
  }
 },
 {
  "pkg": "okta",
  "mod": "factor/factor",
  "fqn": "pulumi_okta.factor",
  "classes": {
   "okta:factor/factor:Factor": "Factor"
  }
 },
 {
  "pkg": "okta",
  "mod": "group/group",
  "fqn": "pulumi_okta.group",
  "classes": {
   "okta:group/group:Group": "Group"
  }
 },
 {
  "pkg": "okta",
  "mod": "group/membership",
  "fqn": "pulumi_okta.group",
  "classes": {
   "okta:group/membership:Membership": "Membership"
  }
 },
 {
  "pkg": "okta",
  "mod": "group/role",
  "fqn": "pulumi_okta.group",
  "classes": {
   "okta:group/role:Role": "Role"
  }
 },
 {
  "pkg": "okta",
  "mod": "group/roles",
  "fqn": "pulumi_okta.group",
  "classes": {
   "okta:group/roles:Roles": "Roles"
  }
 },
 {
  "pkg": "okta",
  "mod": "group/rule",
  "fqn": "pulumi_okta.group",
  "classes": {
   "okta:group/rule:Rule": "Rule"
  }
 },
 {
  "pkg": "okta",
  "mod": "idp/oidc",
  "fqn": "pulumi_okta.idp",
  "classes": {
   "okta:idp/oidc:Oidc": "Oidc"
  }
 },
 {
  "pkg": "okta",
  "mod": "idp/saml",
  "fqn": "pulumi_okta.idp",
  "classes": {
   "okta:idp/saml:Saml": "Saml"
  }
 },
 {
  "pkg": "okta",
  "mod": "idp/samlKey",
  "fqn": "pulumi_okta.idp",
  "classes": {
   "okta:idp/samlKey:SamlKey": "SamlKey"
  }
 },
 {
  "pkg": "okta",
  "mod": "idp/social",
  "fqn": "pulumi_okta.idp",
  "classes": {
   "okta:idp/social:Social": "Social"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/adminRoleCustom",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/adminRoleCustom:AdminRoleCustom": "AdminRoleCustom"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/adminRoleCustomAssignments",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/adminRoleCustomAssignments:AdminRoleCustomAssignments": "AdminRoleCustomAssignments"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/adminRoleTargets",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/adminRoleTargets:AdminRoleTargets": "AdminRoleTargets"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/appGroupAssignments",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/appGroupAssignments:AppGroupAssignments": "AppGroupAssignments"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/appOauthApiScope",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/appOauthApiScope:AppOauthApiScope": "AppOauthApiScope"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/appSamlAppSettings",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/appSamlAppSettings:AppSamlAppSettings": "AppSamlAppSettings"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/appSharedCredentials",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/appSharedCredentials:AppSharedCredentials": "AppSharedCredentials"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/appSignonPolicyRule",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/appSignonPolicyRule:AppSignonPolicyRule": "AppSignonPolicyRule"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/appUserBaseSchemaProperty",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/appUserBaseSchemaProperty:AppUserBaseSchemaProperty": "AppUserBaseSchemaProperty"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/appUserSchemaProperty",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/appUserSchemaProperty:AppUserSchemaProperty": "AppUserSchemaProperty"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/authServerClaimDefault",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/authServerClaimDefault:AuthServerClaimDefault": "AuthServerClaimDefault"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/authServerDefault",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/authServerDefault:AuthServerDefault": "AuthServerDefault"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/authenticator",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/authenticator:Authenticator": "Authenticator"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/behaviour",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/behaviour:Behaviour": "Behaviour"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/captcha",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/captcha:Captcha": "Captcha"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/captchaOrgWideSettings",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/captchaOrgWideSettings:CaptchaOrgWideSettings": "CaptchaOrgWideSettings"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/domain",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/domain:Domain": "Domain"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/domainCertificate",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/domainCertificate:DomainCertificate": "DomainCertificate"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/domainVerification",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/domainVerification:DomainVerification": "DomainVerification"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/emailSender",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/emailSender:EmailSender": "EmailSender"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/emailSenderVerification",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/emailSenderVerification:EmailSenderVerification": "EmailSenderVerification"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/eventHook",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/eventHook:EventHook": "EventHook"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/eventHookVerification",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/eventHookVerification:EventHookVerification": "EventHookVerification"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/factorTotp",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/factorTotp:FactorTotp": "FactorTotp"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/groupMemberships",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/groupMemberships:GroupMemberships": "GroupMemberships"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/groupSchemaProperty",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/groupSchemaProperty:GroupSchemaProperty": "GroupSchemaProperty"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/linkDefinition",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/linkDefinition:LinkDefinition": "LinkDefinition"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/linkValue",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/linkValue:LinkValue": "LinkValue"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/orgConfiguration",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/orgConfiguration:OrgConfiguration": "OrgConfiguration"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/orgSupport",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/orgSupport:OrgSupport": "OrgSupport"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/policyMfaDefault",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/policyMfaDefault:PolicyMfaDefault": "PolicyMfaDefault"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/policyPasswordDefault",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/policyPasswordDefault:PolicyPasswordDefault": "PolicyPasswordDefault"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/policyProfileEnrollment",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/policyProfileEnrollment:PolicyProfileEnrollment": "PolicyProfileEnrollment"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/policyRuleProfileEnrollment",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/policyRuleProfileEnrollment:PolicyRuleProfileEnrollment": "PolicyRuleProfileEnrollment"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/rateLimiting",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/rateLimiting:RateLimiting": "RateLimiting"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/resourceSet",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/resourceSet:ResourceSet": "ResourceSet"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/roleSubscription",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/roleSubscription:RoleSubscription": "RoleSubscription"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/securityNotificationEmails",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/securityNotificationEmails:SecurityNotificationEmails": "SecurityNotificationEmails"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/templateSms",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/templateSms:TemplateSms": "TemplateSms"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/threatInsightSettings",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/threatInsightSettings:ThreatInsightSettings": "ThreatInsightSettings"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/userAdminRoles",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/userAdminRoles:UserAdminRoles": "UserAdminRoles"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/userBaseSchemaProperty",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/userBaseSchemaProperty:UserBaseSchemaProperty": "UserBaseSchemaProperty"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/userFactorQuestion",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/userFactorQuestion:UserFactorQuestion": "UserFactorQuestion"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/userGroupMemberships",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/userGroupMemberships:UserGroupMemberships": "UserGroupMemberships"
  }
 },
 {
  "pkg": "okta",
  "mod": "index/userSchemaProperty",
  "fqn": "pulumi_okta",
  "classes": {
   "okta:index/userSchemaProperty:UserSchemaProperty": "UserSchemaProperty"
  }
 },
 {
  "pkg": "okta",
  "mod": "inline/hook",
  "fqn": "pulumi_okta.inline",
  "classes": {
   "okta:inline/hook:Hook": "Hook"
  }
 },
 {
  "pkg": "okta",
  "mod": "network/zone",
  "fqn": "pulumi_okta.network",
  "classes": {
   "okta:network/zone:Zone": "Zone"
  }
 },
 {
  "pkg": "okta",
  "mod": "policy/mfa",
  "fqn": "pulumi_okta.policy",
  "classes": {
   "okta:policy/mfa:Mfa": "Mfa"
  }
 },
 {
  "pkg": "okta",
  "mod": "policy/password",
  "fqn": "pulumi_okta.policy",
  "classes": {
   "okta:policy/password:Password": "Password"
  }
 },
 {
  "pkg": "okta",
  "mod": "policy/ruleIdpDiscovery",
  "fqn": "pulumi_okta.policy",
  "classes": {
   "okta:policy/ruleIdpDiscovery:RuleIdpDiscovery": "RuleIdpDiscovery"
  }
 },
 {
  "pkg": "okta",
  "mod": "policy/ruleMfa",
  "fqn": "pulumi_okta.policy",
  "classes": {
   "okta:policy/ruleMfa:RuleMfa": "RuleMfa"
  }
 },
 {
  "pkg": "okta",
  "mod": "policy/rulePassword",
  "fqn": "pulumi_okta.policy",
  "classes": {
   "okta:policy/rulePassword:RulePassword": "RulePassword"
  }
 },
 {
  "pkg": "okta",
  "mod": "policy/ruleSignon",
  "fqn": "pulumi_okta.policy",
  "classes": {
   "okta:policy/ruleSignon:RuleSignon": "RuleSignon"
  }
 },
 {
  "pkg": "okta",
  "mod": "policy/signon",
  "fqn": "pulumi_okta.policy",
  "classes": {
   "okta:policy/signon:Signon": "Signon"
  }
 },
 {
  "pkg": "okta",
  "mod": "profile/mapping",
  "fqn": "pulumi_okta.profile",
  "classes": {
   "okta:profile/mapping:Mapping": "Mapping"
  }
 },
 {
  "pkg": "okta",
  "mod": "template/email",
  "fqn": "pulumi_okta.template",
  "classes": {
   "okta:template/email:Email": "Email"
  }
 },
 {
  "pkg": "okta",
  "mod": "trustedorigin/origin",
  "fqn": "pulumi_okta.trustedorigin",
  "classes": {
   "okta:trustedorigin/origin:Origin": "Origin"
  }
 },
 {
  "pkg": "okta",
  "mod": "user/baseSchema",
  "fqn": "pulumi_okta.user",
  "classes": {
   "okta:user/baseSchema:BaseSchema": "BaseSchema"
  }
 },
 {
  "pkg": "okta",
  "mod": "user/schema",
  "fqn": "pulumi_okta.user",
  "classes": {
   "okta:user/schema:Schema": "Schema"
  }
 },
 {
  "pkg": "okta",
  "mod": "user/user",
  "fqn": "pulumi_okta.user",
  "classes": {
   "okta:user/user:User": "User"
  }
 },
 {
  "pkg": "okta",
  "mod": "user/userType",
  "fqn": "pulumi_okta.user",
  "classes": {
   "okta:user/userType:UserType": "UserType"
  }
 }
]
""",
    resource_packages="""
[
 {
  "pkg": "okta",
  "token": "pulumi:providers:okta",
  "fqn": "pulumi_okta",
  "class": "Provider"
 }
]
"""
)
