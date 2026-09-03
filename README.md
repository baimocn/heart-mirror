# Heart-Mirror（心镜）

可部署的心理健康/情绪记录 Web 应用（部署于 Railway）。

## 功能简介
- 支持在 Railway 等 PaaS 平台一键部署
- 通过 \Procfile\ + \equirements.txt\ 启动，环境变量配置见 \.env.example\

## 本地运行
\\\ash
pip install -r requirements.txt
# 配置环境变量（参考 .env.example）
\\\

## 部署
- 详见 [DEPLOYMENT.md](DEPLOYMENT.md)（Railway 部署完整步骤）

## 项目结构
- \heart_mirror/\ — 应用主包
- \DEPLOYMENT.md\ — 部署指南
- \Procfile\ / \untime.txt\ / \equirements.txt\ — 部署配置

## License
MIT

© 2026 baimocn