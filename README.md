# AHNU（安徽师范大学）图书馆预约助手

## 使用
* **使用邮件联系我,我会将部署完毕的网站发送给你。**


## 声明
* 本项目仅限个人使用，如果影响到贵单位的利益，请及时联系我
* 开发人员经验不足,服务器可能随时关闭维护,使用时请注意

## 程序效果
<div align = "center">
  <img src="https://i.bmp.ovh/imgs/2022/03/24b47928eeefb26b.png" width="30%"/> 
</div>



## AHNU图书馆预约助手——使用指南


##### 登录

* 登录方法：输入您的“图书馆座位预约系统”的账号即可
* 注意：“图书馆座位预约系统”会在23:00~次日6:00期间关闭服务器。所以说如果您在这个时间段第一次登陆，那么将会因为无法检验您提供的账号密码而导致登录失败。



##### 预约座位

* **介绍：** 在输入界面输入您预约座位的参数信息系统会帮您自动预约
  * **开始时间，结束时间**：您预约座位的起止时间，请注意不按要求输入时间将会导致预约失败（比如：开始时间过早，时间间隔小于1小时）
  * **座位号**：使用 **小写** 的方式输入您想预约的座位号，网页将会自动检测您输入的正确性。（部分座位没有收录请见谅）
  * **推进个数**：如果座位发生冲突那么系统将会向后推进，这个值规定了推进的范围
  * **预约日期**：选择是今天还是明天预约
  * **自动签到**：请见下方对自动签到的描述
* **原理：** 系统将会按照您的要求直接向图书馆服务器发送数据来预约座位，相当于服务器中转您的预约信息。




##### 按周预约

* **介绍：** 以周为单位制定一个按周预约的计划,服务器会自动帮您预约,如果您上传了二维码还会帮您自动签到。
* **原理：** 系统内部存在一个定时器，每天早晨6:00系统会自动帮您预约座位
* **注意：** 
  * 为了您可以及时接收信息，本功能需要**绑定微信号**才可以使用
  * 由于系统的预约是在前一天早晨6:00进行，如果您设定了一个“按周预约”任务，那么系统是无法帮您预约，因为这一天座位是在昨天早晨6:15预约，而这个时间已经过去了。同理，如果您在今天设定了一个含有明天的“按周预约”任务也是无法帮您预约的
  * 为了保证图书馆资源充分利用，**如果您没有预约座位的需求，请您删除您的按周预约任务**




##### 自动签到

* **描述：** 自动签到功能可以辅助您在座位开始的时候帮您签到，下面将会列出该功能需要的注意的地方
  * **需要将用户绑定微信：**对于自动签到功能，我们设定的是需要您绑定微信号才可以使用。
  * **上传桌面二维码：**自动签到原理是通过服务器收集的桌面二维码来实现，所以您的座位可能没有收录签到二维码，所以在您使用之前建议您先检查一下是否有签到二维码
  * **请时刻关注签到结果：**对于签到时我们会通过微信的方式提醒您，但是系统不保证一定签到成功（即使存在二维码）所以建议您自己检验签到结果。



##### 绑定微信

* 绑定微信的作用：
  * 每次预约结果可以通过微信进行通知
  * 帮助您确定签到是否成功
  * 为了防止您忘记本系统在帮您自动预约座位，微信是用来接收消息通知。
  * 用来及时接收到网站广播消息



##### 删除用户

* 描述：将您的所有信息从本系统中删除



##### 注销

* 将您现在登录的账号下线

## 如何Clone:
* 请使用邮件向我咨询

## 结尾
* 感谢@yangchnet的AHNUReserve项目，本程序核心参考了该项目
