---
title: Capture the Code - visualising the scale of website surveillance
subtitle: ''
source: That Privacy Guy! Blog
source_url: https://www.thatprivacyguy.com/blog/capture-the-code
author: Alexander Hanff
date: '2026-10-29T00:00:00Z'
fetched: '2026-10-29T14:09:17Z'
image: https://www.thatprivacyguy.com/blog/assets/2026-10-29-001.png
summary: On 17th November I publish my research report on the 100 most visited English-language content websites in the world - news, reference, academic publishing, social and video platforms - and the surveillance conducted by their websites without any consent. I have decided to release a snapshot of the highlights of that data to illustrate just how vast it is.
tags:
- privacy
- ePrivacy
- GDPR
- Consent
- International-Transfers
- AdTech
- WebSentinel
- surveillance
guid: https://www.thatprivacyguy.com/blog/capture-the-code
---

On 17th November I publish my research report on the 100 most visited English-language content websites in the world - news, reference, academic publishing, social and video platforms - and the surveillance conducted by their websites without any consent.

I have decided to release a snapshot of the highlights of that data to illustrate just how vast it is.

## What you are watching

The film is a procedurally rendered representation of the audit data, built in Blender directly from the captured records - every element on screen is generated from the evidence and replayed in real time.

Each website was accessed from my home in Malta, between 1st and 3rd October 2026, in a clean Chrome browser profile with no privacy tools installed, for 5 minutes without any interaction from me.

I didn't click the consent banner specifically because I wanted to measure what is happening in the absence of consent.

The floor is a map of the world. Every company that received data from these pages is placed at its registered headquarters according to public information from their websites or where not possible, from existing crowd sourced lists - and every flow you see travelling across that map is a real connection recorded during the capture, carrying data from a visitor's device sitting in the EU, without any consent. The timing follows the page clock of the capture, so the flows appear in the order and at the pace they really happened - this is the data moving in real time, at scale, across 100 websites at once.

There were over 250 000 events observed in less than 5 minutes across the home pages of these 100 most publicly accessed websites. I also audited the privacy notices and cookie notices (where they existed) and observed a similar number of events, resulting in over half a million privacy events across all pages audited.

The scale of this is clearly visible with the towers of events shown in the renders with some reaching so high, I had to make the map larger and zoom the camera out further just to show them in the scene.

If you saw the earlier film of a single website that I posted on LinkedIn, you will recognise the Sentinel - the drone that moves through the city of scripts, scanning each event, reading the stack trace that shows which line of code caused it and the legal provisions it engages. The global film takes that same evidence and pulls the camera back far enough that you can see where it all ends up.

One very interesting finding is all the rhetoric around China monitoring us appears to be nothing more than moral panic. Very few data flows terminated in China whilst the vast majority of data flows terminated in the US - a country whose administration is currently hostile to the EU.

## Why I made this

The PDF reports for these audits are very long (many exceeding 100 pages each) which is not something I would consider as accessible to the general public. Further, you cannot really conceptualise scale from a 2 dimensional PDF document - so I wanted to put the data in a context that would be accessible and accurately represent the scale of the surveillance in 3D space.

After 20 years of working with dozens of privacy teams across the globe from small startups to some of the largest enterprise groups in the world - I see the same issue in every company - the privacy team do not understand the data flows they are supposed to govern.

In my experience this isn't down to not caring or not wanting to do their job - it is caused by several factors:

- They do not have the technical tools to detect these activities - the current incumbents in the RegTech space are only looking at cookies and even then, they do a terrible job and are often configured incorrectly and are technically incapable of enabling compliance, despite their marketing claims.
- They do not have the technical human resources - in my experience they literally have no idea what the code is doing because they do not have technical expertise on the team and rely on information disclosures from external stakeholders (see 3).
- External stakeholders they rely on to inform them about these processing activities (marketing and engineering teams) do not disclose, obfuscate the code to make it unreadable by humans and bundle non-essential technologies with essential ones, making them impossible to govern and meet compliance obligations.

As a result of this research I have now developed interactive visualisation tools (based on these renders but fully interactive web apps) to help privacy teams, supervisory authorities, policy makers, legislators, litigators, juries, and judges understand the data with the goal of finally, after 20 years of doing this work, forcing real change that protects our fundamental rights to privacy and data protection, even if that change has to come from mass litigation and representative actions. Litigation firms now have access to the tools they need to evidence their cases.

## The evidence behind it

Behind the film is the evidence itself. Every capture was made with WebSentinel to a forensic standard: hash-chained, signed with a hardware-held key, independently timestamped and anchored to the Bitcoin blockchain, with every behaviour traced back to the code responsible for it. None of it rests on my word, and every record can be independently verified by anyone who receives it.

Every audited organisation that publishes a privacy contact address was told about the audit in advance and given the opportunity to discuss its findings with us before publication - so far two have reached out (2% out of 100 organisations).

The audits are observations which engage specific laws - given that, it is important to note that whereas it is my opinion (based on the source code and the privacy notices) that the vast majority of the detected events are unlawful under EU and various other laws across the globe, some of the data may be false positive and legitimate - although would still require disclosure to meet that threshold so arguably still unlawful from a transparency perspective.

The purpose of this research is to raise awareness of the issues, ask the questions and file legal complaints based on my professional expertise and interpretation of the law as a lawyer specialised in these issues. I also believe that many of these observed events are breaches of criminal law focused on unauthorised access and use of computers and unlawful surveillance.

## 17th November

The full report will be published on 17th November and will be sent to legislators, regulators and the press, with the findings for every one of the 100 websites, the legal analysis under EU and US law and the signed evidence that supports it. In the week that follows, complaints will be filed with the competent supervisory authority against every audited organisation.

Watch the film and then ask why despite the fact that all of this has been unlawful since 2003, national supervisory authorities have so far failed to enforce the law almost entirely with nothing more than a handful of enforcements in the last 20 years despite widespread non-compliance and the continuous, ubiquitous surveillance of almost 500 million EU persons, then write to your politicians demanding answers (every MEP currently sitting in the EU Parliament will also receive a copy of the final report as well as the FTC, US Congress, US Senate and the California Privacy Protection Agency).

I can only do so much - it takes a much louder combined voice from all of you to make this stop - I urge you to take action.
