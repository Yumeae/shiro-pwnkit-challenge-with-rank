# Shiro + PwnKit 挑战赛（含排行榜）

一个结合 Apache Shiro 反序列化 RCE 和 PwnKit 提权的网络安全靶场，附带实时排行榜。

CTF 风格的安全挑战靶场，融合了 Apache Shiro RememberMe 反序列化 RCE（CVE-2016-4437）
与 PwnKit 本地提权（CVE-2021-4034），并配有实时排行榜——选手在目标目录创建以自己名字命名
的文件后，排行榜将自动更新。

> ⚠️ **仅供学习与 CTF 练习使用，请在隔离环境中运行。**

---

## ⚠ 安全警告 — 故意引入的漏洞依赖

> **本应用故意使用存在漏洞的依赖版本作为 CTF 挑战目标，请勿在隔离的 Docker 环境之外部署。**

| 依赖 | 版本 | CVE | 保留原因 |
|---|---|---|---|
| `org.apache.shiro:shiro-spring` | **1.2.4** | CVE-2016-4437 | 硬编码 AES rememberMe 密钥 — **这正是挑战第一阶段的攻击目标** |
| `commons-collections:commons-collections` | **3.2.1** | CVE-2015-6420 | InvokerTransformer Gadget 链 — **Shiro RCE Payload 执行所必需** |
| Ubuntu `pkexec` (polkit) | **Ubuntu 20.04 默认版本** | CVE-2021-4034 | PwnKit SUID 漏洞利用 — **这正是挑战第二阶段的攻击目标** |

升级以上任何依赖都会导致挑战目标失效。
完整的隔离部署检查清单请参见 [`SECURITY_NOTICE.md`](./SECURITY_NOTICE.md)。

---

## 架构

```
┌──────────────────────────────────────────────────┐
│  docker-compose                                  │
│                                                  │
│  ┌─────────────────┐    ┌──────────────────────┐ │
│  │  challenge :8080│    │  leaderboard :80     │ │
│  │                 │    │                      │ │
│  │ Spring Boot +   │    │ Python Flask         │ │
│  │ Shiro 1.2.4     │    │                      │ │
│  │ (CVE-2016-4437) │    │ 从共享卷读取选手文件 │ │
│  │                 │    │                      │ │
│  │ Ubuntu 20.04 +  │    │ 提供 HTML + JSON     │ │
│  │ polkit/pkexec   │    │ 排行榜 API           │ │
│  │ (CVE-2021-4034) │    │                      │ │
│  └────────┬────────┘    └──────────┬───────────┘ │
│           │  数据卷                │             │
│           │  user_players ─────────┤             │
│           │  root_players ─────────┘             │
└──────────────────────────────────────────────────┘
```

### 服务说明

| 服务          | 端口 | 描述                                         |
|---------------|------|----------------------------------------------|
| `challenge`   | 8080 | 存在漏洞的 Shiro Web 应用 + PwnKit 环境      |
| `leaderboard` | 80   | 实时排行榜（每 30 秒自动刷新）               |

---

## 快速开始

### 前置条件

- Docker >= 20.10
- Docker Compose >= 1.29

### 启动

```bash
git clone https://github.com/Yumeae/shiro-pwnkit-challenge-with-rank.git
cd shiro-pwnkit-challenge-with-rank
docker-compose up --build -d
```

- 挑战靶场入口 → http://\<host\>:8080
- 排行榜        → http://\<host\>:80

### 远程服务器部署

默认配置下，两个服务之间的跳转链接使用 `localhost`，适合本地运行。
部署到远程服务器时，需要在 `docker-compose.yml` 中将以下两个环境变量替换为服务器的**公网 IP 或域名**，
以确保浏览器侧服务互跳及嵌入式排行榜小组件正常工作：

```yaml
services:
  challenge:
    environment:
      - LEADERBOARD_URL=http://YOUR_HOST:80   # 浏览器访问排行榜的地址

  leaderboard:
    environment:
      - CHALLENGE_URL=http://YOUR_HOST:8080   # 浏览器访问靶场的地址
```

| 变量 | 服务 | 用途 |
|---|---|---|
| `LEADERBOARD_URL` | `challenge` | Shiro 首页跳转链接 & 嵌入式迷你排行榜 API 地址 |
| `CHALLENGE_URL` | `leaderboard` | 排行榜页面「进入靶场」按钮及页脚链接 |

---

## Cloudflare 静态保留排行榜（关闭靶场后使用）

如果你准备关闭靶场，仅保留当前排行榜页面，可在靶场下线前导出一次快照，并部署 `cf-static/` 到 Cloudflare Pages。

1. 导出当前排行榜快照（会覆盖 `cf-static/leaderboard.json`）：

```bash
python3 leaderboard/export_snapshot.py --source http://39.106.85.149/api/leaderboard
```

2. 将 `cf-static/` 目录作为静态站点发布到 Cloudflare Pages（或任意静态托管）。

说明：
- `cf-static/index.html` 保持与原排行榜页面相同的样式与文案；
- 页面数据改为读取同目录下的 `leaderboard.json`；
- 需要更新榜单时，重新执行导出命令并重新部署静态目录即可。

---

## 挑战攻略

### 第一阶段 — Shiro RememberMe RCE（CVE-2016-4437）

Apache Shiro ≤ 1.2.4 内置了**硬编码 AES 密钥**（`kPH+bIxk5D2deZiIxcaaaA==`）用于加密
`rememberMe` Cookie。攻击者可伪造包含序列化 Java Payload 的 Cookie（例如通过
Commons Collections Gadget 链）从而实现远程代码执行。

1. 访问 `http://<host>:8080/login`
2. 勾选 **记住我**，使用账号 `admin` / `admin123` 登录
3. 使用 ysoserial 或 shiro-exploit 等工具构造恶意 `rememberMe` Cookie
4. 携带伪造 Cookie 发起请求 → 以 `ctf` 用户身份获取反弹 Shell
5. 读取 `/home/ctf/flag.txt` 获取 Flag 及上榜说明
6. 执行：`touch /home/ctf/players/<YOUR_NICKNAME>`

### 第二阶段 — PwnKit 本地提权（CVE-2021-4034）

容器运行 Ubuntu 20.04，其中 `polkit`（`pkexec`）为存在漏洞的默认版本。
PwnKit 允许任意无权限本地用户提升至 `root`。

1. 在第一阶段获取的 `ctf` Shell 中操作
2. 下载并编译 PwnKit 漏洞利用代码（如 https://github.com/ly4k/PwnKit）
3. 执行 → 获取 root Shell
4. 读取 `/root/flag.txt` 获取 root Flag 及上榜说明
5. 执行：`touch /root/players/<YOUR_NICKNAME>`

### 排行榜

排行榜地址 `http://<host>:80`，读取以下目录中的文件名：

- `/home/ctf/players/`  → **用户权限**排名
- `/root/players/`      → **ROOT 权限**排名

排名按文件修改时间升序排列（最先解题者排名第一），每 **30 秒**自动刷新。

---

## 目录结构

```
.
├── docker-compose.yml
├── challenge/                    # 存在漏洞的靶机
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── pom.xml                   # Maven 构建：Spring Boot + Shiro 1.2.4
│   └── src/
│       └── main/
│           ├── java/com/ctf/shiro/
│           │   ├── Application.java
│           │   ├── config/ShiroConfig.java     # 硬编码 rememberMe 密钥
│           │   ├── realm/UserRealm.java
│           │   └── controller/HomeController.java
│           └── resources/
│               ├── application.properties
│               └── templates/
│                   ├── login.html
│                   └── index.html
└── leaderboard/                  # 排行榜服务
    ├── Dockerfile
    ├── app.py                    # Flask API + 文件读取器
    ├── requirements.txt
    └── templates/
        └── index.html            # 双榜排行榜界面
```

---

## Flag 说明

| 阶段 | 文件                   | 默认值                                         |
|------|------------------------|------------------------------------------------|
| 用户 | `/home/ctf/flag.txt`   | `flag{user_b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8}` |
| Root | `/root/flag.txt`       | `flag{root_f0e1d2c3b4a5968778695a4b3c2d1e0f}` |

> 在部署前，请在 `challenge/Dockerfile` 中自定义 Flag 值。

---

## 停止服务

```bash
docker-compose down
```

如需同时删除排行榜选手数据卷：

```bash
docker-compose down -v
```
