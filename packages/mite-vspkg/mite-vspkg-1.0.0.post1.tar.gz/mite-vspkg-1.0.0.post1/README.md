# mite-vspkg

A utility to get a list of files per Visual Studio installer package and to unpack Visual Studio installer packages.<br>
Uses manifests of Visual Studio installer to get a list of available Visual Studio packages.<br>
Supported formats: `.msi`, `.vsix`, `.zip`.


## Features

- Check files of the selected packages.

  Download all payloads of a package, check its files, keep the list of filenames, delete downloaded payloads to conserve space. Once all packages are checked, save the result in `.json`.

  Then `mite-vspkg` can be used to get useful info from the resulting `.json` :
  - print a list of filenames per payload (with URLs) per package,
  - print packages per filename regex,
  - print URLs per payload per filename regex.

  Intermediate results are saved after downloading certain amount of bytes so the operation can be resumed if suddenly interrupted.

  Only `.msi`, `.vsix`, `.zip` are downloaded, `.cab` are skipped.

- Download and unpack files from the selected packages.

  If resumed, downloaded payloads are not redownloaded. Hashes of the downloaded payloads are compared with hashes in the installer manifest to remove corrupted payloads.

  Only `.msi`, `.vsix`, `.zip`, `.cab` are downloaded.


## Requirements

1. `python 3.7+`

2. `msitools 0.98+` and `libgcab 1.2+`<br>
`msitools` doesn't work on Windows. <https://gitlab.gnome.org/GNOME/msitools#notes>

`mite-vspkg` was tested on Linux only.


## Installation

This command should install the program on Unix/macOS.<br>
`python3 -m pip install mite_vspkg`

If it doesn't work, see this <https://packaging.python.org/en/latest/tutorials/installing-packages/>


## Usage

The options are loaded from the configuration file in the `config` folder of a `--work-dir` .<br>
By default, the name of the config is `config.py` . Alternative config name can be specified with `--config-name` option.


## Example

This command will copy the default config to `$HOME/mite-vspkg/config/config.py` and execute the program using that config.<br>
By default, the program will download and cache the manifests and print the list of all packages.<br>
`python3 -m mite_vspkg --work-dir="$HOME/mite-vspkg"`

After executing the command, the options can be changed by editing the `$HOME/mite-vspkg/config/config.py` .<br>
If the user scrolls to the bottom of the `config.py` ,<br>
comments<br>
`mode = util_enum.mode.PRINT_SEL_PKGS_VSDOWNLOAD`<br>
uncomments<br>
`#mode = util_enum.mode.CHECK_FILES`<br>
saves the changes,<br>
then executes the same command<br>
`python3 -m mite_vspkg --work-dir="$HOME/mite-vspkg"`<br>
the program will download-check-delete every package and store lists of filenames and `.cab` info in `$HOME/mite-vspkg/check_files/out/out_file.json` .


## Notes

`util_enum.mode.CHECK_FILES`<br>
If there is a partially filled output `.json`, selected packages are ignored and the program tries to finish the interrupted check.<br>
If there is a fully filled output `.json`, the program creates a backup of this `.json` and then tries to check the selected packages.

`util_enum.mode.DOWNLOAD_AND_UNPACK`<br>
After unpacking, filenames are unquoted, i.e. `%xx` escapes are replaced with their single-character equivalent, e.g. `%20` is replaced by space `" "`, `%2B` is replaced by plus `"+"`.

When the program prints a list of packages, there are 3 architectures after the package type.<br>
Example: `Microsoft.VisualStudio.Debugger.Concord.Remote (Vsix) (x64; ARM64; neutral) (3.3 MB; 3.3 MB; 9.8 MB)`<br>
Those are: `chip`, `machineArch`, `productArch`.

When the program prints a list of packages, there are 3 sizes at the end.<br>
Example: `Microsoft.Icecap.Collection.Msi (Msi) (64.0 KB; 1.9 MB; 5.0 MB)`
1. Download size to get list of filenames and `.cab` info from the package, i.e. size of `.msi`, `.vsix`, `.zip` payloads.
2. Download size to unpack the package, i.e. size of `.msi`, `.vsix`, `.zip`, `.cab` payloads.
3. Install size of the package. The program doesn't install the packages and doesn't unpack some file types, so the real unpack size is likely different from the install size.

When the program prints a list of payloads, there are 2 sizes near the payload name.<br>
Example: `SDK Debuggers-x86_en-us.msi (636.0 KB; 138.1 MB)`
1. Size of the payload.
2. Size of the payload, plus size of required `.cab` payloads, plus size of `.msi` payloads which have the required `.cab` files. The program counts an `.msi` only if it has a `.cab` which is not available for download as a payload. If multiple `.msi` have the required `.cab` files, the most lightweight combination is counted.

By default, dependencies of the selected packages are also selected. Dependency resolution can be turned off by setting `"skip_dependencies"` to `True` in the config.


## Acknowledgments

The program contains a modified version of `vsdownload.py` from <https://github.com/mstorsjo/msvc-wine> (ISC license).
