cmake_minimum_required(VERSION 2.8.12)
project(orik)

# hack: fix should be in upstream c4
include_directories(lib/c4/src/libc4/include)

add_subdirectory(lib/c4)
