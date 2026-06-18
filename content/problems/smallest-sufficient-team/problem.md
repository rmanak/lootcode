You are given a list of required skills `req_skills` and a list of `people`, where
`people[i]` is the set of skills person `i` has. A team is **sufficient** if, for every
required skill, at least one team member has it. Return the **size** of the smallest
sufficient team (it is guaranteed one exists).

**Examples**
```
req_skills = ["java","nodejs","reactjs"]
people = [["java"],["nodejs"],["nodejs","reactjs"]]            ->  2
req_skills = ["algorithms","math","java","reactjs","csharp","aws"]
people = [["algorithms","math","java"],["algorithms","math","reactjs"],
          ["java","csharp","aws"],["reactjs","csharp"],
          ["csharp","math"],["aws","java"]]                    ->  2
```

**Constraints:** `1 <= len(req_skills) <= 16`, `1 <= len(people) <= 60`; every skill in
`people[i]` is in `req_skills`.
