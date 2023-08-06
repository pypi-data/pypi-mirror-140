# htmlgen

![](rsc/ex.png)

As easy as 
```python
gen = HtmlGenerator()

with gen.row as r:
    r(0).markdown("# Hello\n- List 1\n- *List 2*")
    r(0).latex(rf"\sum_i^n {__file__[10]}\left(i\right) = \mathbf(E)")
    r(0).markdown("That was an equation, like this one: $$x^2$$")
    r(1).image(rsc.img)
```



## Install
```bash
pip install htmlgen
pip install -e <path-to-repo>/htmlgen
pip install git+ssh://git@github.com/GaetanDesrues/htmlgen.git
```
