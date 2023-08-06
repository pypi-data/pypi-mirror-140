# Tests

TuxRun support some tests, each tests is supported on some but not all architectures.

!!! tip "Listing tests"
    You can list the supported tests with:
    ```shell
    tuxrun --list-tests
    ```

## FVP devices

Device              | Tests        | Parameters                       |
--------------------|--------------|----------------------------------|
fvp-morello-android | binder       |                                  |
fvp-morello-android | bionic       | GTEST_FILTER\* BIONIC_TEST_TYPE\*|
fvp-morello-android | boottest     |                                  |
fvp-morello-android | boringssl    | SYSTEM_URL                       |
fvp-morello-android | compartment  | USERDATA                         |
fvp-morello-android | device-tree  |                                  |
fvp-morello-android | dvfs         |                                  |
fvp-morello-android | libjpeg-turbo| LIBJPEG_TURBO_URL, SYSTEM_URL    |
fvp-morello-android | libpdfium    | PDFIUM_URL, SYSTEM_URL           |
fvp-morello-android | libpng       | PNG_URL, SYSTEM_URL              |
fvp-morello-android | lldb         | LLDB_URL, TC_URL                 |
fvp-morello-android | logd         | USERDATA                         |
fvp-morello-android | multicore    |                                  |
fvp-morello-android | zlib         | SYSTEM_URL                       |
fvp-morello-oe      | fwts         |                                  |

!!! tip "Passing parameters"
    In order to pass parameters, use `tuxrun --parameters USERDATA=http://.../userdata.tar.xz`

!!! tip "Default parameters"
    **GTEST_FILTER** is optional and defaults to
    ```
    string_nofortify.*-string_nofortify.strlcat_overread:string_nofortify.bcopy:string_nofortify.memmove
    ```
    **BIONIC_TEST_TYPE** is optional and defaults to `static`. Valid values are `dynamic` and `static`.

## QEMU devices

Device  | Tests               | Parameters           |
--------|---------------------|----------------------|
qemu-\* | command             |                      |
qemu-\* | kselftest-gpio      | CPUPOWER\* KSELFTEST |
qemu-\* | kselftest-ipc       | CPUPOWER\* KSELFTEST |
qemu-\* | kselftest-ir        | CPUPOWER\* KSELFTEST |
qemu-\* | kselftest-kcmp      | CPUPOWER\* KSELFTEST |
qemu-\* | kselftest-kexec     | CPUPOWER\* KSELFTEST |
qemu-\* | kselftest-rseq      | CPUPOWER\* KSELFTEST |
qemu-\* | kselftest-rtc       | CPUPOWER\* KSELFTEST |
qemu-\* | kunit\*             |                      |
qemu-\* | ltp-fcntl-locktests |                      |
qemu-\* | ltp-fs_bind         |                      |
qemu-\* | ltp-fs_perms_simple |                      |
qemu-\* | ltp-fsx             |                      |
qemu-\* | ltp-nptl            |                      |
qemu-\* | ltp-smoke           |                      |

!!! tip "Passing parameters"
    In order to pass parameters, use `tuxrun --parameters KSELFTEST=http://.../kselftes.tar.xz`

!!! warning "CPUPOWER"
    Parameter CPUPOWER is only used by *qemu-i386* and *qemu-x86_64*.

!!! warning "KUnit config"
    In order to run KUnit tests, the kernel should be compiled with
    ```
    CONFIG_KUNIT=m
    CONFIG_KUNIT_ALL_TESTS=m
    ```
    The **modules.tar.xz** should be given with `--modules https://.../modules.tar.xz`.
