---
title: Google’s selfie video sign-in puts your face on its servers
subtitle: ''
source: Proton Blog
source_url: https://proton.me/blog/google-selfie-video
author: Elena Constantinescu
date: '2026-10-16T20:38:57Z'
fetched: '2026-10-16T18:54:43Z'
image: ''
summary: Google now lets you sign in to your Google Account with a selfie video. You film your face once, Google stores the clip on its servers, and if you get locked out, you record a new one that Google compares against the original. The company presents selfie video verification as a backup for people who lose the device that holds their passkeys, next to recovery phones and recovery emails.
tags:
- News
guid: https://proton.me/blog/google-selfie-video
---

Google now lets you sign in to your [Google Account](https://proton.me/blog/google-account-recovery-gmail-scam) with a selfie video. You film your face once, Google stores the clip on its servers, and if you get locked out, you record a new one that Google compares against the original.

The company presents selfie video verification as a backup for people who lose the device that holds their passkeys, next to recovery phones and recovery emails. The cost is a reference recording of your face, in motion and from several angles, stored on its servers under rules it can change.

Once Google holds that recording, it could help train its AI, power age checks, or end up in a government data request, and Google’s privacy promises leave room for all three. Here’s what that means for your privacy.

- How Google’s selfie video verification works
- Your face lives on Google’s servers, for as long as its rules allow
- Could your selfie video end up training Google’s AI?
- What Google stores, the US government can request
- Age checks need a face, and Google already has yours
- Facebook video selfie verification
- Account recovery doesn’t need your face on Google’s servers
- Give Google less of you

## How Google’s selfie video verification works

To use Google’s selfie video verification, you have to enroll. While signed in, you look at your camera and follow guided head movements so Google capture several angles. The recording is then stored on Google’s servers and used as your reference video.

When you need to get back in, you have to record a new selfie video, which is compared to the reference video. Liveness checks, synthetic media detection and, on some devices, hardware signals that the video came from a real camera are meant to stop photos and deepfakes.

After a significant change in appearance, you delete the old reference video and record a new one, and Google may ask you to update it periodically.

## Your face lives on Google’s servers, for as long as its rules allow

Google stores the reference video on its servers so the feature works across devices. It does not offer an option to keep it on your phone, though it could have asked for a separate reference on each device, as face unlock does. Because the matching runs on Google’s servers, Google can decrypt the video.

Deleting the video removes it from Google’s servers. According to its general privacy policy, it takes around 2 months to clear active systems, up to 6 months for backups, and longer when Google cites security, fraud prevention, or legal requests.

## Could your selfie video end up training Google’s AI?

Google says the video is used only to sign you in, and that allowing it to improve its verification technology is optional. It’s unclear whether that refers to face matching only or extends to broader AI training, such as for its [Gemini](https://proton.me/lumo/ai/is-gemini-safe) models.

Before you consider opting in, remember that [what Google knows about you is valuable](https://proton.me/blog/what-does-google-know-about-me). A reference video refreshed over years shows how a face ages. A re-enrollment after a drastic change, when Google no longer recognizes you, shows which features stay the same.

Letting Google use your video to improve its verification technology may be optional, but it’s important to remember that [Google privacy settings](https://proton.me/blog/google-privacy-settings) and policies shift, especially when it comes to AI. In June 2026, Google changed settings for Search, Maps and Translate so saved images, audio and video can train its AI models, which effectively opted everyone in by default.

## What Google stores, the US government can request

As a US company, Google must answer [FISA](https://proton.me/blog/fisa-702-expiring-surveillance-reform) orders, [CLOUD Act](https://proton.me/business/blog/cloud-act) demands for data stored anywhere in the world, and National Security Letters, which usually come with gag orders that stop Google from telling you. Proton research on [Big Tech government requests](https://proton.me/blog/big-tech-government-requests-parenting) found US account disclosures at Google grew 557% between late 2014 and early 2025. Beyond handing over data on request, the company [signed](https://news.bloomberglaw.com/daily-labor-report/google-allows-pentagon-to-use-its-ai-in-classified-military-work) a deal letting the Pentagon use its AI for classified military work.

Google points to two safeguards:

- Its system only checks a selfie against the video on the same account and can’t search accounts by face.
- The selfie you record when signing in is deleted right after the check.

Neither safeguard covers the reference video, which stays on Google’s servers until you delete it. Anyone who obtains that file, through a court order, a breach or a future product, could run it through a face recognition system.

## Age checks need a face, and Google already has yours

[Age verification](https://proton.me/age-verification) laws make online services check how old you are, usually with an ID scan or a face scan that estimates your age. Some form of it is already law in the UK, Australia, France, Italy, Germany and 25 US states.

Google already [tests machine learning](https://techcrunch.com/2025/07/31/google-is-experimenting-with-machine-learning-powered-age-estimation-tech-in-the-u-s) to estimate whether US users are under 18, and asks people it flags by mistake to prove their age with a selfie or ID. It also says selfie video sign-in may be restricted for younger users. A verified, liveness-checked face video is exactly what facial age estimation needs. Google hasn’t announced that use, but as age verification laws spread, it has the data ready, and [age check results tend to persist](https://proton.me/blog/age-verification) and get linked to accounts.

## Facebook video selfie verification

Google isn’t the only Big Tech company turning your face into a login. [Meta](https://proton.me/blog/stop-meta-tracking) uses video selfie verification on Facebook to confirm identity, including to recover hacked accounts. When it [started testing](https://techcrunch.com/2024/10/21/meta-tests-facial-recognition-for-spotting-celeb-bait-ads-scams-and-easier-account-recovery), Meta said it compares the video with the account’s profile photos and deletes the facial data after matching. Google goes further by asking for a dedicated reference video and keeping it.

## Account recovery doesn’t need your face on Google’s servers

Google secure sign-in already works without your biometrics. [Passkeys](https://proton.me/blog/what-is-a-passkey) and on-device unlock check your face or fingerprint locally, and only a cryptographic proof leaves your device. Google itself recommends passkeys as the main way to sign in. You can change a password but not your face, so a cloud copy of it is a permanent risk taken on just to help you get back in if you lose the device that holds your passkeys.

To stay recoverable without a face video:

- If you’ve already enrolled and want to stop Google from using your selfie video to improve its systems, keep the option to improve Google’s verification technology switched off.
- To leave selfie video sign-in altogether, delete the video in your Google Account.
- Use [passkeys](https://proton.me/pass/passkeys), and store them in a [password manager](https://proton.me/pass) that syncs them across your devices with [end-to-end encryption](https://proton.me/learn/encryption/types-of-encryption/what-is-end-to-end).
- Save backup codes and set a recovery email and phone you control.

## Give Google less of you

Selfie video is one more piece of you that Google holds. Every feature that asks for your face, voice or habits adds to the same profile, governed by the same shifting policies and exposed to the same government requests.

If you’re thinking about [deGoogling your digital life](https://proton.me/blog/how-to-de-google), Proton is a [European alternative](https://proton.me/learn/european-alternatives) that helps you stay in control of your data. Protected by end-to-end and [zero-access encryption](https://proton.me/learn/encryption/types-of-encryption/zero-access) and [Swiss](https://proton.me/blog/switzerland) privacy laws, your sensitive data stays private. Not even we can access your encrypted content. Unlike Google, our business model doesn’t rely on advertising, and we don’t use your data for AI training.
