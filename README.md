# glapi: single-header OpenGL loader and generator

**glapi** is an OpenGL generator and loader which utilizes the latest specification standards published by KhronosGroup.

The project is divided to:
- Generator:
    - name: `glapi.py`
    - written in: `python 3.11`
- Single-header Loader:
    - name: `glapi.h`
    - written in: `c99`

## Minimal example:

```console
$ python3 glapi.py
$ 
```
```c
#define GLAPI_IMPLEMENTATION
#include "./../glapi.h"

#include <GLFW/glfw3.h>

static void *g_window;

int main(void) {
    if (!glfwInit()) { return (1); }

    g_window = glfwCreateWindow(800, 600, "glfw 3.4 - hello, glapi!", 0, 0);
    glfwMakeContextCurrent(g_window);
    
    if (!glapiLoadGL()) { return (1); }

    glViewport(0, 0, 800, 600);
    do {
        glClear(GL_COLOR_BUFFER_BIT);
        glClearColor(0.1, 0.1, 0.1, 1.0);
        glfwSwapBuffers(g_window);
        glfwPollEvents();
    } while (!glfwWindowShouldClose(g_window));

    glapiUnloadGL();
    glfwTerminate();
    return (0);
}
```
```console
$ cc -Wall -Wextra -Werror example.c -o example -lglfw3 -lm
$
```

## Getting started:

To use **glapi** we must generate a header file using a python script.
Let's go step-by-step with process of getting the file!

### 0. Prerequesites:

Ensure that you've the latest versions of the listed software installed on your system:
- [git](https://git-scm.com/) - version control system;
- [python3](https://www.python.org/) - latest python interpreter;

### 1. Cloning from remote git repository:

Currently, **glapi** is hosted only on github.com. To get the latest version of **glapi**,
launch your terminal emulator and type:

```console
$ git clone --recurse-submodules https://github.com/itsYakub/glapi.git
$ cd glapi/
```

### 2. Generate an OpenGL loader:

**glapi's** generator is simply just a python script. It is designed to have as little external dependencies as possible, preferably none at all.
This means that in your terminal you just need to type:

```console
$ python3 glapi.py
```

If everything passes successfully, you should have a brand new `glapi.h` file in the current directory.

## How does it work?

*NOTE(@itsYakub):*

*This section is highly technical. You don't need to read this section.*

<details>
<summary>Details here:</summary>

Okay, to understand how the generator works, let's take a look at the entrypoint:

```py
# SECTION: Entrypoint
# # # # # # # # # # #

if __name__ == '__main__':
    # STEP 1.: Option process
    # # # # # # # # # # # # #
    glapi_getopt()

    # STEP 2.: Spec. parsing
    # # # # # # # # # # # # #
    gl_spec: GLSpec = GLSpec()

    # STEP 3.: Spec. loading
    # # # # # # # # # # # # #
    gl_load: GLLoader = GLLoader(gl_spec)
```

Entrypoint is divided into 3 steps:
- Option processing;
- Loading and parsing the OpenGL specification;
- Generating an OpenGL loader based on the specification object;

Let's start with the Option processing.
It uses the basic python's `getopt` module, which gives a c-style option processing.
The list of options that we're looking for is listed by using:

```console
$ python3 glapi.py --help
```

This simple command should give you a brief summary of what can be done using `glapi.py`,
including the restrictions required for the proper workflow of the script.

Options are stored in the global variable dictionary: `g_settings`:

```py
g_settings: dict = {
    'version':  '4.6',
    'profile':  'core',
    'input':    './OpenGL-Registry/xml/gl.xml',
    'output':   './glapi.h'
}
```

Later on in the program we'll access this fields a lot of times.



There's not that much to say about the option processing so let's move to specification parsing!
For that step we have a special class: `GLSpec`. It contains several dictionaries for extracted enums and functions.

Let's take a look at the members of this class:

```py
# Private variables
# # # # # # # # # #
_xml_file: ET.ElementTree = None
_gl_feat_l: list = []
_gl_enum_l: dict = {}
_gl_func_l: dict = {}

# Public variables
# # # # # # # # # #
enums: dict = {}
functions: dict = {}
```

Each of this member has it's special meaning in the whole workflow of the parser.
Firsly, let's focus on the private field.

`_xml_file` is self-explainatory: it is a variable where the whole XML Tree is stored.

`_gl_feat_l` is a list of extracted features from the `<feature>` block in `gl.xml`.
It's specification looks like:

```py
['number'] : {
    ['name'] : { version name },
    ['enum'] : { list of enums },
    ['func'] : { list of commands },
}
```

Each field of this list is based on the version number, as string.
Every number matches very version of OpenGL ['1.0' - '4.6'].
It makes sense then every field of this value is version-specific to the specification:
- `'name'` stores the name of the version. It is pretty simple: '1.0' -> 'GL_VERSION_1_0';
- `'enum'` stores the list of enum names (only);
- `'func'` stores the list of function names (only);

`_gl_enum_l` is the key-value list of every enum from the specification.
The list is version-independent. The specification looks like:

```py
['name'] : { value }
```

Simple, right? We use the name of the enum as the key and the value is the literal numerical value.

`_gl_func_l` is the key-value list of every function from the specification.
The list is version-independent. The specification looks like:

```py
['name'] : {
    ['type'] : { return type },
    ['params'] : {
        ['name'] : { type },
    }
}
```

This one is more complicated than the `_gl_enum_l`. The name of the function is used as the key.
The value-dictionary has several entries:
- `'type'` for return type of the function;
- `'params'` for the dictionary of the parameters, working similarly as the `_gl_enum_l`;

Now let's move to the public members of the class.
The values stored in those dictionaries are version-separated tupples of keys and values.
There's not really a specific reason why I chose tupples for this job.
The main reason was siplicity it gave for building the blocks of code, but about that later.

In other words, `enums` and `functions` are key-value dictionaries, where the key is the version of OpenGL
and the value is the tupple of the keys and values (yes, it needs some refactoring or rewording).



Huh, that was quite a lot of informations. Let's move to another, the last step of the generations.
This step is creating the loader itself. For that we're using another class: `GLLoader`.

This class has a few private members we should take a look at:

```py
# Private variables
# # # # # # # # # #
_spec: GLSpec = None
_t_loader: str = None
_t_api_def: str = None
_t_api_dec: str = None
_t_api_static: str = None
```

First member, `_spec`, is just a reference to the `GLSpec` object, simple.
Now let's take a look at the other members. the *'t'* in their names stand for *"template"*.

Yes, now we'll use some templates to generate a loader. These templates can be found in [templates/](./templates/) directory.
To explain them briefly:
- [./templates/api-dec.txt](api-dec.txt) - template for declarations of the loader's API.
- [./templates/api-def.txt](api-def.txt) - template for definitions of the loader's API.
- [./templates/api-static.txt](api-static.txt) - template for internal static loader's API.
- [./templates/loader.txt](loader.txt) - the main template for the structure of the loader.

Each template has the special fields that are placeholder for some text. They follow this convention: {_PLACEHOLDER_}
And there we have the complete list of every placeholder and their meaning:
```py
# List of templates:
# > _PROFILE_           : OpenGL profile (g_settings['profile'])
# > _VERSION_           : OpenGL version (g_settings['version'])
# > _API_DEC_           : our own API definitions (api-dec.txt)
# > _API_DEF_           : our own API declarations (api-def.txt)
# > _API_STATIC_        : our own static functions (api-static.txt)
# > _GL_API_DEC_        : OpenGL api declarations (extern declarations)
# > _GL_API_DEF_        : OpenGL api definitions (regular declarations)
# > _GL_API_IMPL_       : implementation part of OpenGL loading
# > _GL_VERSION_DEF_    : OpenGL version macro definitions
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
```

So now the process of creating the loader looks like that:
- we're opening every template file and store their content in the class's member variable;
- if the string contains the placeholder, we need to replace it using `str.replace()` function;
- if the placeholder cannot be replaced with the file template, we need to generate the string template using code.
This is performed by the GLSpec class, especially by: `GLSpec.getVersionBlock()`, `GLSpec.getDeclarationBlock()`, `GLSpec.getImplementationBlock()` and `GLSpec.getFunctionString()`;
- the expanded template `_t_loader` is then written into the loader file itself.

And that's briefly what is happening.
To summarize:
- we're processing the options passed to the program;
- we're parsing the XML specification file;
- we're opening special template files;
- we're replacing placeholder strings by template files and strings;
- we're writing the final output to the loader file.

</details>

## Credit:

The credit must be given where it's needed. The main inspiration for this project was [glad](https://github.com/Dav1dde/glad), from which I borrowed the concept of XML parsing and templates.
And the main source is [specification repository by KhronosGroup](https://github.com/KhronosGroup/OpenGL-Registry).

Links:
- [https://github.com/Dav1dde/glad](https://github.com/Dav1dde/glad)
- [https://github.com/KhronosGroup/OpenGL-Registry](https://github.com/KhronosGroup/OpenGL-Registry)

## Licence:

This project is licenced with [GNU Lesser General Public License, version 3](./LICENCE).
