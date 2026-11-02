A chat agent can only send its model a limited number of tokens, so long
conversations must be trimmed before each call. Doing that naively breaks
things. If you drop an assistant's tool call but keep its tool result, most
model APIs reject the request. If you drop the system prompt, the agent forgets
its instructions. Implement the memory that decides what goes into the next
call.

Implement the class `ConversationMemory`:

- `ConversationMemory(maxTokens, placeholderTokens)`
- `add(role, text, tokens)` appends a message. `role` is `"system"`,
  `"user"`, `"assistant"` or `"tool"`, and `tokens` is its cost. Returns
  nothing.
- `getContext()` returns the messages for the next model call as
  `[role, text]` pairs, oldest first.
- `contextTokens()` returns the total cost of what `getContext()` returns.

**Units.** System messages are **always kept**. The other messages form
**units**, which are kept or dropped whole:

- A `"user"` message is a unit by itself.
- An `"assistant"` message, together with all the `"tool"` messages that
  directly follow it, is one unit.

**Choosing the window.** Let `S` be the total cost of the system messages.

1. If everything fits (`S` + the cost of all other messages `<= maxTokens`),
   the context is every message, in order.
2. Otherwise, some messages must go, and the context will contain a
   placeholder that costs `placeholderTokens`. The budget for units is
   `budget = maxTokens − S − placeholderTokens`. Walk the units from **newest
   to oldest**:
    - The newest unit is **always kept**, even if it alone exceeds the
      budget, so the context can exceed `maxTokens`.
    - Each older unit is kept if its cost fits in what is left of the budget.
      At the **first unit that doesn't fit, stop**: that unit and everything
      older are dropped. Never skip ahead to an older unit that would fit.
3. If any messages were dropped, the context is the system messages, then the
   placeholder `["system", "[k earlier messages omitted]"]`, then the kept
   units' messages in order. Here `k` counts dropped **messages**, not units.
   When `k` is 1, the text is `"[1 earlier message omitted]"`. If nothing was
   dropped, which happens when the conversation is a single oversized unit,
   there is no placeholder.

`contextTokens()` is `S`, plus `placeholderTokens` when the placeholder is
present, plus the kept messages' costs.

## Constraints

- `1 <= maxTokens <= 10⁵` and `0 <= placeholderTokens <= 100`
- `1 <= tokens <= 10⁴`, and `text` is at most 200 characters
- All system messages are added before any other message. A `"tool"` message
  is only added directly after an `"assistant"` or another `"tool"` message
- At most `2000` operations in total

## Examples

**Example 1**
```
Input:
["ConversationMemory", "add", "add", "getContext", "contextTokens", "add", "add", "getContext", "contextTokens"]
[[100, 5], ["system", "You are helpful.", 20], ["user", "hi", 30], [], [],
 ["assistant", "hello!", 30], ["user", "plan my trip", 30], [], []]
Output:
[null, null, null, [["system", "You are helpful."], ["user", "hi"]], 50, null, null,
 [["system", "You are helpful."], ["system", "[1 earlier message omitted]"], ["assistant", "hello!"], ["user", "plan my trip"]], 85]
Explanation: 20 + 30 fits. After four messages the total is 110 > 100, so
the budget is 100 − 20 − 5 = 75. That keeps "plan my trip" (30) and
"hello!" (30), but not "hi" (30 > 15 left). The context costs
20 + 5 + 60 = 85.
```

**Example 2**
```
Input:
["ConversationMemory", "add", "add", "add", "add", "add", "add", "getContext", "contextTokens", "add", "getContext", "contextTokens"]
[[120, 10], ["system", "Use tools.", 10], ["user", "weather in Oslo?", 20], ["assistant", "call get_weather", 15],
 ["tool", "rain, 4C", 40], ["tool", "wind 30 km/h", 25], ["assistant", "Rainy and windy.", 20], [], [],
 ["user", "and tomorrow?", 15], [], []]
Output:
[null, null, null, null, null, null, null,
 [["system", "Use tools."], ["system", "[1 earlier message omitted]"], ["assistant", "call get_weather"],
  ["tool", "rain, 4C"], ["tool", "wind 30 km/h"], ["assistant", "Rainy and windy."]], 120,
 null, [["system", "Use tools."], ["system", "[4 earlier messages omitted]"], ["assistant", "Rainy and windy."],
        ["user", "and tomorrow?"]], 55]
Explanation: the tool call and its two results form one unit costing 80. At
first the budget of 100 holds it plus the newest unit (20). After one more
message, the two newest units (15 + 20) leave 65, and the tool unit (80)
doesn't fit. So the whole tool unit and the user message before it are
dropped, which is 4 messages. Keeping just the tool results is not an option.
```

**Example 3**
```
Input:
["ConversationMemory", "add", "add", "add", "add", "getContext", "contextTokens", "add", "getContext", "contextTokens",
 "add", "getContext", "contextTokens", "add", "getContext", "contextTokens"]
[[50, 8], ["system", "Be brief.", 10], ["user", "a", 12], ["user", "b", 12], ["user", "c", 12], [], [],
 ["user", "d", 30], [], [], ["user", "e", 9], [], [], ["user", "f", 45], [], []]
Output:
[null, null, null, null, null, [["system", "Be brief."], ["user", "a"], ["user", "b"], ["user", "c"]], 46,
 null, [["system", "Be brief."], ["system", "[3 earlier messages omitted]"], ["user", "d"]], 48,
 null, [["system", "Be brief."], ["system", "[4 earlier messages omitted]"], ["user", "e"]], 27,
 null, [["system", "Be brief."], ["system", "[5 earlier messages omitted]"], ["user", "f"]], 63]
Explanation: 46 <= 50 fits with no placeholder, even though 46 + 8 would not.
The budget is 50 − 10 − 8 = 32. After "e", "d" (30) no longer fits in the
23 that is left, and "c" (12) is not rescued even though it would fit.
"f" (45) is over budget on its own but is kept anyway, so the context costs
63.
```
