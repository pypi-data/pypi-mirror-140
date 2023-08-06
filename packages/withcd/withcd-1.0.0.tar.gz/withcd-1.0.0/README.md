# withcd
### Change working directory utility compatible with "with" statement

It changes the working directory while inside the "with", then it changes back to where it was originally

### Usage
```python
from withcd import cd
from os import getcwd

print(getcwd()) #<path>
with(cd('foo')):
    print(getcwd()) #<path>/foo
print(getcwd()) #<path>
```
