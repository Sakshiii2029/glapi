#!/usr/bin/env python3

# USED FOR: getopt
import os
import sys
import getopt

# USED FOR: xml parsing
import xml.etree.ElementTree as ET
import re


# SECTION: Settings
# # # # # # # # # #

g_gl_profile: list = ['core', 'compatibility']
g_gl_version: list = [
    '1.0', '1.1', '1.2', '1.3', '1.4', '1.5',
    '2.0', '2.1',
    '3.0', '3.1', '3.2', '3.3',
    '4.0', '4.1', '4.2', '4.3', '4.4', '4.5', '4.6'
]

g_shortopt: str = 'v:p:s:h'
g_longopt: list = ['version=', 'profile=', 'source=', 'help']
g_settings: dict = {
    'version':  '4.6',
    'profile':  'core',
    'source':   './OpenGL-Registry/xml/gl.xml'
}


def GenGL_getopt():
    global g_settings

    try:
        opts, args = getopt.getopt(sys.argv[1:], g_shortopt, g_longopt)
    except getopt.GetoptError as err:
        loge(err)
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-v', '--version'):
            if arg in g_gl_version:
                g_settings['version'] = arg
                continue

            # fail state...
            loge('invalid version: {}'.format(arg))
            sys.exit(0)

        if opt in ('-p', '--profile'):
            if arg in g_gl_profile:
                g_settings['profile'] = arg
                continue

            # fail state...
            loge('invalid profile: {}'.format(arg))
            sys.exit(0)

        if opt in ('-s', '--source'):
            if os.path.exists(arg):
                if os.path.basename(arg) == 'gl.xml':
                    g_settings['profile'] = arg
                    continue
                else:
                    loge('invalid file: {}'.format(arg))
            else:
                loge('argument isn\'t a valid path: {}'.format(arg))
            sys.exit(0)

        if opt in ('-h', '--help'):
            print('help')
            sys.exit(0)


# SECTION: Parser
# # # # # # # # #

def GLSpec_parse():
    f_gl_xml: str = g_settings['source']
    gl_feat: dict = {}
    gl_types: dict = {}
    gl_enums: dict = {}
    gl_func: dict = {}

    # opening an XML specification file
    try:
        tree = ET.parse(f_gl_xml)
    except FileNotFoundError as err:
        print(err)
    root = tree.getroot()

    # filtering feature list for all the types, enums and functions...
    gl_feat = GLFeat_parse(root.findall('feature'))
    # extracting OpenGL types...
    gl_types = GLTypes_parse(root.findall('types'))
    # extracting OpenGL enums...
    gl_enums = GLEnum_parse(root.findall('enums'))
    # extracting OpenGL functions...
    gl_func = GLFunc_parse(root.findall('commands'))

    return (GLFeat_filter(gl_feat, gl_types, gl_enums, gl_func))


# SECTION: Features
# # # # # # # # # #

def GLFeat_parse(gl_feat_l: dict):
    # specification:
    # ['number'] : {
    #   ['name'] : { version name },
    #   ['type'] : { list of types },
    #   ['enum'] : { list of enums },
    #   ['func'] : { list of commands },
    # }
    gl_feat: dict = {}

    for feat in gl_feat_l:
        number: str = feat.attrib['number']
        name: str = feat.attrib['name']
        gl_feat[number]: dict = {}
        gl_feat[number]['name'] = name
        gl_feat[number]['enum']: list = []
        gl_feat[number]['func']: list = []

        # get the list of enums for this version of gl...
        for enum in feat.findall('./require/enum'):
            gl_feat[number]['enum'].append(enum.attrib['name'])
        # get the list of commands for this version of gl...
        for cmd in feat.findall('./require/command'):
            gl_feat[number]['func'].append(cmd.attrib['name'])

    return (gl_feat)


def GLFeat_filter(gl_feat_l, gl_type_l, gl_enum_l, gl_func_l):
    # specification:
    # ['type'] : { list of types }
    # [GL_VERSION_X] : {
    #   ['enum'] : { list of enums }
    #   ['func'] : { list of functions }
    # }
    gl_spec: dict = {}

    for key in gl_feat_l:
        feat = gl_feat_l[key]
        name = feat['name']

        gl_spec['type'] = gl_type_l
        gl_spec[name] = {'enum': [], 'func': []}
        gl_spec[name]['enum'] = GLFeat_filterEnum(gl_enum_l, feat['enum'])
        gl_spec[name]['func'] = GLFeat_filterFunc(gl_func_l, feat['func'])
        if key == g_settings['version']:
            break
    return (gl_spec)


def GLFeat_filterEnum(enum_l, source_l):
    result: list = []

    for item in source_l:
        if item in enum_l.keys():
            result.append((item, enum_l[item]))
    return (result)


def GLFeat_filterFunc(func_l, source_l):
    result: list = []

    for item in source_l:
        if item in func_l.keys():
            result.append((item, func_l[item]))
    return (result)


# SECTION: Types
# # # # # # # # #

def GLTypes_parse(gl_type_l: dict):
    # specification:
    # ['name'] : { typedef declaration }
    gl_types: dict = {}

    for types in gl_type_l:
        for type in types:
            if type.text and 'typedef' in type.text:
                element: str = type.text
                key: str = None

                for child in type:
                    if child.tag == 'name':
                        key = child.text
                        element += key
                    elif child.tag == 'apientry':
                        element += 'APIENTRY '
                    if child.tail:
                        element += child.tail.strip()
                element = re.sub(r'\s+', ' ', element).strip()
                if not element.endswith(';'):
                    element += ';'
                if key:
                    gl_types[key] = element
    return (gl_types)


def GLTypes_parseElement(type):
    element: str = type.text.strip()

    for child in type:
        if child.tag == 'name':
            element += child.text.strip()
        elif child.tag == 'apientry':
            element += 'APIENTRY'
        if child.tail:
            element += child.tail.strip()
    if not element.endswith(';'):
        element += ';'
    return (element)


# SECTION: Enums
# # # # # # # # #

def GLEnum_parse(gl_enum_l: dict):
    # specification:
    # ['name'] : { value }
    gl_enums: dict = {}

    for enums in gl_enum_l:
        for enum in enums:
            try:
                gl_enums[enum.attrib['name']] = enum.attrib['value']
            except KeyError:
                pass
    return (gl_enums)


# SECTION: Functions
# # # # # # # # # # #

def GLFunc_parse(gl_func_l: dict):
    # specification:
    # ['name'] : {
    #   ['type'] : { return type },
    #   ['params'] : {
    #       ['name'] : { type },
    #   }
    # }
    gl_func: dict = {}

    for cmds in gl_func_l:
        for cmd in cmds:
            name = GLFunc_parseName(cmd.find('proto'))
            type = GLFunc_parseType(cmd.find('proto'))
            params = GLFunc_parseParams(cmd.findall('param'))

            gl_func[name] = {'type': type, 'params': params}
    return (gl_func)


def GLFunc_parseName(proto):
    for child in proto:
        if child.tag == 'name':
            return (child.text.strip())
    return (None)


def GLFunc_parseType(proto):
    if not proto.text:
        for child in proto:
            if child.tag == 'ptype':
                return (child.text.strip())
    return (proto.text.strip())


def GLFunc_parseParams(params: list):
    # specification:
    # ['name'] : { type }
    result: dict = {}

    for param in params:
        type: str = param.text
        name: str = None

        for child in param:
            if child.tag == 'ptype':
                type = child.text
            elif child.tag == 'name':
                name = child.text
        result[name] = type
    return (result)


# SECTION: Entrypoint
# # # # # # # # # # #

def loge(msg: str):
    print('{file}: {msg}'.format(file=os.path.basename(__file__), msg=msg))


# SECTION: Entrypoint
# # # # # # # # # # #

if __name__ == '__main__':
    # STEP 1.: Option process
    # # # # # # # # # # # # #
    GenGL_getopt()

    # STEP 2.: Spec. loading
    # # # # # # # # # # # # #
    gl_spec: list = GLSpec_parse()
    print(gl_spec)

    # STEP 3.: File creation
    # # # # # # # # # # # # #
    f_name: str = 'glapi.h'
    with open(f_name, 'w') as f:
        pass
