# Plot3 Dev Documentation

## Dashboard

dashlist list:

```python
[[str: 'save', str: x-pos+'px', str: y-pos+'px'],
[int: ID, str: x-pos+'px', str: y-pos+'px',str: width+'px',str: height+'px', str: plotType],
[id2...],[id3...]]
```


## Sankey Diagram

link list:

```python
[[node,[link1,linkN..],value],[node2..]...]
```

node: name of node
link1: where the node links to
value: number of links

name list:
```python
[[node,ID],[node2,ID2],...]
```

## CSS Classes

### Header

#### Default

Visible background, stays in sight the whole time.

#### Thin
    <header class="thin">

Invisible background and bottom border, stays in sight the whole time.

#### Float
    <header class="float">

Almost invisible until hover, tucked up into top of page.

Default:
![Example Float Header WIP](http://i.imgur.com/XStC5.png)

Hover:
![Example Float Header WIP2](http://i.imgur.com/XTXee.png)
