<center><h1>FACEBOOK CRAWLING BOT</h1></center>

## 1. BACKGROUND
An Python program which helps finding customers for AhaMove sales team.<br>
Automatically look for shipping request posts in pre-defined groups and notify staffs via Telegram.<br>
Staff will be assign using Telegram Username (Ex: @quancao). Therefore, please make sure all staffs have Username on Telegram.<br>
Posts will be simultaneously logged on Google Sheet.

**Skills involved:**
> 1. Python
> 2. Selenium
> 3. Google Sheet API
> 4. Telegram API
> 5. SQL

## 2. WHAT THIS DOES
### 2.1. Notify shipping request posts from non-ahamove users
#### 2.1.1. Send notification via Telegram

> **NEW POST** <br>
> **Nội dung:** {post_content} <br>
> **Facebook:** {facebook_profile} <br>
> **Phone:** {phone_detected_in_content} <br>
> **Link:** {post_link} <br>
> {staff}

### 2.1.2. Save posts on Google Sheet for staff
|phone   |time               |content|post                               |profile                     |staff   |note|
|--------|-------------------|-------|-----------------------------------|----------------------------|--------|----|
|84xxxxxx|2019-12-24 14:17:00|ứng 100|https://www.facebook.com/groups/...|https://www.facebook.com/...|@quancao|good|

### 2.1.3. Save posts Google Sheet for log
|phone   |time               |content|post                               |profile                     |
|--------|-------------------|-------|-----------------------------------|----------------------------|
|84xxxxxx|2019-12-24 14:17:00|ứng 100|https://www.facebook.com/groups/...|https://www.facebook.com/...|

### 2.2. Notify shipping request posts from ahamove users via Telegram
**Filter:** Only users in their 40 days old.

> **NEW POST** <br>
> **Nội dung:** {post_content} <br>
> **Facebook:** {facebook_profile} <br>
> **Link:** {post_link} <br>
> #nophone

### 2.3. Store posts
All gathered posts will be stored in database for analytics later on.
