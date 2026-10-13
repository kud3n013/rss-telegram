---
title: How Molmo 2’s open release helped an MIT researcher rethink fish tracking
subtitle: ''
source: Ai2 Blog
source_url: https://allenai.org/blog/molmo2fish
author: ''
date: '2026-10-13T08:00:00Z'
fetched: '2026-10-13T22:57:42Z'
image: https://www.datocms-assets.com/64837/1791919335-adobestock-554340853-1550x810-2026-10-13t18-36-01.png
summary: October 13, 2026 Ai2 When we released Molmo 2, our open vision-language model for images and video, we made the model, code, and training data openly available so researchers could inspect how it was built and customize it for their own work.
tags: []
guid: https://allenai.org/blog/molmo2fish
---

October 13, 2026

Ai2

When we released [Molmo 2](https://allenai.org/molmo), our open vision-language model for images and video, we made the model, code, and training data openly available so researchers could inspect how it was built and customize it for their own work. Molmo 2 can follow a particular figure or object as it moves through a video, identify something described in language – such as “the second car to cross the finish line” – and reason about events over time. Making the model and the resources behind it open gives researchers a starting point for applying those capabilities to new problems.

Kai Van Brunt, an MIT ’25 graduate, focuses on computer vision for ecology. He worked on this project as a visiting student in MIT’s BeeryLab with Sara Beery, the Homer A. Burnell Career Development Professor and an assistant professor of electrical engineering and computer science at MIT.

Van Brunt’s research focuses on better ways to count salmon from underwater sonar video. Those counts help researchers understand how salmon populations are changing and inform conservation and fisheries management. Following individual fish through the footage is key to getting those counts right, but doing it by hand is time-consuming.

Computer vision can reduce the amount of video researchers have to review by hand. But tracking systems still make mistakes. They can lose sight of a fish, “forget” which is which, or switch from following one fish to another. Correcting those errors can require manually fixing predictions across many frames of recordings.

Van Brunt wondered whether a researcher could instead describe how a fish-tracking prediction was wrong and ask the model to automatically correct it.

That idea became [Molmo2Fish](https://arxiv.org/abs/2608.18602), a version of Molmo 2 adapted to follow salmon in sonar footage and revise its predictions based on everyday language.

“I needed to build on top of an open model that already understood language, spatiotemporal relations, and tracking in video, and one that was small enough that I could try fine-tuning it,” Van Brunt says. “Molmo 2 was by far the most suitable model I found.”

#### Building on what Molmo 2 already knew

Sonar footage looks very different from the videos Molmo 2 originally learned from. But Molmo 2 already knew how to follow a particular target through video and use language (e.g., “the dog that bites the jeans”) to identify which one to follow over time.

Van Brunt had noticed that watching fish move made them easier to distinguish than viewing a single frame. He tried several video object detection models, but none improved on the still-image baseline. Molmo 2 could process a whole clip and output tracks directly, making it possible to train on the tracking task without a separate detection step.

“Molmo 2 was the first model we used which made it straightforward to consider multi-object tracking as a task that a model could learn directly,” Van Brunt says.

Van Brunt could tailor Molmo 2 for sonar footage rather than develop a new system from scratch. After fine-tuning it on salmon videos, Molmo2Fish performed roughly as well as a specialized fish-tracking system before receiving any corrections, with results varying across rivers.

He then trained Molmo2Fish to respond when a user pointed out an error. The model saw examples of an initial prediction, an instruction describing how it should change, and the corrected result.

A researcher could tell Molmo2Fish that it had missed a fish or treated two separate fish as the same one, then ask the model to automatically correct the prediction.

This worked especially well when Molmo2Fish was given predictions from a conventional fish-tracking system. Molmo2Fish and the conventional system tended to make different kinds of mistakes, so Molmo2Fish could correct some errors the other system produced.

The experiments also showed the limits of language-guided correction. Molmo2Fish could correct some tracking errors when given clear instructions, but it had a harder time improving its own strongest predictions. Molmo2Fish is a first step toward a model reliable enough for real-world use, Van Brunt says. It remains a research project and has not been deployed.

#### What the open release enabled

Molmo 2’s open release gave Van Brunt access to the model, code, and training data behind the capabilities he wanted to build on. He didn’t ultimately use Molmo 2’s original training data to build Molmo2Fish, but being able to inspect it helped him understand what the model had already learned and decide how to prepare his own data. Access to the code also made it easier to tailor Molmo 2 for a very different kind of video modality.

Van Brunt now wants to explore how models that work with both video and language, like Molmo 2, could help scientists find and describe patterns as their research questions evolve. Open releases make room for that kind of experimentation: researchers can take existing capabilities into new fields, test what works, and build from there.

“Broadly, I want to continue exploring learning on video data, and I want to use AI to understand and protect the natural world,” Van Brunt says.

### Join us

At Ai2 we’re building the future of transparent, open-source AI — built in the open to empower scientific progress and fundamental understanding of this world changing technology. We’re not here to make profits, we’re here to make sure benefits of AI are shared widely and for the benefit of humanity. If this appeals to you, please take a look at our open roles.
