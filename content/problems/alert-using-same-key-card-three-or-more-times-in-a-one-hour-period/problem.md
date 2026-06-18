Each worker swipes a key-card to open doors; `[keyName[i], keyTime[i]]` records who
swiped and when, in `"HH:MM"` 24-hour time on a single day. An alert fires for a
worker who swipes **three or more times within any one-hour window** (a window of at
most 60 minutes, inclusive — e.g. `"10:00"`–`"11:00"` counts, `"22:51"`–`"23:52"`
does not). Return the alerted workers' names, sorted alphabetically.

**Examples**
```
keyName = ["daniel","daniel","daniel","luis","luis","luis","luis"],
keyTime = ["10:00","10:40","11:00","09:00","11:00","13:00","15:00"]   ->  ["daniel"]

keyName = ["leslie","leslie","leslie","clare","clare","clare","clare"],
keyTime = ["13:00","13:20","14:00","18:00","18:51","19:30","19:49"]   ->  ["clare","leslie"]
```

**Constraints:** `1 <= len(keyName) == len(keyTime) <= 10^5`, names are lowercase,
each `[name, time]` pair is unique.
