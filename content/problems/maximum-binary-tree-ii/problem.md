> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A *maximum tree* is built from a list `A` of distinct values: the root is the maximum
of `A`, its left subtree is the maximum tree of the elements before it, and its right
subtree the maximum tree of the elements after it. You are given such a tree as a
`TreeNode` `root` (it was built from some `A`) and a value `val` to append to the
end of `A`. Return the root of the maximum tree (a `TreeNode`) built from
`A + [val]`.

**Examples**
```
root = [4,1,3,null,null,2], val = 5   ->  [5,4,null,1,3,null,null,2]
root = [5,2,4,null,1],      val = 3   ->  [5,2,4,null,1,null,3]
root = [5,2,3,null,1],      val = 4   ->  [5,2,4,null,1,3]
```

**Constraints:** the resulting list has length in `[1, 100]` with unique values.
