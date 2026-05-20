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
- [x] 继续评估并落地首轮细拆：已把 `webapp.py` 的运行时节流/待补传分组工具提到独立模块，主文件继续维持在 100 KB 内

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

### 里程碑 7：Target Provider 统一预检能力（起步）

- [x] `target_adapter.py` 正式补齐 `preflight_capability()` 能力声明入口，目标端不再只有“能否创建 adapter”
- [x] `/api/target/preflight` 接入真实 adapter 预检结果，返回 `configured / missing_fields / fast_upload_hashes / fallback_modes / write_mode`
- [x] Guangya / OpenList / WebDAV / S3 / Seafile / SMB / FTP / SFTP / Azure Blob 的目标端能力说明统一下沉到 adapter 层
- [x] 前端目标端预检面板显示真实运行前能力与缺失配置，而不是只显示 implemented/selectable
- [x] 相关回归通过：`python -m compileall src tests`、`node --check src/cloudpan_bridge/web/assets/app.js`、`pytest -q tests/test_sync_logic.py -x`

### 里程碑 8：Source Provider 执行主链抽象（起步）

- [x] 新增 `source_adapter.py`，定义 `SourceProvider` 协议与 `OpenListSourceProvider` 首个实现
- [x] `SyncRunner` 不再直接构造 `OpenListClient`，而是通过 `create_source_provider()` 获取源端 provider
- [x] 执行主链已切换为 `ensure_auth / walk_tree / download_stream` 抽象入口，并保留对旧 `ensure_login / export_tree / download_file` 的兼容回退
- [x] 新增 Source Provider 基础测试，验证 provider key / auth state / factory / SyncRunner 注入链路
- [x] 相关回归通过：`python -m compileall src tests`、`pytest -q tests/test_sync_logic.py -x`

### 里程碑 9：统一文件指纹模型第一层落地（起步）

- [x] `SourceEntry / SyncFileState / PendingFileState` 扩充为统一指纹字段集合：`sha256 / pre_hash / slice_md5 / content_hash / provider_specific`
- [x] `OpenListClient._extract_hash_fields()` 已统一提取扩展指纹字段，并将底层特有值归入 `provider_specific`
- [x] 源分析序列化、秒传 JSON 预览、状态持久化、待补传恢复链路已统一携带扩展指纹字段
- [x] 源摘要统计已补充 `sha256 / pre_hash / slice_md5 / content_hash` 覆盖率
- [x] 相关回归通过：`python -m compileall src tests`、`pytest -q tests/test_sync_logic.py -x`

### 里程碑 10：目录级秒传决策第一层落地（起步）

- [x] 新增 `fast_upload_decision.py`，统一输出目录级秒传等级：`native_fast_upload / fast_upload_after_enrichment / partial_fast_upload / upload_only / download_then_upload / unsupported`
- [x] `provider/capability_assess` 已回传 `fastUploadDecision`，把源分析摘要与目标端真实能力合并成目录级判断
- [x] `source/analyze` 与 `source/miaochuan_preview` 已返回 `target_key + fastUploadDecision`，前端可以直接显示“当前目录秒传决策”
- [x] 前端源分析摘要面板已显示目录级秒传等级、分桶与中英文解释
- [x] 相关回归通过：`python -m compileall src tests`、`node --check src/cloudpan_bridge/web/assets/app.js`、`pytest -q tests/test_sync_logic.py -x`

### 里程碑 11：执行期补指纹第一层闭环（起步）

- [x] `OpenListClient` / `OpenListSourceProvider` 已补齐单文件指纹读取入口，支持按文件路径回查当前目录下的真实元数据
- [x] `SyncRunner` 在执行元数据秒传前，若首轮扫描缺少 `MD5/GCID`，会先调用 `get_file_fingerprints()` 尝试补指纹
- [x] 补指纹成功后会直接复用刷新后的 `SourceEntry` 继续秒传，并将增强后的指纹写回同步状态
- [x] 补指纹后仍缺少秒传指纹时，会明确记录日志并以“未命中秒传库存”进入待补传，而不是继续沿用“新增文件/源文件已修改”这类计划原因
- [x] 相关回归通过：`python -m compileall src tests`、`pytest -q tests/test_sync_logic.py -k "enriches_missing_fast_upload_fingerprint_before_direct_sync or enrichment_still_lacks_fast_upload_fingerprint"`、`pytest -q tests/test_sync_logic.py -x`

### 里程碑 12：补指纹能力提示贯通到矩阵与页面（起步）

- [x] `sourceProfile` 序列化结果已显式返回 `supportsFingerprintEnrichment`
- [x] `provider/capability_assess` 在目录级判断为 `fast_upload_after_enrichment` 时，会把推荐模式切到 `enrich_then_direct`
- [x] 若当前源 Profile 已声明支持补指纹，能力建议会明确提示执行期会先回查单文件元数据
- [x] 前端能力面板与 About 源 Profile 列表已显示“补指纹能力”状态
- [x] 相关回归通过：`python -m compileall src tests`、`node --check src/cloudpan_bridge/web/assets/app.js`、`pytest -q tests/test_sync_logic.py -k "prefers_enrichment_mode_when_directory_needs_more_hashes or provider_capability_assess_uses_analysis_summary"`

### 里程碑 13：前端主流程门控与登录壳页收口（起步）

- [x] 新增控制台锁屏壳页，启用控制台管理员时未登录不再直接展示后续连接/源端/目标端/同步界面
- [x] 补齐前端缺失的控制台登录运行时函数：`updateAuthUi / showAuthDialog / hideAuthDialog / ensureAuthorizedAndBootstrap / startAutoRefresher / stopAutoRefresher`
- [x] 总览页新增四阶段路线卡：`连接 OpenList -> 选择源目录 -> 配置目标端 -> 执行任务`
- [x] 标签页已按当前阶段 readiness 做门控，未满足前置条件时会禁用对应页签并给出说明
- [x] 增加首页壳页测试，固定 `auth-lock-panel / workflow-roadmap` 等关键容器
- [x] 相关回归通过：`python -m compileall src tests`、`node --check src/cloudpan_bridge/web/assets/app.js`、`pytest -q tests/test_sync_logic.py -x`

### 里程碑 14：Target Provider 抽象兼容层第一步（起步）

- [x] `target_adapter.py` 已补统一 helper：`target_upload_stream / target_delete_if_enabled`
- [x] `SyncRunner` 已改为优先走统一 helper，而不是直接依赖旧的 `upload_local_file / delete_if_exists` 命名
- [x] 新旧目标端方法名可以共存，后续新适配器可逐步向 `upload_stream / delete_if_enabled` 迁移
- [x] 相关回归通过：`python -m compileall src tests`、`pytest -q tests/test_sync_logic.py -k "target_adapter_upload_stream_helper_falls_back_to_legacy_upload_method or target_adapter_delete_helper_prefers_new_delete_if_enabled_method or enriches_missing_fast_upload_fingerprint_before_direct_sync"`、`pytest -q tests/test_sync_logic.py -x`

### 里程碑 15：Target Provider 统一方法名下沉到类本身（起步）

- [x] 新增 `TargetAdapterCompatMixin`，把 `upload_stream / delete_if_enabled` 兼容实现下沉到目标端类层
- [x] Guangya / OpenList / LocalFS / WebDAV / S3 / Seafile / SMB / Azure Blob / FTP / SFTP 目标端类都已接入该 mixin
- [x] 新增真实适配器回归，确认 `LocalFsTargetAdapter` 这类正式目标端实例可以直接调用统一方法名
- [x] 相关回归通过：`python -m compileall src tests`、`pytest -q tests/test_sync_logic.py -k "target_adapter_compat_mixin_exposes_unified_methods_on_real_adapter or target_adapter_upload_stream_helper_falls_back_to_legacy_upload_method or target_adapter_delete_helper_prefers_new_delete_if_enabled_method"`、`pytest -q tests/test_sync_logic.py -x`

### 里程碑 16：Source Provider 统一方法名下沉到抽象层（起步）

- [x] `source_adapter.py` 新增统一 helper：`source_ensure_auth / source_walk_tree / source_download_stream / source_get_file_fingerprints`
- [x] 新增 `SourceProviderCompatMixin`，把 `ensure_auth / walk_tree / download_stream` 兼容实现下沉到源端类层
- [x] `SyncRunner` 已改为优先走统一 source helper，不再直接散落 `hasattr` 分支
- [x] 新增 source provider helper / compat mixin 回归，确认 legacy source 与真实 mixin provider 都能走统一入口
- [ ] 后续继续把更多直连源 provider 纳入该抽象，而不是只停留在 OpenList 首个实现

### 里程碑 17：`webapp.py` 运行时工具首轮拆分（起步）

- [x] 新增 `web_runtime_utils.py`，承接风控节流判定、冷却时间计算、待补传目录分组等纯工具逻辑
- [x] `webapp.py` 改为引用独立运行时工具模块，避免继续把非路由逻辑堆在主入口里
- [x] 原有回归测试已改为直接覆盖新模块，接口语义保持不变
- [x] 相关回归通过：`python -m compileall src tests`、`node --check src/cloudpan_bridge/web/assets/app.js`、`pytest -q tests/test_sync_logic.py -k "pending_selected_execution_groups_run_deepest_directories_first or source_provider_helpers_fall_back_to_legacy_methods or rate_limit_cooldown"`、`pytest -q tests/test_sync_logic.py -x`

### 里程碑 18：前端主流程拆成“任务 / 执行”双阶段（起步）

- [x] 原 `sync` 页签已拆为 `task` 与 `execute` 两个独立阶段，分别承载任务配置与正式执行
- [x] 主流程路线卡已扩成五段：`连接 -> 源端 -> 目标端 -> 任务 -> 执行`
- [x] 前端门控与快捷动作已同步更新，执行类动作默认跳到 `execute`，兼容旧 `sync` 标签页状态回写
- [x] 首页壳页测试已补充 `task / execute` 标签存在性检查
- [ ] 后续仍需继续梳理“补传 / 秒传能力 / 关于”与主流程的边界，决定是否进一步弱化次级页签

### 里程碑 19：挂载驱动映射上下文升级为统一 Provider 语义（起步）

- [x] `provider_registry.py` 新增统一 `build_source_mapping_context()`，把 mount override、source profile、target capability 归一为标准 provider 语义
- [x] `/api/provider/registry`、`/api/provider/capability`、`/api/provider/capability_assess` 现已返回扩充后的 `sourceMappingContext`
- [x] 映射上下文已显式给出 `provider_key / source_mode / target_mode / supports_fast_upload / fallback_strategy` 等统一字段
- [x] 对未知挂载驱动统一归入 `generic_openlist_driver`，并明确保守降级策略，而不是只回一个裸 `generic`
- [ ] 后续仍需把这套统一 provider 语义继续接入更多直连 source provider，而不是只停留在 OpenList 挂载源

### 里程碑 20：`/api/provider/captures` 升级为统一连接 Provider Catalog（起步）

- [x] 保留现有抓取定义输出，同时补齐 `provider_key / auth_mode / auth_interface` 等标准字段
- [x] `auth_interface` 已统一描述 `browser_capture / manual_fields / openlist_mount / direct_api / docs / recommended_defaults`
- [x] `/api/provider/registry` 现已回传 `provider_catalog`，让前后端都能基于同一份连接 provider 目录工作
- [x] 相关回归覆盖了复杂驱动的 catalog 输出，不破坏现有 `provider captures` 页面消费
- [ ] 后续仍需把 catalog 与真正的直连 source provider 实现逐步绑实，而不是只停留在连接/抓取描述层

### 里程碑 21：统一 Source Provider 上下文下沉到 adapter/factory（起步）

- [x] `source_adapter.py` 新增 `build_source_provider_context / resolve_source_mount_path / source_get_runtime_context`
- [x] `create_source_provider()` 现会把统一 provider 语义写入 source provider runtime context，而不再只返回裸 OpenList client 包装
- [x] `SyncRunner` 已持有并记录 source provider runtime context，执行主链可以直接看到 `provider_key / source_mode / effective_driver`
- [x] `webapp.py` 的 source mapping 解析已复用 source adapter helper，避免页面侧和执行侧再维护两套路径
- [ ] 后续仍需把这份 runtime context 进一步用于选择真正的直连 source provider，而不是目前先统一到 OpenList 首个实现

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
