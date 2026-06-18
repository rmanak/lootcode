Starting from `startUrl`, you may follow links given by `graph` (a map from a URL
to the list of URLs it links to). Return **all reachable URLs that share the same
hostname as `startUrl`**, sorted ascending. A URL looks like `http://host/path`;
the hostname is the text between `http://` and the next `/`.

## Constraints
- `1 <= number of URLs <= 10^4`; every URL begins with `http://`.

## Examples
Input: `startUrl = "http://a.com/1", graph = {"http://a.com/1": ["http://a.com/2","http://b.com/9"], "http://a.com/2": [], "http://b.com/9": []}`
Output: `["http://a.com/1","http://a.com/2"]`
Explanation: `b.com` is a different host.

Input: `startUrl = "http://x.org/p", graph = {"http://x.org/p": []}`
Output: `["http://x.org/p"]`

Input: `startUrl = "http://a.com/1", graph = {"http://a.com/1": ["http://a.com/1"]}`
Output: `["http://a.com/1"]`
