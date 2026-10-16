---
title: 'Security incident logs: How to create logs that satisfy GDPR and regulators'
subtitle: ''
source: Proton Blog
source_url: https://proton.me/business/blog/security-incident-log
author: Kate Menzies
date: '2026-10-16T17:31:30Z'
fetched: '2026-10-16T18:54:43Z'
image: ''
summary: 'The most difficult part of a security incident usually occurs after the incident itself is over: when the business has to explain what happened, when it was discovered, what data was involved, who was affected, and why certain decisions were made. For many SMBs, these records don’t exist in a complete form.'
tags:
- For business
guid: https://proton.me/business/blog/security-incident-log
---

The most difficult part of a security incident usually occurs after the incident itself is over: when the business has to explain what happened, when it was discovered, what data was involved, who was affected, and why certain decisions were made.

For many SMBs, these records don’t exist in a complete form. Details may be scattered throughout chat messages, inboxes, helpdesk tickets, screenshots, and in team members’ memories. Businesses stay afloat during an incident with these patchwork records, but they become an issue when supervisory authorities, an insurer, a customer, or a board member asks for a clear timeline.

Businesses of all sizes need a thorough security incident log. It should be a single source of truth to record what happened, how the incident was handled, and what evidence supports the decisions made along the way.

The record is valuable even when you don’t need to report an incident. We’ll explain why security incident logs are helpful for your business and how to create your own.

Why security incident logs matter

Incident logs vs incident response plans

What a security incident log should contain

A simple incident log template for SMBs

How to record notification decisions

What supervisory authorities expect from security incident logs

The credential access log

## Why security incident logs matter

Security incident logs create accountability at the moment a business is most likely to lose track of details. During an incident, actions happen quickly: passwords are reset, accounts are disabled, IT providers are contacted, customer data is checked, and leadership is briefed. Those steps may be exactly what the business needs at the moment, but they become much harder to explain later if no one records when each action happened, who approved it, and what evidence supported the decision.

For businesses based in Europe, this isn’t just good practice. Under the General Data Protection Regulation (GDPR), both in the UK and EU, personal data breaches need to be assessed, and some must be reported to the corresponding supervisory authority.

In the UK, the ICO’s [report a breach](https://ico.org.uk/for-organisations/report-a-breach/) guidance explains that organizations must assess the likely risk to people’s rights and freedoms and notify the ICO when that risk is likely. Article 33 also requires controllers to document personal data breaches, including the facts of the breach, its effects, and the remedial action taken. The same requirements apply under the EU GDPR.

For example, the ICO does not expect every SMB to have enterprise-grade systems, but it does expect appropriate records. Its breach response and monitoring framework says organizations should have procedures to make sure personal data incidents and breaches are detected, managed, and appropriately recorded. That means an incident log should not be created only when a serious breach has already happened. It should be part of the normal response process.

Good records also support insurance claims. Cyber insurers may ask for evidence of when the incident was discovered, what containment steps were taken, which accounts were affected, and whether the business followed its incident response process. A well-kept log can show that the business acted promptly and consistently.

It also helps the company learn. Memories and oral records aren’t reliable, but a record that shows the incident began with a reused password, missing [multi-factor authentication](https://proton.me/business/blog/multi-factor-authentication-business) (MFA), vendor access, or delayed offboarding gives the business something concrete to fix and a clearer direction for strengthening security over time.

## Incident logs vs incident response plans

A security incident log and an incident response plan are connected, but they are not the same document.

An [incident response plan](https://proton.me/blog/incident-response) explains what the business should do when something goes wrong. It assigns roles, escalation routes, containment steps, communication responsibilities, and recovery procedures. The incident log records what actually happened. It is the timeline, evidence trail, decision record, and follow-up file for a specific event.

That distinction matters because even a good plan can fail without documentation. A business may follow the right steps but still struggle to prove it later. The log should make it possible to answer practical questions: when did we know, who acted, what did we contain, what data was at risk, what did we decide, and what changed afterward?

|  |  |
| --- | --- |
| **Incident response plan: What your business should do** | **Security incident log: What actually happened** |
| Who leads the response Who contacts IT, legal, insurer, or regulators How to contain, recover, and communicate | When the incident was discovered Which systems and data were affected What actions were taken, by whom, and when |

## What a security incident log should contain

A useful incident log needs to be consistent enough for a business to reconstruct the event later and explain the decisions made during the response.

### Date and time of discovery

Record when the business first became aware of the incident, who noticed it, and how it was discovered. If the time is approximate, mark it as approximate. Discovery time matters because GDPR reporting timelines and insurance requirements often depend on when the business became aware of the issue.

### Nature of the incident

Describe what happened in plain language. Avoid vague labels such as “security issue” or “possible breach” without context. The log should explain which systems were affected and whether the incident involved credentials, email, files, customer data, payment systems, endpoints, or third-party access.

### Data involved

If personal data may have been affected, record what kind of data was involved: names, email addresses, phone numbers, addresses, account details, financial information, employee records, customer communications, login credentials, or any other relevant category. Estimate how many individuals may be affected, and make clear whether the number is confirmed or still under investigation.

### Likely cause

Record the known or suspected cause, even if the investigation is still ongoing. As new details emerge, the log can be updated from “cause unknown” to “phishing email led to credential compromise” or “former contractor account remained active.” The log should show how the business’s understanding changed over time.

### Immediate containment actions

Document what was done to limit damage. This may include password resets, session revocation, MFA enforcement, account suspension, mailbox rule removal, device isolation, vendor access removal, firewall changes, or temporary service shutdowns. Where possible, include the owner and timestamp for each action.

### Notification decisions

Record whether the business notified the relevant supervisory authority (the ICO in the UK, or the national data protection authority elsewhere in the EU affected individuals, customers, suppliers, insurers, legal advisers, or law enforcement. If the decision was not to notify, document the reasoning. That explanation is often as important as the notification itself.

### Remediation steps and timeline

Containment addresses the immediate incident. Remediation reduces the chance of the same issue happening again. Record follow-up actions such as enforcing MFA, removing shared credentials, updating access policies, improving offboarding, fixing a misconfiguration, or changing how backups are protected.

### Lessons learned

End with what the business learned and what will change. This should not be written as blame. It should identify the weakness, the improvement needed, and who owns the follow-up.

## A simple incident log template for SMBs

Specialist software isn’t necessary for documenting incidents. A spreadsheet, secure internal form, ticketing system, or shared register can work if access is controlled and entries are kept consistent.

An effective incident log should include these fields:

- **Incident ID:** A unique reference number.
- **Date and time discovered:** When the business became aware of the incident.
- **Reported by:** Employee, provider, customer, vendor, monitoring alert, or external party.
- **Incident type:** Phishing, malware, credential compromise, data loss, unauthorized access, ransomware, supplier incident, device loss, misdirected email, or other.
- **Summary:** What happened, written in plain language.
- **Systems affected:** Applications, accounts, devices, databases, inboxes, or third-party services involved.
- **Data involved:** Whether personal data was affected, what type, and how many people may be impacted.
- **Likely cause:** Known, suspected, or under investigation.
- **Containment actions:** What was done immediately.
- **Notification decision:** Supervisory authority, individuals, customers, insurer, or no notification with reasoning.
- **Evidence links:** Screenshots, tickets, logs, emails, access records, export files, or provider reports.
- **Remediation actions:** Steps taken after containment.
- **Owner:** Person responsible for follow-up.
- **Status:** Open, monitoring, contained, resolved, closed.
- **Lessons learned:** What should change.

## How to record notification decisions

Notification decisions deserve their own space in a security incident log because they’re often reviewed after the incident.

Under both UK and EU GDPR, organizations must assess the likely risk to people’s rights and freedoms when a personal data breach occurs. If risk is likely, the supervisory authority must be notified as soon as possible and, where feasible, within 72 hours, the [ICO](https://ico.org.uk/for-organisations/report-a-breach/) in the UK, the national data protection authority in each EU member state. If the risk is high, affected individuals must also be notified without undue delay. The thresholds and the clock are the same on both sides; only the authority changes.

A good incident log should show that the business made this assessment. It should record whether personal data was involved, what kind of harm could result, what protections were in place, and why the business decided to report or not report.

For example, an incident involving an exposed admin password may not immediately reveal whether personal data was accessed. The log should reflect that uncertainty. It can record the initial concern, the investigation steps, the account activity review, and the final conclusion once evidence is available.

At this point in the process, many businesses focus on organizing the technical fix and forget to record the compliance reasoning. Passwords are reset, accounts are secured, and operations continue. Weeks later, the business can’t explain why it decided the incident was not reportable.

## What supervisory authorities expect from records

Supervisory authorities do not only look at whether a breach was reported. They may also ask how the business:

- Identified the incident
- Assessed the risk
- Decided whether notification was required
- Documented the actions taken

A good record should make the story of the incident clear from beginning to end. It should show what happened, what personal data was involved, what harm could result, what the business did to contain the issue, and why it reported or did not report the breach.

The level of detail should match the seriousness of the incident. A misdirected email will not need the same record as a ransomware attack, but it still needs to be documented to show that the business assessed it properly.

These records should also be stored securely. Incident logs may include sensitive details about affected individuals, exposed systems, employee actions, screenshots, access logs, or remediation steps. Access should be limited to the people who need it, and retention should align with the company’s wider data retention policy.

## The credential access log

Many incidents involve credentials: they can be triggered by a reused password, shared account, compromised inbox, exposed admin login, suspicious MFA prompt, or an employee who wasn’t [offboarded](https://proton.me/business/blog/employee-offboarding-security) properly.

For that reason, credential access records can become a direct input into cybersecurity incident documentation. When an incident involves a shared login or sensitive account, the business needs to know who had access, how access was shared, whether permissions changed, and whether the credential was rotated after the incident.

A [business password manager](https://proton.me/business/pass) like Proton Pass for Business helps teams manage credentials in encrypted vaults, generate unique passwords, use autofill, share credentials securely, manage passkeys, and use built-in two-factor authentication. For incident documentation, the strongest value is the access trail around credentials: who had access to shared vaults/accounts, how access was managed and who used it, and what changed after the incident.

A [password manager for IT teams](https://proton.me/business/pass/for-it-teams) adds admin features such as policies, reporting, logs, role-based access control, SCIM provisioning, and [SSO](https://proton.me/business/blog/sso-integration) integration. These features can help businesses show how credential access is controlled and provide evidence when a credential-related incident is investigated.

A password manager can’t replace an incident log, legal assessment, regulatory notification process, or incident response plan. But it provides credential evidence that can feed into those processes.

Keep a complete audit trail of credential access with a [business password manager](https://proton.me/business/pass).
