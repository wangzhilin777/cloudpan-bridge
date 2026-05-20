# CloudPan Bridge 下一阶段总计划（合并版）

## 实施进度

### 里程碑 1：运行时治理与控制台基础收口

- [x] 删除 GitHub Actions 自动 Docker 镜像发布链路
- [x] 修正托管 OpenList 的静默失败体验
- [x] 明确拆分 `external_local / external_remote / managed_binary / managed_docker`
- [x] 补齐控制台登录保护、模式独立配置和托管运行时状态展示
- [x] `managed_binary` 缺失二进制时提示拉取本机运行时
- [x] 外部模式与托管模式配置分组落地并兼容旧配置读取
- [x] 相关后端与前端测试通过：`python -m compileall src tests`、`pytest -q`

### 里程碑 2：OpenList Docker 托管模式落地

- [x] `managed_docker` 从占位升级为真实实现
- [x] Docker 运行时预检、状态展示、启动链路与容器重建逻辑落地
- [x] Docker 模式独立配置字段、UI 展示与 README 文案同步
- [x] 兼容旧配置 `managed_docker_placeholder` 读入并统一归档到 `managed_docker`
- [x] 相关后端与前端测试通过：`python -m compileall src tests`、`pytest -q`

### 后续里程碑待推进

- [ ] 统一 Source / Target Provider 抽象与挂载驱动映射层
- [ ] 秒传决策器与补指纹链路全面落地
- [ ] 页面主流程完全切到“连接 -> 源端 -> 目标端 -> 任务 -> 执行”
- [ ] 已支持连接网盘统一纳入互传与秒传优先框架

### 里程碑 3：前端入口拆分与主流程重排（进行中）

- [x] `index.html` 拆为入口壳 + `assets/app.css` + `assets/app.js`
- [x] 再将 `app.js` 内的大型静态字典拆为 `assets/app.data.js`
- [x] 补齐 `/assets/*` 静态资源路由，入口页与拆分资源可独立请求
- [x] 当前标签页顺序重排为“总览 / 连接 / 源端 / 目标端 / 任务执行 / 补传 / 快传能力 / 能力与关于”
- [x] `source_path / target_key / target_path` 收拢到“任务执行”主区域
- [x] Source / Target / Task 的文案、状态摘要和能力面板继续细化
- [x] 本地验证通过：`/`、`/assets/app.css`、`/assets/app.js`、`/assets/app.data.js` 请求 200，`node --check` 通过，`pytest -q` 通过

### 里程碑 4：超大 Python 文件拆分（进行中）

- [x] 识别当前超出阈值的 Python 文件，并优先处理 `provider_registry.py`
- [x] 将 `provider_registry.py` 内的大型静态常量拆到 `provider_registry_data/` 子模块
- [x] 将主逻辑文件 `provider_registry.py` 压缩到 100 KB 以内（当前约 60.6 KB）
- [x] 拆分后编译与测试通过：`python -m compileall src tests`、`pytest -q -x`、`pytest -q`
- [ ] 继续评估是否还需要对 `webapp.py`、`provider_capture.py`、`target_adapter.py` 做进一步细拆

### 里程碑 6：挂载驱动到 Source Profile 映射层（起步）

- [x] 前端加入“源 Profile 覆盖”入口，可针对当前挂载源手动指定 source profile
- [x] 覆盖值写入 `grouped_config.source_session.mount_provider_mapping`
- [x] `AppConfig` 正式接入 `mount_provider_mapping`，并补齐 round-trip 回归测试
- [x] 当前驱动上下文优先读取覆盖值，再决定源端能力评估
- [x] 覆盖保存/清除后会联动刷新源端摘要与任务能力判断
- [x] 后端补齐正式的 `source_mapping` 读取/写入接口，并覆盖保存、清除、回读测试
- [x] `provider/registry` 与 `provider/capability_assess` 返回 `sourceMappingContext`，明确当前挂载源的 override/effective driver
- [x] `load_grouped_config_payload()` 兼容显式 `grouped_config` 读入，避免映射上下文在只读场景下丢失
- [x] 前端源端摘要与能力面板显示后端 `sourceMappingContext`，前后端对当前 effective driver 的认知保持一致
- [x] 将 mapping 结果进一步写回更多矩阵展示与实际同步执行链路

## 摘要

把现有 `cloudpan-bridge-next-stage-plan.md` 的“控制台重构 / OpenList 模式拆分 / 托管闭环 / 多目标端框架”与新的“已支持连接或可手动补到 OpenList 的网盘，统一互传且秒传优先”要求合并为一份总计划。

合并后的最终目标是：

- CloudPan Bridge 不再只是“OpenList 源端 -> Guangya 主目标端”的工具
- 而是升级为“统一源端 -> 统一目标端”的多网盘互传控制台
- 凡是当前已经支持连接，或者用户已经能手动接入 OpenList 并稳定浏览目录的网盘
- 都必须进入统一任务流
- 都必须支持互传
- 都必须执行“秒传优先，不能秒传再补传”
- 控制台页面、配置结构、运行时模式、日志、文档、能力矩阵全部围绕这条主线统一

这份计划同时保留上一版计划里已经明确的高优先级治理项：

- 删除 GitHub Actions 自动 Docker 镜像发布链路
- 修正托管 OpenList 的静默失败体验
- 明确拆分 `external_local / external_remote / managed_binary / managed_docker`
- 补齐控制台登录保护、模式独立配置和托管运行时状态展示

## 总体实施目标

### 1. 产品目标

CloudPan Bridge 要成为一个桌面优先的多网盘桥接控制台，支持：

- 连接 OpenList 已挂载网盘
- 连接已有直连 provider 的网盘
- 以任意已连接网盘作为源端
- 以任意已连接网盘作为目标端
- 执行目录级同步
- 执行最底层目录边扫边同步
- 执行待补传树补传
- 在可行时优先秒传
- 在不可行时自动降级补传
- 保存并恢复任务状态、目录状态、连接状态和面板状态

### 2. 秒传优先目标

“秒传优先”作为硬规则写入计划：

- 只要当前源端文件指纹满足目标端秒传条件，就必须先走秒传
- 不能因为实现偷懒而直接全部走下载上传
- 不能因为 OpenList 当前未返回足够哈希，就直接判定不可秒传
- 必须先尝试：
  - 复用 OpenList 已返回字段
  - 必要时走 provider 直连补指纹
- 只有在“源端拿不到、补指纹失败、目标端不支持”都确认之后，才进入普通上传/补传

### 3. 范围定义

本轮纳入统一互传体系的对象是：

- 当前仓库里已经支持连接的网盘
- 当前仓库里已经有抓取、说明、字段模板、挂载辅助的网盘
- 当前用户可通过页面手动补字段并成功接入 OpenList 的网盘
- 当前用户已经挂载成功、并能稳定浏览目录的 OpenList 驱动

换句话说，范围不再按“当前是否已有完整 target adapter”来界定，而是按“当前是否已可接入并形成稳定连接”界定。

## 架构总改造

### 1. 统一双栈架构

保留并强化双栈：

- `OpenList 栈`
- `直连 Provider 栈`

#### OpenList 栈职责

- 驱动列表
- 驱动字段
- 挂载创建
- 挂载列表
- 已挂载目录浏览
- 已有 token/登录态复用
- 部分文件哈希与元数据读取
- 本机托管或外部连接

#### 直连 Provider 栈职责

- 浏览器抓取登录态
- 手动字段接入
- 专有 token/header/session 管理
- 指纹补齐
- 目标端秒传调用
- 目标端普通上传/覆盖
- 特殊目标端写入逻辑

#### 执行优先级

每次任务固定按以下顺序：

1. 确定源端 provider 与目标端 provider
2. 若源端来自 OpenList 挂载，优先用 OpenList 浏览与读基础元数据
3. 若基础指纹不足，调用源端直连 provider 补齐指纹
4. 若目标端存在真实秒传接口，优先尝试 `try_fast_upload`
5. 未命中或不支持时，走普通上传/覆盖
6. 失败项进入待补传体系

### 2. Provider 抽象统一

#### Source Provider 接口

所有已支持连接的网盘都要统一具备：

- `list_roots`
- `list_dir`
- `walk_tree`
- `walk_leaf_dirs`
- `get_file_fingerprints`
- `download_stream`
- `get_auth_state`
- `get_provider_key`

#### Target Provider 接口

所有已支持连接且可作为目标端的网盘都要统一具备：

- `ensure_target_dir`
- `preflight_capability`
- `try_fast_upload`
- `upload_stream`
- `delete_if_enabled`
- `export_state`
- `close`

#### Auth / Connection Provider 接口

所有已支持连接的网盘都统一描述：

- `auth_mode`
- `browser_capture`
- `manual_fields`
- `openlist_mount`
- `direct_api`
- `docs`
- `recommended_defaults`

### 3. 挂载驱动到 Provider 的映射层

新增统一 `mount_provider_mapping` 机制，把：

- OpenList driver name
- driver aliases
- capture definitions
- source profile aliases
- 用户手动映射

归一成：

- `provider_key`
- `source_mode`
- `target_mode`
- `supports_fingerprint_enrichment`
- `supports_direct_target_write`
- `supports_fast_upload`
- `fallback_strategy`

支持用户手动覆盖映射：

- 冷门驱动或新驱动允许手工指定 provider
- 若无明确 provider，先归到通用 `generic_openlist_driver`
- 仍能互传，但默认按保守能力处理
- 后续通过 registry 持续补全

## OpenList 模式与运行时计划

### 1. OpenList 模式重构

统一固定为四种模式：

- `external_local`
- `external_remote`
- `managed_binary`
- `managed_docker`

兼容旧配置读取，但保存时一律写回新结构。

### 2. 外部与托管语义彻底拆开

配置与 UI 必须明确分开：

- 当前连接实例 URL / token / 用户名 / 密码
- 托管运行参数
- 托管初始化管理员参数
- Docker 托管参数
- 控制台管理员参数

不再混用一套 `openlist_url / username / password / token`。

### 3. managed_binary 闭环

固定流程：

1. 预检本机 `openlist.exe/alist.exe`
2. 若不存在，明确提示是否拉取本机运行时
3. 用户同意则下载到项目运行目录
4. 下载完成后再次预检
5. 启动托管实例并回写状态
6. 若用户拒绝，则引导改用外部模式或直连 provider

不能再出现“点了没反应”的静默失败。

### 4. managed_docker 从占位升级为真实实现

这版总计划里，`managed_docker` 不再只占位，而是纳入正式落地：

- 检测 Docker CLI 与 daemon 可用性
- 若本机无 Docker，页面和 README 明确提示安装与验证步骤
- 若有 Docker，允许创建和启动 OpenList 容器
- 托管 Docker 的端口、卷目录、管理员初始化参数独立保存
- 如果用户不接受 Docker 方案，可回退 `managed_binary` 或外部模式

### 5. 托管初始化管理员策略

必须明确区分：

- OpenList 连接账号
- 托管初始化管理员
- 托管运行参数
- CloudPan Bridge 控制台管理员

规则固定：

- 托管初始化管理员单独保存
- 若用户未填，可自动生成建议密码
- 若底层 OpenList 不支持启动时自动初始化管理员，则页面和日志明确提示：
  - 当前只负责下载/启动
  - 不保证自动写入管理员账号密码

## 秒传与补传计划

### 1. 统一文件指纹模型

所有源端文件统一归一为：

- `size`
- `md5`
- `sha1`
- `sha256`
- `gcid`
- `etag`
- `crc64`
- `pre_hash`
- `slice_md5`
- `pickcode`
- `content_hash`
- `provider_specific`

OpenList 返回值和直连 provider 返回值都先映射成这套模型。

### 2. 目标端秒传能力声明

每个目标端 provider 必须声明：

- 是否支持元数据秒传
- 需要哪些字段
- 是否只支持部分字段组合
- 是否支持跨品牌 metadata import
- 是否需要 session / preflight
- 是否只能普通上传

### 3. 统一秒传决策器

每个文件执行固定流程：

1. 读取 OpenList 可见指纹
2. 判断是否满足目标端秒传条件
3. 若不足，调用源端 provider 补指纹
4. 再次判定
5. 满足则秒传
6. 不满足则补传

目录级别同时做聚合判断：

- 全部可秒传
- 部分可秒传
- 需补指纹后再判断
- 只能补传

### 4. 秒传等级标准

统一在 UI、日志、状态里展示：

- `native_fast_upload`
- `fast_upload_after_enrichment`
- `partial_fast_upload`
- `upload_only`
- `download_then_upload`
- `unsupported`

### 5. 补传体系统一

补传来源统一包括：

- 秒传未命中
- 秒传失败
- 缺少必要指纹
- 目标端不支持秒传
- 上传失败
- 临时网络失败

保留并统一现有执行模式：

- 小文件自动补传
- 当前目录直接补传
- 最底层目录边扫边补传
- 待补传树按目录勾选补传
- 待补传树按最底层顺序补传

### 6. 目标端补传能力要求

所有可作为目标端的已连接网盘都要具备：

- 自动创建目标目录
- 普通文件上传
- 已存在文件覆盖
- 删除开关支持
- 失败日志记录
- 状态回写
- 断点续跑协同

## 页面与交互计划

### 1. 页面主流程统一

主流程收敛为：

1. 控制台登录
2. 连接层
3. 源端配置
4. 目标端配置
5. 任务配置
6. 执行与结果
7. 待补传
8. 能力矩阵与文档

### 2. Tab 重新定义

建议固定为：

- `Overview`
- `Connections`
- `Source`
- `Target`
- `Task`
- `Run`
- `Pending`
- `Capability`
- `About`

### 3. Source / Target 对称化

源端和目标端页面都必须支持：

- 选择 provider
- 选择连接方式
- 查看连接状态
- 查看目录
- 查看当前能力
- 查看当前限制
- 查看接入说明
- 查看推荐默认值
- 手动覆盖映射

### 4. 当前任务区集中化

必须集中显示：

- 当前源 provider
- 当前源路径
- 当前目标 provider
- 当前目标路径
- 当前 OpenList 模式与状态
- 当前源指纹覆盖率
- 当前目标端秒传等级
- 当前推荐执行模式
- 当前补传策略
- 当前删除策略

### 5. 登录保护规则

未完成控制台登录时：

- 只显示登录区和必要说明
- 不显示任务配置
- 不显示同步执行区
- 不显示补传执行区
- 不显示能力操作按钮

### 6. 目标端专属入口动态显示

- Guangya 专属秒传 JSON 直导仅在 Guangya 目标端下显示
- 其它目标端若后续存在真实快传入口，也按同一模式动态显示
- 非真实支持秒传的目标端，不显示误导性的秒传执行按钮

## 配置、状态与持久化计划

### 1. 配置结构统一升级

新增或拆分为：

- `console_admin`
- `openlist_profiles`
- `provider_connections`
- `source_session`
- `target_session`
- `mount_provider_mapping`
- `task_profile`
- `capability_cache`
- `sync_state`
- `ui_state`
- `runtime_profiles`

### 2. Source / Target 独立配置

同一 provider 必须支持：

- 源端账号
- 目标端账号
- 不同连接方式
- 不同根目录

不能再复用一套单实例字段。

### 3. 目录与面板状态恢复

重新进入页面时需要恢复：

- 当前 active tab
- 面板折叠状态
- 当前浏览目录
- 当前挂载选项
- 当前源端/目标端 provider
- 当前任务配置
- 当前补传筛选与勾选状态

### 4. 能力预检缓存

缓存以下信息，避免切页重复计算：

- 当前目录指纹覆盖率
- provider 映射结果
- 目标端秒传能力
- 当前组合推荐执行模式
- 最近一次补指纹结果

## 文档与表达统一计划

### 1. README 统一口径

README 需要统一为：

- CloudPan Bridge 是多网盘互传控制台
- OpenList 是统一接入层，不是唯一运行前提
- 已支持连接或已挂载成功的网盘，都能进入统一互传任务流
- 秒传优先不是 Guangya 专属概念，而是系统执行规则
- 但是否真正秒传成功，取决于源端指纹与目标端真实接口能力

### 2. 新增说明章节

必须新增：

- 外部模式与托管模式区别
- managed_binary 与 managed_docker 的区别
- 什么叫“支持连接”
- 什么叫“支持秒传”
- 什么叫“补指纹”
- 什么叫“补传”
- 为什么能连接不等于一定能跨品牌秒传
- 当前各 provider 的能力分层

### 3. About / Capability 页面统一

必须展示：

- source profiles
- target profiles
- provider matrix
- 挂载驱动覆盖审计
- 当前已支持连接网盘清单
- 当前已支持秒传网盘清单
- 当前只支持补传的网盘清单

## CI、Docker 与风险治理计划

### 1. CI 风险项保留

继续保留原计划要求：

- 删除 GitHub Actions 里在 `push` 时自动构建/推送 Docker 镜像的链路
- 保留 Python 编译、测试、打包
- Docker 构建只作为本地或手动流程，不作为默认 push 行为

### 2. Docker 环境预检

页面和 README 必须支持：

- 检测本机是否有 Docker
- 无 Docker 时给出安装与验证步骤
- 有 Docker 时给出可用状态
- 允许进入 `managed_docker` 运行时流程

## 测试计划

### 1. 控制台与运行时

- 未登录时主操作区不可见或不可交互
- 登录后按主流程显示
- `external_local / external_remote / managed_binary / managed_docker` 独立保存并恢复
- 无二进制时会提示拉取
- 无 Docker 时会提示安装
- 有 Docker 时能进入容器托管流程

### 2. 连接层

- 已有专用 provider 的网盘可进入连接态
- 用户手动补到 OpenList 的网盘可进入任务流
- OpenList 外部实例与托管实例都可读挂载和列目录
- 无 OpenList 时，已支持直连 provider 仍可工作

### 3. 源端能力

- 所有已支持连接网盘都能：
  - 选目录
  - 浏览目录
  - 输出源分析
  - 输出统一指纹模型

### 4. 秒传能力

- Guangya 保持正式秒传主实现
- 满足条件时必须优先秒传
- OpenList 指纹不足时会先补指纹
- 非真实支持秒传的目标端不会误报秒传成功

### 5. 补传能力

- 所有已接通目标写入的目标端都能：
  - 自动建目录
  - 上传
  - 覆盖
  - 失败重试
  - 写回待补传状态

### 6. 任务执行

- 当前目录同步
- 最底层目录边扫边同步
- 勾选补传目录执行
- 断点续跑
- 新增文件同步
- 修改文件覆盖同步
- 删除开关独立控制

### 7. 文档与文案

- README、页面文案、日志、矩阵口径一致
- 不把中转上传包装成秒传
- 不把“已支持连接”误写成“已完整秒传支持”

## 假设与默认值

- 本轮范围按“已支持连接或已成功挂载到 OpenList 的网盘”定义
- 这些网盘都必须进入统一互传体系
- 这些网盘都必须执行秒传优先判定
- OpenList 不足时默认尝试 provider 直连补指纹
- 默认同步语义仍是“新增 + 覆盖”
- 删除仍为独立开关
- Windows 桌面仍是首要场景
- 文案、日志、能力矩阵必须始终诚实，不把普通上传写成秒传
