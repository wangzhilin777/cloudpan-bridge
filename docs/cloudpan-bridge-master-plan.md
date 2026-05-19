# CloudPan Bridge 总体实施计划

## 1. 文档定位

本文档是当前仓库的主计划文档，用来合并并替代早期的“天翼转光鸭”与 `Cloud2Guangya` 阶段性计划。

- 当前仓库历史计划文档仍保留：
  - `docs/cloud2guangya-rebuild-plan.md`
- 前期调研计划独立文档：
  - `docs/cloudpan-bridge-research-plan.md`
- 但后续实施、扩展、验收、README 与对外说明，统一以本文档为准。

## 2. 当前项目现状

当前代码已经不再只是“天翼云盘转光鸭”的单脚本，而是一个本地控制台型工具，已经具备以下基础能力：

- 以 `OpenList` 作为源端统一接入层
- 以 `Guangya` 作为当前主秒传目标端
- 以 `OpenList` 作为当前第二个已实现的可写目标端
- 以 `LocalFS` 作为当前第三个已实现的可写目标端
- 以 `WebDAV` 作为当前第四个已实现的可写目标端
- 以 `FTP` 作为当前第五个已实现的可写目标端
- 以 `SFTP` 作为当前第六个已实现的可写目标端
- 支持本地 Web 控制台、目录浏览、挂载管理、实时日志
- 支持托管 OpenList 与外部 OpenList 两种工作模式
- 支持按目录扫描、最底层目录边扫边同步、目录队列、待补传树
- 支持源端元数据分析、秒传 JSON 生成、秒传 JSON 直导
- 支持 Guangya 登录抓取、Token 自动回填、源网盘登录抓取骨架
- 支持增量同步、覆盖修改文件、记录补传状态、恢复继续执行

这说明项目已经具备“本地控制台 + 源端聚合接入 + 目标端写入”的雏形，但目前仍存在两个结构性问题：

1. 对外命名仍停留在 `Cloud2Guangya`
2. 核心能力还没有被整理成“统一源端 + 可扩目标端 + 能力矩阵”的总架构

补充说明：

- `Provider Registry` 已开始承载复杂驱动说明与推荐默认值
- `Target Adapter` 已抽出 Guangya 适配层，并补上 OpenList / LocalFS / WebDAV / FTP / SFTP 可写目标端
- `能力矩阵与建议` 已有第一版页面/接口链路
- 但“全 OpenList 驱动逐项填实”和“多目标端矩阵”仍未完成

## 3. 最终目标

项目新的正式业务定位为：

- 中文名：`云盘桥`
- 英文名：`CloudPan Bridge`

目标不是继续堆一个“OpenList 页面增强器”，而是构建一个：

- 统一接入所有 OpenList 已支持网盘作为源端
- 提供 Guangya 内置目标端
- 逐步扩展更多目标端适配器
- 尽最大努力优先走秒传 / 快传 / 服务器侧复用
- 在不能秒传时，再明确降级到中转上传 / 下载补传
- 能持续跟上 OpenList 新增驱动的长期可维护桥接工具

## 4. 能力边界原则

后续所有页面提示、README、接口说明，都要遵守下面这组边界，不再混淆概念：

### 4.1 OpenList 的定位

OpenList 在本项目中主要承担：

- 统一登录与挂载入口
- 统一列目录入口
- 统一文件元数据采集入口
- 统一下载链接获取入口

OpenList 不应再被描述成“天然支持所有跨网盘秒传复制”。

### 4.2 秒传能力的真实判断方式

跨网盘是否能“秒传”，必须按“源端可提取的指纹 + 目标端接口要求”逐组合判断。

统一输出能力等级：

- `fast_upload_supported`
  - 当前组合可稳定走秒传/快传
- `fast_upload_partial`
  - 只对部分文件、部分指纹、部分大小范围可快传
- `relay_supported`
  - 可走中转流上传，但不是真秒传
- `download_upload_only`
  - 只能下载后再上传
- `unsupported`
  - 当前组合暂不支持

### 4.3 诚实降级

如果某个组合不能秒传，也必须：

- 在页面上提前提示
- 在任务执行前给出推荐路径
- 在日志里明确写出为何降级

不能继续用“理论可同步”掩盖“实际上只能中转上传”。

### 4.4 默认同步语义

默认同步语义固定为：

- 新增
- 覆盖

也就是：

- 源端新增文件时，目标端补齐
- 源端文件修改时，目标端覆盖
- 源端删除文件时，默认不删除目标端真实文件

如果后续需要“目标端真实删除”，只能作为单独配置项提供，并保持默认关闭。

建议配置语义：

- `delete_removed`
  - 允许把源端已删除文件从同步状态中移除
- `target_delete_removed`
  - 允许在支持的目标端上同步执行真实删除
  - 必须显式开启，且默认关闭

## 5. 总体架构

后续总代码结构，按三层收敛：

### 5.1 Source Layer 源端层

负责统一接入 OpenList 全驱动。

职责：

- 管理 OpenList runtime / external 模式
- 登录 OpenList
- 读取 driver 列表、driver 字段、storage 列表
- 浏览目录、获取文件树
- 读取哈希/etag/gcid/sha1 等指纹
- 获取下载直链
- 维护“驱动说明 / 默认值 / 风控建议 / 复杂流程指引”

### 5.2 Fingerprint Bridge 指纹桥层

负责把不同源端字段，转换成统一文件指纹模型。

统一模型至少包含：

- `provider`
- `provider_file_id`
- `path`
- `name`
- `size`
- `is_dir`
- `mtime`
- `md5`
- `etag`
- `sha1`
- `gcid`
- `crc64`
- `pickcode`
- `extra_hashes`
- `raw_hash_info`

职责：

- 对 OpenList 返回字段做标准化
- 对不同来源的秒传 JSON 做统一导入
- 对后续新增 provider 的指纹差异做扩展映射

### 5.3 Target Adapter 目标端层

负责把统一指纹模型落到目标网盘。

当前首个正式目标端：

- `Guangya`

当前第二个正式可写目标端：

- `OpenList`
  - 用于把文件写回 OpenList 挂载目录
  - 走普通上传/覆盖链路
  - 不承诺跨网盘秒传

当前第三个正式可写目标端：

- `LocalFS`
  - 用于把结果直接落到本机目录
  - 适合作为联调、导出与保底目标端
  - 不承诺跨网盘秒传

当前第四个正式可写目标端：

- `WebDAV`
  - 用于把结果写入 NAS、私有云或第三方 WebDAV 存储
  - 当前走普通上传/覆盖链路
  - 不承诺跨网盘秒传

当前第五个正式可写目标端：

- `FTP`
  - 用于把结果写入传统 NAS、主机面板或轻量服务器目录
  - 当前走普通上传/覆盖链路
  - 不承诺跨网盘秒传

当前第六个正式可写目标端：

- `SFTP`
  - 用于把结果写入 Linux 主机、NAS 或云服务器目录
  - 当前走普通上传/覆盖链路
  - 不承诺跨网盘秒传

后续可扩：

- Baidu
- Quark
- 123
- Thunder
- AliyunDrive
- OneDrive
- PikPak
- 其它支持快传/秒传的目标端

目标端适配器统一接口需要覆盖：

- `capability_probe`
- `ensure_auth`
- `ensure_target_dir`
- `try_fast_upload`
- `upload_by_stream`
- `upload_by_download_file`
- `finalize_state`

## 6. 支持范围原则

### 6.1 源端范围

目标范围是：

- `OpenList 当前已支持的所有驱动`

这意味着页面与后端不能只围绕少数常见盘写死，而要具备：

- 动态驱动元数据渲染
- 通用网页登录抓取模板
- 复杂驱动专属流程指引
- 推荐默认值
- 风控策略模板

### 6.2 重点复杂驱动说明覆盖

第一批必须重点做好的复杂驱动说明，包含但不限于：

- `AliyundriveOpen`
- `123Open`
- `139Yun`
- `Quark`
- `Thunder`
- `Baidu`
- `OneDrive`
- `PikPak`
- `189Cloud`

### 6.3 没有 OpenList 的情况

如果用户本机没有 OpenList，也要有清晰路径：

- 优先提供托管 OpenList 启动能力
- 如果某驱动可以直接网页登录抓取，再把必要字段回填到“创建挂载”表单
- 最终仍以“在本地形成一个可用 OpenList 源端”为主

也就是说，项目目标不是绕开 OpenList，而是：

- 尽量降低用户“手工准备 OpenList”的门槛
- 让项目自己承担更多驱动接入与初始化辅助

## 7. Guangya 目标端规划

Guangya 是当前已完成最多的目标端，必须继续保留并增强。

后续 Guangya 侧重点：

- 保留已有登录抓取
- 自动刷新 access token / refresh token / authorization
- 持久化写回配置
- 秒传 JSON 直导继续增强
- MD5 / etag / gcid 兼容导入继续增强
- 小文件补传完成后自动删除本地缓存
- 目录自动创建逻辑继续保持

同时要把 Guangya 的能力沉淀成标准目标端适配器，而不是继续散落在同步器特殊分支里。

## 8. 页面重构目标

页面不能继续长滚动堆功能，后续统一改造成多 Tab + 折叠面板。

建议固定 Tab：

- `总览`
- `连接`
- `挂载`
- `源目录`
- `同步`
- `秒传`
- `补传`
- `日志`
- `关于`

页面原则：

- 左右布局平衡
- 日志独立抽屉，可固定/隐藏
- 配置与操作分区明确
- 复杂驱动说明用弹窗/抽屉，不挤占主操作区
- 所有描述支持：
  - 中文
  - English
  - 中英混合

## 9. 配置演进原则

旧配置要尽量兼容一版，同时逐步扩展到新结构。

### 9.1 旧配置兼容

保留现有关键字段兼容：

- `openlist_url`
- `openlist_token`
- `openlist_username`
- `openlist_password`
- `source_path`
- `target_path`
- `guangya_*`

### 9.2 新增结构

逐步引入更清晰的结构：

- `app`
- `ui`
- `openlist`
- `source_session`
- `targets`
- `rate_limit_profiles`
- `provider_captures`
- `sync`
- `state`

### 9.3 UI 状态持久化

页面状态也纳入配置/本地状态持久化，例如：

- 当前语言
- 当前选中 tab
- 面板展开/折叠状态
- 当前浏览目录
- 当前挂载选择
- 日志抽屉显示状态

## 10. 同步执行模型

继续保留并完善现有“最底层目录优先”的执行模型。

### 10.1 叶子目录优先

对大目录默认推荐：

- 先向下扫描
- 发现最底层目录
- 立即同步该最底层目录
- 再等待一段时间
- 再继续下一个最底层目录

这样可兼顾：

- 防风控
- 内存占用
- 任务可中断恢复
- 目录粒度日志更清晰

### 10.2 增量与覆盖判定

增量同步仍需要重新扫描源端，但判定规则要明确：

- 新文件：上传
- 已存在但大小/mtime/指纹变化：覆盖
- 已同步且未变：跳过
- 源端已删除：
  - 默认只记录
  - 是否删除目标端由策略决定

### 10.3 补传执行

补传树要继续支持：

- 目录层级显示
- 父子联动勾选
- 全选/全不选
- 按勾选目录的最底层顺序执行

## 11. 风控与频率策略

后续风控体系要做成可配置能力，而不是散在代码里的常量。

基础模式：

- `safe`
- `balanced`
- `fast`
- `custom`

同时支持按 provider 自动套默认值，例如：

- Baidu
- Quark
- 123
- Thunder
- 189Cloud
- AliyunDrive

后续可为每种网盘单独定义：

- 请求间隔
- 页面大小
- 目录间隔
- 冷却时间
- 重试次数
- 风控关键词

## 12. OpenList 新增驱动时的接入规范

为了让后续扩展可持续，新增驱动统一按下面的接入清单处理：

1. 在 driver registry 中登记基础元数据
2. 记录该驱动是否已有专属说明页
3. 补充推荐默认值
4. 补充推荐登录入口 URL
5. 标记它可能产出的哈希字段
6. 标记它当前支持的同步等级
7. 如有需要，增加专属网页登录抓取说明
8. 更新 README 与文档矩阵

也就是说，新增驱动不应该再靠：

- 页面里临时 if/else 堆字段
- README 临时加一段口头说明

而要进入统一 registry。

## 13. 分阶段实施路线

### Phase 0 已有基础整理

- 保留现有同步能力
- 保留 Guangya 目标端
- 保留 OpenList 挂载管理
- 保留现有抓取能力
- 清理文案与页面结构

### Phase 1 命名与计划统一

- 新建本文档
- README 与页面对外名称切换到 `CloudPan Bridge`
- 保留旧命令/旧启动脚本兼容
- 在代码中明确“OpenList 是源端底座，Guangya 是当前目标端”

### Phase 2 Provider Registry

- 引入统一 provider registry
- 把复杂驱动说明、默认值、登录入口、风险提示收敛到 registry
- 页面从 registry 读说明，而不是散落常量

### Phase 3 Fingerprint Bridge

- 提取统一文件指纹模型
- 统一 OpenList 元数据、秒传 JSON、后续网页登录抓取补充字段
- 为目标端秒传判断提供标准输入

### Phase 4 Target Adapter

- 把 Guangya 改造成标准目标端适配器
- 将同步器从“写死 Guangya 分支”改成“调用目标端接口”
- 为后续其它目标端预留位置

### Phase 5 Source Guidance 全覆盖

- 逐步完善所有 OpenList 驱动的流程说明、默认值、登录捕获建议
- 明确哪些驱动只能挂载浏览
- 明确哪些驱动适合秒传桥接
- 页面提供“驱动覆盖审计”，直接显示当前 OpenList 驱动列表里哪些已经接入 profile / guide / capture / capability

### Phase 6 能力矩阵与策略面板

- 页面展示源端/目标端能力矩阵
- 选择源或目标后立即提示推荐同步方式
- 给出：
  - 秒传优先
  - 中转流
  - 下载补传
  - 暂不支持
- 在已有目录分析结果时，继续给出动态执行建议：
  - 是否先分析
  - 是否优先最底层目录模式
  - 是否优先待补传树
  - 推荐频率节奏与当前目录的动作顺序

## 13.5 当前进展快照

截至 2026-05-19，以下主线已经有可运行落点：

- `Phase 1`
  - 新仓库、命名、主计划文档已经切到 `CloudPan Bridge`
- `Phase 2`
  - `provider_registry.py` 已承载复杂驱动说明、默认值、登录入口、风险提示
- `Phase 3`
  - 已有统一指纹模型与 OpenList 哈希字段标准化入口
- `Phase 4`
  - Guangya 已抽出目标端适配器基础结构
  - OpenList / LocalFS / WebDAV / FTP / SFTP 已具备真实可写目标端适配器
  - 已新增 `target_key`、目标端工厂与页面目标端选择点，当前默认仍为 `guangya`
  - 页面切换 `target_key` 后，能力矩阵、覆盖审计与导出链路都会按当前目标端实时刷新
- `Phase 5`
  - 页面已具备驱动覆盖审计、按缺口过滤、导出 JSON/Markdown、优先级 backlog
  - 覆盖审计已修正为按真实 capture spec 判断，不再把 source profile 误当作已具备抓取支持
  - 审计结果现在还能追踪 `guideDocUrl / captureSpecKey / captureMatchedAlias / captureLoginUrl`
  - guide 查询已支持 canonical key / alias 归一，`123Open / BaiduNetdisk / 189Cloud` 这类别名不再误报缺 guide
  - `GoogleDrive / Dropbox / 115` 已补成静态 profile / guide / capture / capability 条目，不再默认落回 generic 兜底
  - `WebDav / S3 / FTP / SFTP / Seafile / SMB / AzureBlob / Mega` 已补成静态条目，并新增“手动凭证模式”，不再误导成浏览器自动抓取型驱动
  - `OpenList / AListV3 / Cloudreve / Github / TeraBox / YandexDisk` 已补成静态条目；其中 `Sharepoint` 已并入 `OneDrive` 档案归一处理
  - `Alias / P123` 已补成静态条目，当前这批常见样本驱动在覆盖审计里已做到 `missing=0`
  - 当前这批重点驱动的已知显式缺口已清空，后续主要剩全 OpenList 驱动的继续扩面
  - 覆盖审计已新增 `onboardingReady / onboardingStage`，可直接筛出“已具备 profile、可以继续补 guide/capture/capability”的驱动
  - 覆盖审计 / Scaffold 现在在未手工传 `drivers` 时，可直接读取当前 OpenList 驱动列表生成缺口视图，便于后续跟进 OpenList 新增驱动
  - 对仓库里尚未建专用条目的驱动，只要拿到了 OpenList live driver fields，现在也能动态推断 profile / capture / 保守 capability，优先把缺口从 “add_profile_first” 收敛到更贴近真实情况的下一步
- `Phase 6`
  - 已有静态能力矩阵与基于目录分析结果的动态策略建议
  - 覆盖审计已支持 `nextAction / missingItem / capabilityLevel / profileKey` 高级筛选，且 backlog/导出保持一致
  - 页面状态恢复链路已进一步收口到 `grouped_config.ui`
  - `language / coverage_filters / browser / panel_open_states` 现在以正式分组配置为主，`localStorage` 仅保留迁移与启动兜底角色
  - 高频后端入口已大面积兼容 `grouped_config`
  - 已覆盖同步启动、执行链路、勾选补传执行、目录浏览、源分析、秒传诊断/导入、OpenList 登录、覆盖审计、能力判断、挂载与抓取辅助入口

仍未完成的重点：

- OpenList 全驱动 profile / guide / capture / capability 逐项补齐
- Guangya 之外的目标端适配器继续扩展
- 更完整的 README 场景建议与最终验收清单收口
- 配置结构虽然已支持新分组存储，但页面与接口层仍处于平面字段兼容过渡期
- 仍需继续清点剩余低频接口里的平面字段直读点，逐步收口到统一解析辅助函数

## 14. 验收标准

主计划落地后，每个阶段至少满足：

- `python -m compileall src tests`
- `pytest -q`

里程碑验收重点：

### 文档与命名

- 新主计划文档存在
- README 与页面主标题改到新名称
- 旧命令仍兼容

### 架构

- 能看到统一 registry / adapter / fingerprint 的代码落点
- 不再继续把复杂逻辑直接堆进单一页面脚本

### 体验

- 新用户能理解：
  - OpenList 的作用
  - Guangya 的作用
  - 哪些情况能秒传
  - 哪些情况只能补传

## 15. 对 README 的说明策略

README 后续要明确给出“推荐优先级”：

1. 有秒传 JSON：优先秒传 JSON 导入
2. 有 OpenList 哈希：优先源端元数据秒传
3. 小文件：可自动下载补传
4. 大文件：先挂待补传树，再分目录执行
5. 超大目录：优先最底层目录边扫边执行

## 16. 当前实施结论

从现在开始，本仓库不再继续以“天翼转光鸭脚本”的临时项目心态扩展，而是正式转入：

- `CloudPan Bridge`
- `OpenList 全源端接入`
- `Guangya 首个目标端`
- `统一能力矩阵`
- `统一指纹桥`
- `统一目标端适配器`

本文档就是后续所有重构和扩展的总入口。
