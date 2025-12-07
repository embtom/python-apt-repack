cmake_minimum_required(VERSION 3.15)
list(
    APPEND
    CMAKE_MODULE_PATH
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

# Require a modern-enough standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(
    Python3
    COMPONENTS Interpreter Development
    REQUIRED)

find_package(AptPkg REQUIRED)

# -Wall -Wextra
set(COMMON_COMPILE_FLAGS -Wno-write-strings)

set(COMMON_COMPILE_DEFS
    PY_SSIZE_T_CLEAN
    APT_8_CLEANER_HEADERS
    APT_9_CLEANER_HEADERS
    APT_10_CLEANER_HEADERS)

message(STATUS "CMAKE_BUILD_TYPE        : ${CMAKE_BUILD_TYPE}")
message(STATUS "Python3_EXECUTABLE      : ${Python3_EXECUTABLE}")
message(STATUS "Python3_VERSION         : ${Python3_VERSION}")
message(STATUS "Python3_INCLUDE_DIRS    : ${Python3_INCLUDE_DIRS}")
message(STATUS "Python3_SITEARCH        : ${Python3_SITEARCH}")
message(STATUS "Python3_SITELIB         : ${Python3_SITELIB}")
message(STATUS "SKBUILD_PROJECT_VERSION : ${SKBUILD_PROJECT_VERSION_FULL}")
message(STATUS "SKBUILD_PROJECT_NAME    : ${SKBUILD_PROJECT_NAME}")
message(STATUS "SKBUILD_SOABI           : ${SKBUILD_SOABI}")

# ------------------------------------------------------------------------------
# apt_pkg
# ------------------------------------------------------------------------------
set(APT_PKG_SRCS
    python/apt_pkgmodule.cc
    python/acquire.cc
    python/cache.cc
    python/cdrom.cc
    python/configuration.cc
    python/depcache.cc
    python/generic.cc
    python/hashes.cc
    python/hashstring.cc
    python/indexfile.cc
    python/metaindex.cc
    python/pkgmanager.cc
    python/pkgmanagerprogress.cc
    python/pkgrecords.cc
    python/pkgsrcrecords.cc
    python/policy.cc
    python/progress.cc
    python/sourcelist.cc
    python/string.cc
    python/tag.cc
    python/lock.cc
    python/acquire-item.cc
    python/python-apt-helpers.cc
    python/cachegroup.cc
    python/orderlist.cc
    python/hashstringlist.cc)

python3_add_library(
    apt_pkg
    MODULE
    ${APT_PKG_SRCS})

set_target_properties(apt_pkg PROPERTIES SUFFIX ".${SKBUILD_SOABI}${CMAKE_SHARED_MODULE_SUFFIX}")

target_compile_options(apt_pkg PRIVATE ${COMMON_COMPILE_FLAGS})
target_compile_definitions(apt_pkg PRIVATE ${COMMON_COMPILE_DEFS})

target_link_libraries(
    apt_pkg
    PRIVATE AptPkg::AptPkg
    PRIVATE stdc++)

# ------------------------------------------------------------------------------
# apt_inst (C++ extension)
# ------------------------------------------------------------------------------
set(APT_INST_SRCS
    python/apt_instmodule.cc
    python/generic.cc
    python/arfile.cc
    python/tarfile.cc)

python3_add_library(
    apt_inst
    MODULE
    ${APT_INST_SRCS})

target_compile_options(apt_inst PRIVATE ${COMMON_COMPILE_FLAGS})
target_compile_definitions(apt_inst PRIVATE ${COMMON_COMPILE_DEFS})
target_link_libraries(apt_inst PRIVATE AptPkg::AptPkg)

set_target_properties(apt_inst PROPERTIES SUFFIX ".${SKBUILD_SOABI}${CMAKE_SHARED_MODULE_SUFFIX}")

# ##################################################################################################

file(
    GLOB
    PO_FILES
    "${CMAKE_SOURCE_DIR}/po/*.po")
set(MO_FILES "")

foreach(po ${PO_FILES})
    get_filename_component(
        lang
        ${po}
        NAME_WE)

    set(mo "${CMAKE_BINARY_DIR}/locale/${lang}/LC_MESSAGES/python-apt.mo")

    add_custom_command(
        OUTPUT "${mo}"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_BINARY_DIR}/locale/${lang}/LC_MESSAGES"
        COMMAND msgfmt -o "${mo}" "${po}"
        DEPENDS "${po}"
        COMMENT "Compiling ${po} -> ${mo}"
        VERBATIM)

    list(
        APPEND
        MO_FILES
        "${mo}")

    install(FILES "${mo}" DESTINATION "share/locale/${lang}/LC_MESSAGES")
endforeach()

add_custom_target(generate_translations ALL DEPENDS ${MO_FILES})


set(INFO_IN_FILES
    ${CMAKE_SOURCE_DIR}/data/templates/debian.info.in
    ${CMAKE_SOURCE_DIR}/data/templates/ubuntu.info.in
    ${CMAKE_SOURCE_DIR}/data/templates/kali.info.in
    ${CMAKE_SOURCE_DIR}/data/templates/gnewsense.info.in
    ${CMAKE_SOURCE_DIR}/data/templates/blankon.info.in
)

set(MIRROR_FILES
    ${CMAKE_SOURCE_DIR}/data/templates/debian.mirrors
    ${CMAKE_SOURCE_DIR}/data/templates/ubuntu.mirrors
    ${CMAKE_SOURCE_DIR}/data/templates/kali.mirrors
    ${CMAKE_SOURCE_DIR}/data/templates/gnewsense.mirrors
    ${CMAKE_SOURCE_DIR}/data/templates/blankon.mirrors
)

set(GENERATED_FILES "")

# Rule for *.info.in → *.info
foreach(info_in ${INFO_IN_FILES})
    get_filename_component(
        fname
        "${info_in}"
        NAME_WE)
    set(outfile "${CMAKE_BINARY_DIR}/data/templates/${fname}.info")

    add_custom_command(
        OUTPUT "${outfile}"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_BINARY_DIR}/data/templates"
        COMMAND ${CMAKE_COMMAND} -DINPUT=${info_in} -DOUTPUT=${outfile} -P
                "${CMAKE_SOURCE_DIR}/cmake/strip_underscores.cmake"
        DEPENDS "${info_in}"
        COMMENT "Generating ${outfile}"
        VERBATIM)
    list(
        APPEND
        GENERATED_FILES
        "${outfile}")
endforeach()

# Rule for *.mirrors (just copy)
foreach(mfile ${MIRROR_FILES})
    get_filename_component(
        fname
        "${mfile}"
        NAME)
    set(outfile "${CMAKE_BINARY_DIR}/data/templates/${fname}")

    add_custom_command(
        OUTPUT "${outfile}"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_BINARY_DIR}/data/templates"
        COMMAND ${CMAKE_COMMAND} -E copy "${mfile}" "${outfile}"
        DEPENDS "${mfile}"
        COMMENT "Copying ${mfile}"
        VERBATIM)
    list(
        APPEND
        GENERATED_FILES
        "${outfile}")
endforeach()

add_custom_target(generate_templates ALL DEPENDS ${GENERATED_FILES})

# ------------------------------------------------------------------------------
# install
# ------------------------------------------------------------------------------
install(
    TARGETS apt_pkg
    LIBRARY DESTINATION .
    RUNTIME DESTINATION .)
install(
    TARGETS apt_inst
    LIBRARY DESTINATION .
    RUNTIME DESTINATION .)

install(
    FILES ${CMAKE_SOURCE_DIR}/typehinting/apt_inst.pyi
    DESTINATION apt_pkg-stubs
    RENAME __init__.pyi)

install(
    FILES ${CMAKE_SOURCE_DIR}/typehinting/apt_inst.pyi
    DESTINATION apt_inst-stubs
    RENAME __init__.pyi)

install(FILES ${GENERATED_FILES} DESTINATION share/python-apt/templates)
