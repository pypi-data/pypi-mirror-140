# withcd
### Change working directory utility compatible with "with" statement

Changes the working directory while inside the "with" statement, then it changes the working directory back to where it was originally.

### Install

`python -m pip install withcd`

### Usage
```python
from withcd import cd
from os import getcwd

print(getcwd()) #<path>
with(cd('foo')):
    print(getcwd()) #<path>/foo
print(getcwd()) #<path>
```
