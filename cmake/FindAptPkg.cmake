find_package(PkgConfig REQUIRED)
pkg_check_modules(PC_APT_PKG REQUIRED apt-pkg)

find_path(APT_PKG_INCLUDE_DIR
    NAMES apt-pkg/init.h
    PATHS ${PC_APT_PKG_INCLUDE_DIRS}
)

find_library(APT_PKG_LIBRARY
    NAMES apt-pkg
    PATHS ${PC_APT_PKG_LIBRARY_DIRS}
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(AptPkg
    REQUIRED_VARS APT_PKG_LIBRARY APT_PKG_INCLUDE_DIR
)

if(AptPkg_FOUND AND NOT TARGET AptPkg::AptPkg)
    add_library(AptPkg::AptPkg UNKNOWN IMPORTED)
    set_target_properties(AptPkg::AptPkg PROPERTIES
        IMPORTED_LOCATION "${APT_PKG_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${APT_PKG_INCLUDE_DIR}"
    )
endif()
