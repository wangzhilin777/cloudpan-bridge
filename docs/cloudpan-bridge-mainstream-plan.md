# CloudPan Bridge 主流网盘互传与秒传优先总计划（首批主流版）

## 当前进度

- [x] 建立 `source_enrich.py` 与 `transfer_planner.py` 的主骨架
- [x] 把补指纹运行态、传输预览接入 `/api/source/analyze`、`/api/source/miaochuan_preview`、能力矩阵摘要
- [x] 为首批主流源端建立差异化补指纹规则表，避免把所有 provider 的 `etag` 都误判成 `md5`
- [x] 把补指纹运行态与目标能力摘要接入 `/api/status` 和任务摘要区
- [x] 拆出前端工作流摘要脚本 `app.workflow.js`，降低 `app.js` 耦合
- [x] 建立首批主流源端的 `bridge_runtime` / hook 结构，明确缺失字段、桥接成熟度和下一步动作
- [x] 建立 `source_bridge_registry.py`，把首批主流源端桥接入口收敛为统一 registry / preparation 结果
- [x] 把 `source_enrich` 主执行路径切到 bridge executor，统一 session snapshot / API pending 两类执行语义
- [x] 为 bridge executor 补充 provider 级候选哈希、pending 原因与执行状态报告
- [x] 让 `source analyze / miaochuan preview` 基于 enrich 后视图输出 bridge batch 摘要
- [x] 让 `transfer_planner` 读取 bridge 候选哈希与挂起原因，并把原因汇总到传输预览
- [x] 把会话桥接 `bridge_ready` 与 API pending 路由语义拆开，避免运行态继续把已可归并的 provider 标成 pending
- [x] 拆出 `app.drivercapture.js`、`app.pending.js`，把驱动抓取面板与待补传目录树从 `app.js` 剥离
- [x] 继续拆出 `app.registry.js`、`app.status.js`、`app.capability.js`，把关于页审计、运行概览和能力动作逻辑继续从 `app.js` 剥离
- [x] 再拆出 `app.runtimeview.js`，把同步状态、运行时状态、目标端抓取状态从 `app.js` 剥离，并把 `app.js` 压回 `100 KB` 优先线附近
- [x] 支持从 `content_hash / etag` 里解析可识别的 `md5 / sha1` 候选，提升主流 provider 的补指纹命中率
- [x] 收紧 API placeholder bridge 的 `pending_reason`，避免文件本身已具备快传哈希时仍被误记成 API pending
- [x] 让传输预览继续输出 `reason_code / bridge_provider_stage / bridge_transport_hint` 等诚实摘要，避免页面只剩 mode 计数
- [x] 目录分析样本条目附带 `transferPlan`，页面可直接看到当前文件会走快传、普通上传还是仅记录待补传
- [x] 新增 `app.bridgeview.js`，把桥接挂起原因、桥接阶段、传输原因与执行模式文案从 `app.workflow.js` 剥离
- [x] 把 `bridge_preparation_summary` 扁平化到 `sourceEnrichment` 运行态，直接暴露预期补指纹、命中字段组与 transport hint
- [x] 页面摘要已显示主流 provider 的 bridge 准备态细节，不再只显示 `bridge_ready_but_api_pending` 这类状态码
- [x] 新增 `bridge_maturity_summary`，把会话快照 ready、API 准备态、缺 capture、未注册 bridge 等阶段显式分层
- [x] 为 `189Cloud / Quark / 123Pan / Baidu / Thunder / AliyunDriveOpen / OneDrive` 继续补专用 enrich/runtime 回归，强化首批主流 provider 覆盖
- [x] 将 bridge 成熟度落到文件级 `transferPlan` 与目录级预览分桶，页面能直接看到当前目录主要卡在哪个 bridge 层级
- [x] 收紧 `source_adapter` 选路语义，API 型 provider 不再误记为 `direct_provider_ready`，而是单独落到 `api_pending / capture_gap` 分支
- [x] API 型 provider 的文件级规划会继续暴露“理论预期哈希 / 当前仍缺哈希”，不再只停留在笼统的 pending 原因
- [x] 页面摘要与目录分析样本已显示 API provider 的预期哈希缺口，目录级也会统计当前最缺哪些预期哈希
- [ ] 深化首批主流源端的真实直连补指纹桥接实现
- [x] 继续拆分前端与过大的 Python/JS 文件，优先压到单文件 `100 KB` 左右，并按统一分级阈值治理
- [x] 完成更多主流 provider 的互传能力验证与 UI 诚实提示收口

### 最近推进记录

- 已补齐 `source_bridge_executor.py` 对 `hashes[] / file_hashes[] / algorithm-value` 类结构的识别
- 现在支持从以下额外结构补指纹：
  - `[{algorithm:\"sha1\",value:\"...\"}]`
  - `[{name:\"gcid\",hash:\"...\"}]`
  - 字符串化 JSON 的同类 `hashes` 数组
- 已新增对应回归，确保 `Quark / Thunder` 这类主流 provider 的嵌套哈希载荷可进入统一 enrich 流水线
- API 型 bridge 已支持从 `provider_captures` 里的文件级哈希缓存补指纹
- 当前已覆盖的缓存结构包括：
  - `file_hashes_by_path / fingerprints_by_path`
  - `file_hashes_by_id / fingerprints_by_id`
  - `entries / items / file_hashes` 列表中的按 `path / source_id` 匹配条目
- 这让 `AliyunDriveOpen / OneDrive / Thunder` 这类 API 型 provider 不再只能停留在“纯占位准备态”，而是可以先消费已抓到的文件级指纹快照
- 页面与传输规划摘要已开始区分两种 API 型阶段：
  - `api_bridge_prepared_but_not_executed`
  - `api_capture_cache_normalized`
- 当前如果只是吃到了抓取缓存，但还没补齐目标端真正可用的快传哈希，会在页面上诚实显示为：
  - 抓取缓存补指纹已生效
  - 仍不是在线直连 enrich
  - 下一步应继续扩抓取缓存或再执行真实 provider API enrich
- 前端继续拆分了一轮：
  - 新增 `app.sourceops.js`
  - 将目录浏览、挂载列表、队列、秒传诊断、驱动字段渲染从 `app.js` 剥离
- 当前 `app.js` 已从约 `97.4 KB` 继续压到约 `88.8 KB`，回到统一体积分级阈值的黄色区下半段
- 运行态现在会先暴露 API 型 provider 的抓取缓存摘要：
  - 是否已有文件级哈希缓存
  - 缓存条目数
  - 按 `path / source_id / collection_scan` 哪种方式可命中
  - 缓存里大概有哪些哈希类型
- `source_target_route` 也新增了这条诚实分支：
  - `api_capture_cache_candidate`
  - 表示“当前应先消费抓取缓存，再决定是否真的要走在线 provider API enrich”
- 页面摘要现在也会直接显示这些抓取缓存信号：
  - 缓存条目数
  - `path / source_id / collection_scan` 哪种查找方式可用
  - 缓存里当前有哪些哈希类型
  - 路由里哪些目标端快传哈希已经可以优先从缓存尝试
- 已补主流 provider 的更多真实字段兼容，避免只认理想字段名：
  - `AliyunDriveOpen` 现在支持 `content_hash_name + content_hash` 组合推导 `sha1`
  - `OneDrive` 现在支持 `sha1Hash / contentHash` 这类 Graph 风格字段
  - provider 专用别名不再覆盖通用别名，而是按去重合并，避免新补的驼峰字段再次失效
- 抓取缓存的文件级哈希结构也继续向真实返回体靠拢：
  - 现在支持从 `data / result / payload` 下的 `list / records / value / children` 递归读取缓存条目
  - 按 `source_id` 匹配时新增兼容 `fs_id / item_id / driveItemId / drive_item_id`
  - 这让 `OneDrive / Baidu / 123Pan` 一类常见“外层包一层 data/result”的抓取快照也能进入统一 enrich 流水线
- 能力评估与页面摘要现在新增了“目标端哈希接受度”这一层：
  - 会区分源端当前原生就重叠的快传哈希
  - 会区分桥接后理论可补到的目标端快传哈希
  - 会区分抓取缓存里已经可直接喂给目标端的快传哈希
  - 也会明确显示源端常见哈希里哪些当前目标端根本不认，避免多目标端切换时只剩笼统 recommended flow
- enrich 提取器现在补了一层统一键名归一化：
  - 常见的 `camelCase / PascalCase / 连字符` 哈希键名会先归一化再进入统一提取流程
  - 已覆盖的真实变体包括 `contentMd5 / gcidHash / sha1Hash / crc64Hash / pickCode` 等
  - 这让 `189Cloud / Thunder / OneDrive / AliyunDriveOpen` 一类常见返回体不必每个 provider 单独再写一轮键名兼容
- 抓取缓存摘要也同步学会识别这些真实哈希键名：
  - `gcidHash / md5Sum / pickCode` 这类字段现在会被统一折叠成 `gcid / md5 / pickcode`
  - 这样 `capture_cache_fast_hashes` 与后续目标能力判断，不会因为缓存键名写法不同而漏掉本来可命中的快传路径
- 主流 provider 的抓取缓存容器键和条目定位键也继续向真实返回体靠拢：
  - 现在兼容 `fileHashesByPath / entryHashesById` 这类驼峰缓存容器键
  - 条目匹配时也兼容 `filePath / sourceId / fileId / resourceId / fsId` 等真实字段名
  - 这让 `OneDrive / Thunder / AliyunDriveOpen` 一类浏览器抓取快照，即使不是仓库内部理想的 snake_case 结构，也能进入统一 enrich 流水线
- 条目匹配规则也继续补了一层真实返回体兼容：
  - 现在支持只给 `parentPath + server_filename`、而不直接给完整 `path` 的抓取条目
  - 这类结构在 `Baidu / 123Pan` 一类目录接口里更常见，补上后能减少“缓存明明有哈希但仍匹配不到文件”的情况
- `file_hashes_by_path / ...by_id` 这类缓存 map 的值也继续向真实抓包靠拢：
  - 现在不仅支持平铺 dict，还支持值本身是 JSON 字符串、算法列表，或再包一层 `data / hash_info`
  - 这让 `AliyunDriveOpen / OneDrive / Thunder` 一类抓取缓存，即使值不是仓库内部理想的扁平对象，也能继续被 summary 与 enrich 主链消费
- 统一体积分级阈值这轮也已落到实处：
  - 当前生产源码里最大的 Python / JS 文件是 `webapp.py`，约 `94.2 KB`
  - 前端主入口 `app.js` 约 `88.8 KB`
  - 当前没有超过 `100 KB` 的生产源码文件，说明“优先压到 100 KB 左右并按阈值治理”这一项已达到当前阶段目标

## 摘要

这版计划只聚焦首批主流网盘，范围固定为：

- 源端首批：`189Cloud`、`Quark`、`123Pan`、`Baidu`、`Thunder`、`AliyunDriveOpen`、`OneDrive`
- 目标端范围：当前仓库已实现的全部可写目标端
  - `guangya`
  - `openlist`
  - `localfs`
  - `webdav`
  - `s3`
  - `seafile`
  - `azureblob`
  - `ftp`
  - `sftp`
  - `smb`

最终目标不是“只围着 Guangya 转”，而是把这 7 个主流源网盘全部纳入统一互传任务流；系统规则统一为：

1. 先读 OpenList 已暴露指纹
2. 指纹不够时，按 source provider 直连补指纹
3. 若目标端支持当前指纹的快传/秒传，则优先快传
4. 若目标端不支持，或快传未命中，则降级普通上传/下载补传
5. 全流程都必须诚实显示“当前命中的是哪一层能力”

这份计划按“最终版方案”书写，但实现必须诚实遵守当前仓库事实：

- `Guangya` 是首个正式秒传目标端
- 其他目标端先统一纳入互传框架与能力矩阵
- 如果目标端没有真实秒传接口，就只走普通上传，不伪装成秒传

## 关键实现变更

### 1. 固定首批主流源网盘清单与能力策略

为以下 7 个 source provider 建立专用实现档案，不再只停留在 profile / capture / guide 描述层：

- `189Cloud`
- `Quark`
- `123Pan`
- `Baidu`
- `Thunder`
- `AliyunDriveOpen`
- `OneDrive`

每个 source provider 都必须明确 5 个维度：

- OpenList 常规可见指纹：如 `md5 / sha1 / gcid / pickcode / etag / size / mtime`
- 直连补指纹策略：Cookie、Token、Header、session 字段从哪里取，用哪个 provider capture 快照喂给实现
- 指纹优先级：例如 `Thunder` 优先 `gcid`，`AliyunDriveOpen` 优先 `sha1`，`189Cloud / Quark / 123Pan / Baidu` 优先 `md5`
- 风控节流默认值：分页、请求间隔、目录间隔、是否强制小批量
- 降级边界：哪些情况下只允许记录待补传，不允许自动下载补传

实现上新增统一 source 直连补指纹接口层，接口语义固定为：

- `supports_enrichment(provider_key) -> bool`
- `enrich_entry(entry, capture_snapshot, config) -> SourceEntry`
- `enrich_batch(entries, provider_key, capture_snapshot, config) -> list[SourceEntry]`

第一批只要求对以上 7 个 provider 给出专用实现；其余 provider 继续回退通用 OpenList 模式。

### 2. 统一秒传决策器，改成“源指纹 -> 目标能力”双向判断

当前秒传判断继续升级为固定流水线，所有源到所有目标统一走这一套：

1. 从 OpenList 读取当前目录树文件元数据
2. 对缺关键指纹的文件，尝试 source provider 直连补指纹
3. 生成标准化 `SourceEntry` 指纹视图
4. 读取当前目标端能力声明
5. 对每个文件计算执行模式：
   - `fast_upload`
   - `stream_upload`
   - `download_upload`
   - `record_pending_only`

目标端能力声明必须固定输出这些字段：

- `supports_fast_upload`
- `fast_upload_hashes`
- `fallback_modes`
- `requires_local_download`
- `supports_overwrite`
- `supports_auto_create_dir`

规则固定如下：

- `guangya`
  - 若文件具备 `md5` 或 `gcid`，先走元数据秒传
  - 未命中再走 `stream_upload` 或 `download_upload`
- `openlist / localfs / webdav / s3 / seafile / azureblob / ftp / sftp / smb`
  - 当前全部纳入统一互传框架
  - 默认不承诺元数据秒传
  - 统一走普通上传/覆盖
  - 页面必须明确显示“已纳入互传，但当前目标端无正式秒传能力”

不允许实现者自行发明新的隐式优先级；所有目标端都必须通过同一决策器输出执行模式。

### 3. 页面主流程重构为“源端 -> 目标端 -> 任务 -> 执行”，并把主流网盘选路讲清楚

页面结构固定为 5 步：

1. 控制台登录 / 运行时连接
2. 选择或挂载源网盘
3. 选择目标端
4. 配置任务
5. 执行与查看结果

任务配置区必须固定包含：

- `source provider`
- `source_path`
- `target_key`
- `target_path`
- `source_provider_preference`
- `auto_download_threshold_mb`
- `rate_limit_mode`
- `delete_removed`
- `target_delete_removed`

界面必须新增两块固定信息：

- `源端指纹能力摘要`
  - OpenList 已给出哪些指纹
  - 当前 provider 是否支持直连补指纹
  - 本次目录分析里有多少文件具备快传关键指纹
- `目标端执行能力摘要`
  - 当前目标端是否支持秒传
  - 支持哪些 hash
  - 本次任务最终会优先走哪种模式

首批 7 个主流源网盘在页面上必须有专用说明和默认值，不再只靠 generic driver 提示。复杂驱动如 `AliyunDriveOpen`、`OneDrive` 必须保留单独流程提示、默认值和文档入口。

### 4. 执行层固定成“统一互传框架 + 诚实分级”，不允许虚假宣传

执行层必须固定支持：

- `dry_run`
- `direct`
- `full`
- `download_selected`
- `leaf_stream`
- `leaf_stream_full`
- `queue_next`
- `queue_all`

并统一输出以下运行态字段：

- `provider_key`
- `requested_provider_preference`
- `selected_source_mode`
- `selected_provider_key`
- `selection_reason`
- `fallback_reason`
- `target_key`
- `target_capability`
- `planned_transfer_mode`
- `fingerprint_coverage_summary`

日志中必须分开标记：

- `[OpenList 指纹]`
- `[直连补指纹]`
- `[秒传命中]`
- `[秒传未命中]`
- `[普通上传]`
- `[下载补传]`
- `[仅记录待补传]`

实现时不允许把“目标端已纳入统一互传”误写成“目标端已经支持秒传”。

### 5. 代码拆分约束

这轮继续控制大文件体积，默认按统一分级阈值治理；`100 KB` 仍是优先目标线。实现者必须继续拆分：

- source provider enrich 逻辑拆到独立模块，不塞回 `webapp.py`
- 秒传决策器独立为单模块，不把 provider 判断散在 `syncer.py`
- 页面 JS 若继续增大，拆为多文件入口，`index.html` 只保留壳与静态挂载

至少新增以下模块边界：

- `source_enrich/`：首批 7 个主流 provider 的补指纹实现
- `transfer_planner.py`：统一文件级执行模式决策
- `task_runtime.py` 继续承接 current task / source runtime 组装
- 前端若继续扩展，拆出 `task.js / source.js / target.js / execute.js`

补充统一文件体积阈值，后续默认按这个分级执行：

- `0 - 80 KB`
  - 绿色区，默认可继续维护
- `80 - 120 KB`
  - 黄色区，允许继续存在，但新增较大功能时优先拆分
- `120 - 180 KB`
  - 橙色区，进入本轮或下个里程碑拆分目标，避免继续堆新职责
- `180 KB 以上`
  - 红色区，原则上不再继续堆功能，优先拆分后再扩展

执行口径：

- Python / JS / TS 默认都适用这套阈值
- `100 KB` 仍然是优先目标线，但不再作为绝对硬上限
- 如果文件职责单一、改动稳定，短期处于 `80 - 120 KB` 可接受
- 如果文件已经跨多个职责，即使还没超过 `120 KB`，也应提前拆分

## 测试与验收

### 必做回归

- `pytest` 回归继续覆盖现有 `test_sync_logic.py` 主链
- 新增 source provider enrich 单测：
  - 189Cloud
  - Quark
  - 123Pan
  - Baidu
  - Thunder
  - AliyunDriveOpen
  - OneDrive
- 新增 transfer planner 单测：
  - `md5 -> guangya -> fast_upload`
  - `gcid -> guangya -> fast_upload`
  - `sha1 only -> guangya -> download_upload`
  - `md5 -> openlist -> stream_upload/download_upload`
  - `no hash -> target unsupported -> record_pending_only`

### 页面验收

- 任务区能直接选择 `source_provider_preference`
- 首批 7 个主流源网盘都有专用提示、默认值、能力摘要
- 选择不同目标端时，目标能力摘要会同步变化
- 页面不会把非 Guangya 目标端误显示为“可秒传”

### 执行验收

- 对首批 7 个主流源网盘，目录分析时能稳定输出指纹覆盖统计
- 当 OpenList 缺少关键指纹时，系统会尝试 provider 直连补指纹
- `Guangya` 目标端能吃到增强后的 `md5/gcid` 并优先尝试秒传
- 非 Guangya 目标端统一进入普通上传路径，但仍保留统一任务与日志结构
- `leaf_stream`、队列、待补传执行时，`current_source_context` 与日志输出一致

## 假设与默认值

- 首批主流范围固定为：`189Cloud / Quark / 123Pan / Baidu / Thunder / AliyunDriveOpen / OneDrive`
- 当前所有已实现目标端都纳入统一互传框架，但只有真实有接口能力的目标端才允许声明秒传
- `Guangya` 仍是第一优先秒传目标端
- `openlist / localfs / webdav / s3 / seafile / azureblob / ftp / sftp / smb` 当前默认按普通上传目标处理
- OpenList 仍是第一层指纹来源；直连 source provider 只作为补强层
- 默认同步语义仍为“新增 + 覆盖”；删除仍为独立开关
- 如果某主流 provider 的直连补指纹在实现中发现接口不可稳定复用，允许该 provider 暂时回退为 `OpenList-only + pending-first`，但页面、日志、能力矩阵必须明确标记为“未完成直连增强”
