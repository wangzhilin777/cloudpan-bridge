# CloudPan Bridge 前期调研计划

## 1. 文档定位

本文档是 `CloudPan Bridge` 的前期调研计划，专门用于收敛：

- OpenList 全驱动源端调研
- Guangya 目标端能力补强调研
- 跨网盘秒传 / 快传 / 中转上传边界调研
- 后续 provider 扩展时的调研模板

主计划文档：

- `docs/cloudpan-bridge-master-plan.md`

本文档负责“先查什么、怎么归类、产出什么”；
主计划文档负责“最后怎么实施、怎么落代码、怎么验收”。

## 2. 调研总目标

调研不是为了证明“所有组合都能秒传”，而是为了把每个组合的真实能力查清楚。

统一产出以下结论：

- `fast_upload_supported`
- `fast_upload_partial`
- `relay_supported`
- `download_upload_only`
- `unsupported`

## 3. 第一阶段调研范围

### 3.1 源端范围

第一阶段源端范围：

- `OpenList 当前已支持的所有驱动`

重点先覆盖复杂且高频的驱动：

- `AliyundriveOpen`
- `123Open`
- `139Yun`
- `Quark`
- `Thunder`
- `Baidu`
- `OneDrive`
- `PikPak`
- `189Cloud`

### 3.2 目标端范围

当前优先目标端：

- `Guangya`

后续预研目标端：

- Baidu
- Quark
- 123
- Thunder
- AliyunDrive
- OneDrive
- PikPak

## 4. 每个源端驱动需要调研的内容

对每个 OpenList 驱动，至少调研：

1. 是否支持稳定登录
2. 是否支持托管 OpenList 挂载
3. 是否能稳定列目录
4. 是否能提供文件大小与修改时间
5. 是否能提供 `md5`
6. 是否能提供 `etag`
7. 是否能提供 `gcid`
8. 是否能提供 `sha1 / crc64 / pickcode` 等附加指纹
9. 是否能稳定拿到下载链接
10. 是否存在强代理、强 UA、强 Header、验证码、风控等限制

## 5. 每个目标端需要调研的内容

对每个目标端适配器，至少调研：

1. 登录态获取方式
2. Token 刷新方式
3. 是否支持自动创目录
4. 是否支持真正秒传
5. 秒传需要哪些指纹
6. 是否支持部分秒传
7. 秒传失败后的错误模式
8. 是否支持流式中转上传
9. 是否只能本地下载后再上传
10. 风控与频率限制特征

## 6. Guangya 专项调研

Guangya 已有基础实现，但还需要继续调研：

- Authorization 是否总能从网页登录态稳定抓取
- access token / refresh token / device id 的刷新时机
- 秒传接口实际要求的字段集合
- `md5 / etag / gcid` 的兼容程度
- 上传兜底接口对字段类型的严格要求
- 自动建目录与覆盖上传的真实行为

## 7. OpenList 文档与源码双线调研

对 OpenList 驱动不要只看页面字段说明，调研来源分三层：

1. OpenList 官方文档
2. OpenList 驱动字段返回结果
3. OpenList 驱动源码或已知社区说明

这样可以分清：

- 文档支持
- 字段支持
- 实际运行时支持

## 8. 调研产出格式

后续每个 provider 都要沉淀成统一记录，建议字段：

- `provider_key`
- `display_name`
- `openlist_driver_names`
- `login_mode`
- `hash_fields_supported`
- `download_link_supported`
- `fast_upload_targets`
- `recommended_rate_limit_profile`
- `risk_notes`
- `doc_links`
- `capture_strategy`
- `default_mount_values`

## 9. 调研执行顺序

建议顺序：

1. 先做 OpenList 高复杂驱动文档归档
2. 再做字段能力核对
3. 再做真实挂载验证
4. 再做秒传能力矩阵整理
5. 最后再补页面提示与 registry

## 10. 与代码实施的衔接

本调研计划对应的代码落点：

- `provider_registry.py`
- `provider_capture.py`
- `openlist_admin.py`
- `openlist.py`
- `webapp.py`
- `web/index.html`

后续新增调研结论时，应该同步更新：

1. 调研文档
2. provider registry
3. 页面说明
4. README 使用建议

## 11. 当前结论

截至目前：

- 主计划文档里已经写入了“全 OpenList 驱动 + Guangya”的总方向
- 复杂驱动说明 registry 已开始落代码
- 前期调研产出字段已经开始结构化落地到 `provider_registry.py`
  - 已覆盖基础字段：
    - `login_mode`
    - `hash_fields_supported`
    - `download_link_supported`
    - `doc_links`
    - `capture_strategy`
    - `default_mount_values`
    - `risk_notes`
- 页面 `关于` Tab 也已开始直接可视化这些 registry 数据
- 但完整的“前期调研矩阵”仍没有对所有 OpenList 驱动逐项填实

所以本文档从现在开始作为独立入口，承接后续所有调研细化工作。
