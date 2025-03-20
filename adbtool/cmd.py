import os
import platform
import shlex
import subprocess
import sys
import asyncio

from semantic_version import Version

from .errors import raise_error


# return (output, isOk)
def call(cmd: str, printOutput: bool = False) -> tuple[str, bool]:
    # print(f"{printOutput = }, {cmd = }")
    if sys.platform == "win32":
        args = cmd
    else:
        # linux must split arguments
        args = shlex.split(cmd)
    try:
        if printOutput:
            isOk = subprocess.call(args) == 0
            return "", isOk

        data = subprocess.check_output(args)
        # python3 output is bytes
        output = data.decode("utf-8")
        return output, True
    except subprocess.CalledProcessError as callerr:
        print(f"cmd = {cmd}, callerr.output = {callerr.output}", file=sys.stderr)
        return (callerr.output, False)
    except IOError as ioerr:
        print(f"cmd = {cmd}, ioerr = {ioerr}", file=sys.stderr)
        return "", False


async def call_async(cmd: str, printOutput: bool = False) -> tuple[str, bool]:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    isOk = proc.returncode == 0

    output = ""
    if stdout:
        output = stdout.decode("utf-8")
    if printOutput:
        if output:
            print(output)
        if stderr:
            print(stderr.decode("utf-8"))
    return output, isOk


def getAdb() -> str:
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK_ROOT")
    if androidHome is None:
        # print('can not found ANDROID_HOME/ANDROID_SDK in environment value')
        return "adb"

    return os.path.join(androidHome, "platform-tools/adb")


def getAapt() -> str:
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK_ROOT")
    if androidHome is None:
        print("can not found ANDROID_HOME/ANDROID_SDK in environment value")
        return "aapt"

    aaptname = "aapt.exe" if sys.platform == "win32" else "aapt"

    buildtools = os.path.join(androidHome, "build-tools")
    if os.path.isdir(buildtools):
        vers = list(map(lambda v: Version(v), os.listdir(buildtools)))
        vers.sort(reverse=True)
        for ver in vers:
            filename = os.path.join(buildtools, str(ver), aaptname)
            if os.path.isfile(filename):
                return filename

    raise_error("can not found aapt in ANDROID_HOME/ANDROID_SDK")


def getZipalign() -> str:
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK_ROOT")
    if androidHome is None:
        print("can not found ANDROID_HOME/ANDROID_SDK in environment value")
        return "zipalign"

    # aaptname = "apksigner.bat" if sys.platform == "win32" else "apksigner.bat"
    aaptname = "zipalign.exe"

    buildtools = os.path.join(androidHome, "build-tools")
    if os.path.isdir(buildtools):
        vers = list(map(lambda v: Version(v), os.listdir(buildtools)))
        vers.sort(reverse=True)
        for ver in vers:
            filename = os.path.join(buildtools, str(ver), aaptname)
            if os.path.isfile(filename):
                return filename

    raise_error("can not found aapt in ANDROID_HOME/ANDROID_SDK")


def getApksigner() -> str:
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK_ROOT")
    if androidHome is None:
        print("can not found ANDROID_HOME/ANDROID_SDK in environment value")
        return "apksigner"

    # aaptname = "apksigner.bat" if sys.platform == "win32" else "apksigner.bat"
    aaptname = "apksigner.bat"

    buildtools = os.path.join(androidHome, "build-tools")
    if os.path.isdir(buildtools):
        vers = list(map(lambda v: Version(v), os.listdir(buildtools)))
        vers.sort(reverse=True)
        for ver in vers:
            filename = os.path.join(buildtools, str(ver), aaptname)
            if os.path.isfile(filename):
                return filename

    raise_error("can not found aapt in ANDROID_HOME/ANDROID_SDK")

def get_objdump() -> str:
    androidHome = os.getenv("ANDROID_HOME")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK")
    if androidHome is None:
        androidHome = os.getenv("ANDROID_SDK_ROOT")
    if androidHome is None:
        print("can not found ANDROID_HOME/ANDROID_SDK in environment value")
        return "objdump"

    exename = "toolchains/llvm/prebuilt/windows-x86_64/bin/llvm-objdump.exe"
    # C:\Users\Admin\AppData\Local\Android\Sdk\ndk\23.1.7779620\toolchains\llvm\prebuilt\windows-x86_64\bin\llvm-objdump.exe
    buildtools = os.path.join(androidHome, "ndk")
    if os.path.isdir(buildtools):
        vers = list(map(lambda v: Version(v), os.listdir(buildtools)))
        vers.sort(reverse=True)
        for ver in vers:
            filename = os.path.join(buildtools, str(ver), exename)
            if os.path.isfile(filename):
                return filename


    raise_error("can not found aapt in ANDROID_HOME/ANDROID_SDK")

def get_unity_editor_dir(editor_dir: str) -> str:
    def is_editor_dir(dir):
        if dir is None:
            return False
        if os.path.isdir(dir):
            current_platform = platform.system()
            if current_platform == "Windows" and os.path.isfile(f"{dir}/Unity.exe"):
                return True
            if current_platform == "Darwin" and os.path.basename(dir) == "Unity.app":
                return True
        return False

    if is_editor_dir(editor_dir):
        return editor_dir
    editor_dir = os.getenv("UNITY_EDITOR_ROOT") or ""
    if is_editor_dir(editor_dir):
        return editor_dir
    raise_error("can not found unity editor")


def get_unity_binary2text(unity_editor_dir):
    current_platform = platform.system()
    if current_platform == "Windows":
        return os.path.join(get_unity_editor_dir(unity_editor_dir), "Data/Tools/binary2text")
    if current_platform == "Darwin":
        return os.path.join(get_unity_editor_dir(unity_editor_dir), "Contents/Tools/binary2text")
    
    raise_error("unsupport platform")


def get_unity_webextract(unity_editor_dir):
    current_platform = platform.system()
    if current_platform == "Windows":
        return os.path.join(get_unity_editor_dir(unity_editor_dir), "Data/Tools/WebExtract")
    if current_platform == "Darwin":
        return os.path.join(get_unity_editor_dir(unity_editor_dir), "Contents/Tools/WebExtract")
    
    raise_error("unsupport platform")

def get_malioc():
    malioc = os.getenv("MALIOC")
    if malioc is not None and os.path.isfile(malioc):
        return malioc

    ARM_DIR = r"C:/Program Files/Arm"
    if not os.path.isdir(ARM_DIR):
        raise_error(f"can not found {ARM_DIR}")

    for folder in os.listdir(ARM_DIR):
        fullname = os.path.join(ARM_DIR, folder, "mali_offline_compiler/malioc.exe")
        if os.path.isfile(fullname):
            return fullname
    raise_error("can not found malioc.exe")
