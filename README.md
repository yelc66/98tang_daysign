# 98tang Daysign Script

Notice: Actions is unable to sign 98tang since its IP was filtered by Cloudflare. Try to run locally.

## How to use in [Qinglong](https://github.com/whyour/qinglong) (Recommended)

1. Export cookies from Browser (`Copy as cookie`)
2. Add `CK_98TANG` env variable in Qinglong
3. Add `ql repo https://raw.githubusercontent.com/yelc66/98tang_daysign/main/daysign.py` as scheduled task and run it manually
4. The daysign task would be added automatically

## How to use in Actions

1. Export cookies from Browser
2. Clone this repository
3. Add secrets in repo settings

## How to retrieve cURL/fetch command

1. Go to [`https://www.sehuatang.net/plugin.php?id=dd_sign&view=daysign`](https://www.sehuatang.net/plugin.php?id=dd_sign&view=daysign)
2. Press `F12` to open the developer console
3. Locate the `Network` tab
4. Right click the relevant request, and select `Copy as cookies`

## Environment variables

3. `TG_USER_ID`(optional): @BotFather bot chat ID
4. `TG_BOT_TOKEN`(optional): @BotFather bot token

## Telegram notification

[create a telegram bot](https://medium.com/@ManHay_Hong/how-to-create-a-telegram-bot-and-send-messages-with-python-4cf314d9fa3e)
