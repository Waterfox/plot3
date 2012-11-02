# Plot3 Dev Documentation

## Dashboard

dashlist list:

```python
[[str: 'save', str: x-pos+'px', str: y-pos+'px'],[int: ID, str: x-pos+'px', str: y-pos+'px',str: width+'px',str: height+'px', str: plotType],[id2...],[id3...]]
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