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
        GenGL_loge(err)

    for opt, arg in opts:
        if opt in ('-v', '--version'):
            if arg in g_gl_version:
                g_settings['version'] = arg
                continue

            # fail state...
            GenGL_loge('invalid version: {}'.format(arg))

        if opt in ('-p', '--profile'):
            if arg in g_gl_profile:
                g_settings['profile'] = arg
                continue

            # fail state...
            GenGL_loge('invalid profile: {}'.format(arg))

        if opt in ('-s', '--source'):
            if os.path.exists(arg):
                if os.path.basename(arg) == 'gl.xml':
                    g_settings['profile'] = arg
                    continue
                else:
                    GenGL_loge('invalid file: {}'.format(arg))
            else:
                GenGL_loge('argument isn\'t a valid path: {}'.format(arg))

        if opt in ('-h', '--help'):
            print('help')
            sys.exit(0)


# SECTION: Parser
# # # # # # # # #

class GLSpec:
    # Private variables
    # # # # # # # # # #
    _xml_file: ET.ElementTree = None
    _gl_feat_l: list = []
    _gles1_feat_l: list = []
    _gles2_feat_l: list = []
    _gl_type_l: list = []
    _gl_enum_l: dict = {}
    _gl_func_l: dict = {}

    # Public variables
    # # # # # # # # # #
    types: dict = {}
    enums: dict = {}
    functions: dict = {}

    def __init__(self):
        # opening an XML specification file
        try:
            tree = ET.parse(g_settings['source'])
        except FileNotFoundError as err:
            print(err)
        root = tree.getroot()

        # parsing types, enums and fuctions...
        self._gl_type_l = self.__parseTypes(root)
        self._gl_enum_l = self.__parseEnum(root)
        self._gl_func_l = self.__parseFunc(root)

        # parsing the feature lists...
        # NOTE(yakub):
        #  We're parsing OpenGL and OpenGL ES from the xml file
        self._gl_feat_l = self.__parseFeatures(root, 'gl')
        self._gles1_feat_l = self.__parseFeatures(root, 'gles1')
        self._gles2_feat_l = self.__parseFeatures(root, 'gles2')
        self.__filterFeatures(self._gl_feat_l)
        self.__filterFeatures(self._gles1_feat_l)
        self.__filterFeatures(self._gles2_feat_l)

    # SECTION: Features
    # # # # # # # # # #

    def __parseFeatures(self, root, api):
        # specification:
        # ['number'] : {
        #   ['name'] : { version name },
        #   ['type'] : { list of types },
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
        self.types = self._gl_type_l
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

    # SECTION: Types
    # # # # # # # # #

    def __parseTypes(self, root):
        gl_types: list = []
        gl_type_l: dict = root.findall('types')

        for types in gl_type_l:
            for type in types:
                if type.text and 'typedef' in type.text:
                    element: str = type.text

                    for child in type:
                        if child.tag == 'name':
                            element += child.text
                        elif child.tag == 'apientry':
                            element += 'APIENTRY '
                        if child.tail:
                            element += child.tail.strip()
                    element = re.sub(r'\s+', ' ', element).strip()
                    if not element.endswith(';'):
                        element += ';'

                    gl_types.append(element)
        return (gl_types)

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


# SECTION: Utilities
# # # # # # # # # # #

def GenGL_loge(msg: str):
    print('{file}: {msg}'.format(file=os.path.basename(__file__), msg=msg))
    sys.exit(1)


# SECTION: Entrypoint
# # # # # # # # # # #

if __name__ == '__main__':
    # STEP 1.: Option process
    # # # # # # # # # # # # #
    GenGL_getopt()

    # STEP 2.: Spec. loading
    # # # # # # # # # # # # #
    gl_spec: GLSpec = GLSpec()

    # STEP 3.: File creation
    # # # # # # # # # # # # #
    f_name: str = 'glapi.h'
    with open(f_name, 'w') as f:
        pass
