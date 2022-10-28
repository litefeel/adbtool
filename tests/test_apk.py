import pytest
from pytest import raises
from adbtool import adbtool


# def test_default():
#     _assert_success("apk")

APK_INFO = """package: name='com.litefeel.adbtoolapk' versionCode='1' versionName='1.0' platformBuildVersionName='7.1.1' platformBuildVersionCode='25'
sdkVersion:'15'
targetSdkVersion:'25'
application-label:'adbtoolapk'
application-label-af:'adbtoolapk'
application-label-am:'adbtoolapk'
application-label-ar:'adbtoolapk'
application-label-az-AZ:'adbtoolapk'
application-label-be-BY:'adbtoolapk'
application-label-bg:'adbtoolapk'
application-label-bn-BD:'adbtoolapk'
application-label-bs-BA:'adbtoolapk'
application-label-ca:'adbtoolapk'
application-label-cs:'adbtoolapk'
application-label-da:'adbtoolapk'
application-label-de:'adbtoolapk'
application-label-el:'adbtoolapk'
application-label-en-AU:'adbtoolapk'
application-label-en-GB:'adbtoolapk'
application-label-en-IN:'adbtoolapk'
application-label-es:'adbtoolapk'
application-label-es-US:'adbtoolapk'
application-label-et-EE:'adbtoolapk'
application-label-eu-ES:'adbtoolapk'
application-label-fa:'adbtoolapk'
application-label-fi:'adbtoolapk'
application-label-fr:'adbtoolapk'
application-label-fr-CA:'adbtoolapk'
application-label-gl-ES:'adbtoolapk'
application-label-gu-IN:'adbtoolapk'
application-label-hi:'adbtoolapk'
application-label-hr:'adbtoolapk'
application-label-hu:'adbtoolapk'
application-label-hy-AM:'adbtoolapk'
application-label-in:'adbtoolapk'
application-label-is-IS:'adbtoolapk'
application-label-it:'adbtoolapk'
application-label-iw:'adbtoolapk'
application-label-ja:'adbtoolapk'
application-label-ka-GE:'adbtoolapk'
application-label-kk-KZ:'adbtoolapk'
application-label-km-KH:'adbtoolapk'
application-label-kn-IN:'adbtoolapk'
application-label-ko:'adbtoolapk'
application-label-ky-KG:'adbtoolapk'
application-label-lo-LA:'adbtoolapk'
application-label-lt:'adbtoolapk'
application-label-lv:'adbtoolapk'
application-label-mk-MK:'adbtoolapk'
application-label-ml-IN:'adbtoolapk'
application-label-mn-MN:'adbtoolapk'
application-label-mr-IN:'adbtoolapk'
application-label-ms-MY:'adbtoolapk'
application-label-my-MM:'adbtoolapk'
application-label-nb:'adbtoolapk'
application-label-ne-NP:'adbtoolapk'
application-label-nl:'adbtoolapk'
application-label-pa-IN:'adbtoolapk'
application-label-pl:'adbtoolapk'
application-label-pt:'adbtoolapk'
application-label-pt-BR:'adbtoolapk'
application-label-pt-PT:'adbtoolapk'
application-label-ro:'adbtoolapk'
application-label-ru:'adbtoolapk'
application-label-si-LK:'adbtoolapk'
application-label-sk:'adbtoolapk'
application-label-sl:'adbtoolapk'
application-label-sq-AL:'adbtoolapk'
application-label-sr:'adbtoolapk'
application-label-sr-Latn:'adbtoolapk'
application-label-sv:'adbtoolapk'
application-label-sw:'adbtoolapk'
application-label-ta-IN:'adbtoolapk'
application-label-te-IN:'adbtoolapk'
application-label-th:'adbtoolapk'
application-label-tl:'adbtoolapk'
application-label-tr:'adbtoolapk'
application-label-uk:'adbtoolapk'
application-label-ur-PK:'adbtoolapk'
application-label-uz-UZ:'adbtoolapk'
application-label-vi:'adbtoolapk'
application-label-zh-CN:'adbtoolapk'
application-label-zh-HK:'adbtoolapk'
application-label-zh-TW:'adbtoolapk'
application-label-zu:'adbtoolapk'
application-icon-160:'res/mipmap-mdpi-v4/ic_launcher.png'
application-icon-240:'res/mipmap-hdpi-v4/ic_launcher.png'
application-icon-320:'res/mipmap-xhdpi-v4/ic_launcher.png'
application-icon-480:'res/mipmap-xxhdpi-v4/ic_launcher.png'
application-icon-640:'res/mipmap-xxxhdpi-v4/ic_launcher.png'
application: label='adbtoolapk' icon='res/mipmap-mdpi-v4/ic_launcher.png'
application-debuggable
launchable-activity: name='com.litefeel.adbtoolapk.MainActivity'  label='' icon=''
feature-group: label=''
  uses-feature: name='android.hardware.faketouch'
  uses-implied-feature: name='android.hardware.faketouch' reason='default feature for all apps'
main
supports-screens: 'small' 'normal' 'large' 'xlarge'
supports-any-density: 'true'
locales: '--_--' 'af' 'am' 'ar' 'az-AZ' 'be-BY' 'bg' 'bn-BD' 'bs-BA' 'ca' 'cs' 'da' 'de' 'el' 'en-AU' 'en-GB' 'en-IN' 'es' 'es-US' 'et-EE' 'eu-ES' 'fa' 'fi' 'fr' 'fr-CA' 'gl-ES' 'gu-IN' 'hi' 'hr' 'hu' 'hy-AM' 'in' 'is-IS' 'it' 'iw' 'ja' 'ka-GE' 'kk-KZ' 'km-KH' 'kn-IN' 'ko' 'ky-KG' 'lo-LA' 'lt' 'lv' 'mk-MK' 'ml-IN' 'mn-MN' 'mr-IN' 'ms-MY' 'my-MM' 'nb' 'ne-NP' 'nl' 'pa-IN' 'pl' 'pt' 'pt-BR' 'pt-PT' 'ro' 'ru' 'si-LK' 'sk' 'sl' 'sq-AL' 'sr' 'sr-Latn' 'sv' 'sw' 'ta-IN' 'te-IN' 'th' 'tl' 'tr' 'uk' 'ur-PK' 'uz-UZ' 'vi' 'zh-CN' 'zh-HK' 'zh-TW' 'zu'
densities: '160' '240' '320' '480' '640'"""


def test_apkinfo(capsys):
    adbtool.main(["apk", "./test/adbtooltest.apk"])
    captured = capsys.readouterr()
    out:str = captured.out
    out = out.strip().replace('\r\n', '\n')
    assert out == APK_INFO
    assert captured.err == ""


def test_missing_path(capsys):
    with pytest.raises(SystemExit, match="Missing parameter: apkpath"):
        adbtool.main(["apk"])
