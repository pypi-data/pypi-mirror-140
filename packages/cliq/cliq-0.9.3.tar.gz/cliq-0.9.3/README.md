# cliq: creating command line interfaces quickly in Python

`cliq` is a lightweight framework for creating a command line application or
writing a libary powered with command line tools in Python.

- supports nested subcommands
- equiped with init and config system
- supports multiple command line tools in a single library
- only depends on the standard library


## Quick Start

Install cliq:

```
$ pip install cliq
```

Create your project:

``` 
$ cliq create project ./myapp
$ pip install -e ./myapp
$ myapp
```

Create a new command:

```
$ cliq create command do.py
$ python do.py -h
```

Add the command to your project:

```
$ mv do.py ./myapp/myapp/main/command/
$ myapp do -h
```

Remove `help`, `init`, `config` commands if you don't need them:

```
$ cd ./myapp/myapp/main/command
$ rm help.py init.py config.py
```

## Commands

- A command is standalone and complete by itself if you don't need config.
- You can run it as an independent script. 
- Just copy a command script into your project.
- There is nothing to be configured.

Try toy sample commands:

```
$ cliq create project myapp --sample
$ pip install -e ./myapp 
$ myapp say hello
hello
$ cliq please say hello
hello
$ cliq please sum 1 2 3 4 5
15.0
```

Write your command:

- It's just an argparse.ArgumentParser
- See <https://docs.python.org/3/library/argparse.html>
- Add arguments to the `self.parser`
- Write the `run` method
- Your command runs standalone if you don't use the `app` variable, which
  allows your command to access config variables through `app.config`.

Create a command script:
```
$ cliq create command say.py 
```

Edit the script:

```python
...

class Command(SimpleCommand):
    def __init__(self, app = None, name = __name__):
        super().__init__(app, name)

        # self.parser is an argparse.ArumentParser
        # see https://docs.python.org/3/library/argparse.html       
        #
        # add arguments. for example:
        #
        # self.parser.add_argument('input', type=str, help='input filename')
        # self.parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
        # self.parser.add_argument('-o', '--output', type=str, help='output filename')

    def run(self, argv):
        args = self.parser.parse_args(argv)

        # implement command line functionalities
        print(args)
 
...
```

## Library

Create a project and add modules:

```
$ cliq create project mylib
$ pip install -e ./mylib
$ echo 'def mean(*x): return sum(x)/len(x)' > mylib/mylib/math.py
```

It is a normal library:

```python
>>> import mylib.math
>>> mylib.math.mean(1, 2, 3, 4, 5)
3.0
```

Add commands. For example,

```
$ cliq create command mylib/mylib/main/command/mean.py
```

```python
import sys
from cliq.main.command import SimpleCommand
import mylib.math

def init(app):
    return Command(app)

class Command(SimpleCommand):
    def __init__(self, app = None, name = __name__):
        super().__init__(app, name)

        self.parser.add_argument('x', type=float, nargs='+')

    def run(self, argv):
        args = self.parser.parse_args(argv)

        # implement command line functionalities
        print(mylib.math.mean(*args.x))
 
```

Run the command:

```
$ mylib mean 1 2 3 4
2.5
```




## Tutorial
### Concepts

#### app, command and subcommand

`cliq` supports nested command line interfaces to the depth 3: app, command, and subcommand.

```
$ cliq   create     project       ./myapp      --with-sample-commands
$ pip    install                               -e ./myapp
$ myapp  please     sum           1 2 3 
$ myapp  say                      hello
$ myapp                                        --help
  <app>  <command>  <subcommand>  <arguments>  <options>
```

#### project, library and app

`cliq` supports a library with multiple command line apps:

```
$ cliq create project ./myproj --name mylib --cli myapp,yourapp
$ pip install -e ./mylib
$ myapp -h
$ yourapp -h
```

See the directory structure: project, library and apps.
 
```
$ tree myproj
myproj
├── README.md
├── mylib
│   ├── __init__.py
│   ├── myapp
│   │   ├── __init__.py
│   │   └── main
│   │       ├── __init__.py
│   │       └── command
│   │           ├── config.py
│   │           ├── help.py
│   │           └── init.py
│   └── yourapp
│       ├── __init__.py
│       └── main
│           ├── __init__.py
│           └── command
│               ├── config.py
│               ├── help.py
│               └── init.py
├── setup.cfg
└── setup.py

7 directories, 14 files
```




### Simple command

Generate a simple command template script file:

```
$ cliq create command say.py  
$ python say.py -h
usage: __main__ [-h]

options:
  -h, --help  show this help message and exit
```

Add arguments to `self.parser` and implement `run` method:

```python
class Command(SimpleCommand):
    def __init__(self, app = None, name = __name__):
        super().__init__(app, name)
        
        self.parser.add_argument('something', type=str, help='something')
        
    def run(self, argv):
        args = self.parser.parse_args(argv)
        print(args.something)
```

Use it:

```
$ python say.py hello
hello
```


### Complex command with nested subcommands

Create a command script file with the subcommands option:

```
$ cliq create command do.py --with-subcommands something,anything,nothing 
```

Test it:

```
$ python do.py
usage: __main__ [-h] {something,anything,nothing} ...

options:
  -h, --help            show this help message and exit

subcommands:
  {something,anything,nothing}
                        command help
    something           something
    anything            anything
    nothing             nothing

```

Edit it and put it into the command directory:

```
$ mv do.py myapp/myapp/main/command/
```

### Project with multiple command line modules

You can create a project with multiple command line interface modules.

```
$ cliq create project ./holy --with-cli graham,terry 
$ pip install -e ./holy
```

Directory strucutre:

```
holy/
└── holy
    ├── graham
    │   └── main
    │       └── command
    └── terry
        └── main
            └── command
```

Test cli modules:

```
$ graham -h 
...

$ terry -h 
...
```

Add commands:

```
$ cliq create command holy/holy/graham/main/command/say.py
$ graham say -h

$ cliq create command holy/holy/graham/main/command/play.py --sub role,instrument
$ graham play role -h
$ graham play instrument -h
```

### Simple command line apps

A command line module can run without predefined commands. Just put your
command script named `__init__.py` into the path `<app>/main/command/`.

```
myapp/
├── __init__.py
└── main
    ├── __init__.py
    └── command
        └── __init__.py
```

For example, you are going to write a image library with command line
converters.

```
$ cliq create project myimglib --cli png2jpg,jpg2png
$ pip install -e ./myimglib/
$ cliq create command myimglib/myimglib/png2jpg/main/command/__init__.py
$ png2jpg --help
```

Open `__init__.py` and write your code. `png2jpg` runs the code in
`__init__.py`. Remove default command scripts if you don't need them.

```
$ rm myimglib/myimglib/png2jpg/main/command/*
$ cliq create command myimglib/myimglib/png2jpg/main/command/__init__.py
```
