---
title: Why did the ASOS hackers go directly to their customers?
subtitle: ''
source: Proton Blog
source_url: https://proton.me/business/blog/asos-data-breach
author: Kate Menzies
date: '2026-10-09T15:56:57Z'
fetched: '2026-10-10T17:51:18Z'
image: ''
summary: 'On Tuesday October 6, customers of ASOS, the British fashion retailer, received a push notification from the official app with the title “ASOS HACKED.” It read: “Dear Asos DPO and IT, we have fully compromised the Snowflake instance.'
tags:
- For business
guid: https://proton.me/business/blog/asos-data-breach
---

On Tuesday October 6, customers of ASOS, the British fashion retailer, received a push notification from the official app with the title “ASOS HACKED.”

It read: “Dear Asos DPO and IT, we have fully compromised the Snowflake instance. Engage with us, or we will leak it.”

With this message, hackers unleashed a new weapon in the cyberattack arsenal: breaching business accounts and taking their extortion demands directly to customers. If these ASOS-style attacks become commonplace, there are implications for any business that regularly sends messaging to customers. Mass messages to consumers through emails or in-app messages are an easy way to amplify phishing attacks from trusted senders, similar to the bitcoin scam sent through [hacked Twitter accounts](https://en.wikipedia.org/wiki/2020_Twitter_account_hijacking) in 2020. It can also add pressure on companies to pay ransoms or provoke general chaos that affects companies’ bottom line.

Luckily, on a fundamental level, your prevention strategies as a business or consumer don’t change much. Here’s what we know.

## What happened to Asos?

Snowflake is a data storage and analysis service that ASOS used as cloud infrastructure. The hackers used a [social engineering attack](https://proton.me/blog/what-is-social-engineering) to gain access to an employee’s account on a platform called Simon AI, which is integrated natively into Snowflake. News [reports](https://www.bbc.com/news/articles/cj62ylzpr6d3o) said the hackers tricked the employee by “impersonating a trusted contact to obtain login credentials”.

(Snowflake itself wasn’t compromised in this instance, but it has been [breached before](https://www.huntress.com/threat-library/data-breach/snowflake-data-breach).)

From there, they launched an unorthodox [ransomware](https://proton.me/business/blog/ransomware-threats-smbs) attack, using the ASOS app’s notification system to make an extortion demand sent to ASOS users. As the notification was addressed to the DPO (data protection officer) and IT department for the company, it appears that the hackers were making the threat public to create pressure on ASOS to make a payment.

In a [market announcement](https://www.londonstockexchange.com/news-article/ASC/update-regarding-cyber-incident/17822931) the same day, ASOS said it was investigating unauthorized activity involving platforms used to communicate with customers. It also notified customers that their personal information, including names and contact details, may have been accessed, but that passwords and payment details didn’t appear to have been impacted.

However, in the following days, it [emerged](https://www.bbc.com/news/live/cjkg7205q9ret) that hackers did in fact collect data about potentially millions of customers. The hackers [contacted the BBC](https://www.bbc.com/news/articles/c3zxjdw5ywgpo) with an example of the stolen data: names, addresses, phone numbers, emails, customer numbers, and dates of birth.

## What should ASOS customers do?

Because hackers obtained personal information, they can now launch much more effective [phishing](https://proton.me/blog/what-is-phishing) attacks against ASOS customers.

If you’re an Asos customer:

- Create a new [strong password](https://proton.me/pass/password-generator) for your ASOS account.
- If you’re contacted by someone claiming to be from ASOS saying they need further information or that your account is now locked, **don’t engage with them**. Inform ASOS of the call, email, or SMS via their [official customer care channel](https://www.asos.com/customer-care/get-in-touch/).
- If you receive any unusual emails from other retailers or someone you don’t know asking you for more information or telling you to click a link, **don’t click or engage with them**. Always navigate to the company’s website or app directly to log in rather than through unexpected links you receive.

## What is the impact?

ASOS’s brand reputation has also been significantly impacted. Not only has customer data been stolen, but the attack was announced directly to its customers in real time: ASOS didn’t have time to contain the attack before notifying customers and regulators of a breach.

Shares in ASOS fell by [as much as 11%](https://www.ft.com/content/eab7052d-6640-4928-a128-8df73455ba0a?syn-25a6b1a6=1) following the attack as concerned customers posted about it on social media. The direct notification created significantly more anxiety and urgency than a standard extortion attack made directly to a business. By targeting users, the hackers caused more chaos because it wasn’t clear how extensive the threat was.

Businesses need to be aware that the platforms they use to communicate with customers are likely to be targeted by hackers more in the future. If hackers can go directly to your customers, you lose control of your response instantly and customer confidence in your brand is shattered.

## How can businesses avoid this type of attack?

Hackers gained access to the Snowflake account by impersonating a trusted ASOS contact, a typical example of phishing. We’ve written extensively about how to [protect your business against phishing](https://proton.me/business/blog/phishing-attacks), but one of the most important actions your business can take is enabling [two-factor authentication (2FA)](https://proton.me/blog/what-is-two-factor-authentication-2fa) for all accounts with access to sensitive customer data.

### Enable 2FA

By enabling 2FA, you create an extra layer of protection for accounts that’s much harder for hackers to breach. Combining 2FA with a strong, unique password for each account is an effective and simple solution to protect your business from phishing attacks.

### Centralize password management

Adopting a [business password manager](https://proton.me/business/pass) with a built-in 2FA authenticator, [email aliases](https://proton.me/pass/aliases), and [secure sharing](https://proton.me/pass/password-sharing) can help your business guard against the kind of attack launched at ASOS. Securing logins in an end-to-end encrypted password manager which can safely generate, store, and autofill passwords helps your team members work safely and protect the sensitive data they need access to.

### Harden communications channels

Often security audits start with critical systems like payment systems, core databases, or customer relationship managers. But the ASOS hack shows that communications channels are dangerous vectors that need to be locked down. Social media accounts, in-app notification platforms, email platforms like Mailchimp, and SMS platforms should be restricted to the minimum number of employees with 2FA strictly enforced.

Even if an email address or password is phished, hackers can’t access an account protected by 2FA. If each account has a unique password and uses an email alias, hackers can’t retry passwords across multiple services or build an activity profile for the email address.

As hackers continue to evolve their attack strategies, don’t give them an opportunity to damage your reputation and target your customers. Adopt a [business password manager](https://proton.me/business/pass) that keeps you and your customers safe.
