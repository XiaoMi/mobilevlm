#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
# 在这里构造闭源闭源模型测试使用的few-shot例子。  
# 

############################# QWEN-VL ##################################### 
#####  qwen 3-few-shot ref task ### 
ref_qwen_prompt = '''
下面有三个例子和一个问题，你需要帮我在图像中找到我要找的文字的位置，并输出它的检测框，请注意，该坐标是相对于图像左上角的相对位置。
下面是三个例子：
问：图片 :<img>{image1}</img> 中"城市精选"在什么位置？
答：<ref>城市精选</ref><box>(24,391),(136,432)</box>
问：图片 :<img>{image2}</img> 中"翻唱"在什么位置？
答：<ref>翻唱</ref><box>(494,187),(546,223)</box>
问：图片 :<img>{image3}</img> ,在界面上，“普思词汇”位于什么地方？
答：<ref>普思词汇</ref>(483,274),(637,329)</box>
接下来我将正式提问，请注意你只需要告诉我对应文字的位置检测框坐标。
'''
actionspace_qwen_prompt = '''
下面是两个例子：
问：图片 :<img>/home/corpus/test_515/few_shot/actionspace/baicizhan0_5_50_363_357_1117/baicizhan0_5_50_363_357_1117-screen.png</img> 在这个页面上，哪些部分可以响应用户的操作？
答：可点击控件有
click(<ref>‎确认订单</ref><box>[0,64][720,112]</box>)
click(<ref>收货地址</ref><box>[46,198][674,242]</box>)
click(<ref>您还没有收货地址，请点击添加</ref><box>[46,248][674,288]</box>)
click(<ref>百词斩单词机，随时随地背单词！</ref><box>[238,394][544,466]</box>)
click(<ref>小白沙</ref><box>[238,478][544,514]</box>)
click(<ref>x 1</ref><box>[238,528][270,564]</box>)
click(<ref>¥ 219.00</ref><box>[558,394][674,426]</box>)
click(<ref>商品总价</ref><box>[46,612][170,650]</box>)
click(<ref>219.00</ref><box>[576,612][674,650]</box>)
click(<ref>邮费满50包邮</ref><box>[46,696][230,744]</box>)
click(<ref>0.00</ref><box>[612,700][674,738]</box>)
click(<ref>优惠券</ref><box>[46,790][140,826]</box>)
click(<ref>无可用优惠券</ref><box>[458,788][644,828]</box>)
click(<ref>cop-icon0.D5qF</ref><box>[46,874][150,918]</box>)
click(<ref>铜板不足或该商品无铜板抵扣</ref><box>[274,878][674,914]</box>)
click(<ref>订单备注</ref><box>[46,966][170,1002]</box>)
click(<ref>支付宝支付</ref><box>[46,1110][270,1162]</box>)
click(<ref>实付款¥219</ref><box>[22,1106][204,1138]</box>)
click(<ref>付款</ref><box>[408,1080][698,1166]</box>)
可输入控件有
input(第1个空白输入框, <box>[212,956][674,1012]</box>)
可滚动控件有
scroll(<box>[0,130][720,1184]</box>,up)
scroll(<box>[0,130][720,1184]</box>,down)
scroll(<box>[0,130][720,1184]</box>,left)
scroll(<box>[0,130][720,1184]</box>,right)
问：图片 :<img>/home/corpus/test_515/few_shot/actionspace/ctrip0_0_866_33_844_842_89_89_13577_16814/ctrip0_0_866_33_844_842_89_89_13577_16814-screen.png</img> 你可以与这个页面的哪些部分进行互动？
答：可点击控件有
click(<ref>桂林</ref><box>[68,488][116,521]</box>)
click(<ref>都江堰</ref><box>[222,488][294,521]</box>)
click(<ref>苏州</ref><box>[376,488][424,521]</box>)
click(<ref>杭州</ref><box>[530,488][578,521]</box>)
click(<ref>济南</ref><box>[684,488][696,521]</box>)
click(<ref>国内/海外酒店</ref><box>[251,81][468,129]</box>)
click(<ref>省钱订</ref><box>[566,109][626,131]</box>)
click(<ref>更多</ref><box>[652,102][692,126]</box>)
click(<ref>41</ref><box>[678,50][716,78]</box>)
click(<ref>购物车/收藏</ref><box>[162,1144][270,1172]</box>)
click(<ref>我的权益</ref><box>[320,1144][400,1172]</box>)
click(<ref>我的点评</ref><box>[464,1144][544,1172]</box>)
click(<ref>我的订单</ref><box>[608,1144][688,1172]</box>)
可输入控件有

可滚动控件有
scroll(<box>[0,0][720,1184]</box>,up)
scroll(<box>[0,0][720,1184]</box>,down)
scroll(<box>[0,0][720,1184]</box>,left)
scroll(<box>[0,0][720,1184]</box>,right)
scroll(<box>[24,0][696,300]</box>,up)
scroll(<box>[24,0][696,300]</box>,down)
scroll(<box>[24,0][696,300]</box>,left)
scroll(<box>[24,0][696,300]</box>,right)
scroll(<box>[50,432][696,540]</box>,up)
scroll(<box>[50,432][696,540]</box>,down)
scroll(<box>[50,432][696,540]</box>,left)
scroll(<box>[50,432][696,540]</box>,right)
scroll(<box>[24,602][696,998]</box>,up)
scroll(<box>[24,602][696,998]</box>,down)
scroll(<box>[24,602][696,998]</box>,left)
scroll(<box>[24,602][696,998]</box>,right)
scroll(<box>[50,1130][696,1184]</box>,up)
scroll(<box>[50,1130][696,1184]</box>,down)
scroll(<box>[50,1130][696,1184]</box>,left)
scroll(<box>[50,1130][696,1184]</box>,right)
下面是我的问题：
'''
navigation_qwen_prompt = '''
下面有两个例子和一个需要你回答的问题，如何从第一张图导航到第二张图，你需要告诉我应该和什么控件进行交互？有三种动作：click、input、scroll。
下面是两个例子：
问：图片一 :<img>/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29-screen.png</img>，图片二：<img>/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29_29-screen.png</img> 如何从第一张图导航到第二张图？
答：click(<ref>直播</ref><box>[200,1132][240,1160]</box>)
问：图片一 :<img>/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018-screen.png</img>，图片二：<img>/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018_13545-screen.png</img> 如何从第一张图导航到第二张图？
答：click(<ref>周四</ref><box>[563,163][603,185]</box>)
接下来我将正式提问，请注意你需要严格遵循例子回答的格式,你只能做一个动作。
'''

stage3_navigation_qwen_prompt = '''
下面有两个例子和一个需要你回答的问题，如何从第一张图导航到第二张图，你需要告诉我应该和什么控件进行交互？有三种动作：click、input、scroll。
下面是两个例子：
问：图片:<img>/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29-screen.png</img>， 我想要点击直播？
答：click(<ref>直播</ref><box>[200,1132][240,1160]</box>)
问：图片一 :<img>/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018-screen.png</img>，如何看到周四的信息？
答：click(<ref>周四</ref><box>[563,163][603,185]</box>)
接下来我将正式提问，请注意你需要严格遵循例子回答的格式,你只能做一个动作。
'''
# navigation_qwen_prompt = '''
# 问：给定两个手机截图，告诉我应该和什么控件进行一次交互可以从第一张图片到第二张图片，交互动作有三种动作：点击、输入、滑动。请以\"动作 值 位置\"回答。图片一 :<img>/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29-screen.png</img>，图片二：<img>/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29_29-screen.png</img> 如何从第一张图导航到第二张图？
# 答：动作：点击；值：直播 ；位置：(200,1132)(240,1160)
# 问：给定两个手机截图，告诉我应该和什么控件进行一次交互可以从第一张图片到第二张图片，交互动作有三种动作：点击、输入、滑动。请以\"动作 值 位置\"回答。图片一 :<img>/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018-screen.png</img>，图片二：<img>/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018_13545-screen.png</img> 如何从第一张图导航到第二张图？
# 答：动作：点击；值：周四 ；位置：(563,163)(603,185)
# '''

ocr_qwen_prompt = '''
下面是两个例子， 你需要告诉我页面中有哪些内容，用<ref></ref>标记，以及他们的坐标，用<box></box>标记。
问：图片 :<img>/home/corpus/test_515/few_shot/ocr/ctrip0_1_36_313_3617_1988_8364_4440_1566/ctrip0_1_36_313_3617_1988_8364_4440_1566-screen.png</img> 阐释当前页面的元素如何支持其内容和功能。
答：<ref>日历</ref><box>[152,144][244,185]</box>
<ref>价格走势</ref><box>[421,144][575,185]</box>
<ref>日历</ref><box>[154,205][242,211]</box>
<ref>仅看直飞 OFF</ref><box>[474,228][696,282]</box>
<ref>2024年5月</ref><box>[32,885][222,939]</box>
<ref>2024年4月</ref><box>[32,357][222,411]</box>
<ref>所选日期为出发地日期，显示单成人价，变价频繁以实际支付价为准</ref><box>[0,1122][720,1184]</box>
问：图片 :<img>/home/corpus/test_515/few_shot/ocr/baicizhan0_1_24_113_159_165_156_206/baicizhan0_1_24_113_159_165_156_206-screen.png</img>  概述页面中各个部分的布局和互动方式。
答：<ref>全部词书</ref><box>[0,66][720,115]</box>
<ref>热门</ref><box>[15,132][123,236]</box>
<ref>大学</ref><box>[123,132][231,236]</box>
<ref>高中</ref><box>[231,132][339,236]</box>
<ref>初中</ref><box>[339,132][447,236]</box> 
<ref>小学</ref><box>[447,132][555,236]</box>
<ref>留学</ref><box>[555,132][663,236]</box>
<ref>其他</ref><box>[663,132][720,236]</box>
<ref>热门</ref><box>[38,266][114,322]</box>
<ref>高考词汇</ref><box>[214,374][377,419]</box>
<ref>完整收录高考基础词汇和高分词汇，适合全国各地考生</ref><box>[214,434][682,514]</box>
<ref>共 4135 词</ref><box>[214,524][324,558]</box>
<ref>已添加</ref><box>[613,524][682,558]</box>
<ref>中考词汇</ref><box>[214,604][377,649]</box>
<ref>完整收录中考必考、常考和重难点词汇，适合全国各地考生</ref><box>[214,664][682,744]</box>
<ref>共 2124 词</ref><box>[214,754][324,788]</box>
<ref>已添加</ref><box>[613,754][682,788]</box>
<ref>四级词汇大全</ref><box>[214,834][439,879]</box>
<ref>四级最新考纲单词全收录，适合所有备考四级的同学</ref><box>[214,894][682,974]</box>
<ref>共 4440 词</ref><box>[214,984][324,1018]</box>
<ref>已添加</ref><box>[613,984][682,1018]</box>
<ref>四级高频</ref><box>[214,1064][377,1109]</box>
<ref>精选四级真题超高频单词，助你快速攻克四级</ref><box>[214,1124][682,1184]</box>
下面是我的问题：
'''
