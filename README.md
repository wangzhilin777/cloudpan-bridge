# CloudPan Bridge

历史阶段名 `Cloud2Guangya` 仅作为文档背景保留；当前正式对外名称与启动入口统一为 `CloudPan Bridge`。

把任意 OpenList 挂载网盘里的文件目录树，桥接同步到光鸭云盘。

主计划文档：

- `docs/02-cloudpan-bridge-master-plan.md`
- 合并执行计划：`docs/04-cloudpan-bridge-merged-plan.md`
- 主流网盘阶段计划：`docs/05-cloudpan-bridge-mainstream-plan.md`
- 后续 TODO：`docs/06-cloudpan-bridge-todo.md`

当前主路线：

- 源端统一走 `OpenList`
- 目标端当前已内置 `Guangya`、`OpenList`、`LocalFS`、`WebDAV`、`S3`、`Seafile`、`SMB`、`FTP`、`SFTP` 与 `Azure Blob`
- 其中 `Guangya` 仍是当前唯一支持元数据秒传/秒传 JSON 直导的正式目标端
- `OpenList` 目标端已经可写入，但按普通上传/覆盖链路处理，不宣传跨盘秒传
- `LocalFS` 目标端已经可写入，但只负责把结果落到本地目录，不宣传成跨盘秒传目标
- 其它内置目标端当前也都走“普通上传/覆盖 + 自动建目录 + 诚实降级”路线，不把它们误写成已经支持跨盘元数据秒传
- 连接页现在区分 `外部本机 / 外部远程 / 本机托管 / Docker 预留` 四种模式，并只显示当前模式对应的配置块
- `WebDAV` 目标端已经可写入，适合 NAS / 私有云 / 第三方 WebDAV 存储，但当前同样只走普通上传/覆盖
- `S3` 目标端已经可写入，适合作为对象存储桶 / 备份桶 / 云原生归档目标，但当前同样只走普通对象上传/覆盖
- `Seafile` 目标端已经可写入，适合作为团队资料库 / 私有云文档库目标，但当前同样只走普通上传/覆盖
- `SMB` 目标端已经可写入，适合作为 NAS / 局域网共享 / Windows 文件服务器目标，但当前同样只走普通上传/覆盖
- `FTP` 目标端已经可写入，适合作为传统 NAS / 主机面板 / 轻量服务器目录型目标，但当前同样只走普通上传/覆盖
- `SFTP` 目标端已经可写入，适合作为 Linux 主机 / NAS / 云服务器目录型目标，但当前同样只走普通上传/覆盖
- `Azure Blob` 目标端已经可写入，适合作为 Azure 对象存储 / 归档容器目标，但当前同样只走普通对象上传/覆盖
- 优先做 `MD5 / etag / GCID` 秒传
- 未命中再进入自动补传或待补传目录树

## 当前能力

- 支持任意 OpenList 已支持的挂载驱动作为源端
- 支持 `外部本机 OpenList`、`外部远程 OpenList` 与 `本机二进制托管 OpenList`
- 托管模式下如果本机还没有 `openlist/alist` 二进制，页面会先提示是否拉取本机运行时
- 如果拒绝拉取本机运行时，当前应改用外部本机或外部远程模式
- 支持在页面里读取 OpenList 驱动列表、驱动字段、挂载列表
- 支持页面直接创建新的 OpenList 挂载
- 支持源网盘网页登录抓取骨架
- 支持源目录元数据分析
- 支持从当前源目录直接生成秒传候选 JSON
- 支持对当前秒传 JSON 做本地诊断预览
- 支持目录结构同步
- 支持新增文件同步
- 支持修改文件覆盖同步
- 默认同步语义是“新增 + 覆盖”，不会因为源端删除而默认删除目标端文件
- 支持把“目标端真实删除”作为独立开关启用
  - `delete_removed = true` 只会把已不存在的源文件从同步状态里移除
  - 只有同时开启 `target_delete_removed = true`，才会尝试删除 `Guangya / OpenList / LocalFS / WebDAV / S3 / Seafile / SMB / FTP / SFTP / Azure Blob` 目标端对应文件
  - 如果你当前只需要“改动覆盖，不做删除”，保持默认关闭即可
- 支持最底层目录边扫边同步
- 支持最底层目录批量入队
- 支持待补传目录树勾选
- 支持秒传 JSON 直接导入光鸭
- 支持自动抓取并回填光鸭 `Authorization / access_token / refresh_token / device_id`
- 支持把当前源目录写入 `OpenList` 目标挂载目录
  - 自动创建目录
  - 已存在文件可先删后传
  - 但当前只走普通上传/覆盖，不支持跨盘秒传
- 支持把当前源目录写入 `LocalFS` 本地目录目标端
  - 自动创建目录
  - 已存在文件可先删后写
  - 适合作为联调、导出与兜底目标端
- 支持把当前源目录写入 `WebDAV` 目标端
  - 自动创建目录
  - 已存在文件可先删后传
  - 适合作为 NAS、私有云或第三方 WebDAV 存储目标
  - 当前只走普通上传/覆盖，不支持跨盘元数据秒传
- 支持把当前源目录写入 `S3` 目标端
  - 对象前缀自动映射
  - 已存在对象可先删后传
  - 适合作为对象存储桶、备份桶或云原生归档目标
  - 当前只走普通对象上传/覆盖，不支持跨盘元数据秒传
- 支持把当前源目录写入 `SMB` 目标端
  - 自动创建共享子目录
  - 已存在文件可先删后传
  - 适合作为 NAS、局域网共享或 Windows 文件服务器目标
  - 当前只走普通上传/覆盖，不支持跨盘元数据秒传
- 支持把当前源目录写入 `FTP` 目标端
  - 自动创建目录
  - 已存在文件可先删后传
  - 适合作为传统 NAS、主机面板或轻量服务器目录目标
  - 当前只走普通上传/覆盖，不支持跨盘元数据秒传
- 支持把当前源目录写入 `SFTP` 目标端
  - 自动创建目录
  - 已存在文件可先删后传
  - 适合作为 Linux 主机、NAS 或云服务器目录目标
  - 当前只走普通上传/覆盖，不支持跨盘元数据秒传
- 支持抓取并缓存常见源网盘登录态
  - `夸克`：优先抓 Cookie
  - `123 网盘`：Cookie + 常见 token
  - `天翼云盘`：Cookie + sessionKey 类字段
  - `百度网盘`：Cookie + `bdstoken`
  - `迅雷云盘`：`Authorization / x-device-id / x-captcha-token / x-client-id`
  - `阿里云盘 Open`：优先抓 `refresh_token`
  - `OneDrive`：优先抓 `refresh_token / access_token`
  - `Google Drive`：优先抓 `refresh_token / access_token`
  - `Dropbox`：优先抓 `refresh_token / access_token`
  - `Cloudreve`：优先抓 `refresh_token / access_token`，必要时回退 Cookie 或用户名密码
  - `Alias`：走手动策略配置模式
  - `P123`：走手动账号/分享参数模式，并配合本地代理策略
  - `TeraBox`：优先抓 `Cookie`
  - `Yandex Disk`：优先抓 `refresh_token / access_token`
  - `WebDAV / S3 / FTP / SFTP / Seafile / SMB / Azure Blob / MEGA`：走手动凭证模式
  - `OpenList / AListV3`：走手动凭证模式
  - `GitHub`：走手动凭证模式
  - `PikPak`：优先抓 `refresh_token / access_token`
  - `115 网盘`：优先抓 `Cookie / token`
  - `139 云盘`：优先抓 `Authorization`
- 支持按当前 OpenList 驱动字段生成“通用网页登录抓取模板”
- 支持复杂驱动的“接入流程说明 / 官方文档链接 / 推荐默认值”
- 第一批已补成静态档案的重点驱动已覆盖：
  - `AliyundriveOpen`
  - `123Open`
  - `189Cloud`
  - `Quark`
  - `Baidu`
  - `Thunder`
  - `OneDrive`
  - `GoogleDrive`
  - `Dropbox`
  - `WebDav`
  - `S3`
  - `FTP`
  - `SFTP`
  - `Seafile`
  - `SMB`
  - `AzureBlob`
  - `Mega`
  - `OpenList`
  - `Cloudreve`
  - `Github`
  - `Alias`
  - `P123`
  - `TeraBox`
  - `YandexDisk`
  - `PikPak`
  - `115`
  - `139Yun`
  - `Sharepoint`
  - `AListV3`
- 对还没补到专用说明的驱动，也会给出通用 OpenList 接入兜底说明和官方驱动文档入口
- 当前这批常见样本驱动在覆盖审计里已做到 `missing=0`
- guide 数据现在还会额外携带 `docUrlCandidates`，方便后续继续扩页面时直接接官方文档候选链路
- 页面里的驱动接入弹窗现在也会直接列出这些文档候选链接，并默认打开第一条最可信候选
- 支持源驱动到当前目标端的基础能力矩阵提示
  - 区分 `fast_upload_partial / download_upload_only / unsupported` 等等级
  - 页面会给出诚实降级后的建议路径，而不是默认宣称都能秒传
  - 如果已经跑过源目录分析，还会进一步给出动态执行建议
    - 是否应先分析
    - 是否优先最底层目录模式
    - 是否优先进入待补传树
    - 当前更适合直接秒传、边扫边同步，还是分目录补传
- 支持本地状态续跑

## 推荐使用顺序

### 1. 先跑小目录

第一次配置、刚更新 token、刚调整挂载时，先找一个小目录试跑。

如果源端比较复杂，建议先在 `源目录` Tab 里点一次“分析当前源目录”，先看：

- 当前目录里有多少文件带 `MD5`
- 有多少文件只有 `GCID`
- provider 分布是否混杂
- 是否已经出现较多“缺少 MD5”的来源

如果分析结果看起来适合秒传，可以直接点：

- `生成当前源目录秒传 JSON`

页面会自动：

- 重新扫描当前源目录
- 生成一份光鸭可导入的候选 JSON
- 自动切到 `秒传` Tab
- 把 JSON 填进文本框，直接可继续导入
- 并立即给出 `文件数 / 总大小 / MD5 / GCID / provider` 诊断结果

### 2. 大目录优先用最底层目录模式

如果源目录很大，优先使用：

- `最底层边扫边秒传`
- `最底层边扫边同步+补传`

这样会先走到叶子目录，再同步这个叶子目录，节奏更温和，更适合防风控。

### 3. 秒传优先级

建议优先级：

1. 已有秒传 JSON 时，优先走 `秒传 JSON 直导`
2. 没有 JSON 时，走 OpenList 源端 `hash_info.md5`
3. 如果源端只有 `GCID`，当前也会先尝试 GCID 秒传
4. 秒传未命中后，再按大小阈值自动补传或转待补传

### 4. 覆盖与删除策略

默认推荐：

- 保持“新增 + 覆盖”模式
- 不开启目标端真实删除

也就是默认只保证：

- 源端新增文件会补到目标端
- 源端修改文件会覆盖到目标端
- 源端已经删掉的文件，不会默认去删目标端真实文件

如果你明确要把目标端也收敛到和源端一致，再额外开启：

- `delete_removed`
- `target_delete_removed`

建议先在小目录验证后，再用于正式数据。

现在还多了一条中间路径：

- 如果没有外部插件导出的 JSON，但当前源端已经能通过 OpenList 读到 `MD5 / GCID`
- 可以先用页面里的“生成当前源目录秒传 JSON”
- 再直接走 `秒传 JSON 直导`

## 页面结构

页面默认地址：

- [http://127.0.0.1:8765](http://127.0.0.1:8765)

当前页面分为 8 个 Tab：

- `总览`
- `源目录`
- `同步`
- `补传`
- `秒传`
- `挂载`
- `配置`
- `关于`

日志不是单独 Tab，而是右侧独立抽屉：

- 可固定显示
- 可隐藏
- 会自动滚动到最新日志
- 可单独清空，不影响配置

其中 `源目录` Tab 现在多了一个“源端元数据分析”面板，可以在正式同步前先做一次源端体检。

`总览` Tab 现在还会显示一个“能力矩阵与建议”面板：

- 根据当前驱动和当前目标端，提示当前组合更接近：
  - `fast_upload_partial`
  - `download_upload_only`
  - `unsupported`
- 如果你已经跑过“源端元数据分析”，它还会把当前目录里的 `MD5 / GCID / 可快传指纹数量` 一起展示出来
- 并且会基于当前目录分析结果做一层动态判断
  - 比如同一个驱动，在某个目录里全部文件都具备快传指纹时，会提示更适合先秒传
  - 如果当前目录几乎没有可快传指纹，则会更明确地建议按补传链路处理
- 现在还会额外给出一层“执行建议模板”
  - 当前更适合 `直接秒传 / 最底层边扫边秒传 / 待补传树优先 / 先人工核对`
  - 是否建议优先叶子目录推进
  - 当前推荐的频率节奏提示
- `总览` 面板下方还会生成对应快捷动作
  - 比如直接跳转到 `秒传 / 同步 / 补传 / 挂载` Tab
  - 或直接触发“分析当前目录”“最底层边扫边秒传”等动作
- 这样可以更早判断当前应该优先走秒传、分目录补传，还是先停下来检查挂载与驱动兼容性

`关于` Tab 现在会把 registry 相关信息直接可视化：

- 当前主计划与调研计划文档入口
- 已内置的源端 profiles
- 已内置的目标端 profiles
  - 会明确显示 `implemented / selectable` 状态
  - 用来区分“只是先建好了目标端档案”与“真的已经接通可写入适配器”
- 当前 driver 到当前目标端的能力矩阵条目
- 当前 OpenList 驱动覆盖审计
  - 直接显示哪些驱动已经具备 `profile / guide / capture / capability`
  - 并给出当前驱动的缺口项和建议下一步
  - 还会生成按优先级排序的 backlog，方便继续批量补驱动
  - 现在还会额外生成“执行波次建议”
    - 按 `add_profile_first / add_guide / add_capture_spec / assess_target_capability` 分波
    - 每一波直接列出对应驱动、缺口类型与相关 profile
  - 现在还支持导出“待补 Scaffold JSON”
    - 会把当前筛选结果整理成可继续补驱动的结构化清单
    - 包含 driver、nextAction、missingItems、guideDocUrl、captureLoginUrl 等信息
  - 现在也支持导出“补全任务 Markdown”
    - 会按 `nextAction` 分组输出待补驱动任务
    - 适合直接拿去继续拆分计划、外包补驱动，或作为后续批量实施的任务书
  - 支持导出 `JSON / Markdown` 审计结果，便于拆分后续任务
  - 如果本次没有手工传 `drivers`
    - 会直接读取当前 OpenList 返回的驱动列表来做审计
    - 更适合在 OpenList 新增网盘后直接扫一遍看缺口
  - 如果某个驱动仓库里还没有专用 profile / capture
    - 现在会尽量根据当前 OpenList live driver fields 自动推断一份动态档案
    - 自动补出保守的登录模式、推荐默认值、抓取需求和 `download_upload_only` 级别能力判断
    - 这类动态档案不会冒充“已人工验证完成的专用支持”，页面和审计链路仍按保守策略展示
  - 支持页面内只看缺口、按下一步动作过滤
  - 还支持按缺口类型过滤，例如只看“缺 capture”的驱动
  - 还支持按 `capability level` 与 `profileKey` 过滤
    - 例如只看 `download_upload_only`
    - 或只看某个具体 profile，如 `aliyundriveopen`
  - 这些筛选项现在会按当前 registry / 审计结果动态生成
    - 不再把 profile key、执行阶段之类的选项写死在前端
  - 当前语言与覆盖审计筛选也会跟随配置持久化
    - 下次重新进入页面时，会优先恢复上次保存的语言和审计过滤条件
  - 当前目录浏览位置、已选挂载源目录也会一起恢复
    - 重新打开页面后，不需要每次都先退回上级目录再重新定位
  - 现在还支持一层“接入阶段”视图
    - `needs_profile_bootstrap`
    - `ready_for_guide`
    - `ready_for_capture`
    - `ready_for_capability`
    - `covered`
  - 并支持“只看可直接接入”
    - 也就是已经有 profile，可直接进入补 guide / 补 capture / 补 capability 的驱动
  - 覆盖筛选条件会自动记住，下次进入页面继续延续
  - 导出结果会跟随当前筛选视图，不再固定导出全量
  - 每条审计记录现在还会展示：
    - `onboardingReady`
    - `onboardingStage`
    - `canonicalDriver`
    - `matchedGuide`
    - `profileKey`
    - `guideDoc`
    - `captureSpec`
    - `capture alias`
    - `captureLogin`
  - 这意味着你现在不只是知道“有没有 capture”，还能直接看出：
    - 当前驱动最终归一到了哪个 canonical driver key
    - guide 是通过哪个 key/alias 命中的
    - capture 命中了哪个内置抓取规格
    - 后续应从哪个登录入口继续补流程
  - 方便后续按缺口继续补 OpenList 全驱动
- 各源端的登录模式、哈希能力、下载链路、抓取策略、默认挂载值、风控备注

这样后面继续补 OpenList 全驱动时，可以直接把新增结果往 registry 填，而不是继续把逻辑散落在页面脚本里。

页面右上角支持语言切换：

- `中文`
- `English`
- `中英混合`

右侧为独立日志抽屉：

- 会自动滚动到最新日志
- 可以单独隐藏
- 可以清空日志，不会清掉你的配置

### 自动登录与抓取

- OpenList：
  - 如果页面检测到已有用户名密码但没有 token，会尝试自动登录并写回 token
- 光鸭：
  - 如果页面检测到 `Authorization / access_token / refresh_token / device_id` 不完整，会自动尝试启动一次抓取窗口
  - 抓取成功后会自动回填并写回配置
- 源网盘：
- `挂载` Tab 里新增“源网盘登录抓取”面板
- 现在可直接选择 `夸克 / 123 / 天翼 / 百度 / 迅雷 / 光鸭`
- 以及 `阿里云盘 Open / OneDrive / PikPak / 139 云盘`
- 抓到的 `Cookie / Token / Header` 会缓存到本地配置里的 `provider_captures`
- 可一键尝试写入当前 OpenList 挂载表单，减少手工复制字段
- 如果当前驱动不在预置网盘列表里，页面还会按当前 OpenList 驱动字段自动生成一个“通用抓取”方案
- 可手动调整 `Login URL` 后再启动抓取，作为更多 OpenList 驱动的兜底入口
- 对 `WebDav / S3 / FTP / SFTP / Seafile` 这类更适合手动凭证的驱动
  - 抓取面板现在会明确切到“手动凭证模式”
  - 不再假装去做浏览器自动抓取
  - 会直接提示你按说明填写 URL / host / bucket / username / password / key 等字段
- 现在在这个面板里也可以直接点“查看该网盘接入流程”
  - 不需要先切到“新增挂载”区域
  - 会直接复用内置的复杂驱动说明与官方文档入口
- 对 `AliyundriveOpen / 123Open / 139Yun / Quark / Thunder / Baidu / OneDrive / PikPak` 这类复杂驱动，页面会额外提供“查看接入流程”和“套用推荐默认值”

### 挂载源下拉与频率策略

- 页面会读取当前 OpenList 挂载列表，并提供“已挂载源目录”下拉选择
- 选择挂载源目录后，会继续保留目录浏览器供你深入到子目录
- 如果 `rate_limit_mode` 不是 `custom`，页面会按挂载驱动类型自动套一组推荐频率参数
  - 例如 `189Cloud / Quark / 123Pan / Baidu / Thunder` 会使用不同默认值
- 队列、最底层边扫边同步、按目录补传过程中，如果命中常见 `429 / rate limit / 风控 / captcha` 报错，会自动进入一轮冷却等待后再继续

### 目录恢复逻辑

页面重新进入时，会优先按配置里的 `source_path` 恢复目录浏览器当前位置。

如果这个目录当前无法读取，才会退回挂载根目录。

## 配置说明

推荐页面使用的本地配置文件：

- `.work/openlist-config.json`

当前配置已升级为“内部按分组存储、页面继续兼容平面字段”的过渡结构。

- 前端仍处于“平面字段 + grouped_config” 并行过渡期，避免一次性重写整页逻辑
- 磁盘上的配置文件默认保存为分组结构，便于后续继续扩展多目标端和 UI 状态
- 旧版平面配置仍可直接读取
- `/api/config` 现在会同时返回平面视图和 `grouped_config` 分组视图，并支持按 `grouped_config` 做局部写回
- 前端关键配置字段现在也已经开始优先读取/回写 `grouped_config`，同时继续兼容平面字段
- 同步启动、最底层执行、勾选补传执行、目录浏览、源分析、秒传诊断/导入、OpenList 登录、覆盖审计、能力判断、挂载创建/抓取辅助入口，现在也已支持直接读取 `grouped_config`
  - 也就是说，后续前端继续减少平面 payload 时，后端不会因为还没传平面字段而失效
- 当前语言、覆盖审计筛选、目录浏览位置、挂载选择也已经进入正式 `ui` 分组
- 这些 UI 状态不再只是依赖页面侧临时透传保存
- 页面状态恢复现在也以 `grouped_config.ui` 为主
  - `language / coverage_filters / browser / panel_open_states` 会优先从正式配置恢复
  - `localStorage` 只保留为旧版本迁移和页面刚启动时的轻量缓存兜底
- `targets.active_target` 当前默认是 `guangya`
- 配置页里已经有“当前目标端”选择点
- 当前切换目标端后，页面里的能力矩阵、覆盖审计与导出都会立即跟随这个选择刷新
- 目标端下拉现在会按内置 `target_profiles` 动态生成，后续扩目标端时不需要再手改前端选项
- 同时只会放出当前真正可选、已实现适配器的目标端，避免页面先暴露还不能写入的目标端
- 在真正启动同步、队列或最底层边扫边同步前，现在也会先做目标端预检，未实现目标端会直接在入口层返回清晰错误
- 现阶段正式可写目标端已有 `guangya`、`openlist`、`localfs`、`webdav`、`s3`、`seafile`、`smb`、`ftp`、`sftp` 与 `azureblob`
- 但真正支持秒传 JSON 直导和元数据秒传的目标端仍只有 `guangya`
- 当前活动 Tab、日志抽屉显隐等页面状态会同步写入 `ui.panel_open_states`
- 老版本本地缓存键也会自动迁移到新的 `CloudPan Bridge` 命名空间

示例：

```json
{
  "app": {
    "name": "CloudPan Bridge",
    "bind_host": "127.0.0.1",
    "bind_port": 8765,
    "admin_username": "",
    "admin_password": ""
  },
  "ui": {
    "panel_open_states": {}
  },
  "openlist": {
    "mode": "external",
    "url": "http://127.0.0.1:5244",
    "token": "",
    "username": "admin",
    "password": "",
    "managed_runtime": {
      "bin": "",
      "data_dir": ".runtime/openlist",
      "port": 5244
    }
  },
  "source_session": {
    "provider_captures": {}
  },
  "targets": {
    "active_target": "guangya",
    "guangya": {
      "phone": "+86 13800138000",
      "authorization": "",
      "access_token": "",
      "refresh_token": "",
      "device_id": ""
    },
    "s3": {
      "endpoint": "",
      "bucket": "",
      "prefix": "",
      "access_key": "",
      "secret_key": "",
      "region": ""
    },
    "seafile": {
      "url": "",
      "token": "",
      "username": "",
      "password": "",
      "repo_id": "",
      "repo_name": ""
    },
    "smb": {
      "url": "",
      "username": "",
      "password": ""
    },
    "sftp": {
      "url": "",
      "username": "",
      "password": ""
    },
    "azureblob": {
      "account_url": "",
      "container": "",
      "prefix": "",
      "account_name": "",
      "account_key": ""
    }
  },
  "sync": {
    "source_path": "/你的挂载目录",
    "target_path": "/同步目标目录",
    "delete_removed": false,
    "openlist_page_size": 200,
    "openlist_request_interval_ms": 300,
    "queue_interval_ms": 3000,
    "auto_download_threshold_mb": 10,
    "rate_limit_mode": "safe"
  },
  "state": {
    "state_file": ".state/sync-state.json",
    "export_file": ".work/source-export.jsonl",
    "temp_dir": ".work/download-cache",
    "log_file": ".state/sync.log"
  }
}
```

如果你希望管理页面本身也加一层登录保护，可以直接在同一个配置文件里填写：

```json
{
  "app": {
    "admin_username": "admin",
    "admin_password": "change-me"
  }
}
```

说明：

- 两个字段都留空：控制台不加锁，直接打开页面即可使用
- 两个字段都填写：页面右上角会出现控制台登录入口，未登录前不能调用 `/api/*`
- 这是 CloudPan Bridge 控制台自己的登录，不是 OpenList 登录，也不是光鸭登录

### 关键参数建议

- `source_path`
  - 不建议一开始就整盘跑
  - 优先具体业务目录
- `target_path`
  - 建议先用单独测试目标目录
- `openlist_page_size`
  - 建议先 `50~100`
- `openlist_request_interval_ms`
  - 建议先 `500~1500`
- `queue_interval_ms`
  - 建议先 `3000~10000`
- `auto_download_threshold_mb`
  - 默认 `10`
  - 设为 `0` 表示只记录待补传，不自动下载补传
- `rate_limit_mode`
  - `safe`：默认最稳
  - `balanced`：折中
  - `fast`：只适合非常熟悉自己网盘风控时
  - `custom`：给后续更细分策略预留

## 同步机制

### 直接同步

- 扫描当前 `source_path`
- 对比本地状态，找出新增和修改文件
- 先尝试元数据秒传
- 未命中时：
  - 小于阈值，自动下载补传
  - 大于阈值，进入待补传列表

### 最底层目录边扫边同步

适合超大目录场景。

流程：

1. 从当前目录开始向下扫
2. 遇到最底层目录就立刻执行
3. 执行完按 `queue_interval_ms` 等待
4. 再继续下一个叶子目录

### 待补传

待补传会持久化到：

- `.state/sync-state.json`

支持：

- 按目录树层级显示
- 父目录勾选联动子目录和文件
- 全选 / 全不选
- 按勾选目录最底层顺序补传
- 页面关闭后重新打开继续

## 秒传 JSON 格式

支持直接粘贴类似下面的 JSON：

```json
{
  "scriptVersion": "2026.05.16",
  "files": [
    {
      "path": "/01豆腐罗曼史.zip",
      "size": "83756519",
      "etag": "d2174b2efeefd51fb115e74f5cafd3b1"
    },
    {
      "path": "/02红烧蔡捕头.zip",
      "size": "92944318",
      "etag": "11072b9d44dfe8c009866c5b04548ed6"
    }
  ],
  "commonPath": ""
}
```

当前会优先识别：

- `etag`
- `md5`
- `gcid`
- `commonPath`

秒传 Tab 现在还支持：

- 对当前 JSON 做本地诊断
- 预览 provider 分布
- 预览前几条样本文件的 `hashType / md5 / gcid / size`

## OpenList 挂载说明

页面里的 `挂载` Tab 现在支持：

- 读取 `/api/admin/driver/names`
- 读取 `/api/admin/driver/info`
- 读取 `/api/admin/storage/list`
- 动态生成驱动字段表单
- 创建新的挂载

这意味着：

- 只要 OpenList 支持的驱动，这个项目就可以尽量复用
- 不需要把每个网盘都手写一遍源端逻辑

当前主设计仍然是：

- 多网盘登录与元数据能力优先交给 OpenList 挂载
- 页面负责统一调度、同步、秒传和补传

但现在多了一层兜底：

- 如果 OpenList 里还没有挂载对应网盘
- 或者别人拿到项目时没有现成挂载
- 可以先在页面里打开对应网页登录抓取，再把抓到的字段回填到挂载表单

这能把“先去 OpenList 后台找字段”的门槛再降一层。

## 启动方式

### 推荐

双击以下任一脚本：

- `start_cloudpan_bridge.bat`
- `start_cloudpan_bridge.ps1`

如果你用的是桌面 Windows 环境，这仍然是当前最省心的非 Docker 启动方式。

### Windows 本机启动

1. 双击 `start_cloudpan_bridge.bat`
2. 脚本会优先尝试 `pwsh`，没有再回退到 Windows PowerShell
3. 首次启动会自动：
   - 创建 `.venv`
   - 安装当前项目依赖
   - 生成 `.work/openlist-config.json`
   - 启动 Web 控制台
   - 自动打开 `http://127.0.0.1:8765`
4. 如需控制台登录保护，先编辑 `.work/openlist-config.json` 里的 `app.admin_username / app.admin_password`

### PowerShell 手动启动

适合想自己看启动过程或手动调试的人：

```powershell
Set-Location E:\Workspace\VSCode\CloudPan Bridge
.\start_cloudpan_bridge.ps1
```

## 使用建议优先级

推荐顺序：

1. 先确认 OpenList 能正常登录，并且能浏览到具体挂载目录
2. 没有挂载时，先用 `挂载 -> 源网盘登录抓取` 抓登录态，再回填当前挂载表单
3. 小目录先试 `直接同步当前目录`
4. 大目录优先用 `最底层边扫边秒传` 或 `最底层边扫边同步+补传`
5. 已有秒传 JSON 时，优先走 `秒传 JSON 直导`

如果你主要关心稳妥性：

- `rate_limit_mode` 先用 `safe`
- `openlist_page_size` 先压到 `50~100`
- `openlist_request_interval_ms` 建议 `800~1500`
- `queue_interval_ms` 建议 `3000~10000`

如果你主要关心补齐率：

- 先保证光鸭 `Authorization / access_token / refresh_token / device_id` 完整
- 再补抓源网盘的 Cookie / Token / Header
- 最后再跑大目录或补传流

如果你主要关心“当前这组网盘到底适不适合秒传”：

- 先看 `总览 -> 能力矩阵与建议`
- 再跑一次 `源目录 -> 分析当前源目录`
- 如果提示 `download_upload_only`，就不要把当前组合当成稳定秒传链路来规划

按场景推荐：

1. 已有插件/油猴导出的秒传 JSON
   - 优先 `秒传 JSON 直导`
   - 这是当前最省时间、最接近批量秒传的入口
2. OpenList 能稳定返回 `md5 / etag / gcid`
   - 优先 `分析当前源目录` + `直接同步当前目录`
   - 适合先试单目录，再扩大范围
3. 小文件很多，且愿意接受下载补传
   - 保持 `auto_download_threshold_mb = 10`
   - 先跑 `最底层边扫边同步+补传`
4. 大目录很多，担心风控
   - 优先 `最底层边扫边秒传`
   - 秒传没命中再进入待补传树按目录补
5. 明显没有可用哈希
   - 直接把预期放在 `待补传树`
   - 不要把当前组合误判为“还能稳定秒传”

启动脚本行为：

- 优先使用 `pwsh`
- 没有 `pwsh` 时回退到 Windows PowerShell
- 若检测到已有实例监听 `127.0.0.1:8765`
  - 直接打开现有页面
- 若没有实例
  - 自动创建虚拟环境
  - 自动安装依赖
  - 自动生成默认配置
  - 自动启动页面服务
  - 自动打开网页

### 命令行

初始化配置：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
cloudpan-bridge init-config --path .work/openlist-config.json
```

初始化后，建议先打开 `.work/openlist-config.json` 补这些内容：

- `openlist.url / username / password / token`
- 目标端配置，例如 `targets.guangya.*`
- 如需页面自身登录，再补 `app.admin_username / app.admin_password`

启动页面：

```powershell
cloudpan-bridge serve --config .work/openlist-config.json
```

如果要覆盖监听地址和端口：

```powershell
cloudpan-bridge serve --config .work/openlist-config.json --host 0.0.0.0 --port 8765
```

直接同步：

```powershell
cloudpan-bridge sync --config .work/openlist-config.json
```

只看计划：

```powershell
cloudpan-bridge sync --config .work/openlist-config.json --dry-run
```

允许下载补传：

```powershell
cloudpan-bridge sync --config .work/openlist-config.json --yes-download-upload
```

只做秒传阶段：

```powershell
cloudpan-bridge sync --config .work/openlist-config.json --no-download-upload
```

### Docker

如果你只想最快跑起来，建议优先顺序是：

1. 本机 Python 直接运行
2. `docker compose up -d --build`
3. 再按需接入远程 OpenList / 托管 OpenList

构建镜像：

```powershell
docker build -t cloudpan-bridge:local .
```

直接运行：

```powershell
docker run --rm -p 8765:8765 ^
  -v ${PWD}/.work:/app/.work ^
  -v ${PWD}/.state:/app/.state ^
  -v ${PWD}/.runtime:/app/.runtime ^
  -v ${PWD}/.exports:/app/.exports ^
  cloudpan-bridge:local
```

或使用 `docker-compose.yml`：

```powershell
docker compose up -d --build
```

建议的容器配置流程：

1. 先执行一次 `docker compose up -d --build`
2. 容器会自动生成 `/app/.work/openlist-config.json`
3. 对应到宿主机就是项目目录下的 `.work/openlist-config.json`
4. 编辑这个文件，补齐：
   - `openlist.url / username / password / token`
   - 目标端凭据
   - 可选的 `app.admin_username / app.admin_password`
5. 重启容器：

```powershell
docker compose restart cloudpan-bridge
```

一个完整的 Compose 使用示例可以直接参考仓库内的 [docker-compose.yml](docker-compose.yml)。

最关键的是配置文件中的控制台登录段：

```json
{
  "app": {
    "name": "CloudPan Bridge",
    "bind_host": "0.0.0.0",
    "bind_port": 8765,
    "admin_username": "admin",
    "admin_password": "change-me"
  }
}
```

如果只想跑容器但不启用页面登录，把 `admin_username / admin_password` 留空即可。

容器版当前建议用途：

- 适合跑 Web 控制台
- 适合跑普通同步、覆盖、目录分析、覆盖审计
- 适合放在 NAS / 轻量服务器 / Linux 主机上做长期运行

容器版当前不建议过度依赖的场景：

- 页面内浏览器自动登录抓取
- 需要本机可见浏览器窗口辅助登录的流程

也就是说，Docker 版本当前更偏“服务端运行版”，而不是“桌面浏览器抓取版”。

如果你希望直接拉现成镜像，也可以使用 GitHub Container Registry：

```powershell
docker pull ghcr.io/wangzhilin777/cloudpan-bridge:latest
docker run --rm -p 8765:8765 ^
  -v ${PWD}/.work:/app/.work ^
  -v ${PWD}/.state:/app/.state ^
  -v ${PWD}/.runtime:/app/.runtime ^
  -v ${PWD}/.exports:/app/.exports ^
  ghcr.io/wangzhilin777/cloudpan-bridge:latest
```

### OpenList 模式说明

当前页面里的 OpenList 模式已经按真实用途拆成：

- `external_local`
  - 连接你本机已经运行好的 OpenList
- `external_remote`
  - 连接远程服务器、NAS 或局域网里的现成 OpenList
- `managed_binary`
  - 由 CloudPan Bridge 在本机直接启动 `openlist.exe/alist.exe`
- `managed_docker`
  - 由 CloudPan Bridge 通过本机 Docker 创建并启动 OpenList 容器

关于 `managed_binary`，当前行为是：

1. 先预检本机是否已有可用的 OpenList 二进制
2. 如果没有，会先提示是否拉取本机运行时
3. 如果你拒绝拉取，本轮不会强行继续托管启动，而是提示改用 `external_local` 或 `external_remote`

也就是说，托管模式当前不是“点一下无论如何都能起”，而是：

- 有本机二进制：可以继续托管启动
- 没有本机二进制：先提示是否拉取
- 不拉取：只能改用外部模式

如果你要走 Docker 相关链路，当前建议先完成本机 Docker 环境验证：

```powershell
docker version
docker info
```

若这两条都通过，说明本机 Docker 环境至少已可用；当前项目会在 `managed_docker` 模式下复用本机 Docker 来创建和启动 OpenList 容器。

### GitHub 自动打包与镜像发布

仓库已补：

- `Dockerfile`
- `docker-compose.yml`
- `.github/workflows/build.yml`

当前 GitHub Actions 触发条件：

- push 到 `main`
- push `v*` tag
- pull request
- 手动 `workflow_dispatch`

会自动执行：

- `python -m compileall src tests`
- `pytest -q`
- 构建 Python 包
- 上传 Python 包产物
- 构建 Docker 镜像
- 在非 PR 场景登录 GHCR
- 推送 `ghcr.io/wangzhilin777/cloudpan-bridge`

当前镜像发布策略：

- `pull_request`
  - 只做构建校验，不推镜像
- `push main`
  - 推送 `latest`、`main`、`sha-*`
- `push v* tag`
  - 推送对应 tag、`sha-*`

如果你后面想切到 Docker Hub 或私有 Registry，只需要改 `.github/workflows/build.yml` 里的登录目标和 `images` 配置即可。

### 当前能力边界

这版项目的对外说法建议按下面理解：

- OpenList 主要负责源端接入、挂载、目录浏览、部分登录态抓取和源文件指纹补齐
- Guangya 仍然是当前元数据秒传能力最完整的正式目标端
- 其它目标端已经支持统一任务配置、普通上传/覆盖、能力提示和诚实降级
- “所有网盘之间都已实现真正跨盘秒传” 这件事当前不能宣传为已完成

也就是说，当前最稳妥的使用方式依然是：

1. 先用 OpenList 接入源网盘
2. 优先走能直接命中的秒传/快传能力
3. 命不中时再按配置回落到普通上传或下载补传

## 状态与续跑

本地状态文件：

- `.state/sync-state.json`

其中会保留：

- 已同步文件状态
- 待补传文件
- 目录队列
- 光鸭 token 信息

因此支持：

- 页面关闭后重新打开继续
- 待补传不丢
- 队列不丢

但仍要注意：

- 新增文件、修改文件，后续依然需要重新扫描对应源目录才能发现

## 风控建议

建议顺序：

1. 小目录试跑
2. 单挂载目录试跑
3. 最底层目录边扫边同步
4. 再逐步扩大范围

默认更稳的参数：

- `openlist_page_size = 50~100`
- `openlist_request_interval_ms = 500~1500`
- `queue_interval_ms = 3000~10000`
- `auto_download_threshold_mb = 10`
- `rate_limit_mode = safe`

## 边界与说明

- 当前多网盘统一源端的前提，仍然是 OpenList 能挂载并正常列目录
- 不同网盘驱动能否稳定返回 `hash_info.md5`，取决于 OpenList 驱动本身
- 没有 `md5 / etag / gcid` 的情况下，秒传能力会明显下降
- 光鸭接口存在变动风险，首次建议始终先跑小目录
- 敏感配置、本地日志、状态文件默认都只保存在本地，不应该提交到 Git

## 验收清单

最少建议按下面顺序验：

1. `连接` Tab 能正常登录 OpenList，且 `目录浏览` 能打开目标挂载目录
2. `挂载` Tab 能看到当前驱动说明、推荐默认值和登录抓取入口
3. `总览 -> 能力矩阵与建议` 能根据当前驱动和目标端给出非空结果
4. `源目录 -> 分析当前源目录` 能返回文件总数、MD5/GCID 命中情况
5. 小目录执行一次 `直接同步当前目录`，日志里能看到明确结果
6. 关闭页面后重新打开，语言、Tab、目录浏览位置和挂载选择能恢复
7. `关于` Tab 的覆盖审计可以导出：
   - `覆盖审计 JSON`
   - `覆盖审计 Markdown`
   - `待补 Scaffold JSON`
   - `补全任务 Markdown`

达到下面这组结果时，才算当前环境已经可长期使用：

- OpenList 登录稳定
- Guangya 抓取信息完整且能自动写回配置
- 小目录同步成功
- 中断后可继续
- 无法秒传时会诚实降级到补传或待补传树

## 自测

当前建议最少跑这两步：

```powershell
.venv\Scripts\python.exe -m compileall src tests
.venv\Scripts\python.exe -m pytest -q
```
