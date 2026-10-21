+++
date = '2026-07-25T15:22:01-04:00'
title = 'Using LLMs to implement delightql'
slug = 'llms'
tags =  ["AI"]
+++


> [!NOTE]
> The date on this post is the date of **writing**,
> and not the date of publication which is 2026-10-21.
>


Delightql has been built with the help of AI. This post is a discussion of that
word _help_ both as an accounting of the full extent to which AI was utilized
and as a means to ramble.

The best way to explain how AI was used is chronological, but before I do
that I will drop here two true sentences that will anchor the rest of the post:

- Of the 150k odd lines of Rust code that make up Delightql, I may have written 1000 lines top.
- The language design was 99.9% me, and the part that was not -- well, that's probably me too.

----

# Mid 2025 LLMs

The first AI-aided implementation of Delightql started in late July of 2025.
But this was not the first implementation as I had spent over 10 years hacking
at things before committing to a language specification.  My programming at
that time included dalliances with Nim, Janet, Tatsu (a parser generator
framework in Python), Go and Rust. -- each time trying to learn more and more
about how to write a compiler front end.  This eventually stopped in 2022 when
I realized that these furtive fits and starts were getting me nowhere.  This
led to me writing a book over the next four years of a language that did not
exist.

July of 2025 was the first time I decided I wanted to turn
this  Borgesian artifact into a real programming language.  Being impressed
with what I saw of the agentic terminal-based LLMs, I knew this new world of
vibe-coding was worth giving a try and so I bit the bullet and got the Claude
Pro plan.

My first interaction was special in all those ways that first interaction are
-- memorable. I gave the model my book and some technical decisions and asked
it to take it as far as it could, and within two days at least half of my book
was implemented.  Then, as part of the experiment, I unblinded myself and
looked at the code.

This was why the first few batches of work had been delivered so fast while the
last few had become slower and slower:  the code was shit. It was a cacophany
of edge-cases, weird crate choices, copy-pasted code and occasional
agent-planted logic bombs and "if in testing mode, report this secret value so
those tests turn green." And it had zero modularization, and a very creaky
understanding of a compiler pipeline from `text->CST->AST->(profit)`.

I don't want to throw July25 claude under the bus, but I realized that what I
had here was an amoral senior engineer who worked twenty times faster than a
real senior engineer and so could go down twenty more rabbit holes if not
circumscribed.  I still had a job!

I have read that it was the October 25 generation of models that really woke up
people's minds to the potential of agentic LLMs, but I was onboard a bit
earlier.  Yay me. Not because I didn't think the October models were a step up
-- they certainly were -- but because even a senior engineer working at twenty
times the speed was still a huge asset. The October models delivered principal
engineers.  These later models also were really good tech leads and project
managers.


So these months between July and October were funny moments of revelation and
robosocial camraderie. Multiple times I asked myself both "Why the heck am I
screaming at this agent for messing up my directions a NINTH time in a row?",
and "Why the heck am I happy when the agent compliments a language
choice?"

What got accomplished is captured in a jj change history that I look back on
with that pride/horror mix.

I was not a Rust programmer before embarking. I had done the rustlings before
and very small toy things. I also felt confident that I understood the language
features, from parametric polymorphism via traits and the functional defaults,
to the difference between stack and heap allocation and what the borrow checker
did and why it was important.  Obviously this is not the same as feeling
confident enough to say to yourself "I know how to program in X."

All of this is to say that those first few months were me pushing hard to
understand how to use Rust properly. And the equvilent statement is that those
first few months were me pushing against the agent and my own somewhat faulty
pre-conceptions to understand how Rust models the world. I believe strongly
that this is 90% of the value in engineering something:  chosing the right data
abstractions. Function follows form.

In these first few months, the modelling was overhauled several times, and each
time I thought to myself, how can I get the Rust compiler to work for me so
that this crackhead won't create that monstrosity again?

I think I eventually got there, and the merits and specifics of the final model
are beyond the scope of this post, but I think that we together (my robot and
me) landed on something that mostly "made illegal states unrepresentable" --
for the most part using type state techniques with trait generics, all to
prevent earlier parts of the pipeline accessing later parts, and vice versa.

From July to October, using jj as my visual narrative editor, I confidently let
the agent loose on pre-designed epics with explicit guardrails and todos.
And I would speed-read every patch and commit and steer real time.


---

# October 2025 Generation

When the October models came around my senior was replaced by a principal.  I
needed some adjustment because I had become so used to real-time watching the
patches come in and interrupting with a "why are you doing that?". The Opus
model 4.5 model was the first time that I felt that I was being listened to and
that when I said something had to be done everytime a task was done, it was
done.  Nothing is more frustrating than investing effort in a huge test corpus
and then having the agent ignore that the NINTH time in a row.   The October
models lowered my frustration level significantly.

It took me a while to get used to the fact that I no longer had to look at each
and every line that was being generated. It was also roughly around this same
time the CLI harnesses mostly removed the chain of reasoning or thought (or
whatever it's called) from my view, which forced the issue but also made me
worried. Luckily, judicious use of super cheap jj changes allowed me to log
realtime.

What happened at this moment was I had taken a step even further back. Before
while I had only written 1000 lines of code myself, I still knew the codebase by
heart and could reference it with my senior. After, there were huge chunks of
new code and massive refactorings that I let happen with me just trusting. I
learned to trust because my test corpus proved that the code was ok and hadn't
regressed, and I had other equally capable agents in other jj workspaces who
were told to be adversarial and code review like every line mattered.

In the near post-October world, I felt loss because I knew that I now no longer
answer all such questions about a code path and why a variable was named that
way, an error was thrown that way, why this method was named that, etc. I knew
I had lost touch and it was up to me to be ok with that or not.

I have just as much ego as the next tech person, so part of me really wanted to
take a stop and comb over everything by hand, but the other part of me -- the
language designer -- was champing at the bit to actively start using delightql
and build things.  This latter me won out. ---

# May 20226 The Fable/Sol/Astra era

Early 2026 opera continued to release and each was incrementally better. I
never had that common complaint of "they are nerfing this on purpose".

But the next big change was the Fable release and then GPT-sol. Up until May of
2026, I had been exclusively on Claude Max (I upgraded back in September of
2025).  My occasional tryouts of other models showed me that while they could
be nearly as good they were not quite there.  Thus for the current max
subscription, being a one vendor shop was fine -- I had no loyalty, but also
not much in the way of any other feelings.

The fable generation was another change in role.  My senior had become a
principal, but what was he now? A god-damned savant.  I huffed with anger when
it knew more about why I designed something in the language than I did. It
understood my motivations for language feature more than I could properly
articulate.

But with savant-like capabilities came savant-like language, and I'm not
talking about the classic "load-bearing" or "seam" but neologisms. I appreciate
coinages much much more than the next guy:  a well chosen name for a concept
(especially the inchoate ones) can make design discussions much more dense and
therefore fruitful.  But man, the fable could really coin with the best of them
and make you feel like an asshole because you weren't in its mind to understand
whatever it was visualizing. This was the era where I mostly followed the
back-and-forth but would need to ocassionally ask for the ELI5.

With fable, and then Sol, my principal became a high-performing product owner
who knows how to code too.  My interactions have become less about designing
epics to asking probing questions and conversations like:  I have a new subset
of the language to implement, here are the requirements, give me a plan and
implement it.  And within a day it's done.

Going from me to PreOctober agents was a step down in capability but a 20x
speedup in code throughput. Going from PreOctober to October was a significant
step up in capability and maybe a 2x speedup.  The fable and sol generations
have unlocked a new kind of speedup, where entire multi-epic projects can be
entrusted and the speedup is probably another 5x.  This is vague, I know, but
true too.

I am writing this in July 2026, and the language has mostly landed. There are
some niggling things I want to take care of and stil some big choices about
abstractions the language supports and surface I might want to elimininate.
But I am mostly done, almost a year after starting.

I tried Sol and decided it was a worthy agent to welcome into my team, so I got
the standard $20 subscription. It feels just about as capable as fable but
without the savant language and I enjoy using its different mindset to do code
reviews and help pick apart designs.

My most recent usages of both these top models is purely around locking them in
the room with just the delighqtl binary and asking them "play with this thing..
tell me what it does? does it have rough edges?"  This activity has surfaced
many old features and assumptions that needed to be revisited. Unfortunately
true adverserial language like "Can you fuzz this?" gets flagged and
auto-downgraded.  As a language designer, I need that cybersecurity hacker to
try to crack every corner of what I've wrought.

By way of conclusion I do want to point out that there is one place where I
think the agents have NOT overshadowed me, and that is in having taste.

Language design I think is about taste.  I sound like a pre-2020 person saying
that AI could never make good art.  I am aware that that might change too.

Whether my taste is shared is a separate question.  I'm sure plenty of people
will disagree with my choices, but they were mine to make and were always done
in service of taste.  The few times I actively asked the agents to imagine how
a new feature or abstraction (things like the effect system or ER-context
rules) _could_ be redesigned their answers were never quite in service of an
underlying point of view that is demanded by a language. Some were laughably in
violation of the 'house voice' (as they like to say) of the current language --
for example suggesting keywords to a language that eschews them.

That made me feel good for now.


