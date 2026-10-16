---
title: 'Third-party vendor risk management: How to assess and monitor your supply chain security'
subtitle: ''
source: Proton Blog
source_url: https://proton.me/business/blog/vendor-risk-management
author: Ben Wolford
date: '2026-10-16T17:28:06Z'
fetched: '2026-10-16T18:54:43Z'
image: ''
summary: Most businesses don’t just rely on internal systems. They run on cloud platforms, payroll providers, marketing tools, IT partners, and dozens of SaaS accounts that keep daily work moving. Each vendor solves a problem, and each one also creates a new relationship of trust.
tags:
- For business
guid: https://proton.me/business/blog/vendor-risk-management
---

Most businesses don’t just rely on internal systems. They run on cloud platforms, payroll providers, marketing tools, IT partners, and dozens of SaaS accounts that keep daily work moving. Each vendor solves a problem, and each one also creates a new relationship of trust.

Vendor risk management (VRM) is the process of assessing, approving, monitoring, and reviewing the security risks that come from working with third parties. It helps businesses understand which vendors can access sensitive systems or data, which controls those vendors have in place, whether their security practices are sound enough to justify that access, and how quickly access can be changed if a contract ends or an incident happens.

We’ll explain how to approach vendor risk management within your own business: how to assess the vendors you already work with, how to classify third party vendor risk, what to include in a vendor security checklist, and how to control vendor credentials before they become long-term exposure.

What vendor risk management covers

Your guide to vendor risk management

Your vendor security checklist

How Proton Pass for Business supports vendor access control

## What vendor risk management covers

Vendor risk management is powered by a simple principle: every external party that touches your data, systems, or business processes changes your risk profile.

Most vendor risk is created by everyday work. For example, a third-party agency may be brought into a business network because a team needs speed, expertise, or software the business does not have in-house. Access is granted, data is shared, and the relationship is established as part of everyday work.

Risk is created when it’s not clear what that vendor can access, which controls stand between that access and a breach — [multi-factor authentication](https://proton.me/business/blog/multi-factor-authentication-business) (MFA), named accounts, encryption — or how quickly that access could be found and cut off. Revoking it usually happens within the system itself or through SCIM provisioning; the hard part for most businesses is knowing where to actually look.

The vendor may be a large cloud provider, a niche SaaS platform, a freelance developer, or an accounting firm. The size and industry of the vendor is not the main issue. Their access is.

Vendor risk manifests in several different ways:

- **Data risk:** The vendor can view, store, process, transfer, or delete business or personal data.
- **Access risk:** The vendor can log in to systems, manage settings, use integrations, or reach admin panels.
- **Operational risk:** The business depends on the vendor for a critical workflow, service, or customer-facing process.
- **Compliance risk:** The vendor’s role affects your obligations under data protection laws (such as [GDPR](https://proton.me/business/gdpr) compliance requirements), contractual, or sector-specific requirements.
- **Credential risk:** Vendor access is shared, reused, undocumented, or difficult to revoke.

Vendor risk is difficult to spot because it often builds through small access choices that make sense in the moment: A team member shares a login they shouldn’t, or a supplier account retains permissions for convenience, or a contractor permission that no one revisits after the project ends. Over time, those exceptions become part of the business environment, even when no one is actively managing them.

## How to build a vendor risk management (VRM) process

Done effectively, vendor risk management doesn’t make every decision more complicated. It creates a reliable framework for how your business grants access with clearer limits. We’ll explore the key steps your business can take to assess your own vendor risk and build a risk management strategy.

### 1. Build an inventory of your vendors

Instead of letting vendor risk management become a reactive task when you’re asked for security evidence or renewing a contract, make it a proactive task. Start by understanding the vendors already inside your operations.

Taking a vendor inventory doesn’t need to be complex. It needs to be clear enough to show:

- Who owns the relationship
- What service the vendor provides
- Which systems or data they can access
- Whether personal data is involved
- Whether subprocessors are used
- When the next contract or security review is due

Access is a crucial component to record because vendors have different privileges and access needs. Some vendors use named accounts. Others rely on shared credentials, admin access, API keys, shared inboxes, or temporary logins that remain active long after the original need has passed. These differences matter because they determine how quickly access can be changed during offboarding or an incident.

The inventory should also include smaller vendors that may sit outside formal procurement. A plugin, consultant, freelance developer, agency, or specialist SaaS service can create meaningful exposure if it touches sensitive data or critical workflows.

The main value of an inventory is creating better access controls. When a vendor relationship ends, your business knows which accounts to disable, which credentials to rotate, which integrations to remove, and what should happen to stored data.

### 2. Classify vendors by risk, not convenience

After mapping your vendors, group them by the risk they create. This keeps the process proportionate and avoids treating every supplier as either harmless or critical.

**High-risk vendors** usually process sensitive data, support essential operations, or hold privileged access. This may include cloud infrastructure, identity platforms, payroll, finance, HR systems, managed IT, security services, or core SaaS platforms.

**Moderate-risk vendors** support important work but have narrower access. They may include collaboration platforms, analytics tools, project management systems, help desk software, or agencies with limited permissions.

**Low-risk vendors** have little or no access to sensitive data or business-critical systems. They should still be recorded, but they do not need the same depth of review unless their role changes.

The tier should follow the actual access, not the vendor’s reputation, size, or price. A familiar platform can become high risk if it stores sensitive data. A small contractor can be at high risk if they hold admin privileges.

Use the risk tier to decide how deeply to assess the vendor, how often to review the relationship, and which minimum controls apply.

### 3. Set security requirements before access is granted

Vendor assessments work best when the business knows its minimum requirements before access is approved.

For **high-risk vendors**, those requirements should cover the controls that protect data and keep access accountable: MFA, encryption in transit and at rest, role-based access control, audit logs, incident response procedures, vulnerability management, subprocessor controls, data deletion commitments, and business continuity planning.

Security evidence can support that review. ISO 27001, SOC 2, national schemes such as Cyber Essentials in the UK, penetration test summaries, or security whitepapers can all help, depending on the vendor’s role and the sensitivity of the relationship.

Certifications and audit reports describe how a vendor operates. They say much less about who the vendor actually is. A recent [investigation into Passwork’s safety](https://proton.me/business/blog/is-passwork-safe) proves that this distinction matters: a European registration, a polished website, and a “built for trust” message were enough to clear the bar at organizations that never traced the ownership, jurisdiction, or origin of the code they were installing.

For any vendor holding sensitive access, two questions belong alongside the control checklist: who owns and controls the company, and under which country’s laws does it operate; and can independent experts inspect the code, or is the business trusting a closed system on the vendor’s word alone?

**Moderate-risk vendors** may need a lighter review, but they should still be able to explain how they protect accounts, restrict employee access, handle data, notify customers of incidents, and remove access when the relationship ends.

For **low-risk vendors**, the main check may be whether they truly have no access to sensitive systems or personal data. If that changes, the vendor should be reassessed.

A good process is strict where risk is high and lightweight where risk is genuinely low. It shouldn’t turn every supplier review into an enterprise audit, but it should prevent sensitive access from being approved on trust alone.

### 4. Monitor vendors after onboarding

Vendors change their systems, subprocessors, policies, staffing, and security controls. Your business may also give them more access over time. Without monitoring, your original assessment becomes outdated.

A practical monitoring process can include annual reviews for high-risk and moderate-risk vendors, checks before contract renewal, reassessment when access expands, and review after any reported incident. Critical vendors may need more frequent access checks.

Monitoring should include the credential layer. Check whether vendor accounts still belong to active contacts, whether permissions match the current scope, whether shared credentials still exist, and whether integrations or API keys are still needed.

This is where many businesses find avoidable exposure: old agency accounts, unused contractor logins, shared passwords that no one owns, integrations created for a past project, and admin permissions granted for convenience.

Vendor risk also belongs in continuity planning. If a critical supplier becomes unavailable, reports a breach, or forces emergency access changes, the business needs a way to keep essential work moving. Proton’s guide to [business continuity strategies](https://proton.me/blog/business-continuity-strategies) explains why resilience depends on more than backups, especially when access and credentials are involved.

### 5. Control third-party credentials

Many vendor risk programs look solid on paper and then fail at the credential level. A vendor can look compliant on paper and still create exposure through the way access is handled day to day.

The risk exists in the gap between the formal process and the realistic one: credentials stored outside approved systems, shared accounts with no clear owner, or API keys that stay active after the vendor relationship changes.

If those access paths are not reviewed and revoked, the business may keep carrying vendor risk long after the original work has ended.

Third-party access should follow the same discipline and use the same [password policies](https://proton.me/business/pass/password-policy) as internal access:

- Give vendors only the access they need
- Use named accounts where possible
- Avoid shared credentials unless there is no alternative
- Store shared credentials in a controlled [credential management](https://proton.me/business/pass/credential-management) system
- Share files with vendors through encrypted [cloud storage for business](https://proton.me/business/drive) with expiring links, not email attachments
- Review access regularly
- Revoke access when work ends
- Rotate credentials after vendor staff changes or incidents
- Require MFA wherever the service supports it

A [business password manager](https://proton.me/business/pass) makes these rules easy to implement. It gives teams a secure place to store vendor credentials, share access without sending passwords through chat or email, rotate passwords, and remove access when a vendor relationship ends.

## Your vendor security checklist

A vendor security checklist should help your business onboard new vendors securely.

Use it to understand the relationship clearly:

- What data will the vendor access, process, or store?
- Will the vendor process personal data on our behalf?
- Will the vendor sign a data processing agreement (DPA) and delete our data when the contract ends?
- Where will data be stored and processed?
- Does the vendor use subprocessors?
- Does the vendor enforce MFA?
- How does the vendor control employee access to customer data?
- Can our business assign role-based permissions?
- Can access be removed immediately?
- Does the vendor provide audit logs or admin activity reports?
- How does the vendor encrypt data?
- How quickly will the vendor notify us of a security incident?
- Does the vendor have business continuity or disaster recovery procedures?
- Can the vendor provide security documentation, certifications, or audit summaries?
- Has the vendor experienced a publicly reported security incident, and how did they handle it?
- Who owns and controls the company, and under which jurisdiction does it operate?
- Is the product open source or independently audited, so its security claims can be verified?

The checklist should show any risk your business is accepting. A vendor that lacks formal certification may still be suitable for low-risk work. A vendor with admin access, weak authentication, vague incident timelines, or no clear deletion process is a different decision entirely.

For vendors already in use, bring the checklist back during renewals and scheduled reviews. The original approval may no longer reflect the way the tool is used today. A vendor brought in for a small project can quietly become part of customer operations, finance workflows, or critical integrations.

## How Proton Pass for Business supports vendor access control

Vendor risk management becomes much harder when third-party access is managed outside a controlled system. A vendor may be approved, documented, and covered by contract, but the real exposure often depends on everyday access paths: shared credentials, permissions, passkeys, recovery codes, API keys, and accounts that need to be reviewed or removed as the relationship changes.

A [business password manager](https://proton.me/business/pass) like Proton Pass for Business helps businesses bring that access into a more secure and auditable process. Teams can store vendor credentials in end-to-end encrypted vaults, generate strong and unique passwords, use autofill to reduce manual handling, manage passkeys, and share access without sending passwords through email, chat, or project documents.

For vendor access specifically, shared vaults can help separate credentials by supplier, project, team, or sensitivity level. This makes it easier to keep access organized, review who has access to what, and remove access when a contract ends, a vendor contact changes, or an incident requires fast containment.

A [password manager for IT teams](https://proton.me/business/pass/for-it-teams) adds the administrative layer needed as the process becomes more formal. Policies, reporting, logs, role-based access control, SCIM provisioning, and single sign-on integration help businesses manage access consistently across teams instead of relying on individual habits.

Proton Pass for Business supports your business by controlling the credentials and access paths vendors use to work with your business. It is also open source and independently audited, so it passes the same checklist we recommend you apply to your own vendors. When supplier access is stored, shared, reviewed, and revoked from a controlled environment, vendor risk becomes easier to manage beyond the initial assessment.

Control third-party credential access securely with a [business password manager](https://proton.me/business/pass).
