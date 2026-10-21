---
title: Manage team access easily with new Admin roles and SCIM for groups
subtitle: ''
source: Proton Blog
source_url: https://proton.me/business/blog/admin-roles
author: Raphael Auphan
date: '2026-10-21T11:21:29Z'
fetched: '2026-10-21T12:57:36Z'
image: ''
summary: 'Today, we’re proud to announce two new features that give you greater access control without the manual overhead: Admin roles and SCIM for groups. Admin roles let you delegate admin responsibilities for more granular, secure control over your organization, while SCIM for groups enable you to provision access to groups through your identity provider for a more seamless way to manage your teams.'
tags:
- For business
- Proton updates
guid: https://proton.me/business/blog/admin-roles
---

Today, we’re proud to announce two new features that give you greater access control without the manual overhead: **Admin roles** and **SCIM for groups**. Admin roles let you delegate admin responsibilities for more granular, secure control over your organization, while SCIM for groups enable you to provision access to groups through your identity provider for a more seamless way to manage your teams.

Managing access at any organization can be tedious and time-consuming. Admins need to grant the right permissions quickly, and revoke them just as fast when roles change or someone leaves. But beyond the resources and effort involved, this can also risk compromising security if something slips through the cracks — especially for fast-growing and larger teams. Our new features are designed to address this to keep your business moving effectively and efficiently.

## Enjoy more granular access control with Admin roles

Permissions for organizations in Proton for Business were built around Administrators and Users, giving organizations a clear, simple way to separate full administrative control from everyday use. But we recognize that this alone isn’t always granular enough for certain teams and businesses, such as when an employee needs specific responsibilities without everything else that comes with full admin access.

Admin roles build on that model with role-based access control (RBAC), giving you more control over who can do what. You can now assign specific roles to individual users or entire groups:

- **Organization Admin** keeps full control over the organization.
- **User Admin** manages users, like adding new addresses or assigning groups, without touching security policy.
- **Security Admin** manages security settings and reviews logs, without broader administrative reach.
- **User** remains the default role for everyone else.

Assign a role to a group once, and everyone in it inherits that role automatically. Group member additions or removals also mean their access gets updated instantly. Access management now scales with how your organization is actually structured, instead of a binary all-or-nothing approach or requiring a one-by-one update every time a team changes.

Admin roles are available now across all Professional plans and Workspace bundles.

## Manage teams more efficiently with SCIM for groups

Proton’s existing SCIM (System for Cross-domain Identity Management) integration already synced users automatically from your identity provider (IdP), enabling user changes to be reflected across both systems without needing to manually replicate each one. However, groups still had to be created and maintained by hand inside Proton. Every time someone joined a team, switched departments, or left the company, an admin had to update Proton separately. Now, that’s no longer necessary on Proton Pass and Proton VPN.

With SCIM for groups, Proton’s SCIM integration has been extended to provision groups, not just individual users. Group names and membership changes now sync automatically from Microsoft Entra or Okta into Proton Pass and Proton VPN. Make that change once on your IdP and it’ll be reflected on the appropriate Proton app, with no separate list to maintain.

Here’s what that looks like in practice:

- Add someone to a group in the IdP, and they automatically gain access to everything that group is entitled to in Proton, whether it’s a shared Pass vault or a VPN gateway.
- Remove someone from an IdP group, and their Proton access updates automatically — no manual cleanup required.

Proton groups created this way are managed and controlled at the IdP, not inside Proton. This keeps your identity provider as the single source of truth and reduces manual effort, so there’s no risk of the two ever falling out of sync.

SCIM for groups is available now on the following plans: Pass Professional, VPN Professional, and the VPN and Pass Professional bundle.

## Get started today

Both admin roles and SCIM for groups are now live.

Admin roles are available on all Professional plans and Workspace bundles, so you can start [assigning users and groups](https://proton.me/support/admin-roles) granular roles straightaway — ensuring the right people get the right level of access.

SCIM for groups is supported for Proton Pass or Proton VPN. If you have SSO and SCIM already set up, this means you no longer need to manage groups manually on Proton. Group membership changes at your IdP are automatically reflected in Proton, so group provisioning is [ready to configure](https://proton.me/support/scim-groups) directly from your Entra or Okta admin console.

Explore our Professional and Workspace plans to find the right tier for your organization, or if you need help, [speak to our sales team](https://proton.me/business/contact) today to learn which Proton plan is best for you.

[Get Proton for Business](https://proton.me/business/plans)
