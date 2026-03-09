# NanoClaw 集成 Skills 文档

本文档记录了从 Agent 安装并集成到 NanoClaw 的所有 Skills。

## 📋 Skills 列表

### 1. agent-browser (原有)
**路径**: `data/sessions/main/.claude/skills/agent-browser/`

网页浏览和自动化工具。

**使用方法**:
```bash
agent-browser open <url>        # 打开网页
agent-browser snapshot -i       # 获取交互元素
agent-browser click @e1         # 点击元素
agent-browser fill @e2 "text"   # 填写表单
agent-browser screenshot        # 截图
agent-browser close             # 关闭浏览器
```

---

### 2. characteristic-voice ⭐ (新增)
**路径**: `data/sessions/main/.claude/skills/characteristic-voice/`

让 AI 语音听起来更人性化、更像同伴，支持情感表达和填充词。

**触发词**: 
- "say like", "talk like", "speak like"
- "companion voice", "comfort me", "cheer me up"
- "sound more human", "good night voice", "good morning voice"

**使用方法**:
```bash
# 使用预设
bash skills/characteristic-voice/scripts/speak.sh \
  --preset goodnight -t "Hmm... rest well~ Sweet dreams." -o night.wav

# 自定义情感
bash skills/characteristic-voice/scripts/speak.sh \
  -t "Aww... I'm right here." --emo '{"Tenderness":0.9}' --speed 0.75 -o comfort.wav

# 使用角色声音
bash skills/characteristic-voice/scripts/speak.sh \
  --preset morning -t "Good morning~" --ref-audio ./hermione.wav -o morning.mp3
```

**可用预设**: goodnight, morning, comfort, celebration, chatting

---

### 3. chat-with-anyone ⭐ (新增)
**路径**: `data/sessions/main/.claude/skills/chat-with-anyone/`

与任何真实人物或虚构角色用他们自己的声音聊天。

**触发词**:
- "我想跟xxx聊天"
- "你来扮演xxx跟我说话"
- "让xxx给我讲讲这篇文章"
- "用xxx的声音说"

**工作流程**:
1. 找到角色的参考视频
2. 下载视频和字幕
3. 提取音频片段
4. 使用TTS生成回复

---

### 4. tts ⭐ (新增)
**路径**: `data/sessions/main/.claude/skills/tts/`

文本转语音，支持两种后端（Kokoro本地, Noiz云端）。

**触发词**:
- "text to speech", "tts", "speak", "say"
- "voice clone", "dubbing"
- "epub to audio", "srt to audio", "convert to audio"
- "语音", "说", "讲", "说话"

**使用方法**:
```bash
# 简单模式
bash skills/tts/scripts/tts.sh speak -t "Hello world" -v af_sarah

# 从文件读取
bash skills/tts/scripts/tts.sh speak -f article.txt -v zf_xiaoni --lang cmn -o out.mp3

# 声音克隆
bash skills/tts/scripts/tts.sh speak -t "Hello" --ref-audio ./ref.wav -o clone.wav

# SRT时间轴模式
bash skills/tts/scripts/tts.sh to-srt -i article.txt -o article.srt
bash skills/tts/scripts/tts.sh render --srt input.srt --voice-map vm.json -o output.wav
```

**配置API Key**:
```bash
bash skills/tts/scripts/tts.sh config --set-api-key YOUR_NOIZ_API_KEY
```

---

### 5. video-translation ⭐ (新增)
**路径**: `data/sessions/main/.claude/skills/video-translation/`

视频翻译和配音，将视频语音翻译成其他语言。

**触发词**:
- "translate this video"
- "dub this video to English"
- "把视频从 X 语译成 Y 语"
- "视频翻译"

**使用方法**:
```bash
# 1. 下载视频和字幕（需要youtube-downloader skill）
# 2. 翻译字幕
# 3. 生成配音音频
bash skills/tts/scripts/tts.sh render \
  --srt translated.srt --voice-map voice_map.json \
  --backend noiz --auto-emotion --ref-audio-track original_video.mp4 \
  -o dubbed.wav

# 4. 替换视频音频
bash skills/video-translation/scripts/replace_audio.sh \
  --video original_video.mp4 --audio dubbed.wav \
  --output final_video.mp4 --srt translated.srt
```

---

### 6. template-skill ⭐ (新增)
**路径**: `data/sessions/main/.claude/skills/template-skill/`

创建新 Agent Skills 的可重用模板。

---

### 7. read-tencent-docs ⭐ (新增)
**路径**: `.claude/skills/read-tencent-docs/`

读取公开分享的腾讯文档表格数据，无需登录。

**触发词**:
- "腾讯文档", "Tencent Docs", "docs.qq.com"
- "读取腾讯文档", "导出腾讯表格"

**使用方法**:
```bash
# 读取并显示表格
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py \
  "https://docs.qq.com/sheet/Dxxxx?tab=BB08J2"

# 导出为 CSV
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py \
  "URL" --format csv --output data.csv

# 导出为 JSON
python3 .claude/skills/read-tencent-docs/scripts/fetch_sheet.py \
  "URL" --format json --output data.json
```

---

### 8. read-tencent-docs-private ⭐ (新增)
**路径**: `.claude/skills/read-tencent-docs-private/`

通过浏览器自动化访问需要登录的腾讯文档私有表格。

**触发词**:
- "private 腾讯文档", "需要登录的表格"
- "access denied", "login required"

**使用方法**:
```bash
# 1. 首次登录（保存会话）
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py login

# 2. 读取私有表格
python3 .claude/skills/read-tencent-docs-private/scripts/fetch_private_sheet.py fetch \
  "https://docs.qq.com/sheet/Dxxxx" \
  --format csv --output data.csv
```

**依赖**: `pip install playwright && playwright install chromium`

---

### 9. qrcode-toolkit ⭐ (新增)
**路径**: `.claude/skills/qrcode-toolkit/`

二维码解码和生成工具包，支持从图片/屏幕/剪贴板读取二维码，以及生成各种类型的二维码。

**触发词**:
- "QR code", "二维码", "scan QR", "generate QR"
- "decode barcode", "read barcode"

**使用方法**:
```bash
# 解码二维码
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py image.png
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py --clipboard
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py --screenshot

# 生成二维码
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py "Hello" --output qr.png
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py --wifi "Network" "pass" --output wifi.png
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py --vcard --name "John" --phone "123" --output contact.png
```

**依赖**: `pip install qrcode[pil] pyzbar opencv-python Pillow`

---

## 🔧 依赖要求

### 必需依赖
- `ffmpeg` - 音频/视频处理

### 可选依赖
- **Noiz API Key** - 用于声音克隆和情感控制 ✅ 已配置
  - 获取地址: https://developers.noiz.ai/api-keys
  - 配置状态: 已保存到 `~/.noiz_api_key` 和 `.env`
  - 验证: `bash skills/tts/scripts/tts.sh config`

### 其他 Skills 依赖
- **youtube-downloader** - video-translation 和 chat-with-anyone 需要
  - 仓库: https://github.com/crazynomad/skills

---

## 📁 文件位置

### Agent Skills (容器内)
```
data/sessions/main/.claude/skills/
├── agent-browser/
├── characteristic-voice/
├── chat-with-anyone/
├── template-skill/
├── tts/
└── video-translation/
```

### NanoClaw Skills (项目级)
```
.claude/skills/
├── read-tencent-docs/          # 公开表格读取
├── read-tencent-docs-private/  # 私有表格读取（需登录）
├── qrcode-toolkit/             # 二维码工具包
├── setup/
├── customize/
├── debug/
└── ...
```

---

## 📝 更新日志

### 2026-03-09
- 新增 `qrcode-toolkit` Skill - 二维码解码和生成工具
- 支持从图片/屏幕/剪贴板读取二维码
- 支持生成 URL/WiFi/联系人/邮件等类型二维码

### 2026-03-08
- 新增 `read-tencent-docs` Skill - 读取公开分享的腾讯文档表格
- 新增 `read-tencent-docs-private` Skill - 通过浏览器自动化读取私有表格
- 更新所有群组的 CLAUDE.md 以包含新能力

### 2026-03-04
- 从 Agent 环境集成 NoizAI/skills 仓库的 5 个 Skills
- 修复断开的符号链接
- 更新 groups/main/CLAUDE.md 以反映新能力
- 创建本文档

---

## 🔗 参考链接

- NoizAI Skills 仓库: https://github.com/NoizAI/skills
- Characteristic Voice 详细文档: `data/sessions/main/.claude/skills/characteristic-voice/SKILL.md`
- TTS 详细文档: `data/sessions/main/.claude/skills/tts/SKILL.md`

---

## ✅ 配置状态

### Noiz API Key
- **状态**: ✅ 已配置
- **配置时间**: 2026-03-04
- **配置位置**: 
  - `~/.noiz_api_key` (tts.sh 默认)
  - `/Users/denny/Zone/Forked/nanoclaw/.env` (项目配置)
- **验证命令**: 
  ```bash
  bash data/sessions/main/.claude/skills/tts/scripts/tts.sh config
  ```

### 文件权限
- `~/.noiz_api_key`: `-rw-------` (600, 仅所有者可读写)

