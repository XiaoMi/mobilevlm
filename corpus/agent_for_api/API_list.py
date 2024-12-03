#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
usr_api_list = '''
The following api list will be listed in this format: ADB Command - Function Description - Parameter Information
------------
api list:
{
    {
      "ADB Command": "adb shell am start -n com.miui.calculator/.cal.CalculatorActivity",
      "Function Description": "启动计算器主界面",
      "Parameter Information": "No additional parameters required."
    },
    {
      "ADB Command": "adb shell am start -a com.miui.calculator.action.SCIENTIFIC_MODE",
      "Function Description": "启动科学计算器模式",
      "Parameter Information": "No additional parameters required."
    },
    {
      "ADB Command": "adb shell am start -n com.miui.calculator/.convert.CurrencyActivity",
      "Function Description": "打开货币转换功能",
      "Parameter Information": "No additional parameters required."
    },
    {
      "ADB Command": "adb shell am start -a com.miui.calculator.action.TAX",
      "Function Description": "打开房贷计算器",
      "Parameter Information": "No additional parameters required."
    },
    {
      "ADB Command": "adb shell am start -a com.miui.calculator.action.MORTGAGE",
      "Function Description": "打开税务计算器",
      "Parameter Information": "No additional parameters required."
    }   
}
'''
usr_api_list_1 = '''

The following api list will be listed in this format: ADB Command - Function Description - Parameter Information
If the current step is completed and you need to return, you should give priority to return to the previous step/return to the main interface in the adb command.

api list:
------------
ADB Command: adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
Function Description: Launches the home screen.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -n com.traveloka.android/.appentry.splash.SplashActivity
Function Description: Open the traveloka app
Parameter Information: No additional parameters required.

ADB Command: adb shell input keyevent KEYCODE_HOME
Function Description: go to the home screen
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.SET_ALARM --ei android.intent.extra.alarm.HOUR <x> --ei android.intent.extra.alarm.MINUTES <y>
Function Description: Triggers an intent to open the alarm clock application with a pre-filled time for setting a new alarm.
Parameter Information: Replace <x> with the hour and <y> with the minutes for the alarm time. For example, for an alarm set at 7:15, <x> would be 7 and <y> would be 15.

ADB Command: adb shell am start -n com.channel.weather.forecast/com.mytools.weather.ui.home.MainActivity
Function Description: Open the weather app
Parameter Information: No additional parameters required.

ADB Command: adb shell input keyevent KEYCODE_BACK
Function Description: Return to previous page
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.WEB_SEARCH
Function Description: Open the Google Search app
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.settings.SETTINGS
Function Description: Opens the system settings.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.settings.WIRELESS_SETTINGS
Function Description: Opens wireless and network settings.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -d package:<package_name> -a android.settings.APPLICATION_DETAILS_SETTINGS
Function Description: Opens the application information page.
Parameter Information: <package_name> - Specific package name of the app.

ADB Command: adb shell am broadcast -a clipper.set -e text "<text_body>"
Function Description: Sends text to the clipboard.
Parameter Information: <text_body> - Text to be sent to the clipboard.

ADB Command: adb shell am start -n com.google.android.contacts/com.android.contacts.activities.PeopleActivity
Function Description: Opens the contacts app.
Parameter Information: Requires contact's URI.

ADB Command: adb shell am start -a android.intent.action.SENDTO -d sms:<phone_number> --es sms_body "<message_body>"
Function Description: Sends an SMS.
Parameter Information: <phone_number> - Recipient's phone number, <message_body> - SMS text.

ADB Command: adb shell am start -a android.intent.action.VIEW -d file://<file_path> -t <mime_type>
Function Description: Plays a multimedia file.
Parameter Information: <file_path> - URI of the file, <mime_type> - MIME type of the file.

ADB Command: adb shell am start -n com.google.android.GoogleCamera/com.android.camera.CameraLauncher
Function Description: Opens the camera.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.DIAL -d tel:<phone_number>
Function Description: Opens the dialer with a specific number.
Parameter Information: <phone_number> - Phone number to dial.

ADB Command: adb shell am start -a android.media.action.STILL_IMAGE_CAMERA
Function Description: Takes a photo and saves it.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.media.action.VIDEO_CAMERA
Function Description: Records a video.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.VIEW -d <http://www.example.com>
Function Description: Opens the browser and visits a web page.
Parameter Information: URL of the web page.

ADB Command: adb shell am start -a android.intent.action.VIEW -d geo:37.7749,-122.4194
Function Description: Opens maps and locates a specific position.
Parameter Information: Geographic coordinates.

ADB Command: adb shell settings put global airplane_mode_on 0; adb shell am broadcast -a android.intent.action.AIRPLANE_MODE
Function Description: Enables airplane mode.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -n com.google.android.calendar/com.android.calendar.AllInOneActivity
Function Description: Opens the calendar app.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.INSERT -t vnd.android.cursor.item/event
Function Description: Creates a new event in the calendar.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.SHOW_ALARMS
Function Description: Opens the system alarm.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.SET_TIMER
Function Description: Opens the system timer.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -n com.google.android.apps.photos/com.google.android.apps.photos.home.HomeActivity
Function Description: Opens the gallery.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -n com.google.android.calculator/com.android.calculator2.Calculator
Function Description: Opens the calculator.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.MUSIC_PLAYER
Function Description: Opens the music player.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -n com.google.android.gm/com.google.android.gm.ConversationListActivityGmail
Function Description: Opens the email app.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.MAIN -c android.intent.category.APP_MESSAGING
Function Description: Opens the SMS app.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.VIEW -t video/*
Function Description: Opens the video player.
Parameter Information: No additional parameters required.

ADB Command: adb shell am start -a android.intent.action.VIEW -d geo:0,0?q=Xiaomi+Technology+Park+Beijing
Function Description: Uses map for location (Xiaomi Technology Park Beijing example).
Parameter Information: Location query.

ADB Command: adb shell am start -a android.intent.action.VIEW -d file:///sdcard/Download/video.mp4 -t video/mp4
Function Description: Opens a specific video.
Parameter Information: <file_path> - File path of the video, <mime_type> - MIME type of the file.

ADB Command: adb shell am start -a android.intent.action.VIEW -d file://<file_path> -t <mime_type>
Function Description: Opens a file.
Parameter Information: <file_path> - Absolute path of the target file, <mime_type> - MIME type of the file.

ADB Command: adb shell screencap -p /sdcard/screenshot.png
Function Description: Takes a screenshot and saves it.
Parameter Information: No additional parameters required.

ADB Command: adb shell screenrecord <path>
Function Description: Records the screen.
Parameter Information: <path> - Save path for the screen recording.

ADB Command: adb shell ls <folder_path> | wc -l
Function Description: Counts the number of files in a folder.
Parameter Information: <folder_path> - Path of the folder.
'''

# 创建备忘录：
# adb shell am start -a android.intent.action.INSERT -t vnd.android.cursor.item/event -e title "<title>" -e begin "<starttime>" -e end "<endtime>" --ei allDay 0 --es description "<task_description>" --ez hasAlarm 1
system_api_list = '''
杀死进程：
adb shell am force-stop <package_name>

清除应用数据：
adb shell pm clear <package_name>

重启设备：
adb shell reboot

清理内存（需要root权限）：
adb shell am send-trim-memory <package_name> <level>

安装应用：
adb install <path_to_apk>

卸载应用：
adb uninstall <package_name>

查看前台应用和服务：
adb shell dumpsys activity services <package_name>

更改系统设置值（例如，关闭自动旋转）：
adb shell settings put system accelerometer_rotation 0

获取设备的电池状态：
adb shell dumpsys battery

设置设备进入休眠状态：
adb shell input keyevent KEYCODE_SLEEP

唤醒设备：
adb shell input keyevent KEYCODE_WAKEUP

查询某个应用的详细信息：
adb shell dumpsys package <package_name>

开启或关闭WiFi（需要root权限）：
adb shell svc wifi enable
adb shell svc wifi disable

数据流量开关（需要root权限）：
adb shell svc data enable
adb shell svc data disable

开启或关闭蓝牙（需要root权限）：
adb shell am start -a android.bluetooth.adapter.action.REQUEST_ENABLE
adb shell am start -a android.bluetooth.adapter.action.REQUEST_DISABLE

更改设备的屏幕亮度（数值为0-255）：
adb shell settings put system screen_brightness <brightness_value>

模拟电池充电状态（需要root权限）：
adb shell dumpsys battery set status <status_code>

模拟电池电量变化（需要root权限）：
adb shell dumpsys battery set level <level>

查询当前的内存使用情况：
adb shell dumpsys meminfo

查询特定应用的内存使用情况：
adb shell dumpsys meminfo <package_name>

获取系统广播列表：
adb shell dumpsys activity broadcasts

获取当前的CPU使用情况：
adb shell dumpsys cpuinfo

查看当前网络状态：
adb shell dumpsys netstats

查看电池统计信息：
adb shell dumpsys batterystats

查看系统服务列表：
adb shell service list
'''
# 还没有测试，不确定，多是java工具包，
non_standard_api_list = ''' 
看壁纸dump信息
adb shell dumpsys activity service com.miui.miwallpaper/.wallpaperservice.ImageWallpaper
adb shell dumpsys activity service com.miui.miwallpaper/.wallpaperservice.MiuiKeyguardPictorialWallpaper


'''
