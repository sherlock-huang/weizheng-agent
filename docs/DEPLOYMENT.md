# 部署指南

本文档介绍魏征 Agent 的各种部署方式。

## 快速部署

### 开发环境（单机）

```bash
# 1. 克隆项目
git clone <repository-url>
cd weizheng-agent

# 2. 安装依赖
pip install Pillow

# 3. 启动（后台模式）
pythonw -m src.server

# 4. 验证
python -m src.cli status
```

### 生产环境（推荐）

使用系统托盘模式：

```bash
# 安装依赖
pip install Pillow pystray

# 启动（带托盘图标）
python run_with_tray.py
```

## 部署方式

### 方式一：后台服务（Windows）

创建 Windows 服务（需要管理员权限）：

```powershell
# 使用 nssm（Non-Sucking Service Manager）
# 1. 下载 nssm: https://nssm.cc/download
# 2. 安装服务
nssm install WeizhengAgent "C:\Python312\pythonw.exe" "-m src.server"
nssm set WeizhengAgent AppDirectory C:\path\to\weizheng-agent
nssm set WeizhengAgent DisplayName "魏征 Agent"
nssm set WeizhengAgent Description "AI 代码审查助手"

# 3. 启动服务
nssm start WeizhengAgent
```

### 方式二：Docker 部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 7788

# 启动无头模式
CMD ["python", "src/server/headless_server.py", "--port", "7788"]
```

构建和运行：

```bash
# 构建镜像
docker build -t weizheng-agent .

# 运行容器
docker run -d -p 7788:7788 --name weizheng weizheng-agent

# 查看日志
docker logs -f weizheng
```

### 方式三：Linux 系统服务

创建 `/etc/systemd/system/weizheng.service`:

```ini
[Unit]
Description=魏征 Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/weizheng-agent
ExecStart=/usr/bin/python3 -m src.server --port 7788
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable weizheng
sudo systemctl start weizheng

# 查看状态
sudo systemctl status weizheng

# 查看日志
sudo journalctl -u weizheng -f
```

### 方式四：PM2 部署（Node.js 用户）

创建 `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'weizheng-agent',
    script: 'python',
    args: '-m src.server --port 7788',
    cwd: '/path/to/weizheng-agent',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production'
    },
    log_file: './logs/weizheng.log',
    error_file: './logs/weizheng-error.log',
    out_file: './logs/weizheng-out.log'
  }]
};
```

启动：

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `WEIZHENG_PORT` | HTTP 端口 | 7788 |
| `WEIZHENG_HOST` | 绑定地址 | localhost |
| `WEIZHENG_SIZE` | 像素大小 | 140 |
| `LLM_PROVIDER` | LLM 提供商 | None |
| `LLM_API_KEY` | API 密钥 | None |

示例：

```bash
export WEIZHENG_PORT=7789
export LLM_PROVIDER=moonshot
export LLM_API_KEY=sk-xxx

python -m src.server
```

## 日志配置

默认日志输出到控制台，可以重定向到文件：

```bash
# 后台运行 + 日志
python -m src.server > logs/server.log 2>&1 &

# Windows
python -m src.server > logs\server.log 2>&1
```

## 性能优化

### 1. 使用无头模式（服务器环境）

```bash
python src/server/headless_server.py
```

- 更低的资源占用
- 无需显示器
- 适合云服务器

### 2. 调整轮播速度

编辑 `src/server/pixel_server.py`：

```python
# 加快轮播（2秒一句）
self.msg_display_duration = 2000

# 减慢轮播（5秒一句）
self.msg_display_duration = 5000
```

### 3. 限制帧率

```python
# 降低动画帧率
speed = 100 if self.is_talking else 200  # 原来是 80/180
```

## 监控与告警

### 健康检查

```bash
# 创建检查脚本
curl -f http://localhost:7788/api/status || echo "Server down!"
```

### Prometheus 指标（可选）

可以扩展 `pixel_server.py` 添加指标端点：

```python
# 在 do_GET 中添加
if path == '/metrics':
    metrics = f"""
weizheng_requests_total {self.status['talk_count']}
weizheng_is_talking {1 if self.status['is_talking'] else 0}
"""
    self._send_json({"metrics": metrics})
```

## 备份与恢复

### 备份配置

```bash
# 备份记忆数据
tar -czf weizheng-backup.tar.gz memory/

# 完整备份
tar -czf weizheng-full-backup.tar.gz --exclude='__pycache__' --exclude='*.pyc' .
```

### 恢复

```bash
tar -xzf weizheng-backup.tar.gz
```

## 安全建议

1. **绑定本地地址**
   ```bash
   python -m src.server --host 127.0.0.1
   ```

2. **使用防火墙**
   ```bash
   # 只允许本地访问
   ufw deny 7788
   ```

3. **定期更新**
   ```bash
   git pull
   pip install -r requirements.txt --upgrade
   ```

## 常见问题

### Q: 服务器启动后自动退出？

检查日志：
```bash
python -m src.server 2>&1 | tee server.log
```

### Q: 端口被占用？

更换端口：
```bash
python -m src.server --port 7789
```

### Q: 如何查看运行状态？

```bash
python -m src.cli status
```

---

更多问题请提交 GitHub Issue。
