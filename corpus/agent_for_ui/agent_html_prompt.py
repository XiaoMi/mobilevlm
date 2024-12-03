# maybe we can use the guidance format
#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
# DengSHIHAN write this prompt for test.
actions_making_prompt = '''
You are a large language model agent stored on a mobile phone, You need to give the current one-step action that needs to be taken to complete the task.
Below I will provide you with a task, a plan, the environment of the current mobile phone interface(UI information), action history, though about the current status of task completion.
You need to select the most suitable one element and give the corresponding one action based on the UI information and thought.
You need to first judge based on the UI information and action history whether the planned action has been completed.
Your selection should also consider action history, and have the courage to try new buttons instead of the same buttons from history.
Action can only be the following three functions: 
    1.click(element) # click a element, only when clickable="true", the element can be clicked.
    2.input(element, text) # When you decide to enter, you first need to select the unit by clicking
    3.scroll[x_start,y_start][x_end,y_end] # scroll the screen from [x_start,y_start] to [x_end,y_end].
        3.1 The four parameters you fill in cannot be directly the same as x_min, y_min, x_max, y_max. x cannot exceed (x_min, x_max), and y can exceed (y_min, y_max).
        3.2 When you have not opened the target APP, you can scroll left and right to find the APP; when you have opened the APP, you can scroll up and down to browse the in-app information.

------Below is examples：
{actions_making_example} 
------examples ended

REMEMBER: 
1.Click and input have higher priority than scrolling. Scrolling is only considered when all elements of the current interface are indeed irrelevant to the task.
2.When you fail to try repeatedly in one interface, maybe you can try to turn back to select other options.
3.When you need to switch apps, you need to return to the HOME page first.
4.When you find that the current page does not have the APP you want, you need to scroll left and right to find more APPs.

Let's Begin!
[Task description]: {task_description}
[Planning]: {planning}
[UI information]: {ui_information}
[Actions history]: {memory}
[Thought]: {thought}
[Answer]: The only action that should be taken below is: 
'''

'''
The content filled in by element belongs to the current mobile phone interface(UI information).
    Scrolling can only be performed within the bounds=[x_min, y_min][x_max, y_max] of the element of scrollable="true".
    Usually, you can try scrolling the screen horizontally, such as: [x_min+(x_max-x_min)/5,(y_min+y_max)/2][x_max-(x_max-x_min)/5,(y_min + y_max)/2], [x_max-(x_max-x_min)/5,(y_min + y_max)/2][x_min+(x_max-x_min)/5,(y_min + y_max)/2].
    or sliding the screen vertically, such as:[(x_min+x_max)/2,y_max-(y_max-y_min)/5][(x_min+x_max)/2,y_min+(y_max-y_min)/5], [(x_min+x_max)/2,y_min+(y_max-y_min)/5][(x_min+x_max)/2,y_max-(y_max-y_min)/5].
'''


actions_making_example = '''
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
[Answer]: The only action that should be taken below is: click(click(<p id="com.miui.calculator:id/digit_5" class="android.widget.TextView" clickable="true"> 5,  </p>))

Example 2:
[Task description]: Write a note for me, title: Sunday, content: Complete the work and finish the file
[Planning]: Open the calendar, create a new event, fill in the title: Sunday, fill in the content: Complete the work and finish the file.
[UI information]: 
<img id="com.miui.notes:id/home" class="android.widget.ImageView" description="返回" clickable="true">  </img>
<img id="com.miui.notes:id/undo" class="android.widget.ImageView" description="撤销" clickable="true">  </img>
<img id="com.miui.notes:id/redo" class="android.widget.ImageView" description="恢复" clickable="true">  </img>
<img id="com.miui.notes:id/done" class="android.widget.ImageView" description="完成编辑" clickable="true">  </img>
<div class="android.webkit.WebView" clickable="false" scrollable="true" bounds="[0,275][1080,2108]"> 小米笔记 </div>
<input class="android.widget.EditText" clickable="true"> 标题 </input>
<p class="android.widget.TextView" clickable="true"> 11月11日 上午11:23 </p>
<p class="android.widget.TextView" clickable="true"> 0字 </p>
<p class="android.widget.TextView" clickable="true"> 开始书写或 </p>
<img class="android.widget.Image" clickable="true"> mind_map </img>
<p class="android.widget.TextView" clickable="true"> 创建思维笔记 </p>
<p class="android.widget.TextView" clickable="true">  </p>
<img id="com.miui.notes:id/audio" class="android.widget.ImageView" description="录音" clickable="true">  </img>
<img id="com.miui.notes:id/gallery" class="android.widget.ImageView" description="添加图片" clickable="true">  </img>
<img id="com.miui.notes:id/edit_image" class="android.widget.ImageView" description="涂鸦" clickable="true">  </img>
<img id="com.miui.notes:id/check" class="android.widget.ImageView" description="任务列表" clickable="true">  </img>
<img id="com.miui.notes:id/rich_text_switch" class="android.widget.ImageView" description="收起富文本编辑" clickable="true">  </img>
[Actions history]: 
click(<img id="com.miui.home:id/icon_icon" class="android.widget.ImageView" description="笔记" clickable="true">  </img>)
click(<img id="com.miui.notes:id/content_add" class="android.widget.ImageView" description="点击创建文字，长按录入语音，松手完成录音并创建，手指上滑取消录音" clickable="true">  </img>)
click(<input class="android.widget.EditText" clickable="true"> 标题 </input>)
[Thought]: I clicked on voice input, but my device doesn't support this feature, so I need to use another input method, such as manual input.
[Answer]: The only action that should be taken below is: input(<input class="android.widget.EditText" clickable="true"> 标题 </input>, Sunday)

Example 3:
[Task description]: Help me set an Write a memorandum for me on November 23, title: work, content: Complete the work and finish the file.
[Planning]: Open the calendar, create a new event, fill in the title: work, fill in the content: Complete the work and finish the file.
<div id="com.google.android.apps.nexuslauncher:id/workspace" class="android.widget.ScrollView" clickable="false" scrollable="true" bounds="[0,0][1080,1857]">  </div>
<p id="com.google.android.apps.nexuslauncher:id/date" class="android.widget.TextView" description="Mon, Nov 20" clickable="true"> Mon, Nov 20 </p>
<div class="android.view.View" description="Home" clickable="false">  </div>
<p class="android.widget.TextView" description="Phone" clickable="true"> Phone </p>
<p class="android.widget.TextView" description="Messages" clickable="true"> Messages </p>
<p class="android.widget.TextView" description="Play Store" clickable="true"> Play Store </p>
<p class="android.widget.TextView" description="Chrome" clickable="true"> Chrome </p>
<p class="android.widget.TextView" description="Camera" clickable="true"> Camera </p>
<img id="com.google.android.apps.nexuslauncher:id/g_icon" class="android.widget.ImageView" description="Google app" clickable="true">  </img>
<img id="com.google.android.apps.nexuslauncher:id/mic_icon" class="android.widget.ImageView" description="Voice search" clickable="true">  </img>
<img id="com.google.android.apps.nexuslauncher:id/lens_icon" class="android.widget.ImageButton" description="Google Lens" clickable="true">  </img>
[Actions history]: None
[Thought]: I need to find and open the calendar first.
[Answer]: The only action that should be taken below is: scroll([540, 1486], [540, 371])
'''

'''
Example 3:
[Task description]: Help me set an alarm clock for five o'clock.
[Planning]: Turn on the clock, set an alarm, and adjust the time to five o'clock.
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
[Actions history]: 
click(<img id="com.miui.home:id/icon_icon" class="android.widget.ImageView" description="时钟" clickable="true">  </img>)
click(<img id="com.android.deskclock:id/end_btn2" class="android.widget.ImageButton" description="添加闹钟" clickable="true">  </img>)
click(<div id="com.android.deskclock:id/hour" class="com.android.deskclock.widget.NumberPicker" description="11时" clickable="true" scrollable="true" bounds="[370,319][709,1036]"> 11.0 </div>)
[Thought]: What I need is 5, the current page is 11, so I need to slide the page until it is 5
[Answer]: scroll([359,558][359,797])

Example：
Task description: Calculate 9×5+2
UI information: 
<img class="android.widget.ImageView" description="小窗" clickable="true" scrollable="false" bounds="[55,143][165,253]">  </img>
<p class="android.widget.TextView" clickable="true" scrollable="false" bounds="[398,158][508,238]"> 计算 </p>
<p class="android.widget.TextView" clickable="true" scrollable="false" bounds="[572,158][682,238]"> 换算 </p>
<img id="com.miui.calculator:id/more" class="android.widget.ImageView" description="更多选项" clickable="true" scrollable="false" bounds="[926,143][1036,253]">  </img>
<div id="com.miui.calculator:id/expression" class="android.view.View" description="0" clickable="true" scrollable="false" bounds="[58,887][1022,1083]">  </div>
<img id="com.miui.calculator:id/btn_c_s" class="android.widget.ImageView" description="清除" clickable="true" scrollable="false" bounds="[76,1149][275,1347]">  </img>
<p id="com.miui.calculator:id/digit_7" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[76,1391][275,1589]"> 7 </p>
<p id="com.miui.calculator:id/digit_4" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[76,1633][275,1832]"> 4 </p>
<p id="com.miui.calculator:id/digit_1" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[76,1876][275,2075]"> 1 </p>
<img id="com.miui.calculator:id/btn_switch" class="android.widget.ImageView" description="切换" clickable="true" scrollable="false" bounds="[76,2119][275,2318]">  </img>
<img id="com.miui.calculator:id/btn_del_s" class="android.widget.ImageView" description="退格" clickable="true" scrollable="false" bounds="[319,1149][518,1347]">  </img>
<p id="com.miui.calculator:id/digit_8" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[319,1391][518,1589]"> 8 </p>
<p id="com.miui.calculator:id/digit_5" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[319,1633][518,1832]"> 5 </p>
<p id="com.miui.calculator:id/digit_2" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[319,1876][518,2075]"> 2 </p>
<p id="com.miui.calculator:id/digit_0" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[319,2119][518,2318]"> 0 </p>
<img id="com.miui.calculator:id/op_pct" class="android.widget.ImageView" description="百分号" clickable="true" scrollable="false" bounds="[562,1149][761,1347]">  </img>
<p id="com.miui.calculator:id/digit_9" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[562,1391][761,1589]"> 9 </p>
<p id="com.miui.calculator:id/digit_6" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[562,1633][761,1832]"> 6 </p>
<p id="com.miui.calculator:id/digit_3" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[562,1876][761,2075]"> 3 </p>
<p id="com.miui.calculator:id/dec_point" class="android.widget.TextView" description="小数点" clickable="true" scrollable="false" bounds="[562,2119][761,2318]"> . </p>
<img id="com.miui.calculator:id/op_div" class="android.widget.ImageView" description="除" clickable="true" scrollable="false" bounds="[805,1149][1004,1347]">  </img>
<img id="com.miui.calculator:id/op_mul" class="android.widget.ImageView" description="乘" clickable="true" scrollable="false" bounds="[805,1391][1004,1589]">  </img>
<img id="com.miui.calculator:id/op_sub" class="android.widget.ImageView" description="减" clickable="true" scrollable="false" bounds="[805,1633][1004,1832]">  </img>
<img id="com.miui.calculator:id/op_add" class="android.widget.ImageView" description="加" clickable="true" scrollable="false" bounds="[805,1876][1004,2075]">  </img>
<img id="com.miui.calculator:id/btn_equal_s" class="android.widget.ImageView" description="等于" clickable="true" scrollable="false" bounds="[805,2119][1004,2318]">  </img>

Actions history: none
Answer: click(<p id="com.miui.calculator:id/digit_9" class="android.widget.TextView" clickable="true" scrollable="false" bounds="[562,1391][761,1589]"> 9 </p>)

Example 3:
Task description: Calculate 9×5+2
UI information: 
<img class="android.widget.ImageView" alt="小窗" clickable="true">  </img>
<p class="android.widget.TextView" clickable="true"> 计算,  </p>
<p class="android.widget.TextView" clickable="true"> 换算,  </p>
<img id="com.miui.calculator:id/more" class="android.widget.ImageView" alt="更多选项" clickable="true">  </img>
<div id="com.miui.calculator:id/expression" class="android.view.View" alt="9.5×5" clickable="true">  </div>
<p id="com.miui.calculator:id/result" class="android.widget.TextView" alt="= 47.5" clickable="true"> = 47.5,  </p>
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
Actions history: 
Action: click(<p id="com.miui.calculator:id/digit_9" class="android.widget.TextView" clickable="true"> 9,  </p>)
Action: click(<img id="com.miui.calculator:id/op_mul" class="android.widget.ImageView" alt="乘" clickable="true">  </img>)
Answer: click(<p id="com.miui.calculator:id/digit_5" class="android.widget.TextView" clickable="true"> 5,  </p>)
'''
'''
Example 4:
Task description: Write a note for me, title: Sunday, content: Complete the work and finish the file
UI information:
<div class="android.widget.FrameLayout" clickable="false">  </div>
<img id="com.miui.notes:id/home" class="android.widget.ImageView" alt="返回" clickable="true">  </img>
<div class="android.view.View" clickable="false">  </div>
<img id="com.miui.notes:id/undo" class="android.widget.ImageView" alt="撤销" clickable="true">  </img>
<img id="com.miui.notes:id/redo" class="android.widget.ImageView" alt="恢复" clickable="true">  </img>
<img id="com.miui.notes:id/done" class="android.widget.ImageView" alt="完成编辑" clickable="true">  </img>
<input class="android.widget.EditText" clickable="true"> Sunday </input>
<p class="android.widget.TextView" clickable="true"> 11月10日 上午9:35 </p>
<p class="android.widget.TextView" clickable="true"> 0字 </p>
<p class="android.widget.TextView" clickable="true"> 开始书写或 </p>
<img class="android.widget.Image" clickable="true"> mind_map </img>
<p class="android.widget.TextView" clickable="true"> 创建思维笔记 </p>
<p class="android.widget.TextView" clickable="true">  </p>
<div id="com.miui.notes:id/mix_view" class="android.view.View" clickable="true">  </div>
<img id="com.miui.notes:id/audio" class="android.widget.ImageView" alt="录音" clickable="true">  </img>
<img id="com.miui.notes:id/gallery" class="android.widget.ImageView" alt="添加图片" clickable="true">  </img>
<img id="com.miui.notes:id/edit_image" class="android.widget.ImageView" alt="涂鸦" clickable="true">  </img>
<img id="com.miui.notes:id/check" class="android.widget.ImageView" alt="任务列表" clickable="true">  </img>
<img id="com.miui.notes:id/rich_text_switch" class="android.widget.ImageView" alt="展开富文本编辑" clickable="true">  </img>
<div id="com.miui.notes:id/panel_divide" class="android.view.View" clickable="true">  </div>
<div id="com.miui.notes:id/navi_placeholder" class="android.view.View" clickable="true">  </div>
Actions history: 
Action: {'click(<img id="com.miui.notes:id/content_add" class="android.widget.ImageView" alt="点击创建文字，长按录入语音，松手完成录音并创建，手指上滑取消录音" clickable="true">  </img>)'}
Action: {'action': 'input(<input class="android.widget.EditText" clickable="true"> 标题 </input>, Sunday)'}
Answer: input(<p class="android.widget.TextView" clickable="true"> 开始书写或 </p>, Complete the work and finish the file)
'''

html_ui_understanding = '''
You are a large language model agent stored on a mobile phone, below I will provide you with an environment of the current mobile phone interface.
Please tell me the information contained in this html interface. 
'''
html_ui_examples = '''
You are a large language model agent stored on a mobile phone, below I will provide you with an environment of the current mobile phone interface.
<img id=17 class="com.miui.calculator:id/btn_c_s" alt="清除" clickable="true">  </img>
<button id=17 class="com.miui.calculator:id/digit_7" clickable="true"> 7 </button>
<button id=17 class="com.miui.calculator:id/digit_4" clickable="true"> 4 </button>
Please tell me the information contained in this html interface. 
Answer: There is a picture that says "Clear" and two buttons representing 4 and 7.
'''

# -------------------------------------------------------------------------------------------------------
app_selection_prompt = '''
You are a large language model agent stored on a mobile phone, below I will provide you with a task, the environment of the current mobile phone interface(Apps information).
Please help me choose the correct app to perform the task based on the Apps information.
On this basis, you should make a simple plan for completing the task.
[Apps information]: 
{apps_information}

----Below are some examples：
{app_selection_example}
----examples ended

[Task description]: {task_description}
[Answer]:
'''
app_selection_example = '''
Example 1:
[Task description]: Read the latest message.
[Answer]: I should open Messages before I can view recent text messages, then using this one application should be enough.

Example 2:
[Task description]: Calculate 7*2.2/4+1
[Answer]: I should open ClevCalc because this is an application directly related to the calculator and since the task only involves calculations, then using this one application should be enough.

Example 3:
[Task description]: I want to go to Wuhan next week. Please help me determine the specific travel time and method. The information you collect can be saved on my phone for easy review by me.
[Answer]: To determine the time and mode of travel, I should at least check the air tickets or train tickets and hotel conditions on Traveloka, and check the weather conditions for the next few days on Weather. Because the collected information needs to be stored on the mobile phone, I will take screenshots of the necessary air and train ticket information and write the most recommended solution in a memo.
'''

# Base passrate
# -------------------------------------------------------------------------------------------------------
Task_finish_prompt = '''
You are a large language model agent stored on a mobile phone, below I will provide you with a task, 
the environment of the current mobile phone interface(UI information), historical action information, thoughts on the current situation.
You need to judge whether the current task has been completed based on the current environment and action history.
If the "Thought" answer indicates that there are no further actions to finish, this means the task is completed.

----Below are the examples：
{task_finish_example}
----examples ended

[Task description]: {task_description}
[UI information]: {ui_information}
[Actions history]: {memory}
[Thought]:{thought}
[Question]: Is the task completed?
[Answer]:
'''
Task_finish_example = '''
Example 1:
[Task description]: Calculate 9×5+2
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
[Actions history]: 
Action: click(<p id="com.miui.calculator:id/digit_9" class="android.widget.TextView" clickable="true"> 9,  </p>)
Action: click(<img id="com.miui.calculator:id/op_mul" class="android.widget.ImageView" alt="乘" clickable="true">  </img>)
Action: click(<p id="com.miui.calculator:id/digit_5" class="android.widget.TextView" clickable="true"> 5,  </p>)
Action: click(<img id="com.miui.calculator:id/op_add" class="android.widget.ImageView" alt="加" clickable="true">  </img>)
Action: click(<p id="com.miui.calculator:id/digit_2" class="android.widget.TextView" clickable="true"> 2,  </p>)
Action: click(<img id="com.miui.calculator:id/btn_equal_s" class="android.widget.ImageView" alt="等于" clickable="true">  </img>)
[Thought]: I have already calculate 9×5+2 = 47, there is no need for any further action.
[Question]: Is the task completed?
[Answer]: Yes, the task is completed.

Example 2:
[Task description]: Calculate 9×5+2
[UI information]: 
<img class="android.widget.ImageView" alt="小窗" clickable="true">  </img>
<p class="android.widget.TextView" clickable="true"> 计算,  </p>
<p class="android.widget.TextView" clickable="true"> 换算,  </p>
<img id="com.miui.calculator:id/more" class="android.widget.ImageView" alt="更多选项" clickable="true">  </img>
<div id="com.miui.calculator:id/expression" class="android.view.View" alt="9×5" clickable="true">  </div>
<p id="com.miui.calculator:id/result" class="android.widget.TextView" alt="= 45" clickable="true"> = 47,  </p>
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
[Actions history]: 
Action: click(<p id="com.miui.calculator:id/digit_9" class="android.widget.TextView" clickable="true"> 9,  </p>)
Action: click(<img id="com.miui.calculator:id/op_mul" class="android.widget.ImageView" alt="乘" clickable="true">  </img>)
Action: click(<p id="com.miui.calculator:id/digit_5" class="android.widget.TextView" clickable="true"> 5,  </p>)
[Thought]: I have already calculate 9×5, next I will click +.
[Question]: Is the task completed?
Answer: No, the task is not completed.
'''

# -------------------------------------------------------------------------------------------------------
Thought_prompt = '''
You are a large language model agent stored on a mobile phone, below I will provide you with a task, a plan,
the environment of the current mobile phone interface before action (Previous UI information), action history, the environment of the current mobile phone interface(Now UI information).
Action history records completed operations, including click, input, scroll and api_call.
You need to summarize these four aspects: changes in the UI page, task progress, actions that have been completed, one next action based on UI information and action history.
[Action History] are all previous historical actions, and [current action] is the current action that causes the UI page to change.
[task progress] Where in the plan is the current page?
[One next action] You need to choose one among click, input, scroll and one api as the next action, and give one and only one operation object.
[One next action] Strictly refer to [current action] and [action history] result to do the next action. 

------Below are examples：
{thought_example}
------examples ended

Let's Begin!
[Task description]: {task_description}
[Planning]: {planning}
[Previous UI information]: {ui_information}
[Now UI information]: {now_ui_information}
[Action History]: {action_history}
[Current Action]:{action}
[Answer]: 
'''
Thought_example = '''
Example 1:
[Task description]: I'm going to travel from chengdu to Beijing next week. Please help me determine the flight and specific time.
[Planning]: Open the travel APP, check flight from chengdu to beijing, sort by price, take a screenshot, then open Google search, search and check the weather conditions in Beijing next week.

[Previous UI information]: <button id="com.traveloka.android:id/toolbar_left" class="android.widget.ImageButton" clickable="true">  </button>
<p id="com.traveloka.android:id/text_view_toolbar_title" class="android.widget.TextView" clickable="false"> Flights </p>
<button id="com.traveloka.android:id/toolbar_right" class="android.widget.ImageButton" clickable="true">  </button>
<div id="com.traveloka.android.flight:id/layout_scroll" class="android.widget.ScrollView" clickable="false" scrollable="true" bounds="[0,210][1080,1717]">  </div>
<p id="com.traveloka.android.flight:id/text_owrt" class="android.widget.TextView" clickable="true"> One-way / Round-trip </p>
<p id="com.traveloka.android.flight:id/text_mc" class="android.widget.TextView" clickable="true"> Multi-city </p>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> From </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Chengdu (CTUA) </input>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> To </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Beijing (BEIA) </input>
<button id="com.traveloka.android.flight:id/btn_swap" class="android.widget.ImageButton" description="flight_searchform_button_swap" clickable="true">  </button>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Departure Date </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Wednesday, 29 Nov 2023 </input>
<p id="com.traveloka.android.flight:id/text_rt" class="android.widget.TextView" clickable="false"> Round-trip? </p>
<div id="com.traveloka.android.flight:id/switch_rt" class="android.widget.Switch" description="flight_searchform_button_roundtrip" clickable="true">  </div>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Return Date </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Saturday, 2 Dec 2023 </input>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Passengers </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> 1 passenger </input>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Seat Class </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Economy </input>
<button id="com.traveloka.android.flight:id/btn_search" class="android.widget.Button" description="flight_searchform_button_search" clickable="true"> Search </button>
<p id="com.traveloka.android.flight:id/flight_searchform_textview_recent_search" class="android.widget.TextView" clickable="false"> Your Recent Searches </p>
<div id="com.traveloka.android.flight:id/flight_searchform_recyclerview_recent_search" class="androidx.recyclerview.widget.RecyclerView" clickable="false" scrollable="true" bounds="[0,1711][1080,1717]">  </div>
<p id="com.traveloka.android.flight:id/textview_search" class="android.widget.TextView" clickable="true"> Search </p>
<p id="com.traveloka.android.flight:id/textview_discover" class="android.widget.TextView" clickable="true"> Discover </p>

[Now UI information]: <button id="com.traveloka.android.flight:id/image_arrow_back" class="android.widget.ImageButton" clickable="true">  </button>
<p id="com.traveloka.android.flight:id/text_title" class="android.widget.TextView" clickable="true"> Chengdu (CTUA)   Beijing (BEIA) </p>
<p id="com.traveloka.android.flight:id/text_subtitle" class="android.widget.TextView" clickable="true"> Wed, 29 Nov • 1 pax • Economy </p>
<div id="com.traveloka.android.flight:id/recycler_date" class="androidx.recyclerview.widget.RecyclerView" clickable="true" scrollable="true" bounds="[0,215][954,387]">  </div>
<p id="com.traveloka.android.flight:id/text_date" class="android.widget.TextView" clickable="true"> Mon, 27 Nov </p>
<p id="com.traveloka.android.flight:id/text_price" class="android.widget.TextView" clickable="true"> See Price </p>
<p id="com.traveloka.android.flight:id/text_date" class="android.widget.TextView" clickable="true"> Tue, 28 Nov </p>
<p id="com.traveloka.android.flight:id/text_price" class="android.widget.TextView" clickable="true"> See Price </p>
<p id="com.traveloka.android.flight:id/text_date" class="android.widget.TextView" clickable="true"> Wed, 29 Nov </p>
<p id="com.traveloka.android.flight:id/text_price" class="android.widget.TextView" clickable="true"> USD  81.49 </p>
<p id="com.traveloka.android.flight:id/text_date" class="android.widget.TextView" clickable="true"> Thu, 30 Nov </p>
<p id="com.traveloka.android.flight:id/text_price" class="android.widget.TextView" clickable="true"> See Price </p>
<p id="com.traveloka.android.flight:id/text_date" class="android.widget.TextView" clickable="true"> Fri, 1 Dec </p>
<p id="com.traveloka.android.flight:id/text_price" class="android.widget.TextView" clickable="true"> See Price </p>
<div id="com.traveloka.android.flight:id/recycler" class="androidx.recyclerview.widget.RecyclerView" clickable="false" scrollable="true" bounds="[0,387][1080,1857]">  </div>
<p id="com.traveloka.android.flight:id/quick_filter_item_name" class="android.widget.TextView" clickable="true"> Smart Combo </p>
<p id="com.traveloka.android.flight:id/text_flight_name" class="android.widget.TextView" description="text_view_flight_name " clickable="true"> China Eastern Airlines </p>
<p id="com.traveloka.android.flight:id/text_departure_time" class="android.widget.TextView" clickable="true"> 20:30 </p>
<p id="com.traveloka.android.flight:id/text_flight_duration" class="android.widget.TextView" clickable="true"> 2h 45m </p>
<p id="com.traveloka.android.flight:id/text_reduced_price" class="android.widget.TextView" clickable="true"> USD 81.49 </p>
<p id="com.traveloka.android.flight:id/text_real_price" class="android.widget.TextView" clickable="true"> USD  84.05/pax </p>
<p id="com.traveloka.android.flight:id/text_arrival_time" class="android.widget.TextView" clickable="true"> 23:15 </p>
<p id="com.traveloka.android.flight:id/text_departure_airport_code" class="android.widget.TextView" clickable="true"> CTU </p>
<p id="com.traveloka.android.flight:id/text_number_of_transit" class="android.widget.TextView" clickable="true"> Direct </p>
<p id="com.traveloka.android.flight:id/text_reduced_price_per_pax" class="android.widget.TextView" clickable="true"> /pax </p>
<p id="com.traveloka.android.flight:id/text_arrival_airport_code" class="android.widget.TextView" clickable="true"> PKX </p>
<p id="com.traveloka.android:id/promo_name" class="android.widget.TextView" clickable="true"> Smart Combo </p>
<p id="com.traveloka.android.flight:id/text_flight_name" class="android.widget.TextView" description="text_view_flight_name " clickable="true"> China Eastern Airlines </p>
<p id="com.traveloka.android.flight:id/text_departure_time" class="android.widget.TextView" clickable="true"> 07:20 </p>
<p id="com.traveloka.android.flight:id/text_flight_duration" class="android.widget.TextView" clickable="true"> 2h 40m </p>
<p id="com.traveloka.android.flight:id/text_reduced_price" class="android.widget.TextView" clickable="true"> USD 102.53 </p>
<p id="com.traveloka.android.flight:id/text_real_price" class="android.widget.TextView" clickable="true"> USD  104.47/pax </p>
<p id="com.traveloka.android.flight:id/text_arrival_time" class="android.widget.TextView" clickable="true"> 10:00 </p>
<p id="com.traveloka.android.flight:id/text_departure_airport_code" class="android.widget.TextView" clickable="true"> CTU </p>
<p id="com.traveloka.android.flight:id/text_number_of_transit" class="android.widget.TextView" clickable="true"> Direct </p>
<p id="com.traveloka.android.flight:id/text_reduced_price_per_pax" class="android.widget.TextView" clickable="true"> /pax </p>
<p id="com.traveloka.android.flight:id/text_arrival_airport_code" class="android.widget.TextView" clickable="true"> PKX </p>
<p id="com.traveloka.android:id/promo_name" class="android.widget.TextView" clickable="true"> Smart Combo </p>
<p id="com.traveloka.android.flight:id/text_title" class="android.widget.TextView" clickable="true"> Be the first to know when prices drop! </p>
<p id="com.traveloka.android.flight:id/text_description" class="android.widget.TextView" clickable="true"> Create a price alert and we’ll let you know as soon as prices have dropped significantly. </p>
<p id="com.traveloka.android.flight:id/text_button_action" class="android.widget.TextView" clickable="true"> Create Price Alert </p>
<p id="com.traveloka.android.flight:id/text_flight_name" class="android.widget.TextView" description="text_view_flight_name " clickable="true"> China Eastern Airlines </p>
<p id="com.traveloka.android.flight:id/text_flight_duration" class="android.widget.TextView" clickable="true"> 2h 25m </p>
<p id="com.traveloka.android.flight:id/text_real_price" class="android.widget.TextView" clickable="true"> USD  118.11/pax </p>
<div id="com.traveloka.android.flight:id/container_pill" class="android.widget.HorizontalScrollView" clickable="true" scrollable="true" bounds="[0,1709][950,1857]">  </div>
<p id="com.traveloka.android.flight:id/pill_title" class="android.widget.TextView" clickable="true"> Stops </p>
<p id="com.traveloka.android.flight:id/pill_title" class="android.widget.TextView" clickable="true"> Airlines </p>
<p id="com.traveloka.android.flight:id/pill_title" class="android.widget.TextView" clickable="true"> Time </p>
<p id="com.traveloka.android.flight:id/pill_sort_title" class="android.widget.TextView" clickable="true"> Cheapest </p>
<p id="com.traveloka.android:id/button_text" class="android.widget.TextView" clickable="true"> Filter </p>

[Action History]: 
{'[Action]': 'click(<p class="android.widget.TextView" description="Traveloka" clickable="true"> Traveloka </p>)'}
{'[Action]': 'click(<p id="com.traveloka.android:id/text_view_product_text" class="android.widget.TextView" clickable="true"> Flights </p>)'}
{'[Action]': 'click(<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Thursday, 23 Nov 2023 </input>)'}
{'[Action]': 'click(<div id="com.traveloka.android:id/calendar_date_text" class="android.view.View" description="19" clickable="true">  </div>)'}
{'[Action]': 'click(<div id="com.traveloka.android:id/calendar_date_text" class="android.view.View" description="26" clickable="true">  </div>)'}
{'[Action]': 'click(<button id="com.traveloka.android.flight:id/btn_search" class="android.widget.Button" description="flight_searchform_button_search" clickable="true"> Search </button>)'}

[Current Action]: {'[Action]': 'click(<button id="com.traveloka.android.flight:id/btn_search" class="android.widget.Button" description="flight_searchform_button_search" clickable="true"> Search </button>)'}

[Answer]: 
Changes: I clicked "Search" button. The page changes from the flight search page to the flight search results page. The page contains two flight information from Chengdu to Beijing.
Actions Complete: I have opened traveloka app, clicked "flight" button, filled the form and clicked the "search" button. 
Task progress: The current mission progress is check flight from chengdu to beijing.
One next action: Click on the cheapest flight to see more detailed information.

Example 2:
[Task description]: I'm going to travel from chengdu to Beijing next week. Please help me determine the flight and specific time.
[Planning]: Open the travel APP, check flight from chengdu to beijing, sort by price, take a screenshot, then open Google search, search and check the weather conditions in Beijing next week.

[Previous UI information]: 
<button id="com.traveloka.android:id/toolbar_left" class="android.widget.ImageButton" clickable="true">  </button>
<p id="com.traveloka.android:id/text_view_toolbar_title" class="android.widget.TextView" clickable="false"> Flights </p>
<button id="com.traveloka.android:id/toolbar_right" class="android.widget.ImageButton" clickable="true">  </button>
<div id="com.traveloka.android.flight:id/layout_scroll" class="android.widget.ScrollView" clickable="false" scrollable="true" bounds="[0,210][1080,1717]">  </div>
<p id="com.traveloka.android.flight:id/text_owrt" class="android.widget.TextView" clickable="true"> One-way / Round-trip </p>
<p id="com.traveloka.android.flight:id/text_mc" class="android.widget.TextView" clickable="true"> Multi-city </p>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> From </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Chengdu (CTUA) </input>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> To </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Beijing (BEIA) </input>
<button id="com.traveloka.android.flight:id/btn_swap" class="android.widget.ImageButton" description="flight_searchform_button_swap" clickable="true">  </button>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Departure Date </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Saturday, 2 Dec 2023 </input>
<p id="com.traveloka.android.flight:id/text_rt" class="android.widget.TextView" clickable="false"> Round-trip? </p>
<div id="com.traveloka.android.flight:id/switch_rt" class="android.widget.Switch" description="flight_searchform_button_roundtrip" clickable="true">  </div>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Return Date </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Saturday, 2 Dec 2023 </input>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Passengers </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> 1 passenger </input>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Seat Class </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Economy </input>
<button id="com.traveloka.android.flight:id/btn_search" class="android.widget.Button" description="flight_searchform_button_search" clickable="true"> Search </button>
<p id="com.traveloka.android.flight:id/flight_searchform_textview_recent_search" class="android.widget.TextView" clickable="false"> Your Recent Searches </p>
<div id="com.traveloka.android.flight:id/flight_searchform_recyclerview_recent_search" class="androidx.recyclerview.widget.RecyclerView" clickable="false" scrollable="true" bounds="[0,1711][1080,1717]">  </div>
<p id="com.traveloka.android.flight:id/textview_search" class="android.widget.TextView" clickable="true"> Search </p>
<p id="com.traveloka.android.flight:id/textview_discover" class="android.widget.TextView" clickable="true"> Discover </p>

[Now UI information]: 
<button id="com.traveloka.android:id/toolbar_left" class="android.widget.ImageButton" clickable="true">  </button>
<p id="com.traveloka.android:id/text_view_toolbar_title" class="android.widget.TextView" clickable="false"> Flights </p>
<button id="com.traveloka.android:id/toolbar_right" class="android.widget.ImageButton" clickable="true">  </button>
<div id="com.traveloka.android.flight:id/layout_scroll" class="android.widget.ScrollView" clickable="false" scrollable="true" bounds="[0,210][1080,1717]">  </div>
<p id="com.traveloka.android.flight:id/text_owrt" class="android.widget.TextView" clickable="true"> One-way / Round-trip </p>
<p id="com.traveloka.android.flight:id/text_mc" class="android.widget.TextView" clickable="true"> Multi-city </p>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> From </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Chengdu (CTUA) </input>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> To </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Beijing (BEIA) </input>
<button id="com.traveloka.android.flight:id/btn_swap" class="android.widget.ImageButton" description="flight_searchform_button_swap" clickable="true">  </button>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Departure Date </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Saturday, 2 Dec 2023 </input>
<p id="com.traveloka.android.flight:id/text_rt" class="android.widget.TextView" clickable="false"> Round-trip? </p>
<div id="com.traveloka.android.flight:id/switch_rt" class="android.widget.Switch" description="flight_searchform_button_roundtrip" clickable="true">  </div>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Return Date </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Saturday, 2 Dec 2023 </input>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Passengers </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> 1 passenger </input>
<p id="com.traveloka.android:id/label_text_view" class="android.widget.TextView" clickable="false"> Seat Class </p>
<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Economy </input>
<button id="com.traveloka.android.flight:id/btn_search" class="android.widget.Button" description="flight_searchform_button_search" clickable="true"> Search </button>
<p id="com.traveloka.android.flight:id/flight_searchform_textview_recent_search" class="android.widget.TextView" clickable="false"> Your Recent Searches </p>
<div id="com.traveloka.android.flight:id/flight_searchform_recyclerview_recent_search" class="androidx.recyclerview.widget.RecyclerView" clickable="false" scrollable="true" bounds="[0,1711][1080,1717]">  </div>
<p id="com.traveloka.android.flight:id/textview_search" class="android.widget.TextView" clickable="true"> Search </p>
<p id="com.traveloka.android.flight:id/textview_discover" class="android.widget.TextView" clickable="true"> Discover </p>

[Action History]: 
{'[Action]': 'click(<p class="android.widget.TextView" description="Traveloka" clickable="true"> Traveloka </p>)'}
{'[Action]': 'click(<p id="com.traveloka.android:id/text_view_product_text" class="android.widget.TextView" clickable="true"> Flights </p>)'}
{'[Fail]: InvalidElementStateException action': 'input(<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Chengdu (CTUA) </input>, Chengdu (CTUA))'}

[Current action]:{'[Action]': 'input(<input id="com.traveloka.android:id/edit_text_field" class="android.widget.EditText" clickable="true"> Chengdu (CTUA) </input>, Chengdu (CTUA))'}

[Answer]: 
Changes: The current page is the flight search form page in the Traveloka app. And There is no change between two pages.
Task progress: From the current action and action history, I am currently on the flight search form page, ready to search for flights from Chengdu to Beijing.
Actions completed: From the current action and action history, I have opened the traveloka app and clicked the flight button to search for flights
One next action: Because the operation of inputting information in Chengdu (CTUA) failed, I will try other operations, such as clicking Chengdu (CTUA) first. The one next action I will do is click "Chengdu (CTUA)" button to select departure city.
'''

'''

Example 3:
Task description: Help me set an alarm clock for five o'clock.
Planning: Open the clock, create a new alarm clock, and set the time to five o'clock.
Previous UI information: 
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
[Action]: 
Action: click(<img id="com.miui.home:id/icon_icon" class="android.widget.ImageView" description="时钟" clickable="true">  </img>)
Action: click(<img id="com.android.deskclock:id/end_btn2" class="android.widget.ImageButton" description="添加闹钟" clickable="true">  </img>)
Action: click(<div id="com.android.deskclock:id/hour" class="com.android.deskclock.widget.NumberPicker" description="11时" clickable="true" scrollable="true" bounds="[370,319][709,1036]"> 11.0 </div>)
[Answer]: I need to set the hour to five. In the last step, I tried to click on the eleven hours, but it seems that the element can't be click, now I will try to scroll the element to set the hour to five.
'''

passrate_prompt = '''
You are a large language model agent stored on a mobile phone, below I will provide you with a task, a system logcat.
You need to judge whether the task is completed based on the system logcat.
Task: {task}
Logcat: {logcat}
Ans: 
'''
