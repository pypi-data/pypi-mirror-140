## Installation

```sh
pip install numpy
pip install calculator
```

## Usage

With use of this tool you can:

-  add numbers - via add() metod
-  subtract numbers - via subtract() metod
-  multiply numbers - via multiply() metod
-  divide numbers - via divide() metod
-  root numbers - root add() metod
## Before start using

There is always number in memory of calculator.
Operations are perfomed on this number.
You can get it via get_state() method.

```python
>>> calc = Calculator()
>>> calc.add(0.1)
0.1
>>> calc.add(0.2)
0.3
>>> calc.subtract(10.3)
-10.0
>>> calc.divide(3)
-3.333333333333
>>> calc.multiply(3)
-10.0
>>> calc.root(1/3)
-1000.0
>>> calc.reset()
0.0
>>> calc.get_state()
0.0
```


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Make sure to add or update tests as appropriate.


## License

[MIT](https://choosealicense.com/licenses/mit/)
