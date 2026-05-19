# CloudPan Bridge TODO

本文档用于收口“当前已完成”和“后续继续推进”的边界，方便本阶段先提交、先发布，后面再按优先级继续做。

## 当前已完成

- 已完成主名称切换到 `CloudPan Bridge`
- 已完成主计划文档收口到 `docs/cloudpan-bridge-master-plan.md`
- 已完成统一目标端选择与能力矩阵基础链路
- 已完成以下正式可写目标端：
  - `guangya`
  - `openlist`
  - `localfs`
  - `webdav`
  - `s3`
  - `seafile`
  - `smb`
  - `ftp`
  - `sftp`
  - `azureblob`
- 已完成重点 OpenList 源驱动的静态档案、guide、capture spec、capability 覆盖收口
- 已完成 grouped config 主链路和一批低频接口兼容

## 当前明确边界

- 真正支持秒传 JSON 直导和元数据秒传的正式目标端，当前仍只有 `guangya`
- 其他目标端虽然已经可写，但当前都只能诚实描述为“普通上传/覆盖”
- Docker 版本当前优先保证“控制台 + 普通同步 + 目录分析 + 覆盖审计”可运行
- 容器内浏览器登录抓取不是当前首推模式，优先建议本机桌面版运行

## 下一阶段优先级

### P1

- 继续扩更多真实可写目标端
  - 候选优先：
    - `MEGA`
    - 其它依赖轻、接口稳定、可做自动测试替身的目标端
- 继续清点 `webapp.py` 剩余平面字段兼容点，逐步统一到 grouped config
- README 再补一轮“场景建议 / 部署方式 / 不同运行模式边界”

### P2

- 继续扩 OpenList 全驱动覆盖，不只停留在重点样本
- 给覆盖审计补“已实现目标端 vs 仅档案目标端”更直观的页面提示
- 补更完整的导出脚手架，方便后续新增驱动时自动生成 profile/guide/capture/capability 模板

### P3

- 评估更多目标端的真正快传/秒传接口可能性
- 评估容器模式下的浏览器抓取增强方案
- 评估发布成单文件桌面分发包或更完整的安装包

## 发布前已确认

- 当前仓库可通过：
  - `python -m compileall src tests`
  - `pytest -q`
- 当前仓库已补 Docker 基础运行方式
- 当前仓库已补 GitHub Actions 自动构建打包流程
