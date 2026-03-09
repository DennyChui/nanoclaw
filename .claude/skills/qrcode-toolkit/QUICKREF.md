# QR Code Toolkit - 快速参考

## 安装

```bash
pip install qrcode[pil] pyzbar opencv-python Pillow

# macOS 用户还需要:
brew install zbar
```

---

## 解码二维码 (decode_qr.py)

### 从图片解码
```bash
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py image.png
```

### 从剪贴板解码 (macOS)
```bash
# 先截图到剪贴板: Cmd+Ctrl+Shift+4
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py --clipboard
```

### 从屏幕解码
```bash
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py --screenshot
```

### 从 URL 解码
```bash
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py "https://example.com/qr.png"
```

---

## 生成二维码 (generate_qr.py)

### 基础文本/URL
```bash
# 保存为图片
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py "Hello World" --output hello.png

# 终端显示 ASCII 艺术
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py "Hello" --ascii

# 复制到剪贴板
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py "Hello" --clipboard
```

### WiFi 二维码 (扫描自动连接)
```bash
# 基础用法
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --wifi "网络名称" "密码"

# 完整选项
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --wifi "MyHome" "password123" \
  --type WPA \
  --output wifi.png

# 隐藏网络
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --wifi "HiddenNet" "pass" --hidden
```

### 联系人卡片 (vCard)
```bash
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --vcard \
  --name "张三" \
  --phone "+86 138-0000-0000" \
  --email "zhangsan@example.com" \
  --org "公司名" \
  --output contact.png
```

### 邮件二维码
```bash
# 简单邮件
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --email "contact@example.com"

# 带主题和正文
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --email "support@example.com" \
  --subject "问题反馈" \
  --body "我遇到了以下问题..."
```

### 电话/SMS
```bash
# 拨打电话
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --phone "+86 138-0000-0000"

# 发送短信
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --sms "+86 138-0000-0000" "短信内容"
```

---

## 高级选项

### 自定义样式
```bash
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  "https://example.com" \
  --size 20 \              # 方格大小
  --border 4 \             # 边框宽度
  --error-correction H \   # 容错等级 (L/M/Q/H)
  --fg-color "#000000" \   # 前景色
  --bg-color "#FFFFFF"     # 背景色
```

### 添加 Logo
```bash
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  "https://mybrand.com" \
  --logo ~/logo.png \
  --error-correction H     # 必须设置高容错才能加 Logo
```

---

## 常见场景

### 场景 1: 识别用户发来的二维码图片
```bash
# 保存图片后执行
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py ~/Downloads/qr_image.png
```

### 场景 2: 为客户生成 WiFi 连接卡
```bash
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --wifi "Guest-WiFi" "Welcome2024" \
  --size 15 \
  --output guest-wifi.png
```

### 场景 3: 创建个人电子名片
```bash
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --vcard \
  --name "Denny Chui" \
  --phone "+86 138-xxxx-xxxx" \
  --email "denny@example.com" \
  --url "https://github.com/DennyChui" \
  --output my-card.png
```

### 场景 4: 快速分享当前屏幕上的二维码
```bash
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py --screenshot
```

---

## 故障排除

### "No QR codes found"
- 图片质量太低，尝试更高清的图片
- 二维码被部分裁剪
- 确认是 QR Code 而非其他码制 (Data Matrix, Aztec 等)

### macOS: "zbar shared library not found"
```bash
brew install zbar
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
```

### 剪贴板无法读取
- macOS 使用 `Cmd+Ctrl+Shift+4` 截图到剪贴板
- 或使用 `--screenshot` 直接截取全屏

---

## 技术规格

| 功能 | 支持 |
|------|------|
| 解码格式 | QR Code, Data Matrix, PDF417, Code 128, Code 39, EAN, UPC |
| 生成功能 | QR Code (所有标准) |
| 输出格式 | PNG, JPG, ASCII, 剪贴板 |
| 容错等级 | L (~7%), M (~15%), Q (~25%), H (~30%) |
