# Testing

Testing is done by spinning up a local dev node in a QEMU VM and running the tests against it. Follow [this guide](https://github.com/rafalum/optimism-local-devnet) to setup your local dev net and place the .qcow2 file in the root of this directory. Further make the binaries `start_devnet` and `stop_devnet` available in your path.

Then, run the tests with:
```bash
python -m unittest discover -s test -p 'test_*.py'
```

