#!/usr/bin/env python3

# USED FOR: getopt
import os
import sys
import getopt

# USED FOR: xml parsing
import xml.etree.ElementTree as ET


# SECTION: Templates
# # # # # # # # # # #

g_template_loader: str = '''
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 *  glapi.h : single-header OpenGL API header and loader
 *
 *      profile : {_PROFILE_}
 *      version : {_VERSION_}
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

#if defined (__cplusplus)
# pragma once
#endif /* __cplusplus */
#if !defined (_glapi_h_)
# define _glapi_h_
# if defined (__gl_h_) || defined (__gl_glext_h_)
#  error "glapi.h: detected OpenGL inclusion before this file."
# endif /* __gl_h_ || __gl_glext_h_ */
# define __gl_h_
# define __gl_glext_h_
#
# if defined(_WIN32) && !defined(APIENTRY) && !defined(__CYGWIN__) && !defined(__SCITECH_SNAP__)
#  if defined (WIN32_LEAN_AND_MEAN)
#   define WIN32_LEAN_AND_MEAN 1
#  endif /* WIN32_LEAN_AND_MEAN */
#  include <windows.h>
# endif /* _WIN32 && APIENTRY && __CYGWIN__ */
#
# if !defined (GLAPI)
#  define GLAPI extern
# endif /* GLAPI */
#
# if !defined (GLAPIS)
#  define GLAPIS static inline
# endif /* GLAPIS */
#
# if !defined (GLAPIENTRY)
#  define GLAPIENTRY
# endif /* GLAPIENTRY */
#
# if !defined (APIENTRY)
#  define APIENTRY
# endif /* APIENTRY */
#
# if !defined (APIENTRYP)
#  define APIENTRYP APIENTRY *
# endif /* APIENTRYP */
#
{_GL_VERSION_DEF_}
#
# include <stddef.h>
# include <stdint.h>

/* SECTION:
 *  OpenGL API
 * * * * * * */

typedef unsigned int GLenum;
typedef unsigned char GLboolean;
typedef unsigned int GLbitfield;
typedef void GLvoid;
typedef signed char GLbyte;
typedef short GLshort;
typedef int GLint;
typedef int GLclampx;
typedef unsigned char GLubyte;
typedef unsigned short GLushort;
typedef unsigned int GLuint;
typedef int GLsizei;
typedef float GLfloat;
typedef float GLclampf;
typedef double GLdouble;
typedef double GLclampd;
typedef void *GLeglImageOES;
typedef char GLchar;
typedef char GLcharARB;

# ifdef __APPLE__
typedef void *GLhandleARB;
# else
typedef unsigned int GLhandleARB;
# endif /* __APPLE__ */

typedef unsigned short GLhalfARB;
typedef unsigned short GLhalf;
typedef GLint GLfixed;
typedef ptrdiff_t GLintptr;
typedef ptrdiff_t GLsizeiptr;
typedef int64_t GLint64;
typedef uint64_t GLuint64;
typedef ptrdiff_t GLintptrARB;
typedef ptrdiff_t GLsizeiptrARB;
typedef int64_t GLint64EXT;
typedef uint64_t GLuint64EXT;
typedef struct __GLsync *GLsync;
struct _cl_context;
struct _cl_event;
typedef void (APIENTRY *GLDEBUGPROC)(GLenum source,GLenum type,GLuint id,GLenum severity,GLsizei length,const GLchar *message,const void *userParam);
typedef void (APIENTRY *GLDEBUGPROCARB)(GLenum source,GLenum type,GLuint id,GLenum severity,GLsizei length,const GLchar *message,const void *userParam);
typedef void (APIENTRY *GLDEBUGPROCKHR)(GLenum source,GLenum type,GLuint id,GLenum severity,GLsizei length,const GLchar *message,const void *userParam);
typedef void (APIENTRY *GLDEBUGPROCAMD)(GLuint id,GLenum category,GLenum severity,GLsizei length,const GLchar *message,void *userParam);
typedef unsigned short GLhalfNV;
typedef GLintptr GLvdpauSurfaceNV;

{_GL_API_DEC_}

/* SECTION:
 *  Loader API
 * * * * * * */

{_API_DEC_}

/* SECTION:
 *  Implementation
 * * * * * * * * */

# if defined (GLAPI_IMPLEMENTATION)
#  include <stdio.h>
#  include <stdlib.h>
#  if defined (__linux__)
#   include <dlfcn.h>
#   include <unistd.h>
#  endif /* __linux__ */
#  if defined (_WIN32)
#   include <windows.h>
#  endif /* _WIN32 */
#
#  if !defined (glapiLogInfo)
#   if defined (GLAPI_VERBOSE) || defined (GLAPI_VERBOSE_INFO)
#    define glapiLogInfo(...) (fprintf(stdout, "glapi.h: "__VA_ARGS__))
#   else
#    define glapiLogInfo(...)
#   endif /* GLAPI_VERBOSE || GLAPI_VERBOSE INFO */
#  endif /* glapiLogInfo */
#
#  if !defined (glapiLogError)
#   if defined (GLAPI_VERBOSE) || defined (GLAPI_VERBOSE_ERROR)
#    define glapiLogError(...) (fprintf(stderr, "glapi.h: "__VA_ARGS__))
#   else
#    define glapiLogError(...)
#   endif /* GLAPI_VERBOSE || GLAPI_VRBOSE_ERROR */
#  endif /* glapiLogError */

/* SECTION:
 *  Loader API
 * * * * * * */

{_API_STATIC_}

{_API_DEF_}

/* SECTION:
 *  OpenGL API
 * * * * * * */

{_GL_API_DEF_}
# endif /* GLAPI_IMPLEMENTATION */
#endif /* _glapi_h_ */
'''

g_template_api_dec: str = '''
typedef void    *(* glapiLoadProc_t) (const char *);

GLAPI int   glapiLoadGL(void);
GLAPI int   glapiLoadGLLoader(glapiLoadProc_t);
GLAPI int   glapiUnloadGL(void);
'''

g_template_api_def: str = '''
GLAPI int   glapiLoadGL(void) {
    return (glapiLoadGLLoader((glapiLoadProc_t) __glapiDefaultLoader));
}

GLAPI int   glapiLoadGLLoader(void *(*load)(const char *)) {

{_GL_API_IMPL_}

    return (1);
}

GLAPI int   glapiUnloadGL(void) {
    if (!g_handle) {
        return (1);
    }

#  if defined (__linux__)
    dlclose(g_handle), g_handle = 0;
#  endif /* __linux__ */
#  if defined (_WIN32)

#  endif /* _WIN32 */

    return (1);
}
'''

g_template_api_static: str = '''
static void *g_handle = 0;

GLAPIS void *__glapiDefaultLoader(const char *name) {
    void    *symbol;

#  if defined (__linux__)

    const char  *NAMES[] = {
        "libGL.so", "libGL.so.1", 0
    };

    /* Checking if handle is already loaded...
     * */
    if (!g_handle) {
        for (size_t i = 0; NAMES[i]; i++) {
            g_handle = dlopen(NAMES[i], RTLD_NOW | RTLD_GLOBAL);
            if (g_handle) {
                break;
            }
        }

        /* Null-check if dlopen fails for every NAME...
         * */
        if (!g_handle) {
            glapiLogError("could not find a dynamic handle\\n");
            return (0);
        }
    }

    /* Now we can load a symbol...
     * */
    symbol = dlsym(g_handle, name);
    if (!symbol) {
        glapiLogError("could not find a symbol: %s\\n", name);
        return (0);
    }

#  endif /* __linux__ */
#  if defined (_WIN32)

    /* NOTE(yakub):
     *  Here we're trusting microsoft that `HMODULE` is indeed `PVOID`.
     *  And PVOID is indeed `void *`.
     *  I'm giving a lot of trust in microsoft right now...
     * */

#  endif /* _WIN32 */

    return (symbol);
}
'''

# SECTION: Settings
# # # # # # # # # #

g_script_path: str = os.path.dirname(__file__)

g_gl_profile: list = ['core', 'compatibility']
g_gl_version: list = [
    '1.0', '1.1', '1.2', '1.3', '1.4', '1.5',
    '2.0', '2.1',
    '3.0', '3.1', '3.2', '3.3',
    '4.0', '4.1', '4.2', '4.3', '4.4', '4.5', '4.6'
]

g_shortopt: str = 'v:p:i:o:h'
g_longopt: list = ['version=', 'profile=', 'input=', 'output=', 'help']
g_settings: dict = {
    'version':  '4.6',
    'profile':  'core',
    'input':    f'{g_script_path}/OpenGL-Registry/xml/gl.xml',
    'output':   f'{g_script_path}/glapi.h'
}

g_help_msg: str = f'''
glapi.py - OpenGL loader generator written in python 3.11.

Usage: python3 glapi.py <options>...
   of: python glapi.py <options>...
   or: ./glapi.py <options>...

Options:

    -h, --help              show this help message and exit.
    -v, --version=<value>   set the OpenGL version used by the loader:
                            > default: 4.6;
                            > acceptable literals:
                                [ 1.0, 1.1, 1.2, 1.3, 1.4,
                                  1.5, 2.0, 2.1, 3.0, 3.1,
                                  3.2, 3.3, 4.0, 4.1, 4.2,
                                  4.3, 4.4, 4.5, 4.6 ];
    -p, --profile=<value>   set the OpenGL procile used by the loader:
                            > default: core;
                            > accepable literals: [ core, compatibility ];
    -i, --input=<value>     set the path to the OpenGL specification xml file:
                            > default: {g_settings['input']}
    -o, --output=<value>    set the path where OpenGL loader will be created:
                            > default: {g_settings['output']}
'''


def glapi_getopt():
    global g_settings

    try:
        opts, args = getopt.getopt(sys.argv[1:], g_shortopt, g_longopt)
    except getopt.GetoptError as err:
        glapi_loge(err)

    for opt, arg in opts:
        if opt in ('-v', '--version'):
            if arg not in g_gl_version:
                glapi_loge(f'{opt}: invalid version: {arg}')
            g_settings['version'] = arg

        elif opt in ('-p', '--profile'):
            if arg not in g_gl_profile:
                glapi_loge(f'{opt}: invalid profile: {arg}')
            g_settings['profile'] = arg

        elif opt in ('-i', '--input'):
            if not os.path.exists(arg):
                glapi_loge(f'{opt}: invalid path: {arg}')

            if os.path.basename(arg) != 'gl.xml':
                # we need to ensure that the path ends with a '/'
                if not arg.endswith('/'):
                    arg += '/'

                if not os.path.exists(arg + 'gl.xml'):
                    glapi_loge(f'{opt}: invalid path: {arg}')
                arg = arg + 'gl.xml'

            g_settings['input'] = arg

        elif opt in ('-o', '--output'):
            if os.path.isdir(arg):
                # we need to ensure that the path ends with a '/'
                if not arg.endswith('/'):
                    arg += '/'
                g_settings['output'] = arg + 'glapi.h'

            else:
                if os.path.basename(arg) != 'glapi.h':
                    glapi_loge(f'{opt}: invalid path: {arg}')
                g_settings['input'] = arg

        elif opt in ('-h', '--help'):
            print(g_help_msg.strip())
            sys.exit(0)


# SECTION: Parser
# # # # # # # # #

class GLSpec:
    # Private variables
    # # # # # # # # # #
    _xml_file: ET.ElementTree = None
    _gl_feat_l: list = []
    # _gles1_feat_l: list = []
    # _gles2_feat_l: list = []
    _gl_enum_l: dict = {}
    _gl_func_l: dict = {}

    # Public variables
    # # # # # # # # # #
    enums: dict = {}
    functions: dict = {}

    def __init__(self):
        # opening an XML specification file
        try:
            tree = ET.parse(g_settings['input'])
        except FileNotFoundError as err:
            print(err)
        root = tree.getroot()

        # parsing types, enums and fuctions...
        self._gl_enum_l = self.__parseEnum(root)
        self._gl_func_l = self.__parseFunc(root)

        # parsing the feature lists...
        # NOTE(yakub):
        #  We're parsing OpenGL and OpenGL ES from the xml file
        self._gl_feat_l = self.__parseFeatures(root, 'gl')
        self.__filterFeatures(self._gl_feat_l)
        # TODO(yakub):
        #  Uncomment those when you'll figure out how to store
        #  OpenGL ES modules...
        # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # self._gles1_feat_l = self.__parseFeatures(root, 'gles1')
        # self.__filterFeatures(self._gles1_feat_l)
        # self._gles2_feat_l = self.__parseFeatures(root, 'gles2')
        # self.__filterFeatures(self._gles2_feat_l)

    # =========================================================================

    def getVersionName(self, number: str):
        if number not in g_gl_version:
            return (None)
        return (self._gl_feat_l[number]['name'])

    def getVersionBlock(self):
        result: str = ''

        for key in self._gl_feat_l:
            name: str = self._gl_feat_l[key]['name']
            d_line: str = f'# define {name}'

            result = result + d_line + '\n'
            if key == g_settings['version']:
                break
        return (result.rstrip())

    def getDeclarationBlock(self):
        enum: str = self.getEnumString()
        func: str = self.getFunctionString(True)
        result: str = f'{enum}\n{func}'

        return (result)

    # #  if defined (GL_VERSION_1_0)
    # glClear = (PFNFLCLEARPROC) load("glClear");
    # #  endif /* GL_VERSION_1_0 */
    def getImplementationBlock(self):
        result: str = ''

        for key in self.functions:
            k_name: str = self.getVersionName(key)
            k_line0: str = f'# if defined ({k_name})\n'
            k_line1: str = f'# endif /* {k_name} */\n'

            result = result + k_line0
            for func in self.functions[key]:
                f_name: str = func[0]

                f_line: str = (f'\tglapi_{f_name} = (PFN{f_name.upper()}PROC) '
                               f'load("{f_name}");')
                result = result + f_line + '\n'
            result = result + k_line1
        return (result)

    def getEnumString(self):
        result: str = ''

        for key in self.enums:
            k_name: str = self.getVersionName(key)
            k_line: str = f'# if defined ({k_name})\n'

            result = result + k_line
            for enum in self.enums[key]:
                e_name: str = enum[0]
                e_value: str = enum[1]
                e_line: str = f'#  define {e_name} {e_value}\n'

                result = result + e_line
            k_line = f'# endif /* {k_name} */\n'
            result = result + k_line
        return (result)

    def getFunctionString(self, extern: bool):
        result: str = ''

        for key in self.functions:
            k_name: str = self.getVersionName(key)
            k_line0: str = f'# if defined ({k_name})\n'
            k_line1: str = f'# endif /* {k_name} */\n'

            if extern:
                result = result + k_line0
                for func in self.functions[key]:
                    f_line: str = None
                    f_name: str = func[0]
                    f_param: str = ''
                    f_type: str = func[1]['type']
                    f_params: dict = func[1]['params']

                    for param in f_params:
                        p_type = param[0]
                        p_name = param[1]
                        p_line = f'{p_type} {p_name}, '

                        f_param = f_param + p_line
                    if len(f_param) != 0:
                        # trimming the last ', ' characters
                        f_param = f_param[:-2]
                    else:
                        f_param = 'void'

                    f_line = (f'typedef {f_type} '
                              f'(APIENTRYP PFN{f_name.upper()}PROC)'
                              f'({f_param});')
                    result = result + f_line + '\n'
                    f_line = (f'extern '
                              f'PFN{f_name.upper()}PROC '
                              f'glapi_{f_name};')
                    result = result + f_line + '\n'
                    f_line = (f'#  define '
                              f'{f_name} '
                              f'glapi_{f_name}')
                    result = result + f_line + '\n\n'
                result = result[:-1]
                result = result + k_line1

            else:
                result = result + k_line0
                for func in self.functions[key]:
                    f_line: str = None
                    f_name: str = func[0]

                    f_line = (f'PFN{f_name.upper()}PROC '
                              f'glapi_{f_name};')
                    result = result + f_line + '\n'
                result = result + k_line1

        if not extern:
            result = result.replace('#', '# ')
        return (result)

    # SECTION: Features
    # # # # # # # # # #

    def __parseFeatures(self, root, api):
        # specification:
        # ['number'] : {
        #   ['name'] : { version name },
        #   ['enum'] : { list of enums },
        #   ['func'] : { list of commands },
        # }
        feat_l: dict = {}

        # parsing the feature list...
        for feat in root.findall('feature'):
            if feat.attrib['api'] != api:
                continue

            number: str = feat.attrib['number']
            name: str = feat.attrib['name']
            feat_l[number]: dict = {}
            feat_l[number]['name'] = name
            feat_l[number]['enum']: list = []
            feat_l[number]['func']: list = []

            # get the list of enums for this version of gl...
            for enum in feat.findall('./require/enum'):
                feat_l[number]['enum'].append(enum.attrib['name'])
            # get the list of commands for this version of gl...
            for cmd in feat.findall('./require/command'):
                feat_l[number]['func'].append(cmd.attrib['name'])

        return (feat_l)

    def __filterFeatures(self, feat_l):
        for key in feat_l:
            feats = feat_l[key]
            self.enums[key] = self.__filterList(
                self._gl_enum_l,
                feats['enum']
            )
            self.functions[key] = self.__filterList(
                self._gl_func_l,
                feats['func']
            )
            if key == g_settings['version']:
                break

    def __filterList(self, l0, l1):
        result: list = []

        for item in l1:
            if item in l0.keys():
                result.append((item, l0[item]))
        return (result)

    # SECTION: Enums
    # # # # # # # # #

    def __parseEnum(self, root):
        # specification:
        # ['name'] : { value }
        gl_enums: dict = {}
        gl_enum_l: dict = root.findall('enums')

        for enums in gl_enum_l:
            for enum in enums:
                try:
                    gl_enums[enum.attrib['name']] = enum.attrib['value']
                except KeyError:
                    pass
        return (gl_enums)

    # SECTION: Functions
    # # # # # # # # # # #

    def __parseFunc(self, root):
        # specification:
        # ['name'] : {
        #   ['type'] : { return type },
        #   ['params'] : {
        #       ['name'] : { type },
        #   }
        # }
        gl_func: dict = {}
        gl_func_l: dict = root.findall('commands')

        for cmds in gl_func_l:
            for cmd in cmds:
                proto = cmd.find('proto')
                param = cmd.findall('param')
                name0: str = None
                type0: str = None
                params: list = []

                for child in proto:
                    if child.tag == 'name':
                        name0 = child.text.strip()
                    elif child.tag == 'ptype':
                        type0 = child.text.strip()
                if type0 is None:
                    type0 = proto.text.strip()

                for par in param:
                    type1: str = par.text
                    name1: str = None

                    for child in par:
                        if child.tag == 'ptype':
                            type1 = child.text
                        elif child.tag == 'name':
                            name1 = child.text
                    params.append((type1, name1))
                gl_func[name0] = {'type': type0, 'params': params}
        return (gl_func)


# SECTION: Loader
# # # # # # # # #

class GLLoader:
    # Private variables
    # # # # # # # # # #
    _spec: GLSpec = None

    # Private template files
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
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
    _t_loader: str = None
    _t_api_def: str = None
    _t_api_dec: str = None
    _t_api_static: str = None

    def __init__(self, spec: GLSpec):
        self._spec = spec
        self.__resolveTemplates()
        self.__createLoaderFile()

    # SECTION: File creation
    # # # # # # # # # # # # #

    def __createLoaderFile(self):
        with open(g_settings['output'], 'w') as f:
            f.write(self._t_loader)

    def __resolveTemplates(self):
        self._t_api_static = g_template_api_static.strip()
        self._t_api_dec = g_template_api_dec.strip()

        self._t_api_def = g_template_api_def.replace(
            '{_GL_API_IMPL_}', self._spec.getImplementationBlock()
        ).strip()

        self._t_loader = g_template_loader.replace(
            '{_PROFILE_}', g_settings['profile']
        ).replace(
            '{_VERSION_}', g_settings['version']
        ).replace(
            '{_GL_VERSION_DEF_}', self._spec.getVersionBlock()
        ).replace(
            '{_GL_API_DEC_}', self._spec.getDeclarationBlock()
        ).replace(
            '{_GL_API_DEF_}', self._spec.getFunctionString(False)
        ).replace(
            '{_API_DEC_}', self._t_api_dec
        ).replace(
            '{_API_DEF_}', self._t_api_def
        ).replace(
            '{_API_STATIC_}', self._t_api_static
        ).strip()


# SECTION: Utilities
# # # # # # # # # # #

def glapi_loge(msg: str):
    f_name = os.path.basename(__file__)

    print(f'{f_name}: {msg}')
    sys.exit(1)


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
