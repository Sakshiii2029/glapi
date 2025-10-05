#define GLAPI_IMPLEMENTATION
#include "./../glapi.h"

#include <GLFW/glfw3.h>

static void *g_window;

int main(void) {
    if (!glfwInit()) {
        return (1);
    }

    g_window = glfwCreateWindow(800, 600, "glfw 3.4 - hello, glapi!", 0, 0);
    if (!g_window) {
        glfwTerminate();
        return (1);
    }

    glfwMakeContextCurrent(g_window);
    
    if (!glapiLoadGL()) {
        glfwTerminate();
        return (1);
    }

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
