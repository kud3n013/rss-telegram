---
title: A crop-mapping benchmark for the tropics
subtitle: ''
source: Ai2 Blog
source_url: https://allenai.org/blog/planteur
author: ''
date: '2026-10-22T08:00:00Z'
fetched: '2026-10-22T18:51:48Z'
image: https://www.datocms-assets.com/64837/1792681400-planteur-tropical-regions-tan.png
summary: Foundation models and open data are driving rapid progress in machine learning for remote sensing, and benchmarks play a key role in understanding model improvement. PASTIS is one of the community's most trusted benchmarks, thanks to its high-quality labels and geospatial metadata. It also represents an important problem.
tags: []
guid: https://allenai.org/blog/planteur
---

Foundation models and open data are driving rapid progress in machine learning for remote sensing, and benchmarks play a key role in understanding model improvement. PASTIS is one of the community's most trusted benchmarks, thanks to its high-quality labels and geospatial metadata. It also represents an important problem. Crop-type mapping is the starting point for food security planning, water allocation, and tracking how farmland changes. However, its coverage is limited to metropolitan France. We present [PLANTEUR](https://allenai.org/papers/planteur), an extension of PASTIS to six tropical regions, in hopes that teams building geospatial foundation models can check whether their model performs in agricultural systems where mapping could be most valuable: smallholder, tropical, topographically complex.

### What’s in PLANTEUR

PLANTEUR was built from the same reliable data source as PASTIS, France’s Land Parcel Identification System, and spans Réunion, Guadeloupe, Martinique, Guyane, Mayotte, and Saint-Martin. To make PLANTEUR easy to adopt into existing evaluation pipelines, its format closely resembles that of PASTIS: 2,750 aligned Sentinel-2, Sentinel-1, and Landsat-8 time series, and 4,506 km² of parcel-derived labels across seven crop classes, including sugarcane, banana, pineapple, and tropical tubers (root crops such as cassava, yam, and taro).

We include baseline numbers for several linear probes and supervised methods on a standard split, a leave-one-island-out split, a few-shot setup, and even one that includes PASTIS samples in the training data. These baselines introduce new challenges, in new places, like performing well in the tropics, generalizing to unseen regions, learning from scarce labels, and transferring knowledge across agricultural systems.

### What it opens up, and how far there is to go

We built PLANTEUR to increase the geographic diversity of remote sensing benchmarks. By building on the success of the PASTIS dataset, we hope to provide builders of remote sensing models a way to evaluate how good their models are at crop type mapping in many different geographies.

Every method we evaluated, ours included, scores substantially lower on PLANTEUR than on PASTIS, and every model loses roughly half its accuracy when tested on an island it never saw in training. Just as PASTIS motivated the community to develop strong methods for crop mapping in metropolitan France, we hope PLANTEUR motivates the community to develop methods which perform well in tropical contexts as well.

PLANTEUR is available on [Hugging Face](https://huggingface.co/datasets/allenai/planteur-benchmark) and [GitHub](https://github.com/allenai/planteur-benchmark).
