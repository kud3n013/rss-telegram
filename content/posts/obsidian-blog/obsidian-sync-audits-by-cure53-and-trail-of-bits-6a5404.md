---
title: Obsidian Sync audits by Cure53 and Trail of Bits
subtitle: ''
source: Obsidian Blog
source_url: https://obsidian.md/blog/cure53-tob-sync-audits/
author: kepano
date: '2026-05-13T00:00:00Z'
fetched: '2026-10-10T18:24:09Z'
image: ''
summary: Obsidian regularly performs security audits with independent research firms to ensure that our code and procedures meet the highest security standards. Previously we shared audits assessing Obsidian’s desktop and mobile apps in January 2024 and December 2024. Two new audits are now available on our Security page assessing the Obsidian Sync API, server, and cryptography.
tags: []
guid: https://obsidian.md/blog/cure53-tob-sync-audits/
---

Obsidian regularly performs [security audits](https://obsidian.md/security) with independent research firms to ensure that our code and procedures meet the highest security standards. Previously we shared audits assessing Obsidian’s desktop and mobile apps in [January 2024](https://obsidian.md/blog/cure53-security-audit/) and [December 2024](https://obsidian.md/blog/cure53-second-client-audit/).

Two new audits are now available on our [Security](https://obsidian.md/security) page assessing the [Obsidian Sync](https://obsidian.md/sync) API, server, and cryptography. These were completed by [Cure53](https://cure53.de/) in October 2024, and [Trail of Bits](https://www.trailofbits.com/) in December 2025.

We’re pleased to report that all findings from these reports have been addressed via remediations and disclosures validated by the respective auditors.

### Background

Obsidian Sync’s encryption code has been relatively unchanged since the launch of the service in 2020. The most notable change was a minor encryption upgrade released on [August 22, 2025](https://obsidian.md/changelog/2025-08-22-sync/) alongside [Obsidian 1.9.11](https://obsidian.md/changelog/2025-08-22-desktop-v1.9.11/). At that time we also published updated instructions for how to [verify Obsidian Sync’s end-to-end encryption](https://obsidian.md/blog/verify-obsidian-sync-encryption/).

### Obsidian Sync audit by Cure53

We asked the Berlin-based security firm [Cure53](https://cure53.de/) to perform an audit of the Obsidian Sync service including the API, server, and cryptography.

We invite you to read [a summary of the findings](https://obsidian.md/files/security/2024-Obsidian-Cure53-Sync-Audit-Summary.pdf) and the [full report](https://obsidian.md/files/security/2024-Obsidian-Cure53-Sync-Audit-Full.pdf).

The report identified four low priority issues and one medium priority issue. We’re proud to report that the Cure53 team reviewed the resolutions and concluded that their recommendations were properly followed:

> It is imperative to acknowledge the swift actions taken by the Obsidian team in working on addressing several of these identified vulnerabilities shortly after the conclusion of the audit. This proactive approach underscores the Obsidian team’s unwavering dedication to safeguarding the user experience.

#### Encryption upgrade

During this audit Cure53 validated our proposed [August 2025](https://obsidian.md/changelog/2025-08-22-sync/) encryption upgrade, stating:

> Cure53 was favorably impressed by the enhanced backend security features implemented in the latest version of the Obsidian Sync software. In comparison to its predecessors, Obsidian has made substantial progress in fortifying its cryptographic mechanisms.

#### Renaming “Managed encryption” to “Standard encryption”

Cure53 identified DYL-04-005 described as *“Key mgmt. confusion in managed vault encryption mode”*. It found that the app and documentation did not clearly describe the risks of *not* choosing Sync’s default end-to-end encryption option.

Since launch Obsidian Sync has always provided two encryption options: end-to-end encryption (default) and “managed encryption” (optional) which was renamed to “standard encryption”.

As a result of this audit the app and Help site were updated to reflect the [risks of choosing standard encryption](https://obsidian.md/help/sync/security) in October 2024, via commit [d18640c](https://github.com/obsidianmd/obsidian-help/commit/d18640c6d3010d73354e75853a4e3dde86c2bd52).

### Obsidian Sync audit by Trail of Bits

After completing the August 2025 Sync encryption upgrade, we asked the New York-based firm [Trail of Bits](https://www.trailofbits.com/) to perform a new audit of the Sync API, server, and cryptography.

Our aim was to gain even deeper coverage of potential vulnerabilities in Obsidian Sync. We invite you to read the [full report](https://raw.githubusercontent.com/trailofbits/publications/refs/heads/master/reviews/2025.12-obsidiansync-securityreview.pdf).

The audit identified eleven issues. Remediations were implemented and validated by Trail of Bits. The report mentions three unresolved issues, which we cover below. The latter two were documented on our [Sync security page](https://obsidian.md/help/sync/security) in November 2025, via commit [ec32a5c](https://github.com/obsidianmd/obsidian-help/commit/ec32a5c).

#### Deleting vaults for inactive subscriptions

Trail of Bits identified TOB-OBSYNC-2, *“Logged-out clients can look up and trigger deletion of vaults with inactive subscriptions”*:

> Using Obsidian Sync requires a subscription, and 30 days after a vault owner’s subscription expires, the server-side copy of the synchronized vault can be deleted. […] Since this applies only to vaults that are already due for deletion, it does not appear to create any security concern.

For now we have decided to keep this endpoint so that the Sync server can clean up data after the grace period. In the future we will consider how this action can be handled via a scheduled job.

#### Deterministic file-hash encryption

Trail of Bits identified TOB-OBSYNC-9, *Deterministic encryption of file hash endangers file confidentiality*.

In response to this report we created a new *Limitations* section on our [Sync security page](https://obsidian.md/help/sync/security) to help explain trade-offs we make so that we can deliver fast, reliable sync, and efficient storage across devices.

> We encrypt file hashes deterministically: the same file content, using the same encryption key and salt, always produces the same encrypted hash on the server. This helps Sync detect duplicates and avoid re-uploading or re-storing identical data, which saves bandwidth and remote storage, especially in version history or when large files repeat.
>
> However, if an attacker compromises a Sync server, and they have a separate way to force a user to upload files of their choosing, then the attacker could force the user to upload specific files and determine if the file matches against a file the user has previously uploaded.

#### No cryptographic binding between path and content

Trail of Bits identified TOB-OBSYNC-10, *General lack of cryptographic binding between file content and metadata*. As with the issue above, we added the following details to our Sync security page:

> Some metadata is not end-to-end encrypted: which device uploaded or deleted a file, when it was uploaded, and the *mapping* between encrypted file paths and encrypted content. This data is readable by the server so it can route changes, determine the version history for a file, and keep devices in sync.
>
> If a Sync server were compromised, an attacker could tamper with that mapping, causing the contents of one encrypted file to be delivered under a different file path. This doesn’t reveal your plaintext data, it remains encrypted.

### Conclusion

We’d like to thank Cure53 and Trail of Bits for their collaboration with us on these audits. Their depth of expertise reinforced our confidence in the security of Obsidian Sync.

We make Obsidian to capture our own private thoughts and ideas, and we want you to feel confident doing the same. We will continue working with industry-leading security firms on audits that provide comprehensive coverage and transparency towards this commitment.
