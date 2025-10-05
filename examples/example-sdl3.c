#include <SDL3/SDL.h>
#include <SDL3/SDL_events.h>
#include <SDL3/SDL_init.h>
#include <SDL3/SDL_video.h>

#define GLAPI_IMPLEMENTATION
#include "./../glapi.h"

static int      g_exit = 0;
static void    *g_window = 0,
               *g_context = 0;

int main(void) {
    if (!SDL_Init(SDL_INIT_VIDEO)) {
        return (1);
    }

    g_window = SDL_CreateWindow("SDL3 - hello, glapi.h!", 800, 600, SDL_WINDOW_OPENGL);
    if (!g_window) {
        SDL_Quit();
        return (1);
    }

    g_context = SDL_GL_CreateContext(g_window);
    if (!g_context) {
        SDL_DestroyWindow(g_window), g_window = 0;
        SDL_Quit();
        return (1);
    }

    if (!SDL_GL_MakeCurrent(g_window, g_context)) {
        SDL_GL_DestroyContext(g_context), g_context = 0;
        SDL_DestroyWindow(g_window), g_window = 0;
        SDL_Quit();
        return (1);
    }

    if (!glapiLoadGLLoader((glapiLoadProc_t) SDL_GL_GetProcAddress)) {
        SDL_GL_DestroyContext(g_context), g_context = 0;
        SDL_DestroyWindow(g_window), g_window = 0;
        SDL_Quit();
        return (1);
    }

    glViewport(0, 0, 800, 600);
    do {
        SDL_Event   event;

        glClearColor(0.1, 0.1, 0.1, 1.0);
        glClear(GL_COLOR_BUFFER_BIT);
        SDL_GL_SwapWindow(g_window);

        while (SDL_PollEvent(&event)) {
            switch (event.type) {
                case (SDL_EVENT_QUIT): {
                    goto exit;
                } break;

                case (SDL_EVENT_WINDOW_RESIZED): {
                    glViewport(0, 0, event.window.data1, event.window.data2);
                } break;
            }
        }
    } while (!g_exit);
   
exit:

    glapiUnloadGL();
    SDL_GL_DestroyContext(g_context), g_context = 0;
    SDL_DestroyWindow(g_window), g_window = 0;
    SDL_Quit();
    return (1);
}
