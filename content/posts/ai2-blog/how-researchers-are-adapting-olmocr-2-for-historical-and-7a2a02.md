---
title: How researchers are adapting olmOCR 2 for historical and archaeological archives
subtitle: ''
source: Ai2 Blog
source_url: https://allenai.org/blog/olmocr-2-historical-archives
author: ''
date: '2026-10-28T08:00:00Z'
fetched: '2026-10-28T16:48:46Z'
image: https://www.datocms-assets.com/64837/1793156211-olmocr-featured.png
summary: October 28, 2026 Ai2 olmOCR 2 is Ai2’s open model for extracting searchable, structured text from document images, including handwriting and complex layouts. Its weights, fine-tuning data, and code let researchers run it locally and adapt it to their research needs.
tags: []
guid: https://allenai.org/blog/olmocr-2-historical-archives
---

October 28, 2026

Ai2

olmOCR 2 is Ai2’s open model for extracting searchable, structured text from document images, including handwriting and complex layouts. Its [weights, fine-tuning data, and code](https://allenai.org/blog/olmocr-2) let researchers run it locally and adapt it to their research needs.

Researchers have used olmOCR 2 to make archival photo libraries searchable and improve transcription of handwritten archaeological records. ArtificeOCR uses olmOCR 2 on historian Maurice Casey’s own computer to transcribe his photographs of letters, newspapers, and other sources on radical politics in early twentieth-century Europe. CENTURIA adapts olmOCR 2 to transcribe handwritten notes accompanying archaeological pottery drawings from Carnuntum, a Roman site in present-day Austria.

#### Searching archives on local hardware

Maurice Casey, a historian of radical politics in early twentieth-century Europe, works with sources in English, Russian, and German. Over years of research, he accumulated thousands of photographs of letters, newspapers, and other records, taken on different smartphones under varying conditions. He wanted to search the collection by keyword without uploading material entrusted to him by archives and families to a third-party service.

Casey built [ArtificeOCR](https://github.com/MauriceJCasey/artifice-ocr), a tool that connects locally running vision-language models such as olmOCR 2 with Tropy, the open-source application he uses to organize archival photographs. Through ArtificeOCR, Casey made his existing Tropy library searchable while preserving the metadata he had entered since 2019.

Casey finds olmOCR 2 especially useful for varied page layouts, including the standardized forms he encounters in secret police archives. He says the model handles these layouts without requiring him to prepare each document format differently. He also reports strong results with cursive English and typescript across his research languages.

In Casey’s experience, a language model can produce plausible, fluent text where conventional OCR would return obvious garbling. He also reports errors when the model transcribes handwriting in languages less represented in its training data. In ArtificeOCR, researchers can compare a scan with its transcription, correct any mistakes, and inspect changes made during later processing.

“Fidelity to the source material, including capturing how people in the past made errors or wrote in coded or euphemistic language, is hugely important for my work as a historian,” he says.

ArtificeOCR is still in early development. Casey wants interfaces that make local models easier for historians to use, and he sees potential in fine-tuning them for particular kinds of sources.

#### Adapting olmOCR 2 to archaeological handwriting

Researchers at TU Wien’s Computer Vision Lab and the Austrian Archaeological Institute at the Austrian Academy of Sciences studied handwritten pottery records from Carnuntum, a Roman site in present-day Austria. In the course of the research project [LEGION](https://legion-hsa-2-0.github.io), they tested whether fine-tuning olmOCR 2 on a small set of annotated examples could improve its transcription.

Their archive contains roughly 70,000 pottery records. Handwritten notes identify vessel forms, excavation contexts, and other details archaeologists need to compare finds. Annotations appear around technical drawings, sometimes overlap them, and use abbreviated German terminology. Differences in handwriting and recording conventions across decades make the annotations harder to transcribe accurately.

The team created [CENTURIA](https://github.com/gissuvalentina/CENTURIA), a benchmark of 507 annotated records, to evaluate transcription and extraction of structured information. Of the five open models tested, olmOCR 2 had the lowest transcription error before adaptation. Access to its weights meant they could also train it on examples from the collection.

“We wanted the resulting pipeline to be reproducible and realistically deployable by heritage institutions, which often do not have the resources to process tens of thousands of documents through commercial APIs,” CENTURIA co-author Dominik Hagmann and his colleagues write.

Using LoRA, a method that trains a small set of additional parameters, the researchers fine-tuned olmOCR 2 on 57 records. On the remaining 450 test records, transcription error fell from 15.58% to 1.11%.

The team’s next goal is to apply the approach beyond its 507-record benchmark to the roughly 70,000 pottery records in their Carnuntum archive. Making the full collection searchable could help archaeologists compare pottery forms across the site and between historical periods.

“Those questions are impractical when your data lives in paper annotations. Once you have structured, searchable records for the full collection, they become tractable,” Hagmann and his colleagues write.

Archives have different recording conventions and conditions of access. With olmOCR 2’s weights and code available, researchers can choose where to run it and adapt it to their documents. ArtificeOCR and CENTURIA offer practical examples of how to do that while building expert review into the process.

“The ability to run the model locally was the most important part of this for me,” Casey says. “There’s so much material I simply would not feel comfortable sending to a third party.”

### Join us

At Ai2 we’re building the future of transparent, open-source AI — built in the open to empower scientific progress and fundamental understanding of this world changing technology. We’re not here to make profits, we’re here to make sure benefits of AI are shared widely and for the benefit of humanity. If this appeals to you, please take a look at our open roles.
