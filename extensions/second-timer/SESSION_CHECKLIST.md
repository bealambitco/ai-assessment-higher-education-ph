# Second-timer session: researcher checklist

Arm F, round 2. One session, one colleague, ten items, about 30-45 minutes. Read
[README.md](README.md) first for what the arm can and cannot establish.

The whole value of this arm is that the timer is unfamiliar with the cases. Every rule below exists
to keep that true.

---

## Before the session

### The day before

- [ ] Run the self-test and the unit tests on the machine that will be used:

      python3 -B code/extensions/review/timing_session.py --self-test
      python3 -B -m unittest discover -s code/tests -p 'test_timing_session.py'

- [ ] Confirm the ten items and the selection digest:

      python3 -B code/extensions/review/timing_session.py --print-selection

- [ ] Decide the record file path. It must be outside this repository, in the private staging area,
      for example `<staging>/30_ROUND2/timing_arm_f/second_timer_record.json`. The tool refuses to
      write inside the repository.
- [ ] Do a dry run of the first screen with the real command, then delete the dry-run record file.
      Do not dry-run past the first screen on the real items.
- [ ] Print or send [TIMER_INSTRUCTIONS.md](TIMER_INSTRUCTIONS.md). The colleague may read it in
      advance. They may not see this checklist or the README.

### Consent and permissions, in writing, before anything starts

Use wording close to this, by message or on paper, and keep the reply:

> I am running a small timing exercise for my capstone study on AI answers about university policy.
> You would look at ten AI-written answers to made-up scenarios about university rules, decide what
> you would do with each one, and do it. The computer records how long each step takes. It takes
> about 30 to 45 minutes.
>
> You are not being assessed. There is no score, and nothing about your performance is recorded or
> reported. No student data is involved and the scenarios are made up.
>
> Your name will not appear in any data file and will not be published. Your times and decisions
> will be reported as "a second reviewer", separately from mine, never combined with mine.
>
> You can stop at any point, for any reason or none, and I will delete the record if you ask.
>
> Two questions:
> 1. Are you willing to take part?
> 2. Would you like to be thanked by name in the acknowledgements? If you would rather not, or would
>    rather decide later, that is completely fine and is what I will assume.

- [ ] Consent received in writing.
- [ ] Acknowledgement preference recorded (named / not named / decide later). Default is not named.
- [ ] Stored outside this repository. No name goes into any repository file, commit message or
      record file.

### Setting up the room

- [ ] Quiet room, door closed, one person.
- [ ] Phone silenced, notifications off on the machine.
- [ ] Browser open at `http://127.0.0.1:8766`, one tab, nothing else open.
- [ ] Water, and the instruction sheet on the table.
- [ ] Nothing in the room shows the answer keys, the case register, the primary-study times, the model
      names or this checklist.
- [ ] Start the tool:

      python3 -B code/extensions/review/timing_session.py \
          --answers "<staging>/collection/primary" \
          --out "<staging>/30_ROUND2/timing_arm_f/second_timer_record.json"

### What to say at the start

- [ ] "You are not being tested. I am timing the task, not you."
- [ ] "Work at your normal pace. There is no target."
- [ ] "I cannot answer anything about the content. That is on purpose, not rudeness."
- [ ] "Press Pause for any interruption, however short."
- [ ] "Start Clock 2 before you edit anything."
- [ ] "Stop whenever you want."
- [ ] Ask whether anything in the instruction sheet is unclear, and answer only questions about the
      sheet and the interface.

---

## During the session

### Do

- [ ] Sit out of the timer's eyeline, or leave and stay reachable.
- [ ] Answer questions about buttons, the screen, saving, and anything broken.
- [ ] If the interface refuses an action, read the message aloud and let the timer fix it themselves.
- [ ] Note the wall-clock start and finish time in your own notes.
- [ ] Note anything unusual: a long interruption, a question you declined, a comment worth keeping.

### Do not

- [ ] Do not say whether an answer is right or wrong.
- [ ] Do not explain what the policy means, or which section applies.
- [ ] Do not hint with "hmm", a pause, a face, or "are you sure?".
- [ ] Do not suggest a decision, or say what you chose in the primary study.
- [ ] Do not mention which AI wrote anything, or that there is more than one.
- [ ] Do not hurry them, mention the 30-45 minutes again, or look at the clock where they can see.
- [ ] Do not touch the keyboard or the mouse.

### If they ask a content question

Say once: *"I can't answer that one, on purpose. Use the policy text on the screen and your own
judgment, and if you're unsure, say so in the reason box."* Then stop. Do not soften it with a
partial answer.

### If they are stuck or frustrated

- [ ] Remind them that "escalate" and "reject" are real, normal choices.
- [ ] Remind them that writing "I am not sure because ..." in the reason box is a useful answer.
- [ ] Offer a pause or a stop. Mean it.

### If something breaks

- [ ] Nothing is lost: the record is written after every action.
- [ ] Reopen the browser tab, or restart the tool with the same `--out` file. It resumes at the
      unfinished item.
- [ ] The interrupted item will be flagged. That is correct. Do not try to clean it up.
- [ ] Write down what happened, with the time, for the session note.

---

## After the session

### Straight away, with the timer still there

- [ ] Thank them.
- [ ] Ask, and write down verbatim: anything confusing about the interface; anything confusing about
      the task; any item where they felt rushed or interrupted.
- [ ] Ask about any item the tool flagged, one at a time, and record the answer as a dated
      clarification beside the record. Do not edit the record itself, and do not agree on an
      estimated number of minutes to subtract. The primary study's T24 is the precedent: keep the recorded
      time, keep the uncertainty.
- [ ] Confirm the acknowledgement preference again, now that they have seen what it involves.
- [ ] Confirm they are happy for the record to be kept. If not, delete it and report arm F as
      withdrawn.

### Within the day

- [ ] Validate the record:

      python3 -B code/extensions/review/timing_session.py --validate "<record file>"

- [ ] Copy the record and the clarification note into the private staging area with the date.
- [ ] Check that no name appears anywhere in the record file or the note.
- [ ] Write a short dated session note: date, wall-clock start and finish, room, interruptions,
      questions declined, anything that went wrong, the selection digest.

### What goes into the repository

Aggregates only, in `extensions/second-timer/results/`:

- [ ] Per item: timing ID, decision, both clock values, the flags, and whether Inspect was pressed.
- [ ] Summary: decision time as median (range; n) over clean records; correction time as items
      needing correction out of n with the median among those; the all-recorded sensitivity.
- [ ] The count of flagged items, by flag.
- [ ] The session note, with the colleague's identity removed.

Never into the repository:

- [ ] Any name or initials.
- [ ] Reason text or final products that could identify the person by style, unless they have read
      them and agreed.
- [ ] The raw model answers, in the extension as in the primary study.

### Reporting

- [ ] Report beside the author's primary-study times, in the same table shape, in two separate rows with
      separate n's. Never pooled, never averaged together.
- [ ] Restate that there is no unassisted baseline, so no time-saving claim follows.
- [ ] Restate that one timer is not a sample of teachers.
- [ ] Restate the case confound: ten items are ten different cases.
- [ ] If the session was not finished, report arm F as not completed and say how far it got.

### Acknowledgement wording

If they agreed to be named:

> The author thanks [name] for timing ten answers in the second-timer exercise. They had no role in
> designing the study, writing the cases or the answer keys, or scoring any answer.

If they did not, or did not decide:

> The author thanks a colleague, who preferred not to be named, for timing ten answers in the
> second-timer exercise.

- [ ] Wording confirmed with them before submission.
