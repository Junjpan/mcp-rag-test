# Python Loops Syntax
## For Loops
The `for` loop is used to iterate over sequences (lists, tuples, strings).
```
for item in [1, 2, 3]:
    print(item)
```

## For While Loops
The `while` loop continues as long as a specified condition is true.
```
n = 0
while n < 5:
    print(n)
    n += 1
```

## Nested Loops
You can use loops inside other loops.
``` 
for i in range(3):
    for j in range(2):
        print(i, j)
```

## Loop Control Statements
- `break`: Exits the loop.
- `continue`: Skips the current iteration and moves to the next.
```
for i in range(5):
    if i == 3:
        break
    print(i)
```