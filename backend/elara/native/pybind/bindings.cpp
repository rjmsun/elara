#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>

namespace py = pybind11;

// Simple hello world function to test the build pipeline
std::string hello_world() {
    return "Hello from C++! Elara native module is working.";
}

// Module definition
PYBIND11_MODULE(elara_native, m) {
    m.doc() = "Elara native C++ extensions for high-performance poker analysis";
    
    m.def("hello_world", &hello_world, "A simple test function to verify the build pipeline");
} 