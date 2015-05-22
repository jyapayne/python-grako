# python-grako
Python parser for grako.

### Requirements

This requires grako to be installed. You can do this via pip:

```bash
pip install grako
```

###Usage

With grako installed, use this to generate the parser:

```bash
python -m grako Python.grako -o parser_class.py
```

And then run the parser on the test code with:

```bash
python python_parser.py test/test.py start
```
