# 地月空间入门指南（项目入口）

本仓库用于建设「地月空间入门指南」知识站点，内容围绕地月空间基础概念、轨道类型、研究前沿、术语词典及资源工具整理。

## 项目结构

- `web/`：VuePress 文档站点源码与内容目录（当前主项目）
- `README.md`：仓库入口说明（本文件）

## 站点内容导航

站点主要内容位于 `web/` 下，包括：

- `地月空间是什么/`
- `地月空间飞行器在什么轨道上运行/`
- `地月空间科学研究前沿在哪里/`
- `地月空间术语词典/`
- `资源与工具/`
- `关于本站/`

## 本地开发

请在 `web/` 目录执行：

1. 安装依赖

```bash
npm install
```

2. 启动开发环境

```bash
npm run docs:dev
```

3. 构建静态站点

```bash
npm run docs:build
```

## 说明

- 首页与内容主入口见 `web/README.md`
- 本项目持续完善中，欢迎补充地月空间相关高质量资料

## 微信分享卡片配置

微信分享卡片相关说明维护在仓库根目录 README（本节），不放在站点首页文档中。

### 1. 站点级配置

在 `web/.vuepress/config.ts` 的 `themeConfig.wechatShare` 中配置：

- `enabled`: 是否开启
- `signatureEndpoint`: 签名接口地址（必须可被线上页面访问）
- `defaultTitle`: 默认分享标题
- `defaultDesc`: 默认分享描述
- `defaultImage`: 默认分享图片（建议使用绝对可访问路径，如 `/logo.png`）

### 2. 页面级配置

在任意 Markdown frontmatter 中使用：

```yaml
wechatShare:
	title: 页面分享标题
	desc: 页面分享描述
	image: /your-share-image.png
```

### 3. 签名接口

可参考示例文件：`web/.vuepress/wechat-signature-server.example.js`。

接口约定：

- `GET /api/wechat-signature?url=<当前页面完整URL>`
- 返回 JSON：

```json
{
	"appId": "wx1234567890",
	"timestamp": 1710000000,
	"nonceStr": "randomString",
	"signature": "sha1signature"
}
```

### 4. 注意事项

- 微信签名使用的 `url` 必须与页面实际 URL（不含 hash）严格一致。
- 公众号后台要配置 JS 接口安全域名。
- 分享卡片在微信中可能有缓存，修改后建议更换参数或等待刷新。
