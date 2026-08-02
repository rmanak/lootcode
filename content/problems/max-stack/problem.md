Design a max stack that supports the usual stack operations and additionally
supports finding and removing the stack's maximum element.

Implement the `MaxStack` class:

- `MaxStack()` initializes the stack object.
- `void push(int x)` pushes the element `x` onto the stack.
- `int pop()` removes the element on top of the stack and returns it.
- `int top()` gets the element on top of the stack without removing it.
- `int peekMax()` retrieves the maximum element in the stack without removing it.
- `int popMax()` retrieves the maximum element in the stack and removes it. If
  there is more than one maximum element, only remove the **top-most** one.

**Example 1:**

```
Input
["MaxStack","push","push","push","top","popMax","top","peekMax","pop","top"]
[[],[5],[1],[5],[],[],[],[],[],[]]

Output
[null,null,null,null,5,5,1,5,1,5]

Explanation
MaxStack stk = new MaxStack();
stk.push(5);      // [5]
stk.push(1);      // [5, 1]
stk.push(5);      // [5, 1, 5]
stk.top();        // return 5, [5, 1, 5]
stk.popMax();     // return 5, [5, 1] -- the top-most 5 is removed
stk.top();        // return 1, [5, 1]
stk.peekMax();    // return 5, [5, 1]
stk.pop();        // return 1, [5]
stk.top();        // return 5, [5]
```

**Constraints:**

- `-10⁷ <= x <= 10⁷`
- At most `10⁴` calls will be made to `push`, `pop`, `top`, `peekMax`, and `popMax`.
- There will be **at least one element** in the stack when `pop`, `top`, `peekMax`,
  or `popMax` is called.
