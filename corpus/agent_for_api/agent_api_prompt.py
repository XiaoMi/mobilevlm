#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
from agent_for_api.API_list import *

action_type_prompt = '''
You are a large language model agent stored on a mobile phone, below I will provide you with a task, a plan to accomplish the task, a next action thought, HTML information of the current page, and actions history.
Your task is to determine whether the task is finished based on the current page and action history, and if the task is not finished, you need to consider the next action category,
You have two action categories to choose from, adb or ui action.
    1. adb: If you see multiple apps in the html page, it means that you have not entered any app, then you should choose adb to open the target app.
    2. ui action: If you judge that you are already inside an app, you should select ui action to interact with the app.
Remember, your answer can only be one of the following three: "task is finished", "task is not finished, the next action type is adb" or "task is not finished, the next action type is ui action".

------Below are examples：
{action_type_example}
------examples ended

[Task description]: {task_description}
[Planning]: {planning}
[Thought]: {thought}
[UI information]: {now_ui_information}
[Action History]: {action_history}
[Answer]: 
'''


action_type_example = '''
Example 1:
[Task description]: Help me set an alarm clock for five o'clock.
[Planning]: Open the clock, create a new alarm clock, and set the time to five o'clock.
[Thought]:
I need to set the hour to five. In the last step, I tried to click on the eleven hours, but it seems that the element can't be click, now I will try to scroll the element to set the hour to five.
[UI information]: 
<button id="android:id/button1" class="android.widget.Button" description="取消" clickable="true">  </button>
<p id="android:id/title" class="android.widget.TextView" clickable="false"> 添加闹钟 </p>
<p id="com.android.deskclock:id/alarm_in_future" class="android.widget.TextView" clickable="false"> 23小时56分钟后响铃 </p>
<button id="android:id/button2" class="android.widget.Button" description="确定" clickable="true">  </button>
<div id="com.android.deskclock:id/amPm" class="com.android.deskclock.widget.NumberPicker" descript  ion="下午" clickable="true" scrollable="true" bounds="[31,319][369,1036]"> 1.0 </div>
<div id="com.android.deskclock:id/hour" class="com.android.deskclock.widget.NumberPicker" descript  ion="12时" clickable="true" scrollable="true" bounds="[370,319][709,1036]"> 12.0 </div>
<div id="com.android.deskclock:id/minute" class="com.android.deskclock.widget.NumberPicker" descript  ion="11分" clickable="true" scrollable="true" bounds="[710,319][1049,1036]"> 11.0 </div>
<p id="com.android.deskclock:id/title" class="android.widget.TextView" clickable="true"> 铃声 </p>
<p id="com.android.deskclock:id/summary" class="android.widget.TextView" clickable="true"> 元素动态铃声 </p>
<p id="com.android.deskclock:id/title" class="android.widget.TextView" clickable="true"> 重复 </p>
<p id="com.android.deskclock:id/summary" class="android.widget.TextView" clickable="true"> 只响一次 </p>
<p id="com.android.deskclock:id/title" class="android.widget.TextView" clickable="true"> 响铃时振动 </p>
<p id="com.android.deskclock:id/title" class="android.widget.TextView" clickable="true"> 响铃后删除此闹钟 </p>
<p id="com.android.deskclock:id/title" class="android.widget.TextView" clickable="true"> 备注 </p>
<p id="com.android.deskclock:id/summary" class="android.widget.TextView" clickable="true"> 请输入 </p>
[Action history]: 
Action: click(<img id="com.miui.home:id/icon_icon" class="android.widget.ImageView" description="时钟" clickable="true">  </img>)
Action: click(<img id="com.android.deskclock:id/end_btn2" class="android.widget.ImageButton" description="添加闹钟" clickable="true">  </img>)
Action: click(<div id="com.android.deskclock:id/hour" class="com.android.deskclock.widget.NumberPicker" description="11时" clickable="true" scrollable="true" bounds="[370,319][709,1036]"> 11.0 </div>)
[Answer]: The task is not finished, next action type is ui action.

Example 2:
[Task description]: Calculate 9×5+2
[Planning]: I should turn on my computer and click key by key.
[Thought]: I have already calculate 9×5+2 = 47, there is no need for any further action.
[UI information]: 
<img class="android.widget.ImageView" alt="小窗" clickable="true">  </img>
<p class="android.widget.TextView" clickable="true"> 计算,  </p>
<p class="android.widget.TextView" clickable="true"> 换算,  </p>
<img id="com.miui.calculator:id/more" class="android.widget.ImageView" alt="更多选项" clickable="true">  </img>
<div id="com.miui.calculator:id/expression" class="android.view.View" alt="9×5+2" clickable="true">  </div>
<p id="com.miui.calculator:id/result" class="android.widget.TextView" alt="= 47" clickable="true"> = 47,  </p>
<img id="com.miui.calculator:id/btn_c_s" class="android.widget.ImageView" alt="清除" clickable="true">  </img>
<p id="com.miui.calculator:id/digit_7" class="android.widget.TextView" clickable="true"> 7,  </p>
<p id="com.miui.calculator:id/digit_4" class="android.widget.TextView" clickable="true"> 4,  </p>
<p id="com.miui.calculator:id/digit_1" class="android.widget.TextView" clickable="true"> 1,  </p>
<img id="com.miui.calculator:id/btn_switch" class="android.widget.ImageView" alt="切换" clickable="true">  </img>
<img id="com.miui.calculator:id/btn_del_s" class="android.widget.ImageView" alt="退格" clickable="true">  </img>
<p id="com.miui.calculator:id/digit_8" class="android.widget.TextView" clickable="true"> 8,  </p>
<p id="com.miui.calculator:id/digit_5" class="android.widget.TextView" clickable="true"> 5,  </p>
<p id="com.miui.calculator:id/digit_2" class="android.widget.TextView" clickable="true"> 2,  </p>
<p id="com.miui.calculator:id/digit_0" class="android.widget.TextView" clickable="true"> 0,  </p>
<img id="com.miui.calculator:id/op_pct" class="android.widget.ImageView" alt="百分号" clickable="true">  </img>
<p id="com.miui.calculator:id/digit_9" class="android.widget.TextView" clickable="true"> 9,  </p>
<p id="com.miui.calculator:id/digit_6" class="android.widget.TextView" clickable="true"> 6,  </p>
<p id="com.miui.calculator:id/digit_3" class="android.widget.TextView" clickable="true"> 3,  </p>
<p id="com.miui.calculator:id/dec_point" class="android.widget.TextView" alt="小数点" clickable="true"> .,  </p>
<img id="com.miui.calculator:id/op_div" class="android.widget.ImageView" alt="除" clickable="true">  </img>
<img id="com.miui.calculator:id/op_mul" class="android.widget.ImageView" alt="乘" clickable="true">  </img>
<img id="com.miui.calculator:id/op_sub" class="android.widget.ImageView" alt="减" clickable="true">  </img>
<img id="com.miui.calculator:id/op_add" class="android.widget.ImageView" alt="加" clickable="true">  </img>
<img id="com.miui.calculator:id/btn_equal_s" class="android.widget.ImageView" alt="等于" clickable="true">  </img>
[Action history]: 
Action: click(<p id="com.miui.calculator:id/digit_9" class="android.widget.TextView" clickable="true"> 9,  </p>)
Action: click(<img id="com.miui.calculator:id/op_mul" class="android.widget.ImageView" alt="乘" clickable="true">  </img>)
Action: click(<p id="com.miui.calculator:id/digit_5" class="android.widget.TextView" clickable="true"> 5,  </p>)
Action: click(<img id="com.miui.calculator:id/op_add" class="android.widget.ImageView" alt="加" clickable="true">  </img>)
Action: click(<p id="com.miui.calculator:id/digit_2" class="android.widget.TextView" clickable="true"> 2,  </p>)
Action: click(<img id="com.miui.calculator:id/btn_equal_s" class="android.widget.ImageView" alt="等于" clickable="true">  </img>)
[Answer]: Yes, the task is finished.

Example 3:
[Task description]: Read the latest message.
[Planning]: I should open Messages before I can view recent text messages, then using this one application should be enough.
[Thought]:
I am on the home page and I should open Messages first.
[UI information]: 
<div id="com.miui.home:id/workspace" class="com.miui.home.launcher.ScreenView" clickable="false" scrollable="true" bounds="[0,0][1080,2400]">  </div>
<div class="com.miui.home.launcher.ScreenView" clickable="false" scrollable="true" bounds="[0,1911][1080,1964]">  </div>
<img package="com.miui.home" class="android.widget.ImageView" description="智能助理" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="第1屏" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="第2屏" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="第3屏" clickable="true">  </img>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="米家" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 米家 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="多看" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 多看 </p>
<p id="com.miui.player:id/title" package="com.miui.player" class="android.widget.TextView" clickable="true"> 来听歌吧！ </p>
<p id="com.miui.player:id/album" package="com.miui.player" class="android.widget.TextView" clickable="true"> 点击进入音乐 </p>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 音乐 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="小米社区" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 小米社区 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="主题壁纸" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 主题壁纸 </p>
<p id="com.mi.health:id/tv_value" package="com.mi.health" class="android.widget.TextView" clickable="true"> 0 </p>
<p id="com.mi.health:id/tv_label" package="com.mi.health" class="android.widget.TextView" clickable="true"> 目标6000步 </p>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 小米运动健康 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="钱包" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 钱包 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="小米有品" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 小米有品 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="热门" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 热门 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="短信" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 短信 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="系统工具" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="日历" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="计算器" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="联系人" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="音乐" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="时钟" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="文件管理" clickable="true">  </img>
<img package="com.miui.home" class="android.widget.ImageView" description="天气" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 系统工具 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="京东" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 京东 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="高德地图" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 高德地图 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="爱奇艺" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 爱奇艺 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="喜马拉雅" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 喜马拉雅 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="今日头条" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 今日头条 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="拼多多" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 拼多多 </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="QQ" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> QQ </p>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="携程旅行" clickable="true">  </img>
<p id="com.miui.home:id/icon_title" package="com.miui.home" class="android.widget.TextView" clickable="true"> 携程旅行 </p>
<div id="com.miui.home:id/hotseat_content_screen" class="com.miui.home.launcher.ScreenView" clickable="false" scrollable="true" bounds="[11,1974][1069,2156]">  </div>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="电话" clickable="true">  </img>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="短信" clickable="true">  </img>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="浏览器" clickable="true">  </img>
<img id="com.miui.home:id/icon_icon" package="com.miui.home" class="android.widget.ImageView" description="相机" clickable="true">  </img>
[Action history]: There is no action yet.
[Answer]: The task is not finished, next action type is adb.
'''

select_api_prompt = '''
You are the greatest large language model agent stored on a mobile phone. 
You will be provided with a API list that can be called by mobile phone, the task you need to complete, the thought about what have done and what need to do now.
You are just the first step to interact with the phone, and your follow-up is UI interaction components. If you find that there is no suitable API and the next step is UI interaction, please answer directly sorry.
You should not use the API to complete the work that has been completed by the UI interactive components in the previous steps.
Your decision should consider the following factors:
        1. You need to first judge based on the UI information and actions complete whether the planned action has been completed.
        2. You must only choose one API that should be executed most at present to finish the first action in next actions.
        3. If there is no suitable API, you can just say sorry without providing any additional suggestions.
Strings within <> needs to be replaced with specific parameters, you must return a fully executable adb command. 
Perhaps you can hand over this task to the UI interaction module.
API list: {api_list}
Below are some examples.
-----
{select_api_example}
-----

Your [Answer] can only follow the two templates: "Yes, the most suitable api function call is [adb command]" or "Sorry,[explain]" 
[Task]: {task}
[Planning]: {planning}
[UI information]: {ui_information}
[Actions History]: {memory}
[Thought]: {thought}
[WARNING]: It is strictly prohibited to use any commands other than the ADB commands listed in the API list.
[Answer]: 
'''
#
# shell 似乎可以直接调用基本运算，这是意料之外的事情。
#
'''
Notice!
You must choose only one API that should be executed most at present and give the specific adb command in [].
The API you choose must come from the API list. APIs from unknown sources are prohibited from being used.
If an API command fails to execute in the actions history, you should no longer use it as an answer.
'''

select_api_example = '''
Example 1:
[Task]：Hello, I plan to travel from Chengdu to Beijing on business next week to attend the Xiaomi Technology Park meeting on Sunday. Please help me plan the specific travel time and mode, and make simple suggestions.

[Planning]: To plan your travel from Chengdu to Beijing, we can use the following apps:

1. Open Traveloka: 
   - Search for flights from Chengdu to Beijing for the desired date.
   - Take screenshots of the flight options, including prices and timings.
   - Save the screenshots in a designated folder on your phone for easy access.

2. Open Weather:
   - Check the weather forecast for both Chengdu and Beijing for the upcoming week.
   - Take screenshots of the weather forecast for each city.
   - Save the screenshots in the same folder as the flight options.

3. Open New event:
   - Create a memo titled "Travel Plan to Beijing."
   - Write down the recommended flight options, including the airline, departure time, and arrival time.
   - Mention the weather conditions in Chengdu and Beijing for the travel dates.
   - Save the memo for easy review.

By using Traveloka, Weather, and New event apps, you can gather the necessary information and save it on your phone for future reference. Remember, this plan does not involve directly booking the tickets; it's solely for collecting information and making suggestions.
[UI information]: 
<div id="com.traveloka.android:id/recycler_view" class="androidx.recyclerview.widget.RecyclerView" clickable="false" scrollable="true" bounds="[0,63][1080,1723]">  </div>
<p id="com.traveloka.android:id/text_view_product_text" class="android.widget.TextView" clickable="true"> Flights </p>
<p id="com.traveloka.android:id/text_view_product_text" class="android.widget.TextView" clickable="true"> Hotels </p>
<p id="com.traveloka.android:id/text_view_product_text" class="android.widget.TextView" clickable="true"> Xperience </p>
<p id="com.traveloka.android:id/text_view_product_text" class="android.widget.TextView" clickable="true"> Airport Transfer </p>
<p id="com.traveloka.android:id/text_view_product_text" class="android.widget.TextView" clickable="true"> Car Rental </p>
<p id="com.traveloka.android:id/text_background_banner" class="android.widget.TextView" clickable="false"> Get access to Traveloka's complete features by choosing to enable location service all the time. </p>
<p id="com.traveloka.android:id/text_allow_background" class="android.widget.TextView" clickable="false"> Enable </p>
<p id="com.traveloka.android:id/text_widget_item_description" class="android.widget.TextView" clickable="true"> You're missing security alerts, booking updates, and chat replies. </p>
<p id="com.traveloka.android:id/text_widget_item_button" class="android.widget.TextView" clickable="true"> Check notification settings </p>
<p id="com.traveloka.android:id/text_view_title" class="android.widget.TextView" clickable="true"> Flight Discount up to 10% is yours! </p>
<p id="com.traveloka.android:id/text_view_subtitle" class="android.widget.TextView" clickable="true"> Just book a trip and explore the world </p>
<p id="com.traveloka.android:id/text_more_button" class="android.widget.TextView" clickable="true"> More </p>
<button id="com.traveloka.android:id/icon_notification" class="android.widget.ImageButton" description="Open Notification" clickable="true">  </button>
<button id="com.traveloka.android:id/icon_inbox" class="android.widget.ImageButton" description="Open Inbox" clickable="true">  </button>
<p id="com.traveloka.android:id/text_label" class="android.widget.TextView" clickable="true"> Home </p>
<p id="com.traveloka.android:id/text_label" class="android.widget.TextView" clickable="true"> Explore </p>
<p id="com.traveloka.android:id/text_label" class="android.widget.TextView" clickable="true"> Bookings </p>
<p id="com.traveloka.android:id/text_label" class="android.widget.TextView" clickable="true"> Saved </p>
<p id="com.traveloka.android:id/text_label" class="android.widget.TextView" clickable="true"> My Account </p>

[Actions history]: 
{'[API call]': 'adb shell am start -n com.traveloka.android/.appentry.splash.SplashActivity. [Call result]:API execution successful'}

[Thought]: Based on the changes in UI information and action history, the following steps have been completed:

1. The Traveloka app was opened by clicking on the "Traveloka" option.
2. The app successfully launched, and the current UI information shows the available products: Flights, Hotels, Xperience, Airport Transfer, and Car Rental.

Next, you should perform the following actions:

1. Click on the "Flights" option in the Traveloka app to search for flights.
2. Enter the necessary travel details, such as the origin (Chengdu) and destination (Beijing), and select the desired travel dates.
3. Take screenshots of the flight options, including prices and timings.
4. Save the screenshots in a designated folder on your phone for easy access.
5. Open the Weather app to check the weather forecast for both Chengdu and Beijing for the upcoming week.
6. Take screenshots of the weather forecast for each city.
7. Save the weather forecast screenshots in the same folder as the flight options.
8. Open the New event app and create a memo titled "Travel Plan to Beijing."
9. Write down the recommended flight options, including the airline, departure time, and arrival time.
10. Mention the weather conditions in Chengdu and Beijing for the travel dates.
11. Save the memo for easy review.

Remember, this plan does not involve directly booking the tickets but focuses on collecting information and making suggestions.

[Answer]：Sorry, the next action is to click the "Flights" option. I cannot complete it through the appropriate API. I suggest handing over this task to the UI interaction module.

Example 2:
[Task]: Recommend to me the most suitable ticket to Beijing this Saturday
[Planning]: 
1. Open Traveloka: 
   - Search for flights from Chengdu to Beijing for the desired date.
   - Take screenshots of the flight options, including prices and timings.
   - Save the screenshots in a designated folder on your phone for easy access.
[UI information]: 
<button id="com.traveloka.android:id/tray_text_button_left" class="android.widget.Button" clickable="true">  </button>
<p id="com.traveloka.android:id/tray_title" class="android.widget.TextView" clickable="false"> Your Trip </p>
<button id="com.traveloka.android:id/tray_text_button" class="android.widget.Button" clickable="true">  </button>
<button id="com.traveloka.android:id/tray_text_button2" class="android.widget.Button" clickable="true">  </button>
<p id="com.traveloka.android.flight:id/text_title_journey" class="android.widget.TextView" clickable="true"> Chengdu   Beijing </p>
<p id="com.traveloka.android.flight:id/text_card_title_departure" class="android.widget.TextView" clickable="true"> Sat, 25 Nov 2023 </p>
<p id="com.traveloka.android.flight:id/text_departure_time" class="android.widget.TextView" clickable="true"> 07:20 </p>
<p id="com.traveloka.android.flight:id/text_flight_duration" class="android.widget.TextView" clickable="true"> 2h 40m </p>
<p id="com.traveloka.android.flight:id/text_arrival_time" class="android.widget.TextView" clickable="true"> 10:00 </p>
<p id="com.traveloka.android.flight:id/badge_departure_airport" class="android.widget.TextView" clickable="true"> CTU </p>
<p id="com.traveloka.android.flight:id/text_flight_transit" class="android.widget.TextView" clickable="true"> Direct </p>
<p id="com.traveloka.android.flight:id/badge_arrival_airport" class="android.widget.TextView" clickable="true"> PKX </p>
<p id="com.traveloka.android.flight:id/text_airline_name" class="android.widget.TextView" clickable="true"> China Eastern Airlines </p>
<p id="com.traveloka.android.flight:id/text_seat_class" class="android.widget.TextView" clickable="true"> Economy </p>
<p id="com.traveloka.android.flight:id/text_details" class="android.widget.TextView" clickable="true"> Details </p>
<p id="com.traveloka.android.flight:id/text_title" class="android.widget.TextView" clickable="false"> Your ticket type </p>
<p id="com.traveloka.android.flight:id/text_title" class="android.widget.TextView" clickable="true"> Original </p>
<p id="com.traveloka.android.flight:id/text_price" class="android.widget.TextView" clickable="true"> USD  125.71 </p>
<p id="com.traveloka.android.flight:id/text_per_pax" class="android.widget.TextView" clickable="true"> /pax </p>
<p id="com.traveloka.android.flight:id/text" class="android.widget.TextView" clickable="true"> Cabin baggage 1 x 5 kg </p>
<p id="com.traveloka.android.flight:id/text" class="android.widget.TextView" clickable="true"> Baggage 1 x 20 kg </p>
<p id="com.traveloka.android.flight:id/text" class="android.widget.TextView" clickable="true"> Reschedule not available </p>
<p id="com.traveloka.android.flight:id/text" class="android.widget.TextView" clickable="true"> Refund info unavailable </p>
<p id="com.traveloka.android.flight:id/text_see_detail" class="android.widget.TextView" clickable="true"> Learn more </p>
<p id="com.traveloka.android.flight:id/text_view_label" class="android.widget.TextView" clickable="true"> Total price for 1 person(s) </p>
<p class="android.widget.TextView" description="pre_booking_price" clickable="true"> USD  125.71 </p>
<p id="com.traveloka.android.flight:id/text_description" class="android.widget.TextView" clickable="true"> Inclusive of all fares & taxes </p>
<button id="com.traveloka.android.flight:id/button_select" class="android.widget.Button" clickable="true"> Continue </button>
[Actions history]: 
{'[API call]': 'adb shell am start -n com.traveloka.android/.appentry.splash.SplashActivity. [Call result]:API execution successful'}
{'[Action]': 'click(<p id="com.traveloka.android:id/text_view_product_text" class="android.widget.TextView" clickable="true"> Flights </p>)'}
{'[Action]': 'click(<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Saturday, 25 Nov 2023 </input>)'}
{'[Action]': 'click(<div id="com.traveloka.android:id/calendar_date_text" class="android.view.View" description="25" clickable="true">  </div>)'}
{'[Action]': 'click(<button id="com.traveloka.android.flight:id/btn_search" class="android.widget.Button" description="flight_searchform_button_search" clickable="true"> Search </button>)'}
{'[Action]': 'click(<p id="com.traveloka.android.flight:id/text_flight_name" class="android.widget.TextView" description="text_view_flight_name " clickable="true"> China Eastern Airlines </p>)'}

[Thought]: I have already opened the traveloka, searched for flight from chengdu to beijing this Saturday, And i found the cheapest flight. Then, I will take the screenshot and save it.
[Answer]：Yes, the most suitable api function call is [adb shell screencap -p /sdcard/flight_info.png]
'''
# Task: 今晚8点要洗衣服， 请建立备忘录提醒我
# Ans：Yes, the api function call is :"adb shell am start -a android.intent.action.INSERT -t vnd.android.cursor.item/event --es title "洗衣服" --es description "今晚不要忘记洗衣服" --ez allDay false --ei beginTime 1662820800000 --ei endTime 1662824400000"
'''
Example 3：
[Task]：I'm going to travel to Beijing next week. Please help me determine the hotel and specific time.
[Planning]: Open the travel APP, check Beijing hotels, sort by rating, recommend the top three, then open Google search, search and check the weather conditions in Beijing next week.
[UI inforamtion]: 
<div id="com.google.android.apps.nexuslauncher:id/workspace" class="android.widget.ScrollView" clickable="false" scrollable="true" bounds="[0,0][1080,1857]">  </div>
<p class="android.widget.TextView" description="ClevCalc" clickable="true"> ClevCalc </p>
<p class="android.widget.TextView" description="New event" clickable="true"> New event </p>
<p class="android.widget.TextView" description="Traveloka" clickable="true"> Traveloka </p>
<p class="android.widget.TextView" description="Weather" clickable="true"> Weather </p>
<p class="android.widget.TextView" description="Clock" clickable="true"> Clock </p>
<p class="android.widget.TextView" description="Maps" clickable="true"> Maps </p>
<p class="android.widget.TextView" description="Play Store" clickable="true"> Play Store </p>
<p class="android.widget.TextView" description="Agent-LLM" clickable="true"> Agent-LLM </p>
<div class="android.view.View" description="Home" clickable="false">  </div>
<p class="android.widget.TextView" description="Phone" clickable="true"> Phone </p>
<p class="android.widget.TextView" description="Messages" clickable="true"> Messages </p>
<p class="android.widget.TextView" description="Play Store" clickable="true"> Play Store </p>
<p class="android.widget.TextView" description="Chrome" clickable="true"> Chrome </p>
<p class="android.widget.TextView" description="Camera" clickable="true"> Camera </p>
<img id="com.google.android.apps.nexuslauncher:id/g_icon" class="android.widget.ImageView" description="Google app" clickable="true">  </img>
<img id="com.google.android.apps.nexuslauncher:id/mic_icon" class="android.widget.ImageView" description="Voice search" clickable="true">  </img>
<button id="com.google.android.apps.nexuslauncher:id/lens_icon" class="android.widget.ImageButton" description="Google Lens" clickable="true">  </button>
[Actions history]: No action has been completed yet
[Thought]: I am on the home page. No action has been completed yet. I will open the Traveloka app first and check the flight.
[Answer]：Yes, the most suitable api function call is [adb shell am start -n com.traveloka.android/.appentry.splash.SplashActivity]


Example 1:
[Task description]: Calculate 9.5×5+2
[Planning]: Open a computing-related application and click the buttons one by one.
[UI information]: 
<img class="android.widget.ImageView" description="小窗" clickable="true">  </img>
<p class="android.widget.TextView" clickable="true"> 计算 </p>
<p class="android.widget.TextView" clickable="true"> 换算 </p>
<img id="com.miui.calculator:id/more" class="android.widget.ImageView" description="更多选项" clickable="true">  </img>
<div id="com.miui.calculator:id/view_pager" class="androidx.viewpager.widget.OriginalViewPager" clickable="false" scrollable="true" bounds="[0,275][1080,2400]">  </div>
<div id="com.miui.calculator:id/expression" class="android.view.View" description="9.5×5" clickable="true">  </div>
<p id="com.miui.calculator:id/result" class="android.widget.TextView" description="= 47.5" clickable="true"> = 47.5 </p>
<img id="com.miui.calculator:id/btn_c_s" class="android.widget.ImageView" description="清除" clickable="true">  </img>
<p id="com.miui.calculator:id/digit_7" class="android.widget.TextView" clickable="true"> 7 </p>
<p id="com.miui.calculator:id/digit_4" class="android.widget.TextView" clickable="true"> 4 </p>
<p id="com.miui.calculator:id/digit_1" class="android.widget.TextView" clickable="true"> 1 </p>
<img id="com.miui.calculator:id/btn_switch" class="android.widget.ImageView" description="切换" clickable="true">  </img>
<img id="com.miui.calculator:id/btn_del_s" class="android.widget.ImageView" description="退格" clickable="true">  </img>
<p id="com.miui.calculator:id/digit_8" class="android.widget.TextView" clickable="true"> 8 </p>
<p id="com.miui.calculator:id/digit_5" class="android.widget.TextView" clickable="true"> 5 </p>
<p id="com.miui.calculator:id/digit_2" class="android.widget.TextView" clickable="true"> 2 </p>
<p id="com.miui.calculator:id/digit_0" class="android.widget.TextView" clickable="true"> 0 </p>
<img id="com.miui.calculator:id/op_pct" class="android.widget.ImageView" description="百分号" clickable="true">  </img>
<p id="com.miui.calculator:id/digit_9" class="android.widget.TextView" clickable="true"> 9 </p>
<p id="com.miui.calculator:id/digit_6" class="android.widget.TextView" clickable="true"> 6 </p>
<p id="com.miui.calculator:id/digit_3" class="android.widget.TextView" clickable="true"> 3 </p>
<p id="com.miui.calculator:id/dec_point" class="android.widget.TextView" description="小数点" clickable="true"> . </p>
<img id="com.miui.calculator:id/op_div" class="android.widget.ImageView" description="除" clickable="true">  </img>
<img id="com.miui.calculator:id/op_mul" class="android.widget.ImageView" description="乘" clickable="true">  </img>
<img id="com.miui.calculator:id/op_sub" class="android.widget.ImageView" description="减" clickable="true">  </img>
<img id="com.miui.calculator:id/op_add" class="android.widget.ImageView" description="加" clickable="true">  </img>
<img id="com.miui.calculator:id/btn_equal_s" class="android.widget.ImageView" description="等于" clickable="true">  </img>
[Actions history]: 
adb shell am start -n com.cleveni.app.calculator/com.cleveni.app.calculator.MainActivity
click(<p id="com.miui.calculator:id/digit_9" class="android.widget.TextView" clickable="true"> 9,  </p>)
click(<p id="com.miui.calculator:id/dec_point" class="android.widget.TextView" description="小数点" clickable="true"> . </p>)
click(<p id="com.miui.calculator:id/digit_5" class="android.widget.TextView" clickable="true"> 5,  </p>)
click(<img id="com.miui.calculator:id/op_mul" class="android.widget.ImageView" description="乘" clickable="true">  </img>)
[Thought]: Calculate 9.5×5+2, I have clicked on 9.5 and the multiplication sign, now I should click on 5.
Ans：Sorry, I can't help you click on 5 with suitbale api. I suggest handing over this task to the UI interaction module.

'''
