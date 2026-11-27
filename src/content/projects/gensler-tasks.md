---
title: "Gensler-tasks"
tagline: "The working record of my City Design Index engagement at Gensler Research Institute, kept in the order the work happens: the sync, the tasks it sets, the tickets that report them, the messages that announce them."
domain: gensler
stack: ["Python", "Node.js", "Slide design", "Asana"]
stats:
  - { value: "12", label: "recorded syncs, September to November 2026" }
  - { value: "12", label: "task folders" }
  - { value: "4", label: "steps, in the order of work" }
order: 2
status: private
repo: "https://github.com/zihjyunderek/Gensler-tasks"
---

The City Design Index (CDI) at Gensler Research Institute moves in weekly syncs. Each sync sets a few tasks; each task ends in a deliverable, a ticket that reports it and a message that announces it. This repository keeps that record in one place, and every other CDI repository points back to the task it came from.

> The meetings, the tasks and their results are confidential under NDA. This page describes how the record is kept.

## Four folders, in the order of work

| Step | Folder | What goes in |
| --- | --- | --- |
| 1 | `01_meetings/` | The sync, read from its recording into a transcript, a summary and its action items |
| 2 | `02_tasks/` | One folder per task, named by the task and dated by the week it was set: its inputs, scripts and deliverables |
| 3 | `03_tickets/` | The tickets written for the round, one file per sync |
| 4 | `04_messages/` | The messages that announce the round, ready to post |

The numeric prefixes keep the folders in that order on every operating system, so the folder list reads like the week.

## A task is a folder

A task is named by what it is, not by the meeting that set it: a recurring task keeps its name and only the date changes, so every edition of one task sorts together. Each task folder carries a `data/` folder with everything it was given, so a deliverable can always be traced to its sources. Tasks so far range from literature reviews and a journal rating to a survey-item match across three survey years, proposals for new metrics, a note on city fixed effects with MGWR, and the administrative size of 54 global cities.

## Where the rest lives

Analysis pipelines live in their own repositories with a code-project layout (CDI-Typology, CDI-Survey, CDI-Clusters, CDI-Indices, CDI-Demo), and each one's documentation names the tasks behind it. The edition of a deck that was presented goes to Gensler-Milestone; the papers go to CDI-Papers.
