INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_IONO iono)

FIND_PATH(
    IONO_INCLUDE_DIRS
    NAMES iono/api.h
    HINTS $ENV{IONO_DIR}/include
        ${PC_IONO_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    IONO_LIBRARIES
    NAMES gnuradio-iono
    HINTS $ENV{IONO_DIR}/lib
        ${PC_IONO_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/ionoTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(IONO DEFAULT_MSG IONO_LIBRARIES IONO_INCLUDE_DIRS)
MARK_AS_ADVANCED(IONO_LIBRARIES IONO_INCLUDE_DIRS)
