# Homework #1

### Read first

[First homework](https://gist.github.com/nmatkheev/985ed7fb7a819732ca5539dd43bdc9b5) - task
from [Nikolay Matkheev](https://github.com/nmatkheev)

### Architecture and use

Class attributes:
+ data_stack - stack for operations
+ return_stack - can be used to support correct work of functions (unused at the moment)
+ now (instruction pointer) - pointer for current code instruction
+ code - list of instructions, given by user
+ heap - dictionary of variables and their values
+ heap_func - dictionary of tuples ```(*type (proc or func)*, function code)```
+ slo - dictionary of all supported operations


#### Usage example
1. Create class instance, named ```test_machine``` and pass an expression you want to execute. Let's make simple
   addition ```3 + 5``` and print the result

```python
test_machine = Machine('3 5 + println')
```
2. Call ```run``` method of ```test_machine```

### To be done in the future

+ Need to add better parser for quote characters, because

```python
def remove_excess_quote(lst):
    result = []
    for elem in lst:
        if isinstance(elem, str):
            result.append(elem.replace("\'", ""))
        else:
            result.append(elem)
    return result
```

... it doesn't work very well :)

+ Review [this](https://github.com/ffufcok/KIB_Homework/blob/master/HW_1/Stack_Machine.py#L139-L171) to add support for
  conditions inside other conditions

+ Add REPL for comfortable work with Stack_Machine