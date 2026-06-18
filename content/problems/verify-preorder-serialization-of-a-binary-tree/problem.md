A binary tree's preorder traversal is serialized as comma-separated values, using
`#` for a null child. Given such a string, **return `true` if it is a valid preorder
serialization** of some binary tree — without reconstructing the tree.

**Examples**
```
preorder = "9,3,4,#,#,1,#,#,2,#,6,#,#"  ->  true
preorder = "1,#"                        ->  false
preorder = "9,#,#,1"                    ->  false
```

**Constraints:** values are integers or `#`, comma-separated, no empty tokens.
