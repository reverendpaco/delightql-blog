+++
date = '2023-01-01'
title = 'Original Tree Essay'
+++

> [!NOTE]
> The date on this post is the date of **writing**,
> and not the date of publication which is 2026-10-21.
>
> This is an essay I wrote to myself back in 2023 as
> I started to work through the syntax and arguments
> for having tree-groups.
>
> The syntax is slightly different to what I eventually
> settled on, but is still remarkably similar.
>
> Throughout the development process, I would write these
> essays to myself.  They **were** blog posts but the kind
> that were private markdowns I kept in private repos.
> I share it here because it still is mostly correct
> in all the things it claims.

Representing tree structures as relations is both simple and hard.  It is
simple  because relations naturally induce graphs via unification of
dimensions/columns, and so as trees are a special type of graph, the tree
structure is there if you want it, implicit in the connections. You are done.

Making the trees explicit though, via either a data structure representation or
via a query seems to be something that bedevils the database community. The
terms adjancecy list, materialized path, closure tables, and nested sets are
just a few of the techniques that have arisen to make the querying of
hierarchical data amenable to different flavors of access and update patterns.
Vendor specific 'CONNECTS BY' notions have become standardized to the
Datalog-influence recursive CTE 'UNION ALL' to a recursive table.  And yet it
is still messy.

One could argue that an entire subset of NoSQL technologies have arisen out of
a frustration to be able to get useful _explicit_ tree structures out of a
relational store.  The problem goes by many names, but the most famous is, of
course, object-relational impedance mismatch, a term we could easily rename
"tree-relational impedance mismatch".

That a very important community, the general purpose programmers who surf above
the calm cool logic of the database, became irritated enough to invent ORMs and
even tree/object-oriented data stores is both a shame and a problem.

There is no easy answer, but it's worth examining the way in which both data
structures (of any form) and algorithms can move back and forth between these
two descriptive polarities: explitic vs implicit.

In most programming languages, trees are used to describe and define important
algorithms that programmers see in their mind executing classic breadth-first,
or depth-first vists.  The tree is a natural mental model, even though it might
not be explicit.

A recursive depth-first in simple psuedo-code:
```
fn visit(o):
  do_something(o)
  for child in o:
    visit(child)
```
uses a tree algorithm, to traverse an explicit tree (the obliquely named `o` variable
with its references to its children, and thence to their children).

What is particularly interesting is that in order to execute this algorithm, we
make use of another data structure, the stack, which, at least in this example
is implicit to the programmer but explicit to the language engine.
To make it explicit, we could forego the language's call stack and use our own.

```
fn visit(o):
  stack = [o]
  while stack is not empty:
    current = stack.pop()
    do_something(current)
    for child in current:
      stack.push(child)
```

If we watch the temporal evolution of this stack structure, as it increases
and decreases with pushes and pops, we can see it trace a
tree structure, much like a fast moving glowing object traces lines
in the dark.

While this discussion is not 'a revelation' (inasmuch as many people have been
properly taught this duality between structure and algorithms) it is still
worth revisiting just to remind ourselves how our mental model of these
constructs can influence us.  We view data as more explicit (and real) and view
algorithm structure as more implicit, even though both, if we take an extreme
reductionalist view, are just ones and zeros (or voltages).


But the irony to the above example, is that database tables, just like the
object `o` with its descendants, are very explicit data structures. So why do
we still have such a problem with hierarchy from the database?

To tease an answer, and to motivate where this discussion is going, it could be
quite simply this:  that we have historically 'prohibited' the idea of tables
within tables, i.e. we insist that our tables be in first normal form.  If we
relax this mental model, and maybe our technology, the mismatch goes away.

To flesh out this argument, we will need to see how we can see trees even
within a single table, and then contemplate how 'regular' programming languages
with their table-stakes usage of compound types, specifically product types
(tuples, objects, classes, structs, etc.), choose to model data.


## A Tree Structure in a Simple Table

Imagine the following table called 'Cars':


| color | make   | model    |
|-------|--------|----------|
| red   | toyota | corolla  |
| red   | toyota | camry    |
| red   | honda  | civic    |
| green | toyota | corolla  |
| green | bmw    | 5-series |
| black | toyota | corolla  |

The usage of `Group By` on this table by any dimension creates a momentary tree
(a nested set of tables) that we kill off immediately. Our SQL engine (and our
training) is so against the notion of tables within tables, that we _flatten_
it before it can have its own identity. To wit:

```sql
  select
    color,
    possible_aggregate_flattener_function(make,model)
  from Cars
    group by color;
```

returns a row for each unique color and, unless we _reduce_ one of the other
dimensions by an aggregate function, nothing else.

If we weren't so against the idea of tables within tables, we could imagine two
separate operations: `WELCOMING-GROUP` and `FLATTEN` which operate on the table
as it first turns into a tree and then to a "regular" table.  Our new
`WELCOMING-GROUP` operator would return

```
| color | grouped_contents      |
|-------|-----------------------|
| red   | | make   | model    | |
|       | |--------|----------| |
|       | | toyota | corolla  | |
|       | | toyota | camry    | |
|       | | honda  | civic    | |
|       | |--------|----------| |
|-------|-----------------------|
| green | | make   | model    | |
|       | |--------|----------| |
|       | | toyota | corolla  | |
|       | | bmw    | 5-series | |
|       | |--------|----------| |
|-------|-----------------------|
| black | | make   | model    | |
|       | |--------|----------| |
|       | | toyota | corolla  | |
|       | |--------|----------| |
|-------|-----------------------|
```

which is a tree.  We can see it clearer if we were to write it out
in JSON, a nicely natural syntax for trees:

```json
  "cars": [
    {
      "color" : "red"
      "grouped_contents": [
        {
        "make": "toyota",
        "model": "corolla"
        },
        {
        "make": "toyota",
        "model": "camry"
        }
        {
        "make": "honda",
        "model": "civic"
        }
      ]
    }
    {
      "color" : "green"
      "grouped_contents": [
        {
        "make": "toyota",
        "model": "corolla"
        },
        {
        "make": "bmw",
        "model": "5-series"
        }
      ]
    }
    {
      "color" : "black"
      "grouped_contents": [
        {
        "make": "toyota",
        "model": "corolla"
        },
        {
        "make": "bmw",
        "model": "5-series"
        }
      ]
    }
  }
```

While this might merit a mere 'ok, so what?' it should be noted that there is
one relational query language, Pig -- a higher level abstraction on top of big
data engines (Hadoop originally), that traffics in this exact sort of semantic.
Its heritage of dealing with non-curated data, i.e. data that may be co-located
with zeroth normal-form complex types, necessitated this division of
responsibilities.  Pig separates out `GROUP` from `FLATTEN` and allows bag
types as values within columns.

While the above JSON may be valid, it is not the prototypical form.  If
we engage in some shenanigans -- pivoting, and turning data into metadata (row
values into column names) -- we will get the following table.




```
| red                   |    green              |    black              |
|-----------------------|-----------------------|-----------------------|
| | make   | model    | | | make   | model    | | | make   | model    | |
| |--------|----------| | |--------|----------| | |--------|----------| |
| | toyota | corolla  | | | toyota | corolla  | | | toyota | corolla  | |
| | toyota | camry    | | | bmw    | 5-series | | |--------|----------| |
| | honda  | civic    | | |--------|----------| |                       |
| |--------|----------| |                       |                       |
|-----------------------|-----------------------|-----------------------|
```


This provides us with a more 'natural' tree that could easily be serialized into
any object hierarchy of most general purpose languages, and it shows that
addressing into a column is like addressing into a table (a contained table)
of that same name.

```json
  "cars": {
    "red": [
      {
      "make": "toyota",
      "model": "corolla"
      },
      {
      "make": "toyota",
      "model": "camry"
      }
      {
      "make": "honda",
      "model": "civic"
      }
    ]
    "green": [
      {
      "make": "toyota",
      "model": "corolla"
      },
      {
      "make": "bmw",
      "model": "5-series"
      }
    ]
    "black": [
      {
      "make": "toyota",
      "model": "corolla"
      },
      {
      "make": "bmw",
      "model": "5-series"
      }
    ]

  }

```

The takeaway from this discussion has nothing to do with features, per se, of
any hypothetical or real current SQL or NoSQL technology.  Rather it is to make
evident that the mental model of tables as a two-dimensional sheet filled with
atomic types is, in a way, isomorphic, to an equally valid tree-based model.
In fact, mental models are all we really have access to within the guide rails
of the host programming language.  There are no real "tables" down there in the
innards of a SQL engine, just as there are no real "trees" in the composite
data type structure of most languages.  These are abstractions that we can
choose to place on our gamut from "implicit" to "explicit".

This thought experiment might allow us to define some useful rules for how to
understand trees and tables as two sides of the same coin, without committing
us to overthrowing a regime or fetishizing a technology stack. It is in this
process, starting from the ground up, that we can guess at what a query
language that allows us to address the underlying data either as a
'two-dimensional' sheet or as a tree would look like. Hopefully this
multi-paradigmatic viewpoint will allow us to switch back and forth between
either on the basis of ergonomics, clarity, or comfort.

But let's take the example a bit further.  Rather than starting with a table,
let's start with a typical JSON tree representation. This JSON tree (JSON is
really not the most important thing here -- it is just a serialization standard
that provides us with the most approachable syntax over others, like XML
or S-expressions) will look like a typical packet of data served out of some software
middleware -- maybe something RESTful, or maybe something from a newer technology
like GraphQL.

```json
{
  "first_name" : "Sammy",
  "last_name" : "Shark",
  "location" : "Ocean",
  "websites" : [
    {
      "description" : "work",
      "URL" : "https://www.digitalocean.com/"
    },
    {
      "desciption" : "tutorials",
      "URL" : "https://www.digitalocean.com/community/tutorials"
    }
  ],
  "social_media" : [
    {
      "description" : "twitter",
      "link" : "https://twitter.com/digitalocean"
    },
    {
      "description" : "facebook",
      "link" : "https://www.facebook.com/DigitalOceanCloudHosting"
    },
    {
      "description" : "github",
      "link" : "https://github.com/digitalocean"
    }
  ]
}
```

Working from a tree to a table representation, we first recognize
that containing nodes are effectively multiplied across contained nodes,
and that this parent-to-child relationship is a strong one.  Thus,
the attributes/columns of "first_name","last_name",and "location"
may be treated as if they could belong to each of the internal
relations represented by the enumerated objects within "websites"
and "social_media".

But unlike our first example (before we pivoted, that is), there
are two separate contained tables: "websites" and "social_media".

It is an easy enough to see how an originating set of tables could
have given rise to this tree.  First imagine the "websites" table
consisting of the following columns:

## Websites
| first_name | last_name | location | description | URL                                              |
|------------|-----------|----------|-------------|--------------------------------------------------|
| Sammy      | Shark     | Ocean    | work        | https://www.digitalocean.com/                    |
| Sammy      | Shark     | Ocean    | tutorials   | https://www.digitalocean.com/community/tutorials |

## Social_Media
| first_name | last_name | location | description | URL                                               |
|------------|-----------|----------|-------------|---------------------------------------------------|
| Sammy      | Shark     | Ocean    | twitter     | https://twitter.com/digitalocean                  |
| Sammy      | Shark     | Ocean    | facebook    | https://www.facebook.com/DigitalOceanCloudHosting |
| Sammy      | Shark     | Ocean    | github      | https://www.github.com/digitalocean               |


# Trees and Relations and JSON and Metadata

  * what happens if we allow tables within tables (zeroth-normal form)
  * a closer look at grouping, and
    * how it could be modeled like Pig (as an operator which generates sub-tables)
    * how it can be seen as a function
  * the notions of Pivot and Melt and how they manifest the push-pull of metadata versus data
  * two separate ways to model relations _from_ trees
    * metadata-forward (more rigid schemas)
    * data-forward (more dynamic schemas)
  * two ways to model trees from relations
    * Group-Mode (Pivot) construction
    * Nested-Table Mode construction
  * Pathing (access to a tree structure)
  * Tree/JSON paterns
    * the simple table
    * the tree constructor
    * the ornate table
    * the compression tree
    * the API-packet
  * all the sticky problems
    * case-sensitivity in data, insensitivty in metadata
    * non-functionally dependent data while going from data to metadata
    * uggg... NULL!!!
    * "wild" JSON data and its rough edges

![This is the caption](table-matrix.png)



### Group-Mode (Pivot) Construction


#### Group-Mode Inline Table Notation
```prolog
employees(*)
  |> $[ state,city] -> lower:(&)
  |> ~> [ %state(%city(_(FirstName,LastName,Title))) ]
  |-> employees_as_json.
```
or

#### Group-Mode Tree Notation

```prolog
employees(*)
  |> $[ state,city] -> lower:(&)
  |> ~> [ { %state: { %city: _(FirstName,LastName,Title) } }  ]
  |-> employees_as_json.
```

and both produce:

```json
  {
  	"MA": {
  		"Boston": [{
  				"FirstName": "Daniel",
  				"LastName": "Eklund"
  			},
  			{
  				"FirstName": "Bob",
  				"LastName": "Zarnak"
  			}
  		],
  		"Worcester": [{
  				"FirstName": "Daniel",
  				"LastName": "Eklund"
  			},
  			{
  				"FirstName": "Bob",
  				"LastName": "Zarnak"
  			}
  		]
  	}
  }

```


### Inline Tree Notation (Nested-Mode)

```prolog
employees(*) |> [ { identity: { EmployeeId, LastName, FirstName },
                    ReportsTo,
                    Title,
                    address: { Address,City,State }
                    contact: { Phone,Email } } as x, EmployeeId]
                                 |> %[-EmployeeId] ~> [ [x] as results ]
```

The JSON-like tree construction is shorthand for a nested table.  In the
case where a LVar(column) is left un-adorned without a name, then the name
of the column is automatically inserted.

### Inline Table Construction (Nested-Mode)

This is in contrast to the Inline-Tree Construction (Nested Mode)

```prolog
employees(*) |> [ _( .identity( EmployeeId, LastName, FirstName),
                      ReportsTo,
                      Title,
                     .address(Address,City,State)
                     .contact(Phone,Email)) , EmployeeId]
             |> %[-EmployeeId] ~> [ [.employee] as results ]
```

```json
{
	"identity": {
		"EmployeeId": 23232,
		"LastName": "Eklund",
		"FirstName": "Daniel"
	},
	"address": {
		"Address": "neouh",
		"City": "Boston",
		"State": "MA",
		"Zip": "02118"
	},
	"contact": {
		"Phone": "309-3434-3133",
		"Email": "doeklund@gmail.com"
	}
}
```


### Large Example

```prolog
employee(*) \, customer(*) \, invoice(*) \, invoiceline(*)
  \, track(*), @{CustomerId,InvoiceId,TrackId}, customer.SupportRepId=employee.EmployeeId
  SupportRepId=EmployeeId,EmployeeId=4
    |> [ { %employee.state: { employee: { identity: { EmployeeId, LastName, FirstName },
                      ReportsTo,
                      Title,
                      customers: ~> customers
                      address: { Address,City,State },
                      contact: { Phone,Email }

            }}}  ]
        ~> [ { CustomerId,Company, tracks: ~> tracks } as customers  ],
        ~> [ { Name,Customer } as tracks  ].
```

oenuth

```sql
with
  tablified_data as (
    select
        e.EmployeeId,
        e.Lastname,
        e.FirstName,
        e.ReportsTo,
        e.Title,
        e.Address,
        e.City,
        e.City,
        e.Phone,
        e.Email,
        c.CustomerId,
        c.Company,
        t.Name,
        t.Composer
      from Employee e
        left outer join Customer c on c.SupportRepId=e.EmployeeId
        left outer join Invoice i using(CustomerId)
        left outer join InvoiceLine il using(InvoiceId)
        left outer join Track t using(TrackId) ),
  grouped_tracks as (
    select  EmployeeId,CustomerId,Company,LastName,FirstName ,City,
      json_group_array(json_object('Name',Name,'Composer',Composer)) as CustomerTracks
      from tablified_data group by EmployeeId,CustomerId,Company,LastName,FirstName,City),
  grouped_customers as (
    select EmployeeId,Company,LastName,FirstName, City,
      json_group_array(json_object('CustomerId',CustomerId,'Company',Company, 'Tracks', json(CustomerTracks))) as Customers
      from grouped_tracks group by EmployeeId,Company,LastName,FirstName,City),

  final as (
   select
     EmployeeId,City,
     json_object('identity', json_object('EmployeeId',EmployeeId,'Lastname',Lastname),
                                  'Customers', json(Customers) ) as EmployeeCustomerTracks
     from  grouped_customers
       group by EmployeeId,City)

    select json_object(City , json_group_array(json(EmployeeCustomerTracks)))
        from final where EmployeeId=4 group by City;
```





```json
{"Calgary":[
  {
  	"identity": {
  		"EmployeeId": 4,
  		"Lastname": "Park"
  	},
  	"Customers": [{
  		"CustomerId": 4,
  		"Company": null,
  		"Tracks": [{
  			"Name": "Put The Finger On You",
  			"Composer": "Angus Young, Malcolm Young, Brian Johnson"
  		},{
  			"Name": "Saturnine",
  			"Composer": "Billy Corgan"
  		}, {
  			"Name": "Rock On",
  			"Composer": "David Cook"
  		}]
  	},{
  		"CustomerId": 35,
  		"Company": null,
  		"Tracks": [{
  			"Name": "Wave (Os Cariocas)",
  			"Composer": null
  		}, {
  			"Name": "Garota de Ipanema (Dick Farney)",
  			"Composer": null
  		},{
  			"Name": "Red Light",
  			"Composer": "U2"
  		}, {
  			"Name": "Lemon",
  			"Composer": "U2; Bono"
  		}, {
  			"Name": "The Wanderer",
  			"Composer": "U2; Bono"
  		}]
  	}, {
  		"CustomerId": 39,
  		"Company": null,
  		"Tracks": [{
  			"Name": "Prometheus Overture, Op. 43",
  			"Composer": "Ludwig van Beethoven"
  		}, {
  			"Name": "Sonata for Solo Violin: IV: Presto",
  			"Composer": "Béla Bartók"
  		}, {
  			"Name": "Lodi",
  			"Composer": "J. C. Fogerty"
  		},{
  			"Name": "A Sua",
  			"Composer": "Rodolfo"
  		}, {
  			"Name": "Bê-a-Bá",
  			"Composer": "Rodolfo"
  		}]
  	}, {
  		"CustomerId": 40,
  		"Company": null,
  		"Tracks": [{
  			"Name": "Morena De Angola",
  			"Composer": null
  		}, {
  			"Name": "A Banda",
  			"Composer": null
  		}, {
  			"Name": "União Da Ilha",
  			"Composer": "Dito/Djalma Falcao/Ilha, Almir Da/Márcio André"
  		}, {
  			"Name": "Put Your Lights On",
  			"Composer": "E. Shrody"
  		},{
  			"Name": "City Of Blinding Lights",
  			"Composer": "Adam Clayton, Bono, Larry Mullen & The Edge"
  		}]
  	}, {
  		"CustomerId": 49,
  		"Company": null,
  		"Tracks": [{
  			"Name": "Romance Ideal",
  			"Composer": null
  		}, {
  			"Name": "SKA",
  			"Composer": null
  		}, {
  			"Name": "Finding My Way",
  			"Composer": "Geddy Lee And Alex Lifeson/Geddy Lee And Neil Peart/Rush"
  		}, {
  			"Name": "Evil Ways",
  			"Composer": null
  		}, {
  			"Name": "It's Only Love",
  			"Composer": "Jimmy and Vella Cameron"
  		}, {
  			"Name": "So Beautiful",
  			"Composer": "Mick Hucknall"
  		},{
  			"Name": "Hallowed Be Thy Name",
  			"Composer": null
  		}]
  	}, {
  		"CustomerId": 55,
  		"Company": null,
  		"Tracks": [{
  			"Name": "Walking On The Water",
  			"Composer": "J.C. Fogerty"
  		}, {
  			"Name": "Suzie-Q, Pt. 2",
  			"Composer": "J.C. Fogerty"
  		}, {
  			"Name": "Cathedral",
  			"Composer": "Alex Van Halen/David Lee Roth/Edward Van Halen/Michael Anthony"
  		}, {
  			"Name": "Little Guitars",
  			"Composer": "Alex Van Halen/David Lee Roth/Edward Van Halen/Michael Anthony"
  		}]
  	}, {
  		"CustomerId": 56,
  		"Company": null,
  		"Tracks": [{
  			"Name": "Love Gun",
  			"Composer": "Paul Stanley"
  		}, {
  			"Name": "Deuce",
  			"Composer": "Gene Simmons"
  		}, {
  			"Name": "Wake Me Up When September Ends",
  			"Composer": "Mike Dint, Billie Joe, Tré Cool"
  		} {
  			"Name": "Medo De Escuro",
  			"Composer": null
  		}, {
  			"Name": "The Last Song",
  			"Composer": "Dave Grohl, Taylor Hawkins, Nate Mendel, Chris Shiflett"
  		}, {
  			"Name": "Friend Of A Friend",
  			"Composer": "Dave Grohl, Taylor Hawkins, Nate Mendel, Chris Shiflett/FOO FIGHTERS"
  		}, {
  			"Name": "Sua Impossivel Chance",
  			"Composer": "Nando Reis"
  		}]
  	}]
  }
]}
```


