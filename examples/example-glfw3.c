#define GLAPI_IMPLEMENTATION
#include "./../glapi.h"

#include <GLFW/glfw3.h>


int main(void) {
    void    *window;

    glfwInit();
    window = glfwCreateWindow(800, 600, "glapi 1.0 - glfw 3.4 - hello, glapi!", 0, 0);
    if (!window) {
        return (1);
    }
    glfwMakeContextCurrent(window);

    if (!glapiLoadGL()) {
        glfwTerminate();
        return (1);
    }

    glViewport(0, 0, 800, 600);
    glClear(GL_COLOR_BUFFER_BIT);
    glClearColor(0.2, 0.2, 0.2, 1.0);
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        glfwSwapBuffers(window);
    }

    glfwTerminate();
}
