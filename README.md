# Python Run

Run a python script with configurable access permissions. inspired by `deno run`.

## Example

Create a new file `example.py`:

```python
with open("./hello.txt", "w") as fp:
    fp.write("Hello World!")
```

Run the script with `python-run`:

```bash
python -m python_run example.py
```

