# CloudPan Bridge

历史阶段名 `Cloud2Guangya` 仅作为文档背景保留；当前正式对外名称与启动入口统一为 `CloudPan Bridge`。

把任意 OpenList 挂载网盘里的文件目录树，桥接同步到光鸭云盘。

主计划文档：

- `docs/cloudpan-bridge-master-plan.md`
- 历史计划：`docs/cloud2guangya-rebuild-plan.md`

当前主路线：

- 源端统一走 `OpenList`
- 目标端统一走光鸭接口
- 优先做 `MD5 / etag / GCID` 秒传
- 未命中再进入自动补传或待补传目录树

## 当前能力

- 支持任意 OpenList 已支持的挂载驱动作为源端
- 支持外部 OpenList 与托管 OpenList 两种模式
- 支持在页面里读取 OpenList 驱动列表、驱动字段、挂载列表
- 支持页面直接创建新的 OpenList 挂载
- 支持源网盘网页登录抓取骨架
- 支持源目录元数据分析
- 支持从当前源目录直接生成秒传候选 JSON
- 支持对当前秒传 JSON 做本地诊断预览
- 支持目录结构同步
- 支持新增文件同步
- 支持修改文件覆盖同步
- 支持最底层目录边扫边同步
- 支持最底层目录批量入队
- 支持待补传目录树勾选
- 支持秒传 JSON 直接导入光鸭
- 支持自动抓取并回填光鸭 `Authorization / access_token / refresh_token / device_id`
- 支持抓取并缓存常见源网盘登录态
  - `夸克`：优先抓 Cookie
  - `123 网盘`：Cookie + 常见 token
  - `天翼云盘`：Cookie + sessionKey 类字段
  - `百度网盘`：Cookie + `bdstoken`
  - `迅雷云盘`：`Authorization / x-device-id / x-captcha-token / x-client-id`
  - `阿里云盘 Open`：优先抓 `refresh_token`
  - `OneDrive`：优先抓 `refresh_token / access_token`
  - `PikPak`：优先抓 `refresh_token / access_token`
  - `139 云盘`：优先抓 `Authorization`
- 支持按当前 OpenList 驱动字段生成“通用网页登录抓取模板”
- 支持复杂驱动的“接入流程说明 / 官方文档链接 / 推荐默认值”
- 支持源驱动到 Guangya 的基础能力矩阵提示
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

现在还多了一条中间路径：

- 如果没有外部插件导出的 JSON，但当前源端已经能通过 OpenList 读到 `MD5 / GCID`
- 可以先用页面里的“生成当前源目录秒传 JSON”
- 再直接走 `秒传 JSON 直导`

## 页面结构

页面默认地址：

- [http://127.0.0.1:8765](http://127.0.0.1:8765)

当前页面分为 7 个 Tab：

- `总览`
- `源目录`
- `同步`
- `补传`
- `秒传`
- `挂载`
- `配置`
- `关于`

其中 `源目录` Tab 现在多了一个“源端元数据分析”面板，可以在正式同步前先做一次源端体检。

`总览` Tab 现在还会显示一个“能力矩阵与建议”面板：

- 根据当前驱动和目标端 Guangya，提示当前组合更接近：
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
- 当前 driver 到 Guangya 的能力矩阵条目
- 当前 OpenList 驱动覆盖审计
  - 直接显示哪些驱动已经具备 `profile / guide / capture / capability`
  - 并给出当前驱动的缺口项和建议下一步
  - 还会生成按优先级排序的 backlog，方便继续批量补驱动
  - 支持导出 `JSON / Markdown` 审计结果，便于拆分后续任务
  - 支持页面内只看缺口、按下一步动作过滤
  - 还支持按缺口类型过滤，例如只看“缺 capture”的驱动
  - 覆盖筛选条件会自动记住，下次进入页面继续延续
  - 导出结果会跟随当前筛选视图，不再固定导出全量
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

示例：

```json
{
  "source_path": "/你的挂载目录",
  "target_path": "/同步目标目录",
  "state_file": ".state/sync-state.json",
  "export_file": ".work/source-export.jsonl",
  "temp_dir": ".work/download-cache",
  "openlist_mode": "external",
  "managed_openlist_bin": "",
  "managed_openlist_data_dir": ".runtime/openlist",
  "managed_openlist_port": 5244,
  "openlist_url": "http://127.0.0.1:5244",
  "openlist_token": "",
  "openlist_username": "admin",
  "openlist_password": "",
  "guangya_phone": "+86 13800138000",
  "guangya_authorization": "",
  "guangya_access_token": "",
  "guangya_refresh_token": "",
  "guangya_device_id": "",
  "delete_removed": false,
  "openlist_page_size": 200,
  "openlist_request_interval_ms": 300,
  "queue_interval_ms": 3000,
  "auto_download_threshold_mb": 10,
  "rate_limit_mode": "safe",
  "bind_host": "127.0.0.1",
  "bind_port": 8765,
  "log_file": ".state/sync.log"
}
```

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

启动页面：

```powershell
cloudpan-bridge serve --config .work/openlist-config.json
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

## 自测

当前建议最少跑这两步：

```powershell
.venv\Scripts\python.exe -m compileall src tests
.venv\Scripts\python.exe -m pytest -q
```
