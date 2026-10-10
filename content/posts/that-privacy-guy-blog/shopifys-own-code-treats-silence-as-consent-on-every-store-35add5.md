---
title: Shopify's own code treats silence as consent on every store it hosts, while its DSA filings leave the user numbers blank
subtitle: ''
source: That Privacy Guy! Blog
source_url: https://www.thatprivacyguy.com/blog/shopify-consent-defaults-open
author: Alexander Hanff
date: '2026-09-25T00:00:00Z'
fetched: '2026-10-10T17:51:18Z'
image: https://www.thatprivacyguy.com/blog/assets/2026-09-25-001.png
summary: This started somewhere I didn't want it to go. A small Maltese retailer sent me unsolicited direct marketing, so I ran a forensic audit of their ecommerce site before sending them my concerns. I don't enjoy going after small companies - they buy a platform, they trust the vendor to have done the compliance work.
tags:
- privacy
- ePrivacy
- GDPR
- DSA
- Consent
- Cookies
- Shopify
- Controller
- surveillance
- Compliance
guid: https://www.thatprivacyguy.com/blog/shopify-consent-defaults-open
---

This started somewhere I didn't want it to go. A small Maltese retailer sent me unsolicited direct marketing, so I ran a forensic audit of their ecommerce site before sending them my concerns.

I don't enjoy going after small companies - they buy a platform, they trust the vendor to have done the compliance work.

There was no privacy notice I could reach, either. The owner hadn't configured one, no page in the site linked to it and there was no route by which any visitor could find it - I only got a copy later by guessing the address Shopify's own template would have put it at.

What the capture showed was that almost nothing I was complaining about was theirs. It was Shopify's. The scripts, the storage, the fingerprinting, the telemetry endpoints, the consent banner itself - all of it arrives with the platform - and the shop owner can neither see most of it nor change any of it.

So I went and read Shopify's own code. I've now filed two complaints, one with the Irish Data Protection Commission and one under the Digital Services Act. The rest of this piece is what's in them.

Every figure below comes from a single recorded session: one page, the home page of an ordinary Shopify store, loaded from an EU household on a clean browser profile and left alone for five minutes.

No interaction whatsoever, I pressed no key, clicked nothing and never once touched the consent banner at any point. The capture is hash-chained, signed with ECDSA P-256 in a hardware enclave and RFC 3161 timestamped, so none of this rests on my word - 13 records, 3,447 events, 312 scripts captured with their full source.

## The function

Here is the code that decides whether Shopify may process your data. It is served from

```
consent-tracking-api.js
```

, on the store's own domain:

```
      function W(e){
  const n = U();                      // U() reads and parses the _tracking_consent cookie
  if (!n || !n.purposes) return !0;   // no consent record at all  ->  returns true
  const t = n.purposes[e];
  return "boolean" != typeof t || t;  // flag not a boolean        ->  returns true
}
function $(){return W(a.PREFERENCES)}
function X(){return W(a.ANALYTICS)}
function Z(){return W(a.MARKETING)}
function z(){return W(a.SALE_OF_DATA)}

```

To those who don't understand code what this basically does is if there's no consent record, the function returns

```
true
```

. Those four wrappers underneath are exported as the public interface

```
preferencesProcessingAllowed
```

,

```
analyticsProcessingAllowed
```

,

```
marketingAllowed
```

and

```
saleOfDataAllowed
```

. The identical logic sits in Shopify's Web Pixels Manager bundle as the function

```
Be
```

.

So when a visitor has given no consent whatsoever, Shopify's own interface answers that analytics is allowed, that marketing is allowed, that preferences are allowed and that the sale of their data is allowed. A person who has never been asked anything is handled exactly like a person who clicked yes to everything.

Article 5(3) of the ePrivacy Directive permits storage on, or access to, terminal equipment only where the user has consented and only after clear and comprehensive information about the purposes. Article 4(11) of the GDPR requires a freely given, specific, informed and unambiguous indication by a statement or a clear affirmative action.

Code that returns "allowed" in the absence of any record is the precise inverse of an affirmative action. In Planet49 (C-673/17) the Court held that consent isn't validly given where storage is permitted by a pre-checked box the user has to deselect. Shopify's position is worse than a pre-checked box - because there was no interaction at all, let alone an affirmative one.

Also it is not some accident - the same file contains a function called

```
De
```

. It carries a hard-coded list of country codes -

```
IE
```

,

```
MT
```

and every other Member State - and maps them to the string

```
"GDPR"
```

. Shopify knows exactly when it's operating in the EU. It has written code that identifies the applicable regime and code that defaults to permitted - and it shipped both.

## It recorded that I couldn't be tracked, then sent the data anyway

This is the part I keep coming back to. Shopify's telemetry payloads carry a field called

```
user_can_be_tracked
```

. During my session, on four separate transmissions, that field was set to

```
"false"
```

- and the event was transmitted regardless.

```
      {"schema_id":"web_pixels_manager_event_publish/1.7",
 "payload":{"event_name":"page_viewed","event_type":"standard",
            "user_can_be_tracked":"false",
            "event_id":"sh-d7bc3515-FB2C-46A8-ADA8-09AD1579A878"}}

```

The same value appears on the OpenTelemetry metrics posted to

```
otlp-http-production.shopifysvc.com
```

, attached to

```
"event_name":"Page Viewed"
```

and then again to

```
"event_name":"Viewed Product Variant"
```

.

Shopify's own code reached the conclusion that I couldn't be tracked. It wrote that conclusion into the payload as a field. Then it sent the payload to Shopify's servers describing the page I had looked at and the product variant I had been shown. Whatever this is, it isn't a company that failed to notice the legal position. It's a company that noticed, recorded the fact in a machine-readable field and ignored its own instructions by design.

## Then it told its own servers that I had consented

It gets worse. At 08:43:51.180Z and again at 08:43:51.430Z, Shopify transmitted these to

```
monorail-edge.shopifysvc.com
```

:

```
      {"schema_id":"shopify_pay_login_with_shop_sdk_feature_initialize/1.1",
 "payload":{"analytics_trace_id":"95654f05-6b25-4f16-b4d8-e50f2ef36281", ... },
 "metadata":{"consent":["analytics","marketing","sale_of_data","preferences"],
             "consent_provider":"consent-tracking-api",
             "consent_version":"v1"}}

```

I had consented to nothing. The banner was sitting there on the page and I hadn't touched it. Shopify generated and transmitted two records asserting that consent existed for analytics, for marketing, for the sale of my data and for preferences - attributing that consent to

```
consent-tracking-api
```

.

Those records are false - and they're the entirely predictable output of the function at the top of this article. Any Shopify system downstream that reads that metadata has been told my data was consented data. I've asked the DPC to establish how many of these records exist across the EU, which systems consume them and what has been done with the data.

For completeness, Shopify also transmitted

```
privacy_banner_render/1.1
```

and

```
privacy_banner_initialized/1.0
```

within the same second, each carrying

```
"regulation":"CMP"
```

. It recorded that it had drawn a consent banner - and it shipped my data before that banner had been answered.

## The timing and the fingerprinting

The whole sequence is over before a human could have read anything. Times are from the first recorded event.

| Time | What happened | Which Shopify script |
| --- | --- | --- |
| +0.419s | wrote  ``` consentHeader ```  to sessionStorage | ``` privacy-banner/storefront-banner.js ```  at  ``` fn ```  (1:6873) |
| +0.431s | POST to  ``` otlp-http-production.shopifysvc.com/v1/metrics ``` | ``` cdn/wpm/...js ```  at  ``` xo.exportTo ```  (1:141397) |
| +0.433s | wrote cookie  ``` _shopify_test ``` | ``` cdn/wpm/...js ```  at  ``` zn ```  (1:133860) |
| +0.454s | read  ``` navigator.userAgent ```  , then beaconed | ``` trekkie...min.js ```  at  ``` t.logMetricToMonorail ```  (1:50306) |
| +0.53s | cookie  ``` _shopify_essential ```  set by Shopify's servers | server-side |
| +0.80s | cookie  ``` _shop_app_essential ```  set on  ``` .shop.app ```  , SameSite=None | server-side |
| +0.864s | **canvas fingerprint via  ``` toDataURL ```** | ``` perf-kit/shopify-perf-kit-3.9.4.min.js ```  at  ``` Ke.checkEnvironment ```  (1:47582) |
| +1.102s | enumerated  ``` navigator.plugins ``` | same script, same  ``` Ke.checkEnvironment ``` |
| +1.202s | beaconed 3,777 bytes to Shopify's collector | ``` trekkie...min.js ```  at  ``` e.exportMetrics ```  (1:58188) |

419 milliseconds. Nobody reads a consent notice in 419 milliseconds - and I made no decision at any point in the five minutes.

Note which script went first.

```
storefront-banner.js
```

is Shopify's own privacy banner. The mechanism Shopify hands merchants for the specific purpose of obtaining consent wrote to my device before it had asked me a single thing. I've been saying for years that CMPs which set storage before consent are unlawful by design. Here is a platform that ships one to millions of shops.

Look at the function name doing the fingerprinting.

```
Ke.checkEnvironment
```

. Reading back a rendered canvas and enumerating installed plugins are textbook device fingerprinting - and Shopify's own code names the function after what it's for.

## Shopify is a Controller under the GDPR

Shopify's public posture is that it's plumbing. In the DSA transparency report it filed on 28 February 2026 it says that "As an infrastructure provider, Shopify's core services function primarily as a hosting environment for independent merchants" and that "Content and presentation on each storefront is controlled by the individual merchant".

Now read Appendix E of its own Data Processing Addendum, which is headed "Shopify as a Data Controller or Business for Enhanced Services":

> Shopify is a Data Controller of Your Customer Personal Data that it processes in accordance with this Appendix E and shall individually determine the purposes and means of its processing of such Personal Data and how to use and process such Personal Data, including determining the legal basis for its processing under Applicable Data Protection Law.

Section 9.2 of the Terms describes those services as powered by "Shopify Network Intelligence" - and says that to deliver them "Shopify can use Personal Data from your customers' interactions and transactions with Your Store, with other Merchants, and with Shopify". That is cross-merchant processing for Shopify's own commercial benefit - and it's designed that way.

The switch is on unless the merchant turns it off - and Shopify's own help pages say the setting "takes effect globally", so a merchant can't turn it off for the EU alone. Turning it off costs you features - Appendix E says a merchant who does so "will not be able to use certain apps or features". Having reserved controllership for itself, Shopify puts the consent obligation on the shop owner: a merchant whose customers are in the EEA "must obtain consent for targeted advertising as part of the Enhanced Services, and the use of cookies or other local storage technologies".

Think about what that means in practice. Shopify requires a small retailer in Malta to obtain consent for storage that Shopify's own code performs 419 milliseconds after page load, using a consent interface Shopify wrote, which returns "allowed" when no consent exists. The merchant is contractually on the hook for a breach they can't prevent, can't detect and were never told about.

While we are on the subject of being reachable, try contacting Shopify's Data Protection Officer. For anyone in the EEA or UK their privacy policy gives a postal address, care of a corporate services provider in Dublin - and nothing else. No email address appears anywhere in that policy or in their Data Processing Addendum. Article 37(7) requires the Controller to publish the DPO's contact details. Article 38(4) gives Data Subjects the right to contact the DPO about the processing of their data. A letterbox at an agent's office is a thin reading of both.

This is the same ground as the Belgian case against the IAB TCF. In IAB Europe (C-604/22) the Court held that a body which proposes a framework of rules on consent, containing binding technical rules and detailed arrangements for storing and disseminating the consent data, is a Joint Controller where it exerts influence over the processing for its own purposes - and that not having direct access to the data makes no difference. Shopify is a stronger case than IAB Europe in every way. It operates the infrastructure, it does have direct access - and it has conceded controllership in writing.

## The other half: Shopify told the EU it's too small to regulate

While I was reading the contracts I went and looked at what Shopify has filed under the Digital Services Act - and this is where it stops being a privacy story.

Article 24(2) of the DSA requires providers of online platforms to publish the average monthly active recipients of their service in the EU, every six months, in a publicly accessible place. That figure is what the Commission uses to decide whether a platform crosses 45 million and becomes a Very Large Online Platform (VLOP), with all the systemic-risk obligations that follow.

Shopify has failed to publish those numbers:

> To the extent that any of Shopify's offerings may be considered 'online platforms' under the DSA, we concluded that during the period January 1, 2025 to December 31, 2025, the average number of monthly active recipients of those services in the EU was well below the 45 million user threshold for being designated as VLOPs.

Go and open the actual filings and it's worse than the hedging suggests. Shopify filed two transparency reports, one for "Shopify" and one for "Shop". In both, the table that carries the average monthly active recipients is **completely blank**. Every value empty. They have labelled the section "Only for VLOPs and VLOSEs" and left it at that. The "Shop" report still has the Commission's unedited template placeholders in it -

```
[...]
```

in the country rows,

```
YYYY-MM-DD/YYYY-MM-DD
```

in the reporting period.

That reasoning is circular and it inverts the Regulation. The figure isn't a consequence of being designated, it's the input from which designation is determined. Article 33(4) spells out that the Commission decides "on the basis of data reported by the provider... pursuant to Article 24(2)" - and the second subparagraph says in terms that failing to comply with Article 24(2) "shall not prevent the Commission from designating that provider as a provider of a very large online platform". You don't get to withhold the number because you've decided the number wouldn't have mattered.

Two further failures are in the same documents. Article 24(2) wants an average over the past six months and both reports state a calendar year. It wants publication at least every six months, yet the filings themselves record the previous report as 2025-04-02 and this one as 2026-02-28, roughly eleven months apart.

It is worth sitting with how little those filings actually contain. I went through every cell. In the Shopify report, the section covering content Shopify acted against on its own initiative has 721 value cells, of which exactly one is not zero. The section on notices received has 480, of which 53 carry anything. This is a company reporting to a regulator that it found almost nothing, across a platform its own marketing says 875 million people bought something from last year.

## Is the 45 million plausible? Shopify's own numbers say no

Shopify's defence rests on being infrastructure rather than a platform and on its merchant relationships being business-to-business so the shoppers somehow don't count.

The General Court has already dealt with this. In Zalando v Commission (T-348/23, 3 September 2025) Zalando published two figures - 83.341 million for the whole platform and 30.836 million for the third-party seller portion - and argued that only the latter part was an online platform. The Court dismissed the action - and along the way it held that an online platform is a subcategory of hosting services, so calling yourself hosting puts you inside the category rather than outside it (paragraph 21); that carrying out checks on content doesn't take you out of the definition (paragraph 31); and that the old "mere technical, automatic and passive" reading of an intermediary comes from the Directive 2000/31 liability exemptions and "cannot be used for the purposes of applying Regulation 2022/2065", not least because Article 89(1) of the DSA deleted the very Section that was being interpreted (paragraphs 41 to 42).

Recital 77 then kills the B2B argument twice over. An active recipient is anyone "exposed to information disseminated on the online interface... such as viewing it or listening to it, **or by providing information, such as traders**". Merchants count - because they provide information. Visitors count - because they're exposed. The business-to-business relationship adds to the number and takes nothing away from it. For anyone about to argue that each storefront is its own separate website, recital 77 got there first: recipients across "different uniform resource locators (URLs) or domain names" are to be counted once each, not excluded.

So what would the real number look like? Here is Shopify talking about itself:

| Shopify's own statement | Where |
| --- | --- |
| "more than 875 million people bought something from a Shopify store, that's 1 in every six internet users" | shopify.com/news |
| "having served 875 million shoppers in 2024" | shopify.com/blog |
| "millions of businesses in over 175 countries" | shopify.com/news |
| Merchants 44% US, **31% Europe, Middle East and Africa**, 16% APAC, 5% Canada, 5% LatAm | Form 10-K, FY2025 |
| Revenue by merchant location: **EMEA $2,426m, 21%** of $11,556m | Form 10-K, FY2025 |

Those 875 million are buyers - people who completed a purchase. Under Article 3(p) an active recipient is anyone merely exposed to a listing. The 875 million is a floor, not a measure.

For scale, these are the Commission's own published figures for designated marketplaces: Temu 75 million, Zalando 83.3 million, AliExpress 104.3 million, Shein 108 million, Amazon Store 181.3 million. The lowest number attaching to any designated service on that entire list is 45 million.

Shopify would have the Commission believe that a platform describing its annual buyers as one in every six internet users, with 31% of its merchants in EMEA and 21% of its revenue there, has fewer EU monthly active recipients than Temu? Pull the other one, it has bells on it.

There is one more thread. Shopify's own transparency report claims it "does not possess overall metrics from which an exposure measure for illegal or incompatible content could be derived". A company that fingerprints visitors' devices, streams per-visit telemetry from every storefront to its own collectors and aggregates behaviour across merchants for its own commercial purposes isn't a company that lacks the means to count who saw what.

## The two complaints

The complaint to the Irish Data Protection Commission asks it to determine Shopify's Controller status, to require the source and change history of that consent logic and when the default-to-permitted behaviour was introduced, to produce every false consent record generated for EU Data Subjects, to explain why data marked

```
user_can_be_tracked: false
```

was transmitted rather than discarded and to produce the data protection impact assessment - or confirm that none exists.

It also asks the DPC to use the teeth it has. Regulation 5(1) of S.I. 336 of 2011 prohibits the "listening, tapping, storage or other kinds of interception or surveillance of communications and the related traffic data by persons other than users, without the consent of the users concerned". Regulation 17(11) makes Regulation 5 a prescribed provision, so the Commission can serve an enforcement notice; Regulation 17(10) makes non-compliance with that notice an offence; Regulation 26 lets the DPC prosecute it directly; and Regulation 25 makes officers of the company separately liable where the offence involved their consent, connivance or neglect. I've asked the Commission to serve that notice and to prosecute if Shopify ignores it.

The DSA complaint is with the Malta Communications Authority, Malta's Digital Services Coordinator. Article 53 gives a recipient the right to lodge with the Coordinator of the Member State where they are located - and that Coordinator assesses it and transmits it to the Coordinator of establishment with an opinion. Shopify's establishment is in Ireland, so it goes on to Coimisiun na Mean. The complaint asks for Shopify to be required to produce the actual user numbers and the methodology behind them under Article 51(1)(a) and Article 24(3), for a determination of whether Shopify's services are online platforms and for the Commission to be informed under Article 24(4) if the threshold appears to be met. It also raises Articles 30 to 32, which apply to any platform letting consumers contract with traders regardless of size - and on Article 31, compliance by design, I've a small and rather telling piece of evidence. The store's Terms of Service, generated from Shopify's own template, was live and public carrying the unfilled placeholders

```
[LINK TO PRIVACY POLICY]
```

and

```
[LINK TO REFUND POLICY]
```

where the links belong. Shopify supplies the template, supplies the interface, requires the merchant to post a privacy policy link prominently and neither stopped the template going live unfilled nor noticed that it had.

## This is what platform liability is for

Millions of small businesses bought Shopify partly on the promise that the compliance was handled. They aren't in a position to read minified JavaScript served from a CDN path they don't control, on a domain they think is theirs. When the platform writes the consent interface, writes the code that ignores it, collects the data for its own cross-merchant purposes and then puts the legal obligation on the shop owner in a contract nobody reads, the shop owner isn't the problem - the platform is.

I've done this before and I'll keep doing it. In 2018 I filed against the European Data Protection Board on the day its own website went live - the site didn't comply with the rules the Board exists to enforce. On 1 October 2019, within two minutes of the Court of Justice handing down Planet49, I filed against the Court - because the Court's own website breached the judgment it had just issued. I hold platforms to the standard they set for the people who depend on them.

Shopify's own code treats silence as a yes. Shopify's own telemetry writes down that the user can't be tracked and transmits anyway. Shopify's own contract admits it determines the purposes and means. Shopify's own filings leave the user numbers blank. I haven't had to infer a single one of those things - they're all in material Shopify wrote and published itself, which is precisely why both regulators should have no difficulty with this.

*The complaints, the recorded session, the signed records and the timestamp tokens are available to the regulators on request and to any journalist who wants to verify the findings independently.*
