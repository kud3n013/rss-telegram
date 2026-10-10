---
title: Locked In, Locked Out - Apple's Walled Garden Should Come With Liability
subtitle: ''
source: That Privacy Guy! Blog
source_url: https://www.thatprivacyguy.com/blog/locked-in-locked-out
author: Alexander Hanff
date: '2026-08-11T00:00:00Z'
fetched: '2026-10-10T17:51:18Z'
image: https://www.thatprivacyguy.com/blog/assets/2026-08-11-001.png
summary: 'For years now Apple has stated in its marketing campaigns: "What happens on your iPhone stays on your iPhone".'
tags:
- Apple
- iOS
- App-Store
- ePrivacy
- GDPR
- SDKs
- AdTech
- Liability
guid: https://www.thatprivacyguy.com/blog/locked-in-locked-out
---

For years now Apple has stated in its marketing campaigns: "What happens on your iPhone stays on your iPhone". This was tested by the Washington Post by using a single iPhone for one week and found 5,400 hidden trackers exfiltrating data from the device - phone number, email, precise location, IP address - from apps including Microsoft OneDrive, Spotify, Nike, DoorDash, The Weather Channel, even the Post's own app (<https://www.washingtonpost.com/technology/2019/05/28/its-middle-night-do-you-know-who-your-iphone-is-talking/>). What happens on your iPhone leaves your iPhone thousands of times a week but you wouldn't know that because the only party with the technical means to see it happening in full is Apple.

Apple ships five operating systems - iOS, iPadOS, watchOS, tvOS and visionOS - that are impossible for their own users to audit due to the way these operating systems are locked down. Now don't get me wrong, I am on public record arguing that the walled garden is good for most users from a security perspective and have long stated that Apple provide better privacy than any other commercial platform by default (other platforms either don't have the same level of protection or require significant hoop jumping to configure them in such a way - it is not the default) - and I stand on that even now.

But whereas the lockdown is marketed as a security architecture, it also prevents security teams, researchers, regulators, NGOs and anyone else who might have an interest in what data is leaving their devices, from auditing the apps they use.

This means a person can't investigate what apps on their own device are doing with their own data. Security researchers can't examine the platform without breaking it first and even then at great cost; and a regulator can't verify compliance without asking the app developer for their source code.

Apple is the guardian, claiming that its App Review process keeps everyone safe, while taking a substantial commission on the very apps that are exfiltrating personal data unlawfully. My position is simple: if Apple insists on being the only party capable of auditing its ecosystem they should carry legal liability for what that ecosystem does.

That means when an App is found to be breaking the law (and in my opinion, in the EU that includes almost every single app on the App Store because almost all of them have unlawful SDKs exfiltrating data to third parties without the legally required consent), Apple should be included as complicit in enforcement action and any damages recouped by the injured parties.

Why?

Because if Apple say that we are safe because they review all the apps but those apps break the law anyway - Apple has been dishonest or negligent - either way, the buck stops with them.

## No Transparency

When using any of the 5 operating systems users can't see network traffic their apps generate (unless they jump through extra hoops and set up a lab with a dedicated network just for that one device with a man in the middle (proxy) to access the traffic and even that won't work if the app uses certificate pinning); there is no user configurable firewall on iOS, no packet capture, no equivalent of the tools that have existed on desktop computers for 25 years.

Users can't grant themselves administrative access to their own (very expensive) hardware. You can't install software from outside the App Store, unless you're in the EU where the Digital Markets Act forced a narrow crack in the wall (again, as the default I think this is good for most users but should not restrict legitimate research and legal investigation, the capability should be there even if it is not enabled by default - just like the Android developer mode which if I recall correctly requires 7 taps on the Build Number to enable the developer tools such as ADB).

You and I are simply prevented from running audits with sufficient privileges to observe what other apps actually do, since every app is sealed in its own sandbox precisely to prevent one process observing another.

On the peripheral platforms it is even worse; watchOS, tvOS and visionOS offer no meaningful way to understand anything that is happening on those devices despite the fact that these devices are used to do things which are ordinarily considered protected under privacy laws. WatchOS monitors your heart rhythm, your sleep, your movement; TVOS knows what you watch; VisionOS knows what you look at (it literally monitors your eyes). Yet despite all this sensitive usage (and again this is not just wishful thinking, pretty much each of these things has been protected by privacy law from being monitored at some point over the past 20 years) neither WatchOS, VisionOS or TVOS provides any tools or visibility as to what apps are actually doing with your personal data.

We are supposed to just "trust" Apple despite the evidence that their reviews are failing on a massive scale and actually even when illegality is reported - nothing is done.

I will give you an example - one of the most successful investigative articles (millions of views in a single week) I ever wrote was about Clubhouse - the social media app that did the rounds several years ago that was an absolute privacy nightmare and was subjected to multiple regulatory investigations and enforcement across at least 3 EU Member States for GDPR violations. I contacted Apple directly (I generally have a very good relationship with Apple and have direct contact at the executive level) reporting Clubhouse and asking them to remove it from the app store for blatant GDPR and ePrivacy violations. Clubhouse remained in the App Store despite these legal issues and the enforcement issued against them.

I am sorry Apple, you know I am a fan, but we don't live in an age of trust, we live in an age of chaos and greed and as much as I want to trust you, when the evidence is stacked so high against you, it simply isn't possible - that trust has gone as a result of broken promises and the inability to verify that you force on all of us.

Compare macOS. On a Mac I can run Little Snitch, capture packets, inspect processes, intercept my own TLS traffic, read the filesystem, audit launch agents/daemons. So Apple are perfectly capable of developing a platform that is fully auditable and transparent - it is not down to technical difficulties that Apple refuses to do the same with their peripheral OSs - it is a policy decision and as such should be a decision they are liable for.

Security researchers who want to study iOS apps in any depth need a jailbroken device which is a breach of Apple's terms and also leaves a slam dunk for any defence counsel defending a claim of unlawful behaviour - because the second you jailbreak a device you have altered its environment allowing defence to argue the results are inadmissible as they are synthetic.

When Corellium built virtualised iPhones specifically so that researchers could study iOS, Apple sued them. A federal judge rejected Apple's copyright theory, ruling Corellium's tool fair use, before the parties settled after four years of litigation (<https://9to5mac.com/2023/12/15/apple-vs-corellium-case-settled-again/>). Apple's alternative is its Security Research Device programme: invitation only, on Apple's terms, with Apple deciding who qualifies. Independent audit at scale - the kind regulators, journalists and academics need - is structurally impossible and it needs to change.

## What the apps are actually doing

I have made quite a few claims so far in this piece so now I am going to back them up. One could argue that if Apple's Walled Garden actually worked and stopped Apps from unlawful data exfiltration, it is a good thing (and as I said previously, generally as the default, I don't have a huge issue with it because people should not need to be lawyers or security researchers in order to use a smart device) - but it doesn't...

When Apple introduced App Tracking Transparency (ATT) it was sold as the end of unlawful tracking/profiling. Researchers at Oxford analysed 1,759 apps from the UK App Store before and after the change (<https://dl.acm.org/doi/10.1145/3531146.3533116>) and found that ATT does make the IDFA cross-app identifier unavailable, yet apps continued to collect device information for tracking and fingerprinting, tracking libraries/SDKs remained embedded at scale, the researchers found real-world evidence of apps computing a fingerprinting-derived identifier server-side in direct violation of Apple's own policies. Their conclusion was that the changes reinforced Apple's own market power over first-party data while tracking continued by other means.

An independent study by the developers of Lockdown stated that ATT made "no difference in the total number of active third-party trackers" observed, with minimal impact on tracking connection attempts - they called the feature functionally useless in practice (<https://blog.lockdownprivacy.com/2021/09/22/study-effectiveness-of-apples-app-tracking-transparency.html>, <https://www.washingtonpost.com/technology/2021/09/23/iphone-tracking/>).

Nothing has improved since. NowSecure tested 23,300 iOS apps in August 2025 and 35% failed to disclose the data they collect, 42% were missing their main privacy manifest and 75% of tested apps combined sensitive data access with connections to tracking domains (<https://www.nowsecure.com/blog/2025/09/29/new-nowsecure-research-targets-mobile-app-privacy-risks-what-you-dont-see-is-hurting-you/>).

Academic work published at ACM CCS in 2025 documented an open commercial market for device fingerprinting SDKs - the precise technique Apple's rules claim to prohibit (<https://dl.acm.org/doi/10.1145/3719027.3744877>).

A large-scale assessment of 158 widely used third-party SDKs found 338 instances of privacy data exfiltration, with more than 30% of the SDKs providing no privacy policy at all; the study examined Android builds, yet these are the same cross-platform vendors whose SDKs ship inside iOS apps (<https://arxiv.org/html/2409.10411v1>).

This tracking is not a grey area in Europe. Article 5(3) of the ePrivacy Directive - PECR in the UK - requires prior informed consent before storage of or access to information stored on the user's device (this includes the storage and running of the actual SDK scripts themselves). The GDPR requires that consent be specific, informed and freely given, with transparency obligations under Articles 12 to 14 that must be met before processing begins.

So I am not going to hold my punches here when I say as a legal expert that an advertising SDK that loads on app launch, reads device identifiers and other data (ePrivacy Directive doesn't care what the data is or whether it is personal data - all data is covered), transmits them to a data broker with no valid consent flow, is breaking the law, period. Do not pass go, do not collect 200 Euros. This is precisely how a substantial proportion of the App Store's apps behave, as demonstrated by the above studies. The apps are unlawful despite the claims by Apple that they were each individually reviewed by them; yet they remain on sale and Apple continues to profit handsomely from them.

Apple's defence of the walled garden has always been App Review. The company reports that in 2025 it reviewed more than 9.1 million submissions, rejected over 2 million of them, prevented 2.2 billion dollars in fraudulent transactions (<https://www.apple.com/newsroom/2026/05/the-app-store-stopped-over-2-point-2-billion-usd-in-fraudulent-transactions-in-2025/>). The numbers look impressive and I suspect they are presented specifically in this way so it looks like everything is fine - but the research (again with the research) tells a very different story. Whereas Apple are quick to headline how much potential fraud they prevented with big, big numbers they completely fail to remove Apps that are in direct and blatant breach of the ePrivacy Directive - and Apple know that any app which is exfiltrating data without consent is breaking the law because Apple themselves have been subjected to enforcement for precisely the same offence (see below).

But even with these big numbers look at what they didn't catch. A counterfeit Ledger Live app sat in the App Store harvesting seed phrases until victims had lost 9.5 million dollars in cryptocurrency (<https://appleinsider.com/articles/26/07/27/weak-app-store-protections-at-core-of-18m-crypto-app-fraud-lawsuit>). A subscription scam ran at a million dollars a month before a member of the public, not App Review, exposed it (<https://appleinsider.com/articles/21/04/07/another-1-million-scam-app-surfaces-amid-app-store-legal-battles>). Developers describe fraud and clone apps breezing through review while legitimate updates are held for weeks over payment-rule technicalities (<https://appleinsider.com/articles/23/04/27/anonymous-developers-claim-fraud-scams-clones-breeze-by-app-store-review>). The pattern in those stories is worryingly consistent: app review seems to be very efficient at enforcing Apple's commercial terms with precision while the privacy, security, data protection, consumer protection and fraud screening is, well, let's just say, rather porous.

The privacy labels on the store are self-declared by developers; the Oxford study found they were frequently inaccurate, with no evidence of systematic verification. The clearest recent proof comes from Apple; privacy manifests declaring SDK data practices have been mandatory for App Store submissions since May 2024, yet NowSecure's August 2025 testing found 97 per cent of apps missing the required manifests for their third-party SDKs. Every one of those apps passed App Review with its privacy manifest either absent or at best, incomplete. Apple polices its 30 per cent with far more rigour than it polices your fundamental human rights.

That 30% actually matters, Apple is not a neutral gatekeeper; it takes up to 30 per cent of the revenue of the apps it reviews. A meaningful share of that 30% is paid from advertising revenues, which means it is funded through the exfiltration of your data. The unlawful exfiltration this article describes is not happening despite Apple's business model, it appears to be the business model.

## Apple's own consent record

The French data protection authority fined Apple 8 million euros for reading and storing identifiers on users' devices for App Store advertising unlawfully, with the relevant setting pre-ticked and buried (<https://www.huntonprivacyblog.com/2023/01/06/cnil-fines-apple-8-million-euros-over-personalized-ads/>).

Researchers at Mysk showed that Apple's own apps transmitted detailed analytics - every tap in the App Store, in real time - tied to the DSID, an identifier linked directly to the user's iCloud account name and email, even with the analytics toggle switched off (<https://gizmodo.com/apple-iphone-privacy-dsid-analytics-personal-data-test-1849807619>). NOYB filed complaints in Germany and Spain over the IDFA itself, an identifier Apple writes to every device without asking anyone, which is precisely the conduct Article 5(3) prohibits (<https://noyb.eu/en/noyb-files-complaints-against-apples-tracking-code-idfa>).

In 2025 the French competition authority fined Apple 150 million euros over ATT, finding that Apple imposed a consent regime on everyone else that it did not apply to its own apps until iOS 15 shipped (<https://www.autoritedelaconcurrence.fr/en/press-release/targeted-advertising-autorite-de-la-concurrence-imposes-fine-eu150000000-apple>).

When you look at the evidence (again with the evidence...) it would seem the auditor (the only party capable of doing real forensic audits through the App Review process) is failing its own audits.

## Apple should be liable

In Wirtschaftsakademie the Court of Justice held that a fan-page operator was jointly responsible for processing carried out by Facebook, since the operator's choices enabled the processing. In Fashion ID the Court held that a website embedding a social media button became a joint controller for the collection and transmission it enabled, since it had decisive influence over that processing as a commercial activity (<https://www.clearycyberwatch.com/2019/08/cjeu-judgment-in-the-fashion-id-case-the-role-as-controller-under-eu-data-protection-law-of-the-website-operator-that-features-a-facebook-like-button/>).

Apple defines the APIs and the identifiers an app can access, the contractual SDK requirements, the consent UI, the distribution channel, the app review, the payment methodologies it must use. Apple holds more decisive influence over the data processing of a third-party iOS app than any joint controller the Court ruled on, so to consider them as anything other than a joint controller with joint liability seems inescapable, legally speaking.

Apple has made independent verification impossible, users cannot audit, researchers are litigated against or licensed selectively, regulators see only that which is disclosed during investigation and enforcement actions.

Apple simultaneously claims to review every app on the platform, takes a commission on the revenues and sets up marketing campaigns claiming what happens on your iPhone stays there - contrary to the research (that pesky research again) and the evidence (yeah the evidence).

The legal reform I am arguing for is a rebuttable presumption of joint liability: where a platform prevents independent audit of the software it distributes, it should be jointly liable for unlawful processing carried out by that software, with the SDK vendors and developers, unless it can demonstrate it took effective measures to prevent the violation.

Apple can rebut the presumption any time it likes, by opening the platform and allowing real network transparency for users on all five operating systems, audit APIs that let accountable third parties verify app behaviour, research access that does not require Apple's invitation or a jailbreak, verification of privacy labels rather than self-declaration. All I am asking for is either transparency or accountability and I think that is entirely fair.

## Disclosure

Over the years I have done quite a lot of work with Apple and have had a very good relationship with them but they have always maintained that they value my holding them to account and keeping them honest. So this article is not anti-Apple, it is simply me being honest and holding Apple to account for making it impossible for individuals, researchers, regulators etc to understand how apps are processing their data.

To my friends in Apple's executive - you need to fix this, it is just quite simply a bad policy. Keep the defaults locked down, but don't block people from seeing what is going on - add a switch, a toggle, something - so long as it empowers those who actually own the device to understand what is happening on it - it is quite simply the right thing to do.
