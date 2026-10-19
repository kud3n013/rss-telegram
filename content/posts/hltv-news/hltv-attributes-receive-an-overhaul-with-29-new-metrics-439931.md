---
title: HLTV Attributes receive an overhaul with 29 new metrics
subtitle: Clutching has been renamed Closing while six new stats tables have been added to the website.
source: HLTV News
source_url: https://www.hltv.org/news/45755/hltv-attributes-receive-an-overhaul-with-29-new-metrics
author: NER
date: '2026-10-19T12:19:00Z'
fetched: '2026-10-19T14:01:53Z'
image: https://img-cdn.hltv.org/gallerypicture/paL5MAGucn7Np6AQK4hVYD.jpg?auto=compress&ixlib=java-2.1.0&q=75&w=800&s=9999de3b78892458cc52d118018bd27c
summary: Today we are shipping an update to Attributes to both streamline them and bring them in line with rating 3.0. Since we launched them in 2024, attributes have served as a signal as to what type of player someone is. While rating covers performance, attributes cover style.
tags: []
guid: hltvnews45755
---

Today we are shipping an update to Attributes to both streamline them and bring them in line with rating 3.0.

Since we launched them in 2024, attributes have served as a signal as to what type of player someone is. While rating covers performance, attributes cover style.

With the launch of 29 new metrics today, we get closer to that goal of encapsulating what type of player someone is.

To make that even easier for users to understand, we are no longer showing as many metrics underneath each attribute after you click. Instead, we usually show just four — the ones that contribute to the overall attribute score. 19 of the new metrics are available right here. The whole element now fits in one screenshot on most devices, so you can get a full grasp of a player without needing to scroll.

These are all deliberately stylistic metrics, and we have done our best to remove outcome from the stats. For example, we are now using 'tradeable deaths' instead of 'traded deaths' in Entrying. It should not matter whether a teammate secured the trade or not, as our chosen player made the same action. The same goes in Opening, where opening kills (a half-and-half performance stat) is gone and we just use opening attempts (a clear style one).

Moreover, Clutching has been renamed to Closing, with new metrics aimed at showing which players are most often in late-round situations. Since clutches were so rare, the old attribute didn't always do this; it mostly showed who the strongest clutch players were. Now, with stats like how often a player is alive for a post-plant, or their team's last survivor, Closing can look at far more situations before deciding whether a player is more passive or aggressive.

Another big change is how the attributes are calculated. Before, we used overall averages for every player. Now we are using averages based on a player's role. You can see in the top right, a little indicator that reads 'Compared to: Riflers' automatically for them and 'AWPers' for players with more than 0.20 AWP kills per round in the selected sample.

Sniping is the exception to this and stays the same as before, with its own special treatment given the averages are skewed by the average player rarely picking the AWP up at all.

You can still revert to comparing to all players for this — especially useful for comparing the firepower of an AWPer and a rifler — but by comparing apples with apples we go much closer to our goal of finding out the true style of a player.

For example, AWPers are alive for 63.3% of post-plants, while the average rifler scores 54.6%. This means a rifler with 56.2% is actually quite passive, but does not score as highly in Closing when AWPers are included in the averages. AWPing and rifling averages also vary wildly in metrics like Last Alive, Net Kills, Weapon Attacks, Tradeable Deaths and First Duel Rank.

This is also important by side: CT AWPers' Opening is level with riflers (50 vs 50), but on T AWPers' average Opening drops to 29 and their Closing is 70.

Even in the attributes that weren't renamed, nearly all of them have received new metrics and weighting. These changes beg the question: where can you find the statistics that used to be in attributes, but have now been removed?

With this update, we are launching six new stats tables, one for each attribute. We believe this separation will make attributes give you more of a signal about a player, while still allowing deep dives for users who are interested. If you're unclear on what a new metric is, hover over it and a tooltip will appear with its full name and explanation.

This is where metrics that show how 'good' a player is at Trading can be found, via stats like trade kill success, as opposed to how often a player is in a good trading position. If you can't find something from the old page, chances are it's on the new stats tables, with the exception of a few lesser-used metrics for space reasons.

For example, on the 'Closing' page, you can see a player's 1on1 clutch win rate, and the all-new Clutch Swing (a player's round swing when they are last alive). These pages are where the other 10 new metrics can be found.

It also means you can sort by attribute score to see who has the highest score over a certain period. Just please bear in mind that these are stylistic stats, even more so than before; a high opening score doesn't mean that they are good in opening duels, just that they are more aggressive than the average player.

Here's the new Trading page [at Big Events in 2026 against top 20 teams](https://www.hltv.org/stats/players/trading?startDate=2026-01-01&endDate=2026-12-31&matchType=BigEvents&rankingFilter=Top20), sorted by Trade Kill Success percentage. [Mathieu "ZywOo" Herbaut](https://www.hltv.org/player/11893/zywoo) and [Maksim "kyousuke" Lukin](https://www.hltv.org/player/24177/kyousuke) top the board, at 66.5% and 65.8%, respectively.

These pages also have role filters on them, so you can isolate stats for just AWPers, riflers or in-game leaders. The plan long-term is to also have these filters working for our award show roles, like opener, anchor and closer, so stay tuned.

This means when you open the new Sniping page, you can check out players' AWP Swing and remove any hybrid riflers on low sample sizes. With eco adjustment and aggregated stats, it is hard to tell if an AWPer is getting a high rating based on their rifle play or their sniper play. Now, we can check their AWP Swing against their overall one to get more of a picture.

[At Big Events in 2026 against top 20 teams](https://www.hltv.org/stats/players/sniping?startDate=2026-01-01&endDate=2026-10-19&matchType=BigEvents&rankingFilter=Top20&role=sniper&minMapCount=15), [ZywOo](https://www.hltv.org/player/11893/zywoo) leads this leaderboard too with +5.02%, with [Ilya "m0NESY" Osipov](https://www.hltv.org/player/19230/m0nesy) second on +4.52%.

Back on player profiles, you can use these new and improved attributes to find 'similar players' of your favorite pro, a doppelganger of sorts. This is based on their scores over the six style attributes (excluding firepower) on both T and CT sides, and we display the players with the ten highest similarity scores from top 30 teams.

The similar players are always based on those players' stats in the last six months, so bear that in mind. If you want the radars to look the most similar, select a six month filter on the player you have selected.

For example, top prospect [David "Dawy" Bibik](https://www.hltv.org/player/24282/dawy) scores [most similarly](https://www.hltv.org/stats/players/24282/dawy?startDate=2026-04-19&endDate=2026-10-19) to [kyousuke](https://www.hltv.org/player/24177/kyousuke) (95% similarity score) and [Jonathan "EliGE" Jablonowski](https://www.hltv.org/player/8738/elige) (91%). Second place [Daniel "syph0" Ageyev](https://www.hltv.org/player/23319/syph0) is a more supportive player, and tracks closest to [René "TeSeS" Madsen](https://www.hltv.org/player/12018/teses) (94%) and [Ivan "zweih" Gogin](https://www.hltv.org/player/23685/zweih) (92%).

With that, it's over to you. Have a play around, click on a player or two, and we hope you learn something new about players you thought you were already familiar with, and those you haven't even heard of yet.

## Patch Notes

- Attributes simplified and streamlined, to focus on style of a player by separating intent from outcome of an action
- Six new stats tables released, one for each style attribute plus separate pages for grenades and flashbangs
- Role filter (IGL, AWP, Rifler) added to attributes, and all player stats tables
- Default attributes are now calculated compared to role average. Select versus everyone to revert to old behavior.
- Similar players radar added to each player page

## The 29 new metrics

Round Win Shares\
Perfect KPR\
Trade Denials\
Net Kills\
Net Damage\
Tradeable Deaths\
Trade Opportunities\
Bait Kills %\
First Duel Rank\
First Duel Time\
Weapon Attacks\
Alive for Post Plant\
Last Alive in Team\
Rounds with a Sniper\
Rounds with an AWP

AWP Kills %\
Smokes thrown\
Molotovs Thrown\
HE Grenades Thrown\
Traded Death Success%\
Trade Kill Success%\
Opening Swing\
Clutch Swing\
AWP Duel Win %\
AWP Swing\
Flash Swing\
Assists per Flash\
Grenade Damage Received\
Damage per HE thrown
