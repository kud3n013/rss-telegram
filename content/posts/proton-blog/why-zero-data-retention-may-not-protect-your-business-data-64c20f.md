---
title: Why “zero data retention” may not protect your business data
subtitle: ''
source: Proton Blog
source_url: https://proton.me/business/blog/what-zero-retention-data-means
author: Eamonn Maguire
date: '2026-10-08T17:35:26Z'
fetched: '2026-10-10T18:24:09Z'
image: ''
summary: If you’ve thought twice about sharing proprietary knowledge or customer data with OpenAI or Anthropic, you’re not alone. Data privacy has become a deciding factor for businesses choosing an AI vendor. Fortune reported this week that zero data retention (ZDR) is now where labs at the frontier of AI innovation are now competing.
tags:
- For business
guid: https://proton.me/business/blog/what-zero-retention-data-means
---

If you’ve thought twice about sharing proprietary knowledge or customer data with OpenAI or Anthropic, you’re not alone. Data privacy has become a deciding factor for businesses choosing an AI vendor. [Fortune reported](https://fortune.com/2026/10/05/openai-and-anthropic-battle-over-zero-data-retention-zdr-data-privacy-companies-look-to-open-models-and-sovereign-ai) this week that zero data retention (ZDR) is now where labs at the frontier of AI innovation are now competing. The promise of ZDR is simple: The vendor processes your prompt, returns an answer, and doesn’t keep a record of it. In practice, though, ZDR is reserved for top-tier customers. It also comes with exceptions (more on that soon), that means a vendor can override their own policy over just a few weeks.

## How we got here

On June 9, Anthropic launched its most powerful models, Fable 5 and Mythos 5, with a mandatory 30-day retention requirement on all traffic. It applied on every platform the models run on, including AWS Bedrock and Google Vertex AI, and it overrode zero retention agreements some businesses had already signed. Anthropic said the data was needed to detect misuse, would not be used for training, and would be deleted after 30 days “in almost all cases.”

Businesses didn’t buy it. Within a day, [Microsoft restricted its own employees’ access to Fable](https://www.theverge.com/report/947575/microsoft-claude-fable-5-restricted-internally) while its lawyers reviewed the terms. [Nvidia limited its use of Anthropic models](https://www.reuters.com/business/palantir-nvidia-curb-ai-model-use-over-data-fears-information-reports-2026-09-14/) to lower sensitivity work and leaned on its own Nemotron models internally. [Palantir declined to offer Anthropic models](https://www.reuters.com/business/palantir-nvidia-curb-ai-model-use-over-data-fears-information-reports-2026-09-14/) through its software until Anthropic guarantees irrevocable zero retention. [Booz Allen Hamilton](https://finance.yahoo.com/technology/ai/articles/palantir-nvidia-booz-allen-restrict-173737812.html), the US consultancy that does much of its work for defence and intelligence agencies, barred staff from using the commercial model for proprietary cybersecurity work.

A month later, [Microsoft CEO Satya Nadella](https://techcrunch.com/2026/07/13/satya-nadella-has-issued-a-shocking-warning-to-companies-using-ai/) and [Palantir CEO Alex Karp](https://www.cnbc.com/2026/08/03/palantir-karp-open-ai-anthropic-open-weight.html) warned companies publicly against frontier AI dependence. “You essentially pay for intelligence twice,” Nadella said, “once with money, and again with something even more valuable: the proprietary knowledge you must reveal to make that intelligence useful.”

Vendors are now competing to repair the damage. On August 19, [OpenAI reaffirmed full zero data retention](https://openai.com/index/offering-zero-data-retention-for-frontier-models/) for eligible enterprise and API customers on its frontier models. It previewed Private Safety Processing, a design in which content for eligible customers stays on infrastructure that the customer controls, or sits on OpenAI infrastructure encrypted under keys OpenAI does not hold. Automated systems scan it and return a narrow signal describing the category and severity of the activity.

On September 1, Anthropic announced [Enterprise Frontier Safeguards](https://www.anthropic.com/news/enterprise-frontier-safeguards), or EFS, which stores misuse-monitoring data in the customer’s own cloud account under the customer’s own encryption keys rather than in Anthropic’s. EFS was not available at announcement and is rolling out in phases later this fall, on Enterprise plans. In the meantime, the customers that Anthropic deems eligible get ZDR on Fable as a bridge.

Both fixes preserve monitoring. Where the records sit and who can read them may have changed, but no neither AI lab has committed to removing the records.

## Why data retention has become a dealbreaker

Businesses that adopted enterprise AI accepted retention terms on the understanding that their data would be kept briefly, used only to catch misuse, and never used for training. Four things undermined that understanding.

**A court can override a deletion promise.** In May 2025, a preservation order in [the New York Times lawsuit](https://www.reuters.com/business/media-telecom/openai-appeal-new-york-times-suit-demand-asking-not-delete-any-user-chats-2025-06-06/) forced OpenAI to keep ChatGPT and API output logs indefinitely, including deleted chats and chats on the paid Team plan. The order lasted about four months and some of that data is still held. API customers with ZDR were not affected, because their data was never stored. But once a vendor keeps a copy, a court decides how long it exists.

**US law reaches your data wherever it sits.** Under [the CLOUD Act](https://proton.me/business/blog/cloud-act), US authorities can compel a US company to hand over data in its possession, custody, or control, even if that data sits in a European data centre. An EU data residency option from a US vendor changes where your data is stored, not which government can demand it. Partners and contractors are part of this problem, not a footnote to it: Anthropic’s 30 day rule applied on AWS and Google Cloud too, and OpenAI says specialized third party contractors can access conversations for support, abuse investigations, and legal compliance. Customer-held encryption keys limit what a cloud provider can hand over, but they do not take the provider out of US jurisdiction.

**The FBI can also issue National Security Letters without a judge’s approval.** These demand subscriber and transactional records, meaning who used the service, when, and how much, rather than the content of conversations. They usually carry a gag order, so the vendor may be barred from telling you. That is why metadata matters even when content is deleted.

**The US government can also simply switch the model off.** Three days after the June 9 launch, a letter from the US Department of Commerce [barred access to Fable 5 and Mythos 5](https://proton.me/business/blog/openai-gpt-5-6) for non US nationals. Anthropic revoked customer access worldwide until controls lifted around June 30. For roughly three weeks, the most capable model on the market was unavailable outside the United States because a US agency decided it should be. No data handling term, however well drafted, protects against that. Availability is a jurisdictional risk too, and European buyers have started treating it as one: in a [Proton survey](https://proton.me/business/blog/business-continuity-survey) of 1,500 European business leaders published this year, 74% said they worry a US authority could order a vendor to cut off their access.

**Retention became the price of access.** A ZDR contract a business had negotiated did not protect it on the model it most wanted to use. Firms bound by client confidentiality or sector regulation had to choose between the best model and their own obligations.

A distinction worth holding onto: “we don’t train on it” is not the same as “we don’t learn from it.” A vendor that keeps your prompts can still study them, which tasks you automate, what your workflows look like. Security experts quoted by Fortune say AI companies could use insights like these to improve future products without training on the data directly. That could help a vendor [build something that competes with your product.](https://proton.me/business/blog/ai-training-business-data)

## All the exceptions under zero retention

The headline number is rarely the whole policy. Read the retention terms and the same carve-outs appear again and again.

- **Abuse monitoring.** Most AI APIs keep prompts and outputs by default so they can scan for misuse, typically for around 30 days, sometimes with human reviewers able to read them. Abuse monitoring was exactly the justification for [Anthropic’s 30-day rule](https://privacy.claude.com/en/articles/15425996-data-retention-practices-for-covered-models), and it is why you have to apply for ZDR. The current published defaults: OpenAI API, 30 days for abuse monitoring; Azure OpenAI, 30 days stored in Microsoft’s environment with human review limited to already flagged content, removable only by approval for modified abuse monitoring, which requires an enterprise agreement; Google’s paid Gemini Developer API, 55 days by default, configurable down to 7, 14, or 28, while Vertex AI runs 30 days. The number depends on which surface you are actually buying.
- **Flagged conversations.** If an automated classifier decides a chat breaks the usage policy, the retention clock changes. Under Anthropic’s published terms, inputs and outputs flagged as violations can be kept for up to two years, and the trust and safety classification scores attached to them for up to seven. Classifiers make mistakes: a security team probing its own defences, or a researcher asking about chemistry, could trip one. Retention policies generally do not promise to tell you when it happens.
- **Data about your data.** Even when the conversation itself is deleted, records about it can survive: classifier scores, account and user identifiers, timestamps, usage volumes, which tools or connectors were called. That is enough to build a detailed picture of how your company works. It is also exactly the kind of record a National Security Letter can demand.
- **Feedback buttons.** A [thumbs up or down](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data) sends the whole conversation with it. Anthropic keeps data submitted through feedback or bug reports for five years.
- **Files, memory, and agents.** ZDR typically covers the model call, not the features wrapped around it. Uploaded files, vector stores, memory, saved chats, connectors, and agent sessions are stored until you delete them. Anthropic’s own policy, for example, excludes services “with longer retention under your control,” such as its Files API.
- **Personal accounts.** If staff use AI on personal plans, your company’s data falls under consumer terms. Under consumer terms updated in late 2025, Anthropic users who allow their chats to be used for training have them retained for up to five years.

Deletion promises almost always end with exceptions for safety investigations and legal obligations, the “almost all cases” clause. Those exceptions are where your data stays longest.

## The terms themselves are the risk

Anthropic has changed its policy: its newest models ship without Fable’s retention requirement, and EFS is on its way. But all of these changes prove that a vendor can change the terms on its own and go back on every agreement it has already made.

The AI vendor you use decides the terms for how your data is handled, and it can rewrite them whenever it chooses.

That’s why some companies have decided to keep sensitive AI work in house instead. Fortune’s report says that after the Fable announcement, security software firm Cinder saw a spike in ordinary companies asking how to run open models themselves.

Taking on that complex infrastructure is still rare, though. [Menlo Ventures](https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/) estimated that open source models made up 11% of enterprise LLM use in late 2025, down from 19% the year before. And that was before this summer’s backlash.

Businesses know that when they run a model themselves, security becomes their responsibility. Not many companies can take on that burden.

## Five questions to ask your AI vendor

Start with an inventory: list every AI tool in use, and note which tier and which account, company or personal, each person is on. Then ask each vendor:

1. **What exactly is retained on our tier, and for which models and features?** Ask whether ZDR covers new models as well as current ones, and whether it covers uploaded files, memory, connectors, agents, and feedback, not just the basic API call.
2. **What does abuse monitoring keep, for how long, and does a flag extend it?** Ask who reviews flagged content, whether a human can read it, and whether you will be told when one of your conversations is flagged.
3. **What survives when the conversation is deleted?** Ask about classifier scores, metadata, logs held by partners and contractors, and backups.
4. **Who can access retained data, and which governments can demand it?** Ask whether employees and contractors can read it. Ask whether the vendor or any of its cloud providers is subject to the CLOUD Act, regardless of where your data is stored. Ask whether you will be notified of a subpoena or legal hold, and whether the vendor publishes how many government requests it receives, including National Security Letters. The New York Times order kept deleted chats on paid Team plans for months.
5. **Can you change these terms, and with how much notice?** Ask whether your ZDR agreement binds future models. In June, Anthropic’s new retention rule overrode existing agreements on its newest models from the day they launched.
6. **What do you do about customers who chose your product precisely because you keep no records?** Adversaries gravitate toward zero retention for the same reason enterprises do. Anthropic’s September threat intelligence report describes a platform that tunneled traffic through US infrastructure to evade regional blocks and used a ZDR service to route restricted research requests. Any credible vendor, including one with nothing to log, needs an answer to how misuse gets caught when there is no archive to inspect. If they can’t articulate one, that’s notable.

## Choose a private AI

We built Lumo for businesses that want to work in private, and to have good answers to those questions. Lumo doesn’t keep logs of your conversations, and that’s the default for every user, not a feature reserved for top-tier contracts.

Chats you choose to save are protected with zero-access encryption, so only you can decrypt them on your device, and Proton can’t read them, hand them over, or study them.

Lumo doesn’t train on your conversations, and it runs on open-source models in Proton’s European data centres, under Swiss and EU law rather than US legal process. And because Proton is funded by subscriptions, not by building frontier models, we have no reason to learn from your data.

[Learn more about Lumo](https://proton.me/blog/lumo-ai)
