---
title: "Patch 1.05 Fixes Voice Chat and Highlights a Crucial Sanity Mechanic"
slug: "patch-105-voice-chat-sanity-mechanics"
description: "Patch 1.05 for The Mound: Omen of Cthulhu overhauls crossplay communication and fixes TSR/XeSS bugs. Learn why using Discord ruins the game's horror."
keywords: "the mound omen of cthulhu patch 1.05, voice chat fix, sanity mechanics, tsr xess fix, crossplay communication, the mound orb bug, achievement tracking, proximity chat horror"
image: "auto_patch-105-voice-chat-sanity-mechanics.webp"
quick_facts:
  - "Update Version | Patch 1.05"
  - "Key Feature | Complete voice chat overhaul"
  - "Crucial Fix | TSR and XeSS profile settings saving properly"
  - "Developer Advice | Use in-game chat for sanity effects"
faq:
  - q: "Why is my voice chat robotic in crossplay?"
    a: "Prior to Patch 1.05, a bug caused voice corruption between PC and console players. Updating to the latest version resolves this issue entirely."
  - q: "Should I use Discord for The Mound: Omen of Cthulhu?"
    a: "The developers strongly advise against it. The game ties its <a href=\"sanity-system-explained.html\">sanity mechanics</a> directly to the in-game spatial audio, meaning third-party apps will completely bypass the intended horror experience."
  - q: "Why do I have to reset my graphics every time I launch?"
    a: "Patch 1.05 addresses a specific bug where TSR and XeSS upscaling profiles failed to save. You should now be able to set your preferences once without them reverting upon restart."
---

The development team at ACE Team has officially rolled out Patch 1.05 for *The Mound: Omen of Cthulhu*. While the studio humbly describes this update as a "relatively small patch," its contents actually address some of the most frustrating friction points players have encountered since launch. Released on September 9, 2026, across Steam, PlayStation 5, and Xbox Series X|S, this hotfix primarily targets severe audio corruption, graphics profile bugs, and a specific progression blocker. 

However, hidden within the routine patch notes is a vital piece of advice from the developers that fundamentally changes how you should approach playing this game with your friends. If you have been relying on third-party communication software to organize your expeditions, you are actively sabotaging your own experience.

Here is a detailed breakdown of everything included in Patch 1.05 and why you need to rethink your communication strategy before your next descent.

## The Crossplay Communication Crisis Resolved

Cooperative survival in a Lovecraftian setting requires flawless communication. You need to be able to call out resource locations, coordinate stealth approaches against cosmic horrors, and panic collectively when a plan falls apart. Unfortunately, a persistent bug has been plaguing squads, particularly those utilizing the game's [co-op and crossplay functionality](co-op-crossplay-solo-explained.html). 

Players across various platforms reported that the in-game voice chat would spontaneously corrupt. Teammates would suddenly sound like dial-up modems, robotic androids, or their audio would drop out entirely. This issue was especially prevalent when mixing PC players with those on PS5 or Xbox Series X|S, leading to fractured teamwork and unnecessary squad wipes. 

Patch 1.05 brings a complete overhaul to the voice chat backend. ACE Team has thoroughly tested this reworked system to ensure stability across all supported platforms. Following the update, the robotic distortion and sudden dropouts should be entirely eradicated, allowing for crystal-clear callouts regardless of what hardware your teammates are running. 

## The Crucial Link Between Voice Chat and Sanity Mechanics

Fixing the voice chat was a priority not just for basic functionality, but because it is intertwined with the core design of *The Mound: Omen of Cthulhu*. In the patch notes, ACE Team included a direct plea to the player base: *"Since The Mound: Omen of Cthulhu uses spatial audio, and some sanity effects use voice, we recommend playing using the in-game voice chat."*

This is the most important takeaway from the 1.05 update. 

Modern co-op horror relies heavily on audio design to build tension, a trend heavily popularized by other titles in the genre. If you are interested in how this game stacks up against its peers in that regard, you can check out our comparison of [how it handles horror versus Lethal Company and GTFO](vs-gtfo-lethal-company-darktide.html). But *The Mound* takes the concept of proximity chat several steps further by wiring it directly into the [sanity system](sanity-system-explained.html).

When you use a third-party application like Discord, Party Chat, or TeamSpeak, you receive a clean, unfiltered, and omnidirectional audio feed from your friends. You hear them perfectly whether they are standing right next to you or are lost three levels deep in a subterranean ruin. 

By bypassing the in-game audio, you are effectively cheating yourself out of the game's most terrifying mechanics. The game utilizes advanced spatial audio. When a teammate speaks in-game, their voice originates from their character model. If they walk down a long stone hallway, their voice will echo realistically. If a heavy monolithic door slams shut between you, their screams will be muffled by the thick stone. This creates an unparalleled sense of isolation when you get separated.

More importantly, your character's mental state directly manipulates the VoIP feed. As your sanity drains from witnessing eldritch horrors or spending too much time in the dark, the game begins to mess with your perception of reality, and this includes what you hear from your friends. 

If your sanity is critically low, you might hear a teammate calling for help from the darkness, only to find out they never spoke at all—the game synthesized their voice to lure you away. Conversely, a teammate whose mind is fracturing might sound distorted, pitching down into demonic registers or echoing unnaturally, signaling to the rest of the group that they are losing their grip on reality. 

If you are sitting in a private Discord call, none of this happens. You will miss the auditory hallucinations, the terrifying silence of being truly separated, and the mechanical cues that someone in your squad is going mad. To truly experience the psychological horror the developers intended, you must mute your third-party apps and rely entirely on the in-game voice chat. 

## Technical Polish: Securing Your Upscaling Profiles

Beyond the audio overhaul, Patch 1.05 also brings some much-needed relief for PC players regarding graphics settings. Specifically, the update addresses a bug that prevented profile settings related to TSR (Temporal Super Resolution) and XeSS (Xe Super Sampling) from saving correctly.

To maintain playable frame rates while exploring visually dense, fog-heavy environments, many players rely on these upscaling technologies. They allow the game to render at a lower base resolution before being smartly upscaled to your monitor's native resolution, drastically improving performance without heavily sacrificing visual quality. If you are struggling to maintain a smooth framerate, verifying your setup against the [expected system requirements](system-requirements-expected.html) and utilizing these upscalers is highly recommended.

Prior to this hotfix, the game was failing to remember these specific upscaling choices between sessions. Players were forced to navigate through the options menu every single time they launched the application to re-enable TSR or XeSS and adjust their sharpness preferences. This was a tedious process that disrupted the flow of getting into a match. 

With 1.05 installed, your profile settings will now accurately save and apply upon startup. Once you find the perfect balance between performance and visual fidelity for your specific hardware, the game will properly respect those choices indefinitely. 

## Squashing Progression Blockers and Achievement Bugs

The patch also tackles a specific gameplay hurdle that was halting progress for numerous expedition teams. In the titular "Mound" level, there is a sequence involving a specific, hostile orb entity. Due to a scripting error, this orb was frequently failing to register incoming damage properly. 

Teams would pour ammunition and resources into the entity, only to find its health pool completely static, effectively soft-locking the mission and forcing players to abandon the run. The developers have successfully identified the root cause of this invulnerability bug. The orb now correctly registers hitboxes and damage values, allowing squads to reliably clear the encounter and progress deeper into the subterranean network.

Additionally, while not explicitly detailed in the brief Steam announcement, community reports from the game's official subreddit confirm that the patch includes fixes for achievement tracking. Several achievements that require cumulative actions—such as dispatching a specific number of enemies or surviving multiple extractions—were previously stalling out. Completionists and trophy hunters can now resume their grind with confidence, knowing their milestones are being accurately recorded by the backend servers.

## Looking Ahead: Jungle Terrors and The Next Big Patch

Perhaps the most exciting part of the Patch 1.05 notes is what ACE Team teased for the future. The announcement opens with a pointed question: *"Have the new creatures lurking within the jungle been causing you trouble?"* 

The developers then explicitly state that they are currently working on their "next big patch." This brief mention serves as both a taunt and a roadmap. The jungle biomes in the game are already incredibly hostile environments, known for poor visibility and aggressive fauna. The fact that the developers are specifically highlighting new creatures causing trouble suggests they are closely monitoring telemetry data and player death heatmaps. 

This aligns with what we know about the game's post-launch plans and the [creatures confirmed to be prowling the depths](creatures-confirmed-preview.html). It is highly likely that the upcoming major content update will expand upon the surface-level jungle ruins, potentially introducing new Lovecraftian variations of flora and fauna, or perhaps an entirely new apex predator that forces players to rethink their loadouts before diving underground. 

For now, the focus should be on downloading Patch 1.05, configuring your microphones properly, and ensuring your squad is ready to face the psychological toll of the dark. Remember, if you hear your friend whispering from the shadows, make sure they are actually the one talking.

## Sources
- Steam News: Patch 1.05 - Voice Chat Rework & Other Hotfixes
- Community Bug Reports (Reddit / ACETeam Subreddit)