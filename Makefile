# ========

MK_ROOT		= $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
SCRIPT		= $(MK_ROOT)glapi.py
SFLAGS		= --input=$(GL_INPUT) --output=$(GL_OUTPUT) --version=$(GL_VERSION) --profile=$(GL_PROFILE)
TARGET		= $(MK_ROOT)glapi.h

# ========

GL_INPUT	= $(MK_ROOT)OpenGL-Registry/xml/gl.xml
GL_OUTPUT	= $(MK_ROOT)
GL_PROFILE	= core
GL_VERSION	= 4.6

# ========

$(TARGET) :
	python3 $(SCRIPT) $(SFLAGS)

# ========

.PHONY : all

all : $(TARGET)

.PHONY : clean

clean :
	make -C $(MK_ROOT)examples/ clean
	rm -f $(TARGET)

.PHONY : install

install : all
	cp -f $(TARGET) /usr/local/include

.PHONY : remove

remove : clean
	rm -f /usr/local/include/$(TARGET)

.PHONY : examples

examples : all
	make -C $(MK_ROOT)examples/

# ========
