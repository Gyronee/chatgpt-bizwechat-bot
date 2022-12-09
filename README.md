# ChatGPT BizWechat Bot
A BizWechat Bot that integrates with OpenAI's [ChatGPT](https://openai.com/blog/chatgpt/) to provide answers. Ready to use with minimal configuration required. Based on [acheong08/ChatGPT](https://github.com/acheong08/ChatGPT)

基于 [acheong08/ChatGPT](https://github.com/acheong08/ChatGPT) 开发的企业微信聊天机器人

## Features
- [x] Reply to specific messages / 回复用户信息
- [x] Can reset conversation thread with the `/reset` command / 发送 `/reset` 来重置对话
- [x] Multi-chat support. Every user has their own chat session / 每个用户有自己独立的对话

## ToDo Features
- [ ] Destroy chatbot after setting expire time to save resources / 会话过期机制, 节省资源

## Prerequisites
- Python 3
- A BizWechat Coporation Account / 企业微信企业账号
- Knowledge of how to deploy a self host bot in bizwechat / 了解如何搭建企业微信机器人 (如何获取 `Token`, `EncodingAESKey`, `CorpID`, `SECRET`, `agent_id` 等参数)
- An [OpenAI](https://openai.com) account / [OpenAI](https://openai.com) 账号

## Getting started

### Install with Docker
```bash
docker run -d --name wx-chatbot -p 8868:8868 -v <YOUR PATH TO CONFIG FILE>:/wx-chatbot/config.yaml gyronee/chatgpt-bizwechat-bot:latest
```

### Install from source
1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Gyronee/chatgpt-bizwechat-bot.git
cd chatgpt-bizwechat-bot
```

2. Install dependencies
```
cd src && pip install -r requirements.txt
```

3. Configuration File
create `config.yaml` under `src` folder, it has two section, one for BizWechatBot, one for ChatGPT
```yaml
wx-bot:
  Token: 
  EncodingAESKey: 
  CorpID: 
  SECRET: 
  agent_id: 
// session_token or email/password, choose one  token 和 账户密码二选一即可
chatgpt: 
  session_token: "<__Secure-next-auth.session-token>"
  email: "<YOUR_EMAIL>",
  password: "<YOUR_PASSWORD>"
```

4. Launch Application
```python
python main.py
```

5. Enjoy

## Credits
- [ChatGPT](https://chat.openai.com/chat) from [OpenAI](https://openai.com)
- [acheong08/ChatGPT](https://github.com/acheong08/ChatGPT) for reverse engineering ChatGPT APIs

## Disclaimer
This is a personal project and is not affiliated with OpenAI in any way.
