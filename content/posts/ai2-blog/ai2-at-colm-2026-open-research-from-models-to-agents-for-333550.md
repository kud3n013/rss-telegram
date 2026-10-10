---
title: 'Ai2 at COLM 2026: Open research, from models to agents for science'
subtitle: ''
source: Ai2 Blog
source_url: https://allenai.org/blog/colm-2026-recap
author: ''
date: '2026-10-09T08:00:00Z'
fetched: '2026-10-10T18:24:09Z'
image: https://www.datocms-assets.com/64837/1791590717-colm-2026-recap-blog-google-docs-image-1.jpg
summary: 'October 9, 2026 Ai2 This week Ai2 was at COLM 2026 in San Francisco. The work we shared reflects our wider mission: building AI research artifacts anyone can study and extend, and developing AI for science tools in collaboration with domain experts. Our evening gathering gave colleagues from across the COLM and wider open-source community another setting to connect.'
tags: []
guid: https://allenai.org/blog/colm-2026-recap
---

October 9, 2026

Ai2

This week Ai2 was at COLM 2026 in San Francisco. The work we shared reflects our wider mission: building AI research artifacts anyone can study and extend, and developing AI for science tools in collaboration with domain experts.

Our evening gathering gave colleagues from across the COLM and wider open-source community another setting to connect.

Those exchanges are central to how we approach research. As a fully nonprofit lab, we pursue fundamental scientific questions while sharing the models, data, code, and methods that let others investigate them too. COLM brings us together with the people who use our resources we release, challenge our assumptions, and contribute their own ideas.

Sharing the work in open collaboration with others isn’t an afterthought for us—it’s a fundamental part of how we approach research.

#### **From Olmo Hybrid to the next Olmo**

Our paper [“Olmo Hybrid: From Theory to Practice and Back”](https://arxiv.org/abs/2604.03444), presented at the conference, examines what happens when a language model combines transformer attention with linear recurrent layers. Attention can retrieve specific details from earlier text; recurrent layers maintain a compact state that updates as the model processes a sequence of text tokens.

The research connects theory about what these architectures can represent with controlled training experiments. Olmo Hybrid provides evidence that combining attention and recurrence can improve training efficiency: in the study, it reached the same accuracy as Olmo 3 7B on MMLU, a benchmark covering knowledge across many subjects, using [49% fewer training tokens](https://allenai.org/blog/olmohybrid).

That research is helping inform the next Olmo model, now in pre-training with a hybrid mixture-of-experts architecture. The hybrid design combines attention and recurrence. Mixture-of-experts offers another way to improve efficiency, routing each token through a subset of the model’s components.

We are also opening up the infrastructure behind this direction. Released ahead of COLM, [Olmo-core 3](https://allenai.org/blog/olmocore3) adds a redesigned system for training large mixture-of-experts models. Researchers can use the code to develop their own models and investigate training decisions, alongside the checkpoints and technical reports available through the broader Olmo ecosystem. And Google [recently announced](https://developers.googleblog.com/reproducing-olmo-3-7b-pre-training-in-maxtext-case-study-of-large-scale-training-on-tpus/) that they recreated our Olmo 3 7B training run in MaxText on Google Cloud TPUs, highlighting the reproducibility that our fully open approach enables.\
In our conversation from the conference, Noah A. Smith, Ai2’s senior director of NLP research, joined our comms lead Kyle Wiggers to discuss the next iteration of Olmo and our work on agentic models:

![](https://allenai.org/_next/image?url=https%3A%2F%2Fi.ytimg.com%2Fvi%2FlWQWw8lWxCo%2Fmaxresdefault.jpg&w=3840&q=75)

#### **Developing AI for science with scientists**

Scientific tools need to fit the tasks scientists actually do. That means creating them with researchers and studying both their capabilities and their limits—which we are doing in our development of Asta, our agentic platform for scientific work.\
The recently released [AstaBrief](https://allenai.org/blog/astabrief) is an open-weights model that generates cited reports from research questions and retrieved literature. Scientists can use it in Asta’s Fast mode or download the model to run on their own infrastructure.

We are also working directly with scientific communities to understand where general-purpose models fall short and what future open models should support.\
Ai2 senior research scientist Bodhisattwa Prasad Majumder was at COLM to further these conversations, presenting a number of relevant papers:

![](https://allenai.org/_next/image?url=https%3A%2F%2Fi.ytimg.com%2Fvi%2FS6FNxk5Jh08%2Fmaxresdefault.jpg&w=3840&q=75)

#### **Bolmo in Nature**

During the conference, our paper [“Retrofitting language models to operate over bytes”](https://www.nature.com/articles/s41586-026-11111-4), the research behind Bolmo, was [published in Nature](https://allenai.org/blog/bolmo-nature). Most language models first divide text into chunks from a fixed vocabulary. Bolmo works with the underlying bytes that represent characters, allowing it to handle details that subword tokenization can obscure. Our paper describes how to convert an existing language model to this approach with a relatively short additional training run.

Alongside the publication, we [released additional checkpoints](https://allenai.org/blog/bolmo-nature) so researchers can experiment with the architecture themselves. Publishing the findings and opening the materials behind them gives others a way to test the approach and take it further.

Thank you to everyone who connected with us at COLM, joined our evening event, and shared their work with us. The papers and tools above offer ways to continue the discussion—read the research, try the models, and tell us what you find.

If you would like to help build this work, [explore our open roles](https://allenai.org/careers).

### Join us

At Ai2 we’re building the future of transparent, open-source AI — built in the open to empower scientific progress and fundamental understanding of this world changing technology. We’re not here to make profits, we’re here to make sure benefits of AI are shared widely and for the benefit of humanity. If this appeals to you, please take a look at our open roles.
