+++
date = '2026-10-21T09:23:56-04:00'
draft = true
title = 'Window Syntax'
render.unsafe = true
+++


If there is one place in delightql where I like the syntax the least,
it is in the window functions.

As a reminder:

```delightql
users(*) |> (
  first_name,
  country,
  balance,
  row_number:( <~ %(country), #(balance desc)) as country_balance_rank,
  ntile:( 10  <~  %(country),#(balance desc), groups(_,_))
)
```

The window syntax embeds a reverse aggregate arrow `<~` within the calling
parentheses. It also reuses the `#` for `order by` and the `%` for `partition by`.
These make sense and have _some_ justification.

An analytic window specification also includes something called the frame specification,
which is the source of my unease.  Here is the grammar specification I stole
from the [SQLite specification](https://www.sqlite.org/windowfunctions.html):


{{< svg "triangle.svg" >}}
