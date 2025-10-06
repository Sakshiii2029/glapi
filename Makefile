# ========

MK_ROOT		= $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
MK_NAME		= glapi
SCRIPT		= $(MK_ROOT)$(MK_NAME).py
SFLAGS		= --input=$(GL_INPUT) --output=$(GL_OUTPUT) --version=$(GL_VERSION) --profile=$(GL_PROFILE)
TARGET		= $(MK_ROOT)$(MK_NAME).h

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
	mkdir /usr/local/include/glapi/
	cp -f $(TARGET) /usr/local/include/$(MK_NAME)/
	ln -s /usr/local/include/$(MK_NAME)/$(MK_NAME).h /usr/local/include/$(MK_NAME).h

.PHONY : remove

remove : clean
	rm -rf /usr/local/include/$(MK_NAME)
	rm -f /usr/local/include/$(MK_NAME).h

.PHONY : examples

examples : all
	make -C $(MK_ROOT)examples/

# ========
