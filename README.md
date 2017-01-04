### Overview

Tiny [**Python**](https://www.python.org/) context manager implementing a simple command protocol
over pipes (e.g no deep binding/integration required) The data is serialized as json and arbitrary
payload can be attached to the commands (and returned in the responses). Use it whenever you want
to use python code to drive a project that is not python, typically to automate testing or maybe
prepare some input, coordinate with remote systems, mock a quick REST front-end, etc. The manager
will spawn the specified subprocess and read/write to its stdin/stdout. Any unexpected process
exit will raise an exception and commands can be issued either in blocking mode or with a timeout.

A few simple use-cases:

```python
    try: 
      with driven('/usr/local/bin/my-stuff') as proxy:
        proxy.ask('do something')
        reply = proxy.ask('configure', ext={'foo': 'bar'})
        if proxy.ask('shutdown', timeout=5.0) is None:
          raise Exception('unable to terminate gracefully')
    except BadExit:
      print 'abnormal process exit' 
```

You can simply install this package via pip/git:

```
$ pip install git+https://github.com/opaugam/spika 
```

### Sample

A trivial [**Go**](https://golang.org/) snippet is provided to illustrate how the stuff works in
conjunction with a tiny control script. Just build and try it out:

```
$ cd sample
$ go build snippet.go
$ python runme.py
```

### Support

Contact olivier.paugam@autodesk.com for more information about this project.
