# glapi: single-header OpenGL loader and generator

**glapi** is an OpenGL generator and loader which utilizes the latest specification standards published by KhronosGroup.

The project is divided to:
- **Generator:**
    - name: `glapi.py`
    - written in: `python 3.11`
- **Single-header Loader:**
    - name: `glapi.h`
    - written in: `c99`

## Minimal example:

```console
$ python3 glapi.py
```
```c
/* cc -Wall -Wextra -Werror example.c -o example -lglfw3 -lm
 * */

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

## Getting started:

To use **glapi** we must generate a header file using a python script.
Let's go step-by-step with process of getting the file!

### 0. Prerequesites:

Ensure that you've the latest versions of the listed software installed on your system:
- **[git](https://git-scm.com/);**
- **[python3](https://www.python.org/);**
- **terminal emulator;**
- **internet connection;**

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

<details>
<summary>Details here:</summary><br>

Firstly, let's take a look at the entrypoint of the script:
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
It's divided into 3 steps:
1. Option processing;
2. Specification parsing using `GLSpec` class;
3. Loader creation using `GLLoader` class;

To not get too deep into how the inner workings are designed, let's just talk about how each component work and talk to each other.

The first step, option processing, is simply a getopt operation performed using built-in `getopt` module for python.
It allows us to set an OpenGL version: `-v, --version`, profile: `-p, --profile`, where the specification is stored: `-i, --input` and where the loader will be created: `-o, --output`.
Each option value is stored in the global `g_settings` dictionary:
```py
# `g_script_path` defined above...

g_settings: dict = {
    'version':  '4.6',
    'profile':  'core',
    'input':    f'{g_script_path}/OpenGL-Registry/xml/gl.xml',
    'output':   f'{g_script_path}/glapi.h'
}
```

Now let's move to the `GLSpec` class. It's workflow is pretty straightforward:
1. Open the `gl.xml` specification file;
2. Read every value from `<enums>` block of the file and store its values in the private dictionary: `_gl_enum_l`;
4. Read every value from `<commands>` block of the file and store its values in the private dictionary: `_gl_func_l`;
5. Read every value from `<feature>` block of the file and store its values in the private dictionary: `_gl_feat_l`;
6. Iterate over the every element of `_gl_feat_l` and extract the OpenGL version name (i.e. `'1.0'` == `'GL_VERSION_1_0'`), matching enums from `_gl_enum_l` and matching functions from `_gl_func_l` until we reach the highest version of OpenGL specified by the `g_settings['version']` setting.
7. The results of the filterings are stored in public dictionaries `enums` and `functions`.
And that's basically almost all the `GLSpec` class does. Almost, but we'll get to that.

Now, last step and the `GLLoader` class. Like the name sugests, it creates the `glapi.h` loader file.
The loader is constructed using template strings which you can easly find by searching for text: `SECTION: Templates`.
There're a few key aspects of this template design:
1. The template string used in this step are:
   - `g_template_loader`: The base of the loader, where all the other templates will be placed;
   - `g_template_api_dec`: Template for declarations of the loader's functions;
   - `g_template_api_def`: Template for definitions of loader's functions;
   - `g_template_api_static`: Template for static components of the loader;
2. The placeholder specification: ` {_PLACEHOLDER_} `
3. List of placeholders:
   - `_PROFILE_`: OpenGL profile (`g_settings['profile']`);
   - `_VERSION_`: OpenGL version (`g_settings['version']`);
   - `_API_DEC_`: API declarations placeholder (`g_template_api_dec`);
   - `_API_DEF_`: API definitions placeholder (`g_template_api_def`);
   - `_API_STATIC_`: API static section placeholder (`g_template_api_static`);
   - `_GL_API_DEC_`: OpenGL API declarations (typedefs, enums and extern declarations);
   - `_GL_API_DEF_`: OpenGL API definitions;
   - `_GL_API_IMPL_`: implementation part of OpenGL loading;
   - `_GL_VERSION_DEF_`: OpenGL version macro definitions;

With that said, let's go over the process of creating a loader:
1. We're assigning a reference to the `GLSpec` object in our `GLLoader`;
2. We start to resolve templates:
   - `GLLoader` has a private member variables for the templates;
   - We're going to perform a placeholder replacement using `str.replace()` built-in python function;
   - Some placeholder, such as `_GL_API_DEC_`, `_GL_API_DEF_` and `_GL_VERSION_DEF_` are code-generated. This code is generated using `GLSpec` because it already stores all the filtered arrays of entries;
   - All the templates are mashed together into the final `_t_loader` template string;
3. We're creating a file at the location `g_settings['output']` in the `write` mode.
4. We stream the content of the `t_loader` string to the file.

To summarize:
1. We get the options passed to the program.
2. We parse the given specification XML file.
3. We filter the parsed data based on the desired OpenGL version.
4. We process the template strings to create a final loader string.
5. We stream the loader string to the loader file.
</details>

## Credit:

- **[Dav1dde/glad](https://github.com/Dav1dde/glad)**
- **[KhronosGroup/OpenGL-Registry](https://github.com/KhronosGroup/OpenGL-Registry)**

## Licence:

This project is licenced with [GNU Lesser General Public License, version 3](./LICENCE).
