# 98tang Daysign Script

Notice: Actions is unable to sign 98tang since its IP was filtered by Cloudflare. Try to run locally.
## 错误问题
1. 部署测试问题，如果使用的青龙版本为2.10.2,会出现对象值为空情况，推荐使用最新版本，预计是python环境问题
2. 建议格式为`fetch("https://sehuatang.net/plugin.php?id=dd_sign", {"headers": { "cookie": "xxxxx..."},})`其他可以删除
3. 新增多账号签到

## How to use in [Qinglong](https://github.com/whyour/qinglong) (Recommended)

1. Export cookies from Browser (`Copy as Node.js fetch`)
2. Add `FETCH_98TANG` env variable in Qinglong
3. Add `ql repo https://github.com/xjasonlyu/98tang_daysign` as scheduled task and run it manually
4. The daysign task would be added automatically

## How to use in Actions

1. Export cookies from Browser
2. Clone this repository
3. Add secrets in repo settings

## How to retrieve cURL/fetch command

1. Go to [`https://www.sehuatang.net/plugin.php?id=dd_sign&view=daysign`](https://www.sehuatang.net/plugin.php?id=dd_sign&view=daysign)
2. Press `F12` to open the developer console
3. Locate the `Network` tab
4. Right click the relevant request, and select `Copy as cURL` or `Copy as Node.js fetch`

## Environment variables

<!-- 1. `CURL_98TANG`: cURL command string (e.g. `curl -H 'xxx:xxx'`) -->
2. `FETCH_98TANG`: Node.js fetch string (e.g. `fetch("xxx", ...)`)
3. `TG_USER_ID`(optional): @BotFather bot chat ID
4. `TG_BOT_TOKEN`(optional): @BotFather bot token

## Telegram notification

[create a telegram bot](https://medium.com/@ManHay_Hong/how-to-create-a-telegram-bot-and-send-messages-with-python-4cf314d9fa3e)

## 特别感谢大佬分享

@xjasonlyu(https://github.com/xjasonlyu/98tang_daysign)
