# 2026 个人记录系统

个人 2026 年度记录系统，通过 GitHub Actions 自动同步 Garmin 手表的睡眠/起床数据到 GitHub Issue。

## 功能特性

- 🌙 **自动同步**: 每天上海时间早上 09:05 自动从 Garmin Connect API 获取当天的睡眠数据
- 🌍 **时区转换**: 自动将 GMT/UTC 时间转换为中国时区（UTC+8）
- 📝 **自动记录**: 将睡眠/起床时间自动添加到 issue #1 的评论中
- 🔁 **重复检测**: 自动检测并跳过已记录的数据，避免重复
- 📊 **格式化输出**: 统一的中文格式：`2026-01-06: 昨日睡觉 23:30 今天起床 07:00`

## 技术栈

- **语言**: Python 3.11+
- **依赖管理**: [uv](https://github.com/astral-sh/uv) - 快速的 Python 包管理器
- **核心库**:
  - [garth](https://github.com/matin/garth) - Garmin Connect API 客户端
  - [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API 客户端
- **时区处理**: 使用 Python 标准库 `datetime` 和 `timezone`，将 GMT/UTC 时间转换为中国时区（UTC+8）
- **自动化**: GitHub Actions

## 本地开发

### 前置要求

- Python 3.11 或更高版本
- [uv](https://github.com/astral-sh/uv) 包管理器

### 安装

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv sync

# 运行测试
uv run pytest
```

### 手动运行脚本

```bash
# 获取当天的睡眠数据（默认）
uv run python scripts/fetch_and_post.py

# 获取指定日期的数据
uv run python scripts/fetch_and_post.py --date 2026-01-06

# 指定 issue 编号
uv run python scripts/fetch_and_post.py --issue 1

# 干运行模式（只获取和格式化，不发布到 GitHub）
uv run python scripts/fetch_and_post.py --dry-run

# 查看帮助
uv run python scripts/fetch_and_post.py --help
```

### 环境变量

本地运行需要设置以下环境变量：

```bash
export GARMIN_EMAIL="your-garmin-email@example.com"
export GARMIN_PASSWORD="your-garmin-password"
export GITHUB_TOKEN="your-github-personal-access-token"

# 可选：配置 Garmin 域名（默认为 garmin.com）
export GARMIN_DOMAIN="garmin.cn"  # 或 "garmin.com"

# 可选：是否验证 SSL 证书（garmin.cn 需要设置为 false）
export GARMIN_SSL_VERIFY="false"  # 或 "true"
```

或创建 `.env` 文件：

```bash
GARMIN_EMAIL=your-garmin-email@example.com
GARMIN_PASSWORD=your-garmin-password
GITHUB_TOKEN=your-github-personal-access-token

# 可选配置
GARMIN_DOMAIN=garmin.cn
GARMIN_SSL_VERIFY=false
```

**重要说明**：
- `GARMIN_DOMAIN`: 默认为 `garmin.com`。如果你的 Garmin 账户在中国，需要设置为 `garmin.cn`
- `GARMIN_SSL_VERIFY`: 默认为 `true`。使用 `garmin.cn` 域名时，需要设置为 `false`
- `GARTH_TOKEN_STRING`: 可选。首次运行后，garth 会导出认证令牌。可以将其设置为环境变量以复用认证，避免每次都使用账号密码登录（CN 域名推荐使用）

## GitHub Actions 配置

### 必需的 Repository Secrets

在 GitHub 仓库设置中添加以下 secrets：

1. **GARMIN_EMAIL**: Garmin Connect 账户邮箱
2. **GARMIN_PASSWORD**: Garmin Connect 账户密码

**注意**:
- `GITHUB_TOKEN` 由 GitHub Actions 自动提供，无需手动配置
- 确保 GitHub Token 有 `repo` 和 `issues` 权限

### 可选的 Repository Variables

如果你使用 Garmin 中国账户，需要在 GitHub 仓库设置中添加以下 variables：

1. 进入仓库的 **Settings** > **Secrets and variables** > **Variables**
2. 点击 **New repository variable**
3. 添加以下变量：

   **GARMIN_DOMAIN**: `garmin.cn` （中国账户）或 `garmin.com` （国际账户）
   **GARMIN_SSL_VERIFY**: `false` （中国账户）或 `true` （国际账户）

**示例配置**：
- 中国账户：`GARMIN_DOMAIN=garmin.cn`, `GARMIN_SSL_VERIFY=false`
- 国际账户：`GARMIN_DOMAIN=garmin.com`, `GARMIN_SSL_VERIFY=true`（默认值，可不设置）

### 工作流调度

工作流配置为每天自动运行：

- **时间**: 上海时间早上 09:05
- **时区**: Asia/Shanghai (UTC+8)
- **数据**: 获取当天的睡眠数据
- **目标**: Issue #1
- **时区处理**: 自动将 Garmin API 返回的 GMT/UTC 时间转换为中国时区（UTC+8）

### 手动触发

你可以在 GitHub Actions 页面手动触发工作流：

1. 进入仓库的 **Actions** 标签
2. 选择 **Garmin Sleep Sync** 工作流
3. 点击 **Run workflow** 按钮
4. 选择分支并确认运行

## 项目结构

```
.
├── .github/
│   └── workflows/
│       └── garmin-sync.yml      # GitHub Actions 工作流配置
├── src/
│   ├── __init__.py
│   ├── garmin_client.py         # Garmin Connect API 客户端 (使用 garth)
│   │                            # - 从 GMT 时间戳获取数据
│   │                            # - 自动转换为中国时区（UTC+8）
│   ├── formatter.py             # 数据格式化模块
│   └── github_client.py         # GitHub API 客户端 (使用 PyGithub)
├── scripts/
│   ├── __init__.py
│   └── fetch_and_post.py        # 主脚本（默认获取当天数据）
├── tests/
│   ├── test_garmin_client.py    # Garmin 客户端测试
│   ├── test_formatter.py        # 格式化测试
│   └── test_github_client.py    # GitHub 客户端测试
├── pyproject.toml                # Python 项目配置
└── README.md                     # 本文件
```

## 故障排查

### 时间显示不正确

**问题**: 睡眠/起床时间与实际不符

**可能原因**:
- 时区转换问题
- Garmin API 返回的时间格式问题

**说明**:
- 系统使用 Garmin API 的 `sleep_start_timestamp_gmt` 和 `sleep_end_timestamp_gmt`（GMT/UTC 时间）
- 自动转换为中国时区（UTC+8）
- 如果时间仍然不正确，请检查：
  1. 手表时间设置是否正确
  2. Garmin Connect 账户的时区设置

**调试方法**:
```bash
# 使用干运行模式查看原始数据
uv run python scripts/fetch_and_post.py --dry-run

# 查看日志中的原始时间戳和转换后的时间
# 会打印 "Raw daily_sleep_dto" 和 "Raw GMT timestamps"
```

### 工作流失败：认证错误

**问题**: `Garmin authentication failed`

**解决**:
1. 检查 `GARMIN_EMAIL` 和 `GARMIN_PASSWORD` secrets 是否正确
2. 确认 Garmin Connect 账户可以正常登录
3. 检查是否需要两步验证（目前不支持）

**CN 域名特殊说明**：
对于 `garmin.cn` 域名，建议使用 `GARTH_TOKEN_STRING` 环境变量进行认证：

1. 首次本地运行时，设置域名和 SSL 配置：
   ```bash
   export GARMIN_DOMAIN="garmin.cn"
   export GARMIN_SSL_VERIFY="false"
   uv run python scripts/fetch_and_post.py --dry-run
   ```

2. 运行成功后，从日志中找到 `GARTH_TOKEN_STRING` 的输出

3. 将该 token 字符串添加到 GitHub Secrets：
   - 进入仓库的 **Settings** > **Secrets and variables** > **Secrets**
   - 添加新的 secret：`GARTH_TOKEN_STRING`，值为导出的 token 字符串
   - 设置 `GARMIN_DOMAIN` 和 `GARMIN_SSL_VERIFY` variables（见上文）

这样可以在不暴露账号密码的情况下完成认证

### 工作流失败：issue 不存在

**问题**: `Issue #1 does not exist`

**解决**:
1. 在仓库中手动创建 issue #1
2. 标题建议：`2026 个人记录`

### 工作流失败：无睡眠数据

**问题**: `No sleep data available for ...`

**说明**: 这不是错误，而是正常情况。某些日期可能没有睡眠数据（如忘记佩戴手表）。

### 本地测试失败

**问题**: 导入错误或测试失败

**解决**:
```bash
# 确保使用 uv 运行
uv sync  # 重新安装依赖
uv run pytest -v  # 查看详细测试输出
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_garmin_client.py

# 查看测试覆盖率
uv run pytest --cov=src
```

### 代码风格

项目遵循以下规范：
- 使用类型注解
- 编写单元测试（pytest + pytest-mock）
- 添加详细的 docstrings
- 遵循 PEP 8 代码风格

## 数据格式

### Issue 评论格式

每条记录的格式如下：

```
2026-01-06: 昨日睡觉 23:30 今天起床 07:00
<!-- data-source: garmin, fetched-at: 2026-01-06T22:00:00Z -->
```

### 元数据说明

- `data-source`: 数据来源（固定为 "garmin"）
- `fetched-at`: 数据获取时间（ISO 8601 格式，UTC 时间）

## License

MIT

## 致谢

- [uv](https://github.com/astral-sh/uv) - 快速的 Python 包管理器
- [GitHub Actions](https://github.com/features/actions) - CI/CD 平台
- [Garmin Connect](https://connect.garmin.com/) - 健康数据平台
