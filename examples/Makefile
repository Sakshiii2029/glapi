# ========

MK_ROOT		= $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
MK_EXT		=
CC			= cc
CFLAGS		= -Wall -Wextra -Werror

ifeq ($(OS),Windows_NT)
	MK_EXT = .exe
else
	MK_EXT = .out
endif

# ========

E_SRCS		=
E_LFLAGS	=
E_TARGET0	= $(MK_ROOT)example-glfw3$(MK_EXT)
E_TARGET1	= $(MK_ROOT)example-sdl3$(MK_EXT)

# ========

.PHONY : all

all : example-glfw3 example-sdl3

.PHONY : clean

clean :
	rm -f $(E_TARGET0)
	rm -f $(E_TARGET1)

.PHONY : example-glfw3

example-glfw3 : E_SRCS = $(MK_ROOT)example-glfw3.c
example-glfw3 : E_LFLAGS = -lglfw3 -lm 
example-glfw3 : $(E_TARGET0)

.PHONY : example-sdl3

example-sdl3 : E_SRCS = $(MK_ROOT)example-sdl3.c
example-sdl3 : E_LFLAGS = -lSDL3
example-sdl3 : $(E_TARGET1) 

# ========

$(E_TARGET0) :
	$(CC) $(CFLAGS) -o $@ $(E_SRCS) $(E_LFLAGS)

$(E_TARGET1) :
	$(CC) $(CFLAGS) -o $@ $(E_SRCS) $(E_LFLAGS)

# ========
