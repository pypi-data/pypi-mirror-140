import enum


class mode(enum.Enum):
    PRINT_DEPS_VSDOWNLOAD = enum.auto()
    PRINT_REV_DEPS_VSDOWNLOAD = enum.auto()
    PRINT_SEL_PKGS_VSDOWNLOAD = enum.auto()
    PRINT_SEL_PKGS_RAW = enum.auto()
    PRINT_SEL_PKGS_TRAITS = enum.auto()
    DOWNLOAD_AND_UNPACK = enum.auto()
    CHECK_FILES = enum.auto()
    PARSE_OUT_FILES_PER_PKG = enum.auto()
    PARSE_OUT_PKGS_PER_FILEPATTERN = enum.auto()
    PARSE_OUT_URLS_PER_FILEPATTERN = enum.auto()
    PARSE_OUT_EMBEDDED_CABS = enum.auto()
    PARSE_OUT_ERRORS_PER_PKG = enum.auto()


class retry(enum.Enum):
    FALSE = enum.auto()
    RETRY = enum.auto()
    RETRY_FAILED = enum.auto()
