window.CloudPanBridgeData = (() => {
    const I18N = {
      zh: {
        "tab.overview": "总览",
        "tab.source": "源端",
        "tab.task": "任务",
        "tab.execute": "执行",
        "tab.pending": "补传",
        "tab.miaochuan": "快传能力",
        "tab.mounts": "连接",
        "tab.config": "目标端",
        "tab.about": "能力与关于",
        "hero.title": "CloudPan Bridge",
        "hero.lead": "统一读取 OpenList 挂载源，优先做秒传，未命中再进入自动补传或待补传目录树。页面会按配置恢复当前目录浏览位置，并把日志单独放到右侧抽屉，避免整页长滚动。",
        "panel.overview": "运行概览",
        "panel.auth_locked": "控制台已加锁",
        "panel.current_route": "当前执行路线",
        "panel.next_step": "下一步建议",
        "panel.capability": "能力矩阵与建议",
        "panel.current_task": "当前任务",
        "panel.task_advanced": "更多任务选项",
        "panel.connection_runtime": "连接与运行时",
        "panel.connection_advanced": "连接节奏与说明",
        "panel.source_browser": "目录浏览",
        "panel.source_driver_debug": "源端技术详情",
        "panel.source_profile_tools": "源端覆盖与映射",
        "panel.source_analyze": "源端元数据分析",
        "panel.leaf_mode": "最底层目录模式",
        "panel.sync_actions": "同步执行",
        "panel.queue": "目录队列",
        "panel.pending_tree": "待补传目录树",
        "panel.miaochuan": "秒传 JSON 直导",
        "panel.mount_overview": "OpenList 挂载总览",
        "panel.provider_capture": "源网盘登录抓取",
        "panel.create_mount": "新增挂载",
        "panel.config": "目标端运行与文件设置",
        "panel.guangya_auth": "目标端连接参数",
        "panel.target_connection_details": "目标端连接与字段",
        "panel.console_admin": "控制台管理员",
        "panel.logs": "实时日志",
        "panel.about": "关于与计划",
        "panel.source_profiles": "源端能力画像",
        "panel.target_profiles": "目标端能力画像",
        "panel.driver_matrix": "驱动支持矩阵",
        "panel.coverage_audit": "驱动覆盖审计",
        "card.runtime": "OpenList 运行时",
        "card.sync": "同步状态",
        "card.capture": "光鸭抓取",
        "card.console_auth": "控制台登录",
        "card.openlist_auth": "OpenList 登录",
        "card.provider_auth": "源网盘网页登录抓取",
        "target.title.guangya": "光鸭云盘",
        "target.title.openlist": "OpenList 挂载目标",
        "target.title.localfs": "本地目录",
        "target.title.webdav": "WebDAV",
        "target.title.s3": "S3 / 对象存储",
        "target.title.seafile": "Seafile",
        "target.title.azureblob": "Azure Blob",
        "target.title.smb": "SMB",
        "target.title.ftp": "FTP",
        "target.title.sftp": "SFTP",
        "btn.install_runtime": "拉取本机 OpenList 运行时",
        "btn.start_runtime": "启动托管 OpenList",
        "btn.login_openlist": "登录 OpenList 并写回 Token",
        "btn.capture_guangya": "打开光鸭登录并自动抓取",
        "btn.direct_sync": "直接同步当前目录",
        "btn.jump_connect": "去连接",
        "btn.jump_source": "去选源目录",
        "btn.jump_target": "去配目标端",
        "btn.jump_execute": "去执行",
        "btn.save_task_config": "保存当前任务配置",
        "btn.browse_root": "浏览挂载根目录",
        "btn.browse_up": "返回上级",
        "btn.browse_refresh": "刷新当前目录",
        "btn.analyze_source": "分析当前源目录",
        "btn.build_source_miaochuan": "生成当前源目录秒传 JSON",
        "btn.use_current_dir": "使用当前目录作为源目录",
        "btn.add_current_queue": "当前目录加入队列",
        "btn.add_leaf_queue": "当前目录最底层批量入队",
        "btn.run_leaf_direct": "最底层边扫边秒传",
        "btn.run_leaf_full": "最底层边扫边同步+补传",
        "btn.run_dry": "只看计划 dry-run",
        "btn.run_next_queue": "执行队列下一个",
        "btn.run_all_queue": "连续执行整个队列",
        "btn.select_all": "全选",
        "btn.clear_all": "全不选",
        "btn.pending_run_selected": "补传已勾选文件",
        "btn.pending_run_stream": "按勾选目录最底层顺序补传",
        "btn.diagnose_miaochuan": "诊断当前秒传 JSON",
        "btn.run_miaochuan": "直接导入光鸭",
        "btn.refresh_storages": "刷新挂载列表",
        "btn.refresh_drivers": "刷新驱动列表",
        "btn.start_provider_capture": "打开网页登录并抓取",
        "btn.show_provider_guide": "查看该网盘接入流程",
        "btn.apply_provider_fields": "写入当前挂载表单",
        "btn.create_storage": "创建挂载",
        "btn.show_driver_guide": "查看接入流程",
        "btn.apply_driver_defaults": "套用推荐默认值",
        "btn.close_dialog": "关闭",
        "btn.open_driver_doc": "打开官方文档",
        "btn.save_all_config": "保存全部配置",
        "btn.console_login": "控制台登录",
        "btn.console_logout": "退出登录",
        "btn.console_login_now": "立即登录控制台",
        "btn.save_source_profile_override": "保存源 Profile 覆盖",
        "btn.clear_logs": "清空日志",
        "btn.clear_override": "清除覆盖",
        "btn.reload_all": "重新载入",
        "btn.save_config_top": "保存配置",
        "btn.toggle_logs_hide": "隐藏日志",
        "btn.toggle_logs_show": "显示日志",
        "btn.open_help_center": "帮助与能力",
        "btn.open_advanced_settings": "打开高级设置",
        "btn.use_mounted_source": "使用挂载源目录",
        "btn.browse_mounted_source": "从已挂载源开始浏览",
        "btn.apply_openlist_target_mount": "写入目标目录",
        "dialog.auth_title": "控制台登录",
        "dialog.auth_desc": "如果你在配置里设置了控制台管理员账号密码，这里需要先登录后才能继续调用接口。",
        "dialog.advanced_title": "高级设置",
        "dialog.advanced_desc": "低频运行参数、路径类配置和控制台保护统一放到这里，避免主流程页面太杂。",
        "dialog.help_center_desc": "帮助说明、能力矩阵和覆盖审计统一收进这里，主流程页面只保留必要操作。",
        "notice.sync_idle": "等待操作",
        "notice.runtime_wait": "等待运行时检查。",
        "notice.auth_idle": "等待登录。",
        "label.source_path": "当前源目录",
        "label.target_path": "光鸭目标目录",
        "label.effective_openlist_url": "OpenList 实际访问地址",
        "label.mounted_source_select": "已挂载源目录",
        "label.openlist_target_mount_select": "OpenList 目标挂载",
        "label.openlist_target_mount_select_task": "任务里的 OpenList 目标挂载",
        "label.source_provider_preference": "源端执行偏好",
        "label.auto_download_threshold_mb": "小文件自动补传阈值(MB，0=只记录)",
        "label.sync_cleanup_strategy": "同步收敛策略",
        "label.delete_removed": "源端已删除时，从同步状态移除记录",
        "label.target_delete_removed": "同时删除目标端真实文件",
        "label.miaochuan_payload": "秒传 JSON",
        "label.driver_select": "驱动类型",
        "label.provider_select": "源网盘类型",
        "label.provider_capture_hint": "抓取提示",
        "label.provider_login_url": "登录地址",
        "label.driver_notice": "说明",
        "label.openlist_mode": "OpenList 连接方式",
        "label.rate_limit_mode": "限流节奏",
        "label.openlist_url": "OpenList 地址",
        "label.openlist_token": "OpenList Token",
        "label.openlist_username": "OpenList 用户名",
        "label.openlist_password": "OpenList 密码",
        "label.managed_openlist_bin": "托管 OpenList 可执行文件",
        "label.managed_openlist_data_dir": "托管 OpenList 数据目录",
        "label.managed_openlist_port": "托管 OpenList 端口",
        "label.managed_openlist_docker_image": "Docker 镜像",
        "label.managed_openlist_docker_container_name": "Docker 容器名",
        "label.managed_openlist_init_username": "托管初始化管理员账号",
        "label.managed_openlist_init_password": "托管初始化管理员密码",
        "label.log_file": "日志文件",
        "label.temp_dir": "临时下载目录",
        "label.state_file": "状态文件",
        "label.target_key": "当前目标端",
        "label.openlist_page_size": "OpenList 每页数",
        "label.openlist_request_interval_ms": "OpenList 请求间隔(ms)",
        "label.queue_interval_ms": "目录间隔(ms)",
        "label.guangya_phone": "光鸭手机号",
        "label.guangya_device_id": "光鸭 Device ID",
        "label.guangya_access_token": "光鸭 Access Token",
        "label.guangya_refresh_token": "光鸭 Refresh Token",
        "label.guangya_authorization": "光鸭 Authorization",
        "label.local_target_root": "本地目标根目录",
        "label.webdav_target_url": "WebDAV 目标地址",
        "label.webdav_target_username": "WebDAV 用户名",
        "label.webdav_target_password": "WebDAV 密码",
        "label.s3_target_endpoint": "S3 服务地址",
        "label.s3_target_bucket": "S3 Bucket 名称",
        "label.s3_target_prefix": "S3 前缀目录",
        "label.s3_target_access_key": "S3 访问密钥",
        "label.s3_target_secret_key": "S3 密钥",
        "label.s3_target_region": "S3 区域",
        "label.seafile_target_url": "Seafile 目标地址",
        "label.seafile_target_token": "Seafile Token",
        "label.seafile_target_username": "Seafile 用户名",
        "label.seafile_target_password": "Seafile 密码",
        "label.seafile_target_repo_id": "Seafile 资料库 ID",
        "label.seafile_target_repo_name": "Seafile 资料库名称",
        "label.azureblob_target_account_url": "Azure Blob 账号地址",
        "label.azureblob_target_container": "Azure Blob 容器",
        "label.azureblob_target_prefix": "Azure Blob 前缀",
        "label.azureblob_target_account_name": "Azure Blob 账号名",
        "label.azureblob_target_account_key": "Azure Blob 账号密钥",
        "label.smb_target_url": "SMB 目标地址",
        "label.smb_target_username": "SMB 用户名",
        "label.smb_target_password": "SMB 密码",
        "label.ftp_target_url": "FTP 目标地址",
        "label.ftp_target_username": "FTP 用户名",
        "label.ftp_target_password": "FTP 密码",
        "label.sftp_target_url": "SFTP 目标地址",
        "label.sftp_target_username": "SFTP 用户名",
        "label.sftp_target_password": "SFTP 密码",
        "label.source_profile_override": "源 Profile 覆盖",
        "label.override_note": "覆盖说明",
        "label.app_admin_username": "控制台管理员账号",
        "label.app_admin_password": "控制台管理员密码",
        "label.auth_username": "用户名",
        "label.auth_password": "密码",
        "desc.source_browser": "页面进入时会优先按配置里的 source_path 恢复当前浏览目录；如果该目录读取失败，再回退到挂载根目录。",
        "desc.source_analyze": "开始真正同步前，先做一次源目录分析。这里会统计当前目录中有多少文件带 MD5、多少文件带 GCID、各 provider 占比，以及抽样展示前几条源文件元数据。",
        "desc.overview_flow": "推荐顺序：先在“连接”完成 OpenList 或直连接入，再到“源端”选目录，在“目标端”配置写入目标，然后在“任务”确认路径与策略，最后到“执行”和“补传”完成同步。",
        "desc.connection_login_summary": "这里已经内置 3 类登录/接入能力：控制台登录、OpenList 登录回写 Token、源网盘网页登录抓取并回填挂载表单。",
        "desc.execute_primary": "先在这里完成主执行；补传、秒传和能力说明都在下方折叠区，按需展开即可。",
        "desc.panel_connection_advanced_summary": "Rate limit 和接入说明默认收起，避免第一屏过满。",
        "desc.panel_source_driver_debug_summary": "普通使用可以不看，只有排障时再展开。",
        "desc.panel_source_profile_tools_summary": "只有驱动识别不准时，才需要手动改这里。",
        "desc.panel_task_advanced_summary": "执行偏好、小文件补传阈值、删除策略等低频项收在这里。",
        "desc.panel_target_connection_details_summary": "默认收起，只有填写凭证或排查连接问题时再展开。",
        "desc.console_auth_card": "控制整个控制台页面访问。开启后，必须先通过右上角登录弹窗进入。",
        "desc.openlist_auth_card": "用于把用户名密码登录成 Token，并写回当前模式配置。",
        "desc.provider_auth_card": "用于抓浏览器登录态，再尽量自动回填挂载字段，减少手工抄写。",
        "desc.leaf_mode": "适合防风控慢跑。可以直接边扫边同步，也可以先把叶子目录加入队列后分批执行。",
        "desc.pending_tree": "这里按真实目录树展示，父目录勾选会联动所有子目录和文件。",
        "desc.miaochuan": "支持直接粘贴油猴或插件导出的 JSON。若你已自动抓取到光鸭 Authorization，会优先使用它。",
        "desc.provider_capture": "如果还没有挂载，或想直接从网页登录态抓取 Cookie / Token / Header，可以先在这里选网盘类型，打开登录页抓取，再一键写入当前挂载表单。",
        "desc.openlist_target_bridge": "当前目标端会复用上方“连接”页里已经配置好的 OpenList 连接信息。这里不用重复填目标端账号密码；只要先把 OpenList 连接打通，再在任务区填写目标目录即可。",
        "desc.task_openlist_target_hint": "当前目标端是 OpenList 挂载目标。你可以在这里直接选具体挂载，也可以去“目标端”页先选挂载后再回到这里确认目标目录。",
        "desc.capability": "根据当前选择的源驱动和现有目标端 Guangya，给出诚实降级后的推荐路径。这里不会把“只能补传”的组合误导成可秒传。",
        "desc.logs": "这里会自动滚动到最新日志。同步、队列、挂载和目标端状态都可以从这里看。",
        "desc.target_primary": "这一页只保留目标端选择、目标端凭证和目标挂载。日志路径、状态文件、控制台管理员等高级项已移到二级弹窗。",
        "desc.source_mount_quick_pick": "先在这里选一个已挂载源，再进入目录浏览，会更容易理解当前在操作哪个网盘。",
        "desc.panel_source_analyze_summary": "低频分析工具，默认收起。",
        "desc.panel_leaf_mode_summary": "慢跑、防风控和队列准备放这里。",
        "desc.panel_queue_summary": "当前目录队列与连续执行入口。",
        "desc.panel_pending_summary": "执行失败后再展开这里处理补传。",
        "desc.panel_capability_summary": "是否能秒传、怎么降级，看这里。",
        "desc.panel_miaochuan_summary": "增强入口，默认收起，支持时再用。",
        "desc.panel_mount_overview_summary": "已挂载内容与驱动列表，默认收起。",
        "desc.panel_provider_capture_summary": "没挂载时再展开这里接入源网盘。",
        "desc.panel_create_mount_summary": "需要手动建挂载时再展开。",
        "desc.source_profiles": "这里列出当前内置的 OpenList 源端 profile、常见哈希和推荐频率。后续继续扩全驱动时，就往这层补。",
        "desc.target_profiles": "这里列出当前目标端适配器支持的快传指纹和降级方式。当前内置目标端包括 Guangya、OpenList、LocalFS、WebDAV、S3、Seafile、Azure Blob、SMB、FTP 与 SFTP，其中只有 Guangya 支持元数据秒传。",
        "desc.driver_matrix": "这是当前内置的“源驱动 -> Guangya”能力矩阵，只表示当前项目的真实支持判断，不等于所有跨网盘都能秒传。",
        "desc.coverage_audit": "这里会把当前 OpenList 实际驱动列表和内置 registry 对比，直接看出哪些驱动已经具备 profile、guide、capture、capability，方便后续继续补全。",
        "desc.target_delete_removed": "默认只做新增 + 覆盖。只有同时开启 delete_removed 和 target_delete_removed 时，才会尝试删除目标端真实文件。",
        "desc.auth_locked": "如果你启用了控制台管理员账号密码，需要先登录后才能继续加载连接、源端、目标端和同步页面。",
        "desc.console_admin": "这是 CloudPan Bridge 控制台本身的登录保护，不是 OpenList 管理员账号。",
        "desc.source_profile_override": "默认按挂载驱动自动匹配 source profile；如果当前驱动识别不准，可以在这里手动改绑。",
        "mounts.mode.external_local.title": "连接已有实例（本机）",
        "mounts.mode.external_local.desc": "适合你已经在本机启动了 OpenList，只需要填写地址、账号密码或 Token 并回写。",
        "mounts.mode.external_remote.title": "连接已有实例（远程）",
        "mounts.mode.external_remote.desc": "适合 NAS、服务器或远程机器上已运行的 OpenList。这里只显示远程实例相关配置，不再混进托管参数。",
        "mounts.mode.managed_binary.title": "托管模式（本机二进制）",
        "mounts.mode.managed_binary.desc": "适合你本机直接托管 OpenList。这里会单独显示运行参数、初始化管理员和运行时操作按钮。",
        "mounts.mode.managed_docker.title": "托管模式（Docker 预留）",
        "mounts.mode.managed_docker.desc": "这块先做结构化预留与参数保存，不会假装已经完整实现自动起容器。",
        "btn.export_coverage_json": "导出覆盖审计 JSON",
        "btn.export_coverage_md": "导出覆盖审计 Markdown",
        "btn.export_coverage_scaffold_json": "导出待补 Scaffold JSON",
        "btn.export_coverage_scaffold_md": "导出补全任务 Markdown",
        "option.openlist_mode.external_local": "外部模式（本机）",
        "option.openlist_mode.external_remote": "外部模式（远程）",
        "option.openlist_mode.managed_binary": "托管模式（本机二进制）",
        "option.openlist_mode.managed_docker": "托管模式（Docker）",
        "option.source_provider_preference.auto": "自动",
        "option.source_provider_preference.openlist_only": "只走 OpenList",
        "option.source_provider_preference.direct_preferred": "优先直连 Provider",
        "option.rate_limit_mode.safe": "稳妥",
        "option.rate_limit_mode.balanced": "平衡",
        "option.rate_limit_mode.fast": "快速",
        "option.rate_limit_mode.custom": "自定义",
        "placeholder.auth_username": "请输入控制台账号",
        "placeholder.auth_password": "请输入控制台密码",
        "placeholder.provider_login_url": "https://登录页地址",
        "placeholder.miaochuan_payload": "{\"files\":[{\"path\":\"/demo.zip\",\"size\":\"123\",\"etag\":\"md5\"}]}",
        "placeholder.guangya_authorization": "Bearer ...",
        "placeholder.local_target_root": "E:\\CloudPanBridge\\Exports",
        "placeholder.webdav_target_url": "https://dav.example.com/remote.php/dav/files/demo",
        "placeholder.s3_target_endpoint": "https://s3.example.com",
        "placeholder.s3_target_bucket": "bucket-name",
        "placeholder.s3_target_region": "ap-southeast-1",
        "placeholder.s3_target_prefix": "cloudpan-bridge/archive",
        "placeholder.seafile_target_url": "https://seafile.example.com",
        "placeholder.seafile_target_repo_id": "repo-id",
        "placeholder.seafile_target_repo_name": "My Library",
        "placeholder.azureblob_target_account_url": "https://demo.blob.core.windows.net",
        "placeholder.azureblob_target_container": "archive-container",
        "placeholder.azureblob_target_prefix": "cloudpan-bridge/archive",
        "placeholder.smb_target_url": "smb://server/share/path",
        "placeholder.ftp_target_url": "ftp://example.com:21/uploads",
        "placeholder.sftp_target_url": "sftp://example.com:22/uploads"
      },
      en: {
        "tab.overview": "Overview",
        "tab.source": "Source",
        "tab.task": "Task",
        "tab.execute": "Run",
        "tab.pending": "Reupload",
        "tab.miaochuan": "Fast Upload",
        "tab.mounts": "Connections",
        "tab.config": "Target",
        "tab.about": "Capability and About",
        "hero.title": "CloudPan Bridge",
        "hero.lead": "Read OpenList-mounted sources through one console, try fast upload first, and fall back to automatic or queued reupload when needed. The page restores the last browsed directory and keeps logs in a right-side drawer to avoid long scrolling.",
        "panel.overview": "Runtime Overview",
        "panel.auth_locked": "Console Locked",
        "panel.current_route": "Current Route",
        "panel.next_step": "Next Step",
        "panel.capability": "Capability and Recommendation",
        "panel.current_task": "Current Task",
        "panel.task_advanced": "More Task Options",
        "panel.connection_runtime": "Connection and Runtime",
        "panel.connection_advanced": "Connection Pace and Notes",
        "panel.source_browser": "Directory Browser",
        "panel.source_driver_debug": "Source Debug Details",
        "panel.source_profile_tools": "Source Override and Mapping",
        "panel.source_analyze": "Source Metadata Analysis",
        "panel.leaf_mode": "Leaf Directory Mode",
        "panel.sync_actions": "Sync Actions",
        "panel.queue": "Directory Queue",
        "panel.pending_tree": "Pending Reupload Tree",
        "panel.miaochuan": "Flash Upload JSON Import",
        "panel.mount_overview": "OpenList Mount Overview",
        "panel.provider_capture": "Source Provider Capture",
        "panel.create_mount": "Create Mount",
        "panel.config": "Target Runtime and File Settings",
        "panel.guangya_auth": "Target Connection Fields",
        "panel.target_connection_details": "Target Connection Details",
        "panel.console_admin": "Console Admin",
        "panel.logs": "Live Logs",
        "panel.about": "About and Plan",
        "panel.source_profiles": "Source Profiles",
        "panel.target_profiles": "Target Profiles",
        "panel.driver_matrix": "Driver Capability Matrix",
        "panel.coverage_audit": "Driver Coverage Audit",
        "card.runtime": "OpenList Runtime",
        "card.sync": "Sync Status",
        "card.capture": "Guangya Capture",
        "card.console_auth": "Console Login",
        "card.openlist_auth": "OpenList Login",
        "card.provider_auth": "Source Provider Web Capture",
        "target.title.guangya": "Guangya",
        "target.title.openlist": "OpenList Mount Target",
        "target.title.localfs": "Local Folder",
        "target.title.webdav": "WebDAV",
        "target.title.s3": "S3 / Object Storage",
        "target.title.seafile": "Seafile",
        "target.title.azureblob": "Azure Blob",
        "target.title.smb": "SMB",
        "target.title.ftp": "FTP",
        "target.title.sftp": "SFTP",
        "btn.start_runtime": "Start Managed OpenList",
        "btn.install_runtime": "Install Local OpenList Runtime",
        "btn.login_openlist": "Login OpenList and Save Token",
        "btn.capture_guangya": "Open Guangya Login Capture",
        "btn.direct_sync": "Sync Current Source",
        "btn.jump_connect": "Open Connections",
        "btn.jump_source": "Pick Source",
        "btn.jump_target": "Configure Target",
        "btn.jump_execute": "Open Run",
        "btn.save_task_config": "Save Task Config",
        "btn.browse_root": "Browse Mount Root",
        "btn.browse_up": "Go Parent",
        "btn.browse_refresh": "Refresh Current Directory",
        "btn.analyze_source": "Analyze Current Source",
        "btn.build_source_miaochuan": "Build Flash Upload JSON",
        "btn.use_current_dir": "Use Current Directory as Source",
        "btn.add_current_queue": "Add Current Directory to Queue",
        "btn.add_leaf_queue": "Queue All Leaf Directories",
        "btn.run_leaf_direct": "Leaf Scan and Flash Sync",
        "btn.run_leaf_full": "Leaf Scan with Reupload",
        "btn.run_dry": "Dry Run Only",
        "btn.run_next_queue": "Run Next Queue Item",
        "btn.run_all_queue": "Run Full Queue",
        "btn.select_all": "Select All",
        "btn.clear_all": "Clear All",
        "btn.pending_run_selected": "Reupload Selected Files",
        "btn.pending_run_stream": "Reupload by Selected Leaf Order",
        "btn.diagnose_miaochuan": "Diagnose Current Flash JSON",
        "btn.run_miaochuan": "Import to Guangya",
        "btn.refresh_storages": "Refresh Mount List",
        "btn.refresh_drivers": "Refresh Driver List",
        "btn.start_provider_capture": "Open Login Capture",
        "btn.show_provider_guide": "View Provider Guide",
        "btn.apply_provider_fields": "Apply to Mount Form",
        "btn.create_storage": "Create Mount",
        "btn.show_driver_guide": "View Setup Guide",
        "btn.apply_driver_defaults": "Apply Recommended Defaults",
        "btn.close_dialog": "Close",
        "btn.open_driver_doc": "Open Official Doc",
        "btn.save_all_config": "Save All Config",
        "btn.console_login": "Console Login",
        "btn.console_logout": "Logout",
        "btn.console_login_now": "Login Now",
        "btn.save_source_profile_override": "Save Source Profile Override",
        "btn.clear_logs": "Clear Logs",
        "btn.clear_override": "Clear Override",
        "btn.reload_all": "Reload",
        "btn.save_config_top": "Save Config",
        "btn.toggle_logs_hide": "Hide Logs",
        "btn.toggle_logs_show": "Show Logs",
        "btn.open_help_center": "Help and Capability",
        "btn.open_advanced_settings": "Open Advanced Settings",
        "btn.use_mounted_source": "Use Mounted Source",
        "btn.browse_mounted_source": "Browse From Mount",
        "btn.apply_openlist_target_mount": "Use as Target Directory",
        "dialog.auth_title": "Console Login",
        "dialog.auth_desc": "If console admin credentials are configured, you must log in here before the protected APIs and pages continue loading.",
        "dialog.advanced_title": "Advanced Settings",
        "dialog.advanced_desc": "Low-frequency runtime parameters, path settings, and console protection are grouped here so the main workflow stays clean.",
        "dialog.help_center_desc": "Help text, capability matrices, and coverage audit are grouped here so the main workflow stays focused.",
        "notice.sync_idle": "Waiting for action.",
        "notice.runtime_wait": "Waiting for runtime check.",
        "notice.auth_idle": "Waiting for login.",
        "label.source_path": "Current Source Path",
        "label.target_path": "Guangya Target Path",
        "label.effective_openlist_url": "Effective OpenList URL",
        "label.mounted_source_select": "Mounted Source",
        "label.openlist_target_mount_select": "OpenList Target Mount",
        "label.openlist_target_mount_select_task": "Task-side OpenList Target Mount",
        "label.source_provider_preference": "Source Execution Preference",
        "label.auto_download_threshold_mb": "Auto Reupload Threshold (MB, 0 = record only)",
        "label.sync_cleanup_strategy": "Sync Convergence Strategy",
        "label.delete_removed": "Remove missing source files from sync state",
        "label.target_delete_removed": "Also delete the real target files",
        "label.miaochuan_payload": "Flash Upload JSON",
        "label.driver_select": "Driver Type",
        "label.provider_select": "Source Provider",
        "label.provider_capture_hint": "Capture Hint",
        "label.provider_login_url": "Login URL",
        "label.driver_notice": "Description",
        "label.openlist_mode": "OpenList Mode",
        "label.rate_limit_mode": "Rate Limit Mode",
        "label.openlist_url": "OpenList URL",
        "label.openlist_token": "OpenList Token",
        "label.openlist_username": "OpenList Username",
        "label.openlist_password": "OpenList Password",
        "label.managed_openlist_bin": "Managed OpenList Binary",
        "label.managed_openlist_data_dir": "Managed OpenList Data Dir",
        "label.managed_openlist_port": "Managed OpenList Port",
        "label.managed_openlist_docker_image": "Docker Image",
        "label.managed_openlist_docker_container_name": "Docker Container Name",
        "label.managed_openlist_init_username": "Managed Init Admin Username",
        "label.managed_openlist_init_password": "Managed Init Admin Password",
        "label.log_file": "Log File",
        "label.temp_dir": "Temp Download Dir",
        "label.state_file": "State File",
        "label.target_key": "Active Target",
        "label.openlist_page_size": "OpenList Page Size",
        "label.openlist_request_interval_ms": "OpenList Request Interval (ms)",
        "label.queue_interval_ms": "Directory Interval (ms)",
        "label.guangya_phone": "Guangya Phone",
        "label.guangya_device_id": "Guangya Device ID",
        "label.guangya_access_token": "Guangya Access Token",
        "label.guangya_refresh_token": "Guangya Refresh Token",
        "label.guangya_authorization": "Guangya Authorization",
        "label.local_target_root": "Local Target Root",
        "label.webdav_target_url": "WebDAV Target URL",
        "label.webdav_target_username": "WebDAV Username",
        "label.webdav_target_password": "WebDAV Password",
        "label.s3_target_endpoint": "S3 Endpoint",
        "label.s3_target_bucket": "S3 Bucket",
        "label.s3_target_prefix": "S3 Prefix",
        "label.s3_target_access_key": "S3 Access Key",
        "label.s3_target_secret_key": "S3 Secret Key",
        "label.s3_target_region": "S3 Region",
        "label.seafile_target_url": "Seafile Target URL",
        "label.seafile_target_token": "Seafile Token",
        "label.seafile_target_username": "Seafile Username",
        "label.seafile_target_password": "Seafile Password",
        "label.seafile_target_repo_id": "Seafile Repo ID",
        "label.seafile_target_repo_name": "Seafile Repo Name",
        "label.azureblob_target_account_url": "Azure Blob Account URL",
        "label.azureblob_target_container": "Azure Blob Container",
        "label.azureblob_target_prefix": "Azure Blob Prefix",
        "label.azureblob_target_account_name": "Azure Blob Account Name",
        "label.azureblob_target_account_key": "Azure Blob Account Key",
        "label.smb_target_url": "SMB Target URL",
        "label.smb_target_username": "SMB Username",
        "label.smb_target_password": "SMB Password",
        "label.ftp_target_url": "FTP Target URL",
        "label.ftp_target_username": "FTP Username",
        "label.ftp_target_password": "FTP Password",
        "label.sftp_target_url": "SFTP Target URL",
        "label.sftp_target_username": "SFTP Username",
        "label.sftp_target_password": "SFTP Password",
        "label.source_profile_override": "Source Profile Override",
        "label.override_note": "Override Note",
        "label.app_admin_username": "Console Admin Username",
        "label.app_admin_password": "Console Admin Password",
        "label.auth_username": "Username",
        "label.auth_password": "Password",
        "desc.source_browser": "On load, the page restores the browser to source_path first. If that path fails, it falls back to the mount root.",
        "desc.source_analyze": "Before starting a real sync, run a source analysis first. It counts how many files have MD5, how many have GCID, shows provider distribution, and previews the first few source file metadata rows.",
        "desc.overview_flow": "Recommended order: finish OpenList or direct-provider connection in Connections, choose the source directory in Source, configure the write target in Target, then run the job from Task and Reupload.",
        "desc.connection_login_summary": "This page already includes three login/onboarding flows: console login, OpenList login with token write-back, and source-provider web login capture with mount-form prefill.",
        "desc.execute_primary": "Finish the main execution here first. Reupload, flash-upload, and capability guidance are tucked into the fold-out sections below.",
        "desc.panel_connection_advanced_summary": "Rate limit presets and onboarding notes are collapsed by default so the first screen stays focused.",
        "desc.panel_source_profile_tools_summary": "Only touch this when the mounted driver is mapped incorrectly.",
        "desc.panel_task_advanced_summary": "Execution preference, auto reupload threshold, and delete strategy are grouped here.",
        "desc.console_auth_card": "Controls access to the console itself. When enabled, the top-right login dialog must be completed first.",
        "desc.openlist_auth_card": "Turns the configured username and password into an OpenList token and writes it back to the active mode snapshot.",
        "desc.provider_auth_card": "Captures browser login state from the source provider and then tries to prefill the mount form automatically.",
        "desc.leaf_mode": "Best for throttled syncing. You can sync while scanning, or queue leaf directories first.",
        "desc.pending_tree": "This tree follows the real directory hierarchy. Parent selection cascades to children and files.",
        "desc.miaochuan": "Paste JSON exported by your userscript or plugin. If Guangya Authorization has been captured, it will be used first.",
        "desc.provider_capture": "If you do not have a mount yet, or want to capture Cookie / Token / Header directly from a web login session, choose the provider here, start login capture, then apply the result to the current mount form.",
        "desc.openlist_target_bridge": "This target reuses the OpenList connection configured in the Connections tab. You do not need a second target-side account here; connect OpenList first, then fill only the target directory in the task area.",
        "desc.task_openlist_target_hint": "The active target is an OpenList mount target. You can choose the concrete mount here directly, or pick it in the Target tab first and return here to confirm target_path.",
        "desc.capability": "Show the honest recommendation for the current source driver to Guangya, including fallback behavior instead of overpromising fast upload.",
        "desc.logs": "Logs auto-scroll to the newest line. Sync, queue, mount, and target-state activity all appear here.",
        "desc.target_primary": "This page only keeps target selection, target credentials, and target mount picking. Log paths, state files, and console admin are moved into a secondary dialog.",
        "desc.source_mount_quick_pick": "Pick a mounted source here first, then browse inside it so the active cloud drive is obvious at a glance.",
        "desc.panel_source_driver_debug_summary": "Most users can ignore this. Expand it only when troubleshooting.",
        "desc.panel_source_analyze_summary": "Low-frequency analysis tools, collapsed by default.",
        "desc.panel_target_connection_details_summary": "Collapsed by default. Expand only when entering credentials or debugging a connection issue.",
        "desc.panel_leaf_mode_summary": "Slow-run, anti-risk, and queue preparation live here.",
        "desc.panel_queue_summary": "Current directory queue and continuous execution entry.",
        "desc.panel_pending_summary": "Open this only after execution leaves files pending.",
        "desc.panel_capability_summary": "See whether fast upload is possible and how fallback works.",
        "desc.panel_miaochuan_summary": "Advanced entry, collapsed by default, use only when supported.",
        "desc.panel_mount_overview_summary": "Mounted items and driver list, collapsed by default.",
        "desc.panel_provider_capture_summary": "Expand this when the source provider has not been mounted yet.",
        "desc.panel_create_mount_summary": "Expand only when you need to create a mount manually.",
        "desc.source_profiles": "This lists the built-in OpenList source profiles, likely hashes, and recommended rate presets. Keep extending this layer as more drivers are covered.",
        "desc.target_profiles": "This lists the current target adapters, their fast-upload hashes, and fallback modes. Built-in targets now include Guangya, OpenList, LocalFS, WebDAV, S3, Seafile, Azure Blob, SMB, FTP, and SFTP, while only Guangya supports metadata-based fast upload.",
        "desc.driver_matrix": "This is the current built-in source-driver to Guangya matrix. It reflects this project's real support judgment, not a promise that all cross-cloud copies can fast upload.",
        "desc.coverage_audit": "This compares the live OpenList driver list with the built-in registry so you can see which drivers already have profiles, guides, capture, and capability coverage.",
        "desc.target_delete_removed": "Default mode only adds and overwrites. Real target deletion is attempted only when both delete_removed and target_delete_removed are enabled.",
        "desc.auth_locked": "If console admin credentials are enabled, you must log in before the connection, source, target, and sync areas continue loading.",
        "desc.console_admin": "This protects the CloudPan Bridge console itself. It is not the same as the OpenList admin account.",
        "desc.source_profile_override": "By default, source profiles are inferred from the mounted driver. Use this only when the current driver mapping is inaccurate.",
        "mounts.mode.external_local.title": "Connect Existing Instance (Local)",
        "mounts.mode.external_local.desc": "Use this when OpenList is already running on the current machine and you only need the URL, credentials, or token.",
        "mounts.mode.external_remote.title": "Connect Existing Instance (Remote)",
        "mounts.mode.external_remote.desc": "Use this for OpenList instances that already run on a NAS, server, or another remote machine. Only remote-instance fields are shown here.",
        "mounts.mode.managed_binary.title": "Managed Mode (Local Binary)",
        "mounts.mode.managed_binary.desc": "Use this to host OpenList directly on the current machine. Runtime options, init admin settings, and startup controls stay isolated here.",
        "mounts.mode.managed_docker.title": "Managed Mode (Docker Reserved)",
        "mounts.mode.managed_docker.desc": "This section currently focuses on structured parameters and saved state. It does not pretend full auto-container orchestration is finished yet.",
        "btn.export_coverage_json": "Export Coverage JSON",
        "btn.export_coverage_md": "Export Coverage Markdown",
        "btn.export_coverage_scaffold_json": "Export Scaffold JSON",
        "btn.export_coverage_scaffold_md": "Export Task Markdown",
        "option.openlist_mode.external_local": "External (Local)",
        "option.openlist_mode.external_remote": "External (Remote)",
        "option.openlist_mode.managed_binary": "Managed (Binary)",
        "option.openlist_mode.managed_docker": "Managed (Docker)",
        "option.source_provider_preference.auto": "Auto",
        "option.source_provider_preference.openlist_only": "OpenList Only",
        "option.source_provider_preference.direct_preferred": "Prefer Direct Provider",
        "option.rate_limit_mode.safe": "Safe",
        "option.rate_limit_mode.balanced": "Balanced",
        "option.rate_limit_mode.fast": "Fast",
        "option.rate_limit_mode.custom": "Custom",
        "placeholder.auth_username": "Enter console username",
        "placeholder.auth_password": "Enter console password",
        "placeholder.provider_login_url": "https://provider-login.example.com",
        "placeholder.miaochuan_payload": "{\"files\":[{\"path\":\"/demo.zip\",\"size\":\"123\",\"etag\":\"md5\"}]}",
        "placeholder.guangya_authorization": "Bearer ...",
        "placeholder.local_target_root": "E:\\CloudPanBridge\\Exports",
        "placeholder.webdav_target_url": "https://dav.example.com/remote.php/dav/files/demo",
        "placeholder.s3_target_endpoint": "https://s3.example.com",
        "placeholder.s3_target_bucket": "bucket-name",
        "placeholder.s3_target_region": "ap-southeast-1",
        "placeholder.s3_target_prefix": "cloudpan-bridge/archive",
        "placeholder.seafile_target_url": "https://seafile.example.com",
        "placeholder.seafile_target_repo_id": "repo-id",
        "placeholder.seafile_target_repo_name": "My Library",
        "placeholder.azureblob_target_account_url": "https://demo.blob.core.windows.net",
        "placeholder.azureblob_target_container": "archive-container",
        "placeholder.azureblob_target_prefix": "cloudpan-bridge/archive",
        "placeholder.smb_target_url": "smb://server/share/path",
        "placeholder.ftp_target_url": "ftp://example.com:21/uploads",
        "placeholder.sftp_target_url": "sftp://example.com:22/uploads"
      },
      mix: {}
    };
    const HELP_TEXT = {
      zh: {
        panel_overview: "这里看整体运行状态和常用快捷入口，适合先确认 OpenList、目标端和同步状态。",
        btn_install_runtime: "当你选择本机二进制托管，但当前机器还没有 OpenList 可执行文件时，先用这个按钮拉取本机运行时。",
        btn_start_runtime: "仅托管模式会用到。由本项目按配置自动拉起 OpenList。",
        btn_login_openlist: "使用当前填写的 OpenList 地址、用户名和密码登录，并把 Token 写回配置。",
        btn_capture_guangya: "打开光鸭网页登录抓取，尽量自动补齐 Authorization、access token、refresh token 和 device id。",
        btn_direct_sync: "立即对当前 source_path 执行一次同步。默认语义是新增 + 覆盖，不会自动删除目标端文件。",
        panel_current_task: "这里是本次任务最常改的源目录、目标目录和补传阈值设置。",
        source_path: "真正参与扫描和同步的源目录。可手填，也可从目录浏览或挂载下拉写入。",
        target_path: "目标端保存目录。源目录内容会按相对路径映射到这里。",
        mounted_source_select: "从当前 OpenList 已挂载目录里选一个入口，再写回 source_path。",
        source_provider_preference: "决定当前任务优先走 OpenList 挂载源，还是优先尝试后续的 provider 直连路径。当前版本即使选“优先直连”，也会诚实回退到 OpenList，直到真实直连源执行链路补齐。",
        effective_openlist_url: "当前实际正在使用的 OpenList 地址。托管模式下可能和手填地址不同。",
        auto_download_threshold_mb: "秒传未命中的文件，小于等于这个值会自动走下载后上传。设为 0 表示只记录待补传，不自动补。",
        btn_save_task_config: "保存当前任务相关配置，不用滚动到底部再统一保存。",
        btn_use_mounted_source: "把当前下拉选中的挂载目录直接写入 source_path。",
        panel_source_browser: "用于浏览 OpenList 目录并快速定位 source_path，本身不会开始同步。",
        btn_browse_root: "回到 OpenList 挂载根目录重新选路径。",
        btn_browse_up: "回到当前浏览目录的上一级。",
        btn_browse_refresh: "重新读取当前目录列表。",
        btn_use_current_dir: "把当前浏览到的目录直接设为 source_path。",
        panel_source_analyze: "先只分析元数据，不真正上传。适合先判断当前目录有没有 MD5、GCID 等快传条件。",
        btn_analyze_source: "统计当前目录的文件数、MD5/GCID 可用性和 provider 分布。",
        btn_build_source_miaochuan: "基于当前目录元数据生成一份可继续导入的秒传 JSON 预览。",
        panel_sync_actions: "正式执行区。这里的动作会真正启动同步或队列任务。",
        btn_run_dry: "只生成计划，不实际上传，适合先看会改哪些文件。",
        btn_run_next_queue: "按目录队列顺序，只执行下一个启用项。",
        btn_run_all_queue: "连续执行目录队列里的所有启用项。",
        panel_leaf_mode: "大目录慢跑模式。会下钻到最底层目录后逐个执行，通常更稳。",
        btn_add_current_queue: "把当前目录作为一个队列任务加入。",
        btn_add_leaf_queue: "扫描当前目录下面所有叶子目录，再批量加入队列。",
        btn_run_leaf_direct: "扫描到一个最底层目录就立即同步一个，然后继续下一个。",
        btn_run_leaf_full: "最底层目录立即同步；秒传未命中时，也允许按阈值走补传。",
        panel_pending_tree: "这里管理所有待补传文件，按真实目录树显示，可按目录联动勾选。",
        btn_pending_run_selected: "仅对当前勾选的文件执行补传。",
        btn_pending_run_stream: "按勾选目录的最底层顺序逐批补传，更适合多目录慢跑。",
        panel_miaochuan: "适合已经拿到外部插件或脚本导出的秒传 JSON 时直接导入。",
        miaochuan_payload: "把外部导出的秒传 JSON 粘贴在这里，通常包含 path、size、etag 等快传字段。",
        btn_diagnose_miaochuan: "先检查这份 JSON 是否格式正确、包含多少可用条目。",
        btn_run_miaochuan: "直接把当前 JSON 交给目标端处理。",
        panel_provider_capture: "源网盘网页登录抓取区。适合还没挂载，或想先抓 Cookie/Token/Header 再回填挂载表单。",
        provider_select: "选择你要抓登录态的源网盘类型。",
        provider_login_url: "默认会给推荐登录页；如果你更清楚实际登录入口，也可以手工改成那个地址。",
        btn_start_provider_capture: "打开网页并尝试抓取登录态。部分驱动会退化成手动凭证模式。",
        btn_show_provider_guide: "查看当前源网盘的接入流程、字段说明和文档入口。",
        btn_apply_provider_fields: "把刚抓到的字段尽量自动回填到下面的挂载创建表单里。",
        panel_create_mount: "根据 OpenList 驱动动态生成挂载字段，用来新建一个源挂载。",
        driver_select: "选择 OpenList 驱动类型，下面会动态加载该驱动的字段和默认值。",
        btn_show_driver_guide: "打开当前驱动的接入说明。",
        btn_apply_driver_defaults: "把内置的保守默认值直接回填到当前驱动表单。",
        btn_create_storage: "把当前驱动字段提交给 OpenList，正式创建挂载。",
        panel_config: "全局基础配置区，影响 OpenList 连接方式、频率控制和状态文件位置。",
        openlist_mode: "现在分为外部本机、外部远程、本机二进制托管和 Docker 托管模式。切模式后，会切换到各自独立保存的连接快照。",
        rate_limit_mode: "不同预设会自动套用分页大小和间隔。safe 最稳，fast 最激进。",
        openlist_url: "外部模式下通常填现有 OpenList 地址；托管模式下实际以托管实例地址为准。",
        openlist_token: "如果你已经有可直接使用的 OpenList Token，可填这里；否则可用用户名密码登录自动回写。",
        openlist_username: "用于 OpenList 登录获取 Token 的用户名。",
        openlist_password: "与 OpenList 用户名配套，用于自动登录和写回 Token。",
        managed_openlist_bin: "托管模式要启动的 OpenList 可执行文件路径。",
        managed_openlist_data_dir: "托管 OpenList 的工作数据目录，通常会保存它自己的配置和数据库。",
        managed_openlist_port: "托管模式启动的 OpenList 监听端口，别和现有端口冲突。",
        managed_openlist_docker_image: "Docker 托管模式使用的 OpenList 镜像名。",
        managed_openlist_docker_container_name: "Docker 托管模式使用的容器名；如果同名容器配置不一致，启动时会自动重建。",
        managed_openlist_init_username: "仅用于托管初始化说明的管理员账号，不等同于当前连接凭证。",
        managed_openlist_init_password: "如果留空，后端会把它视为“尚未明确设置初始化密码”，并在状态区提醒。",
        auth_username: "控制台管理员用户名。填写的是 CloudPan Bridge 自己的账号，不是 OpenList 账号。",
        auth_password: "控制台管理员密码。支持回车直接提交登录。",
        target_key_config: "这里是目标端主选择器。切换后，会同步更新任务页和目标端页，并立即刷新能力与预检提示。",
        app_admin_username: "CloudPan Bridge 控制台自己的管理员账号。留空表示不启用控制台登录保护。",
        app_admin_password: "CloudPan Bridge 控制台自己的管理员密码。用户名和密码都填写时才启用登录保护。",
        log_file: "本项目实时日志文件路径。右侧日志抽屉显示的内容主要来自这里。",
        temp_dir: "下载补传时的临时缓存目录。",
        state_file: "同步状态、待补传和目录队列等持久化信息保存位置。",
        openlist_page_size: "每次向 OpenList 列目录时请求的条目数。越大越快，但也更容易触发风控。",
        openlist_request_interval_ms: "两次 OpenList 请求之间的等待间隔，单位毫秒。",
        queue_interval_ms: "目录之间执行的等待间隔，单位毫秒。大目录慢跑时很关键。",
        guangya_phone: "用于光鸭登录态关联和后续接口校验。通常可以通过自动抓取回填。",
        guangya_device_id: "光鸭设备标识。部分接口会依赖它与 token 组合通过校验。",
        guangya_access_token: "光鸭访问令牌，部分读写接口直接使用它。",
        guangya_refresh_token: "光鸭刷新令牌，用于 access token 过期后的续期。",
        guangya_authorization: "如果你有浏览器里抓到的 Authorization 头，可直接填在这里给直导或快传入口使用。",
        local_target_root: "写入本地磁盘时使用的根目录，实际文件会再拼接 target_path。",
        webdav_target_url: "目标端 WebDAV 根地址，建议直接填到要写入的目录层级。",
        webdav_target_username: "WebDAV 登录用户名。",
        webdav_target_password: "WebDAV 登录密码或应用专用密码。",
        s3_target_endpoint: "对象存储服务地址，兼容 S3 的服务通常都需要它。",
        s3_target_bucket: "要写入的 Bucket 名称。",
        s3_target_region: "Bucket 所在区域，部分服务签名时必填。",
        s3_target_prefix: "写入对象时自动追加的公共前缀。",
        s3_target_access_key: "S3 兼容服务 Access Key。",
        s3_target_secret_key: "S3 兼容服务 Secret Key。",
        seafile_target_url: "Seafile 服务地址，建议直接填站点根地址或 API 可达地址。",
        seafile_target_repo_id: "优先使用 Repo ID，可避免同名库选择歧义。",
        seafile_target_repo_name: "如果暂时没有 Repo ID，可先填库名称作为补充定位信息。",
        seafile_target_token: "Seafile API Token，通常比账号密码模式更稳。",
        seafile_target_username: "Seafile 登录用户名。仅当你不用 Token 时才需要它。",
        seafile_target_password: "Seafile 登录密码。仅当你不用 Token 时才需要它。",
        azureblob_target_account_url: "Azure Blob 存储账号地址，通常形如 https://xxx.blob.core.windows.net。",
        azureblob_target_container: "目标容器名称。",
        azureblob_target_account_name: "Azure Blob 账号名。某些部署场景下会与 URL 一起参与鉴权。",
        azureblob_target_prefix: "写入 Blob 时追加的公共前缀。",
        azureblob_target_account_key: "Azure Blob 账号密钥。",
        smb_target_url: "SMB 共享路径，建议写到共享名或目标目录层级。",
        smb_target_username: "SMB 登录用户名。",
        smb_target_password: "SMB 登录密码。",
        ftp_target_url: "FTP 服务地址，包含协议、主机、端口和目标目录。",
        ftp_target_username: "FTP 登录用户名。",
        ftp_target_password: "FTP 登录密码。",
        sftp_target_url: "SFTP 服务地址，包含协议、主机、端口和目标目录。",
        sftp_target_username: "SFTP 登录用户名。",
        sftp_target_password: "SFTP 登录密码。"
      },
      en: {
        panel_overview: "Runtime overview and quick entry points for OpenList, target auth, and sync state.",
        btn_install_runtime: "When managed binary mode is selected but no local OpenList executable is available, use this to fetch a local runtime first.",
        btn_start_runtime: "Used in managed mode to launch OpenList from the configured binary and data directory.",
        btn_login_openlist: "Login with the current OpenList URL, username, and password, then save the token back to config.",
        btn_capture_guangya: "Open Guangya login capture and try to collect authorization, access token, refresh token, and device id.",
        btn_direct_sync: "Run a sync on the current source_path now. Default behavior is add + overwrite without deleting target files.",
        panel_current_task: "Core task settings for this run: source directory, target path, and reupload threshold.",
        source_path: "The real source directory to scan and sync.",
        target_path: "The destination path on the active target adapter.",
        mounted_source_select: "Choose an existing mounted source root from OpenList and write it into source_path.",
        source_provider_preference: "Controls whether the task stays on OpenList or prefers a future direct provider route first. The current build still falls back honestly to OpenList until real direct source execution is implemented.",
        effective_openlist_url: "The actual OpenList endpoint currently in use.",
        auto_download_threshold_mb: "Files at or below this size auto fallback to download-upload when fast upload misses. Set 0 to only record them as pending.",
        btn_save_task_config: "Save the task-related fields here without scrolling to the global save button.",
        btn_use_mounted_source: "Write the selected mounted source into source_path.",
        panel_source_browser: "Browse OpenList directories and locate the source path without starting sync.",
        btn_browse_root: "Jump back to the OpenList mount root.",
        btn_browse_up: "Go to the parent directory.",
        btn_browse_refresh: "Reload the current directory listing.",
        btn_use_current_dir: "Use the current browsed directory as source_path.",
        panel_source_analyze: "Analyze metadata first without uploading anything.",
        btn_analyze_source: "Collect file counts, MD5/GCID availability, and provider distribution.",
        btn_build_source_miaochuan: "Build a flash-upload JSON preview from the current source metadata.",
        panel_sync_actions: "Actual execution area. Actions here start real sync or queue tasks.",
        btn_run_dry: "Generate the plan only without uploading.",
        btn_run_next_queue: "Run only the next enabled queue item.",
        btn_run_all_queue: "Run all enabled queue items in order.",
        panel_leaf_mode: "Leaf-directory mode for large trees. Usually slower but safer.",
        btn_add_current_queue: "Add the current directory as one queue job.",
        btn_add_leaf_queue: "Scan all leaf directories under the current path and add them to the queue.",
        btn_run_leaf_direct: "When a leaf directory is found, sync it immediately, then continue.",
        btn_run_leaf_full: "Leaf sync mode with fallback reupload allowed.",
        panel_pending_tree: "Manage pending reupload files as a real directory tree.",
        btn_pending_run_selected: "Run reupload only for the selected files.",
        btn_pending_run_stream: "Run reupload leaf-by-leaf following the selected directory order.",
        panel_miaochuan: "Use this when you already have a flash-upload JSON from an external script or plugin.",
        miaochuan_payload: "Paste the exported flash-upload JSON here.",
        btn_diagnose_miaochuan: "Validate the JSON and preview usable items first.",
        btn_run_miaochuan: "Submit the current JSON directly to the target side.",
        panel_provider_capture: "Web-login capture area for source providers.",
        provider_select: "Choose which source provider login state you want to capture.",
        provider_login_url: "A recommended login page is provided by default, but you can replace it with a more exact one.",
        btn_start_provider_capture: "Open the login page and try to capture credentials.",
        btn_show_provider_guide: "Show onboarding guide and docs for the current source provider.",
        btn_apply_provider_fields: "Apply the captured fields into the mount form below.",
        panel_create_mount: "Create a new source mount using OpenList driver fields.",
        driver_select: "Choose an OpenList driver type. The form below updates dynamically.",
        btn_show_driver_guide: "Open the current driver's setup guide.",
        btn_apply_driver_defaults: "Apply built-in conservative defaults to the current driver form.",
        btn_create_storage: "Submit the current driver form to OpenList and create the mount.",
        panel_config: "Global settings for connection mode, throttling, and state files.",
        openlist_mode: "Modes are split into external local, external remote, managed binary, and managed Docker. Each mode keeps its own connection snapshot.",
        rate_limit_mode: "Each preset adjusts page size and request intervals. safe is most conservative; fast is most aggressive.",
        openlist_url: "Usually the URL of your external OpenList. In managed mode the actual runtime URL may differ.",
        openlist_token: "If you already have a usable OpenList token, put it here. Otherwise login and write it back automatically.",
        openlist_username: "OpenList username used to obtain a token.",
        openlist_password: "Password paired with the OpenList username.",
        managed_openlist_bin: "Executable path used in managed mode.",
        managed_openlist_data_dir: "Data directory for managed OpenList.",
        managed_openlist_port: "Listening port for managed OpenList.",
        managed_openlist_docker_image: "Docker image used by managed Docker mode.",
        managed_openlist_docker_container_name: "Container name used by managed Docker mode. A mismatched existing container will be recreated on start.",
        managed_openlist_init_username: "Initialization-only admin username for managed mode. It is not the same thing as the current connection credential.",
        managed_openlist_init_password: "If blank, the backend treats it as not explicitly set yet and will warn in runtime status.",
        auth_username: "Console admin username for CloudPan Bridge itself, not the OpenList account.",
        auth_password: "Console admin password. Pressing Enter should submit the login directly.",
        target_key_config: "Primary target selector. Changes here also update the task tab and immediately refresh target capability and preflight hints.",
        app_admin_username: "Admin username for the CloudPan Bridge console itself. Leave blank to disable console login protection.",
        app_admin_password: "Admin password for the CloudPan Bridge console itself. Protection is enabled only when both fields are filled.",
        log_file: "Runtime log file path used by the live log drawer.",
        temp_dir: "Temporary cache directory for download-upload fallback.",
        state_file: "Persistent state for sync history, pending items, and queue progress.",
        openlist_page_size: "Number of entries requested from OpenList per page.",
        openlist_request_interval_ms: "Delay between OpenList requests in milliseconds.",
        queue_interval_ms: "Delay between directory jobs in milliseconds.",
        guangya_phone: "Phone number associated with Guangya login state and some follow-up validation flows.",
        guangya_device_id: "Device identifier expected by some Guangya APIs together with the token set.",
        guangya_access_token: "Guangya access token used by several read and write APIs.",
        guangya_refresh_token: "Refresh token used to renew the Guangya access token when it expires.",
        guangya_authorization: "If you captured the Authorization header from a browser session, you can paste it here for direct import and fast-upload flows.",
        local_target_root: "Root directory used when writing to the local filesystem target. target_path is appended below it.",
        webdav_target_url: "Root WebDAV URL for the write target. It is best to point directly at the final folder level.",
        webdav_target_username: "WebDAV login username.",
        webdav_target_password: "WebDAV password or app-specific password.",
        s3_target_endpoint: "Endpoint URL for the S3-compatible object storage service.",
        s3_target_bucket: "Bucket name used as the destination.",
        s3_target_region: "Bucket region. Some providers require it for request signing.",
        s3_target_prefix: "Common object prefix automatically added during writes.",
        s3_target_access_key: "Access key for the S3-compatible provider.",
        s3_target_secret_key: "Secret key for the S3-compatible provider.",
        seafile_target_url: "Seafile service URL, usually the site root or another API-reachable base URL.",
        seafile_target_repo_id: "Prefer the repo ID when available to avoid ambiguity with duplicate library names.",
        seafile_target_repo_name: "If the repo ID is not available yet, use the library name as a fallback locator.",
        seafile_target_token: "Seafile API token. It is usually more stable than username/password mode.",
        seafile_target_username: "Seafile login username. Needed only when you are not using a token.",
        seafile_target_password: "Seafile login password. Needed only when you are not using a token.",
        azureblob_target_account_url: "Azure Blob storage account URL, usually in the form https://xxx.blob.core.windows.net.",
        azureblob_target_container: "Destination container name.",
        azureblob_target_account_name: "Azure Blob account name. Some setups use it together with the account URL during authentication.",
        azureblob_target_prefix: "Common prefix added when writing blobs.",
        azureblob_target_account_key: "Azure Blob account key.",
        smb_target_url: "SMB share path, ideally pointing at the share or target directory level.",
        smb_target_username: "SMB login username.",
        smb_target_password: "SMB login password.",
        ftp_target_url: "FTP server URL including protocol, host, port, and destination directory.",
        ftp_target_username: "FTP login username.",
        ftp_target_password: "FTP login password.",
        sftp_target_url: "SFTP server URL including protocol, host, port, and destination directory.",
        sftp_target_username: "SFTP login username.",
        sftp_target_password: "SFTP login password."
      }
    };
    const DRIVER_FIELD_I18N = {
      mountpath: { zh: "挂载路径", en: "Mount Path" },
      order: { zh: "排序值", en: "Order" },
      remark: { zh: "备注", en: "Remark" },
      cacheexpiration: { zh: "缓存过期时间", en: "Cache Expiration" },
      customcachepolicies: { zh: "自定义缓存策略", en: "Custom Cache Policies" },
      webdavpolicy: { zh: "WebDAV 策略", en: "WebDAV Policy" },
      downproxyurl: { zh: "下载代理地址", en: "Download Proxy URL" },
      webproxy: { zh: "网页代理", en: "Web Proxy" },
      proxyrange: { zh: "代理 Range", en: "Proxy Range" },
      disableproxysign: { zh: "禁用代理签名", en: "Disable Proxy Sign" },
      orderby: { zh: "排序字段", en: "Sort By" },
      orderdirection: { zh: "排序方向", en: "Sort Direction" },
      disableindex: { zh: "禁用索引", en: "Disable Index" },
      extractfolder: { zh: "文件夹排序", en: "Extract Folder" },
      enablesigning: { zh: "启用签名", en: "Enable Signing" },
      ref: { zh: "引用挂载", en: "Reference Mount" },
    };
    const DRIVER_HELP_PATTERNS = [
      { includes: ["mount to", "unique", "repeated"], zh: "要挂载到的位置，对外显示的名称，必须唯一不能重复。", en: "The mount location and external display name. It must be unique and cannot be repeated." },
      { includes: ["use to sort"], zh: "用于排序，数值越小越靠前。", en: "Used for sorting. Smaller values appear first." },
      { includes: ["cache expiration time", "this storage"], zh: "这个存储的目录结构缓存时间。", en: "Cache duration for this storage directory structure." },
      { includes: ["cache expiration rules", "this storage"], zh: "这个存储的自定义缓存规则。", en: "Custom cache rules for this storage." },
      { includes: ["need to enable proxy"], zh: "是否启用代理功能。", en: "Whether proxy should be enabled." },
      { includes: ["disable sign", "download proxy"], zh: "是否禁用下载代理 URL 的签名。", en: "Whether to disable signing for the download proxy URL." },
      { includes: ["sort by what"], zh: "按什么字段排序。", en: "Which field to sort by." },
      { includes: ["ascending or descending"], zh: "排序方向，升序或降序。", en: "Sort direction, ascending or descending." },
      { includes: ["put all folders to the front"], zh: "排序时将所有文件夹放到前面。", en: "Put all folders in front when sorting." },
      { includes: ["put all folders to the back"], zh: "排序时将所有文件夹放到后面。", en: "Put all folders at the back when sorting." },
      { includes: ["web preview", "direct link", "transfer"], zh: "网页预览、下载和直链是否通过 OpenList 中转。", en: "Whether web preview, download, and direct links go through OpenList transfer." },
      { includes: ["redirect to the real link"], zh: "302 重定向到真实链接。", en: "302 redirect to the real link." },
      { includes: ["redirect to proxy url"], zh: "重定向到代理 URL。", en: "Redirect to the proxy URL." },
      { includes: ["return data directly through local transit"], zh: "通过本地中转直接返回数据，兼容性最好。", en: "Return data directly through local transit for best compatibility." },
      { includes: ["proxy is turned on", "local machine"], zh: "开启代理但未填写地址时，默认使用本机中转。", en: "If proxy is enabled without a URL, the local machine is used for transfer by default." },
      { includes: ["allow users to disable storage indexing"], zh: "允许对这个存储禁用索引。", en: "Allow users to disable storage indexing." },
      { includes: ["reference authentication", "tokens"], zh: "从其他已挂载存储引用认证信息和令牌。", en: "Reference authentication data and tokens from another mounted storage." },
    ];
    const DRIVER_OPTIONS_I18N = {
      "name,size,modified": { zh: "可选: 名称、大小、修改时间", en: "Options: name, size, modified" },
      "asc,desc": { zh: "可选: 升序、降序", en: "Options: asc, desc" },
      "302_redirect,use_proxy_url,native_proxy": { zh: "可选: 302 重定向、使用代理 URL、本机代理", en: "Options: 302 redirect, use proxy URL, native proxy" },
      "extract_front,extract_back": { zh: "可选: 文件夹前置、文件夹后置", en: "Options: extract to front, extract to back" },
    };
    let driverGuideRegistry = {};
    let providerRegistryPayload = { guides: {}, source_profiles: {}, target_profiles: {}, driver_matrix: {} };
    function getStorageValue(primaryKey, legacyKeys = []) {
      const direct = localStorage.getItem(primaryKey);
      if (direct !== null) return direct;
      for (const legacyKey of legacyKeys) {
        const legacyValue = localStorage.getItem(legacyKey);
        if (legacyValue === null) continue;
        localStorage.setItem(primaryKey, legacyValue);
        return legacyValue;
      }
      return null;
    }

    function getSessionStorageValue(primaryKey, legacyKeys = []) {
      const direct = sessionStorage.getItem(primaryKey);
      if (direct !== null) return direct;
      for (const legacyKey of legacyKeys) {
        const legacyValue = sessionStorage.getItem(legacyKey);
        if (legacyValue === null) continue;
        sessionStorage.setItem(primaryKey, legacyValue);
        return legacyValue;
      }
      return null;
    }
    let configCache = {};
    let currentDirectoryPath = "/";
    let currentParentPath = null;
    let pendingSelection = new Set();
    let pendingExpanded = new Set(["/"]);
    let pendingDirectoryFiles = new Map();
    let pendingSelectionTouched = false;
    let latestPendingItems = [];
    let autoRefresher = null;
    let driversCache = [];
    let currentDriverInfo = null;
    let storageRecords = [];
    let sourceAnalyzeCache = null;
    let providerDefinitions = [];
    let providerSnapshots = {};
    let capabilityAssessmentCache = null;
    let driverCaptureBlueprint = null;
    let currentDriverGuide = null;
    let currentProviderGuide = null;
    let coverageAuditCache = null;
    let panelStatePersistTimer = null;
    let uiPrefsPersistTimer = null;
    let authState = { enabled: false, authenticated: true, username: "" };
    let appBootstrapped = false;

    function setAuthNotice(message) {
      const el = document.getElementById("auth-notice");
      if (el) el.textContent = message;
    }

    function showAuthDialog(message = "") {
      document.getElementById("auth-dialog").classList.remove("hidden");
      if (message) setAuthNotice(message);
      const userInput = document.getElementById("auth-username");
      if (userInput && authState?.username) userInput.value = authState.username;
      setTimeout(() => document.getElementById("auth-password")?.focus(), 0);
    }

    function hideAuthDialog() {
      document.getElementById("auth-dialog").classList.add("hidden");
    }

    function setAppLockedState(locked) {
      document.body.classList.toggle("auth-locked", Boolean(locked));
    }

    function stopAutoRefresher() {
      if (autoRefresher) {
        clearInterval(autoRefresher);
        autoRefresher = null;
      }
    }

    function startAutoRefresher() {
      stopAutoRefresher();
      autoRefresher = setInterval(async () => {
        try {
          await refreshStatus();
        } catch (_error) {
        }
      }, 2000);
    }

    function updateAuthUi(nextState = {}) {
      authState = {
        enabled: Boolean(nextState?.enabled),
        authenticated: Boolean(nextState?.authenticated),
        username: String(nextState?.username || ""),
      };
      const badge = document.getElementById("auth-status-badge");
      const loginBtn = document.getElementById("open-auth-login");
      const logoutBtn = document.getElementById("logout-auth");
      if (badge) {
        if (!authState.enabled) badge.textContent = "控制台未加锁";
        else if (authState.authenticated) badge.textContent = `已登录: ${authState.username || "admin"}`;
        else badge.textContent = "控制台已加锁";
      }
      if (loginBtn) loginBtn.classList.toggle("hidden", authState.enabled && authState.authenticated);
      if (logoutBtn) logoutBtn.classList.toggle("hidden", !authState.enabled || !authState.authenticated);
      setAppLockedState(authState.enabled && !authState.authenticated);
    }

    async function fetchAuthStatus() {
      const response = await fetch("/api/auth/status", { credentials: "same-origin" });
      if (!response.ok) throw new Error(response.statusText || "Auth status failed");
      const data = await response.json();
      updateAuthUi(data || {});
      return data;
    }

    async function bootstrapProtectedApp(forceReload = false) {
      if (forceReload || !appBootstrapped) {
        await loadConfig();
        await attemptAutoOpenListLogin();
        await attemptAutoGuangyaCapture();
        await loadDrivers();
        await refreshStorages();
        await ensureDirectoryBrowserReady(true);
        await refreshStatus();
        await loadProviderRegistry();
        await refreshCoverageAudit();
        startAutoRefresher();
        appBootstrapped = true;
      }
    }

    async function ensureAuthorizedAndBootstrap(forceReload = false) {
      const status = await fetchAuthStatus();
      if (status.enabled && !status.authenticated) {
        stopAutoRefresher();
        appBootstrapped = false;
        setAppLockedState(true);
        showAuthDialog("控制台已开启登录保护，请先登录。");
        return false;
      }
      hideAuthDialog();
      setAppLockedState(false);
      await bootstrapProtectedApp(forceReload);
      return true;
    }

    function getGroupedConfigValue(path, fallback = "") {
      let current = configCache?.grouped_config;
      for (const key of Array.isArray(path) ? path : []) {
        if (!current || typeof current !== "object" || !(key in current)) return fallback;
        current = current[key];
      }
      return current ?? fallback;
    }

    function hasGroupedConfigValue(path) {
      let current = configCache?.grouped_config;
      for (const key of Array.isArray(path) ? path : []) {
        if (!current || typeof current !== "object" || !(key in current)) return false;
        current = current[key];
      }
      return current !== undefined;
    }

    function ensureGroupedConfigShape() {
      const grouped = (configCache.grouped_config && typeof configCache.grouped_config === "object") ? configCache.grouped_config : {};
      grouped.app = grouped.app || {};
      grouped.ui = grouped.ui || {};
      grouped.openlist = grouped.openlist || {};
      grouped.openlist.managed_runtime = grouped.openlist.managed_runtime || {};
      grouped.source_session = grouped.source_session || {};
      grouped.targets = grouped.targets || {};
      grouped.targets.guangya = grouped.targets.guangya || {};
      grouped.sync = grouped.sync || {};
      grouped.state = grouped.state || {};
      configCache.grouped_config = grouped;
      return grouped;
    }

    function setGroupedConfigValue(path, value) {
      const grouped = ensureGroupedConfigShape();
      let current = grouped;
      const keys = Array.isArray(path) ? [...path] : [];
      const last = keys.pop();
      for (const key of keys) {
        if (!current[key] || typeof current[key] !== "object") current[key] = {};
        current = current[key];
      }
      if (last) current[last] = value;
    }

    function normalizeFormValue(field, rawValue) {
      const el = document.getElementById(field);
      if (el?.type === "checkbox") return Boolean(el.checked);
      if (el?.type === "number") return Number(rawValue || 0);
      return rawValue;
    }

    function syncConfigFieldsToGrouped(payload) {
      for (const field of CONFIG_FIELDS) {
        const path = CONFIG_GROUPED_PATHS[field];
        if (!path) continue;
        let value = payload?.[field];
        if (value === undefined || value === null || value === "") {
          value = CONFIG_FIELD_DEFAULTS[field] ?? value ?? "";
        }
        setGroupedConfigValue(path, value);
      }
    }

    function normalizeOpenListMode(mode) {
      const normalized = String(mode || "").trim().toLowerCase();
      if (normalized === "external") return "external_local";
      if (normalized === "managed") return "managed_binary";
      return normalized || "external_local";
    }

    function isManagedOpenListMode(mode) {
      return normalizeOpenListMode(mode).startsWith("managed_");
    }

    function getOpenListConnectionGroupedPath(mode) {
      const normalized = normalizeOpenListMode(mode);
      if (normalized === "external_remote") return ["openlist", "connections", "external_remote"];
      if (normalized === "managed_binary" || normalized === "managed_docker") return ["openlist", "connections", "managed_binary"];
      return ["openlist", "connections", "external_local"];
    }

    function getOpenListModeLabel(mode) {
      const normalized = normalizeOpenListMode(mode);
      const labels = {
        external_local: currentLang() === "en" ? "External (Local)" : currentLang() === "mix" ? "外部模式（本机） / External (Local)" : "外部模式（本机）",
        external_remote: currentLang() === "en" ? "External (Remote)" : currentLang() === "mix" ? "外部模式（远程） / External (Remote)" : "外部模式（远程）",
        managed_binary: currentLang() === "en" ? "Managed (Binary)" : currentLang() === "mix" ? "托管模式（本机二进制） / Managed (Binary)" : "托管模式（本机二进制）",
        managed_docker: currentLang() === "en" ? "Managed (Docker)" : currentLang() === "mix" ? "托管模式（Docker） / Managed (Docker)" : "托管模式（Docker）",
      };
      return labels[normalized] || normalized;
    }

    function readOpenListSnapshotFromGrouped(mode) {
      const connectionPath = getOpenListConnectionGroupedPath(mode);
      const connection = getGroupedConfigValue(connectionPath, {}) || {};
      const managedRuntime = getGroupedConfigValue(["openlist", "managed_runtime"], {}) || {};
      const managedInitAdmin = getGroupedConfigValue(["openlist", "managed_init_admin"], {}) || {};
      return {
        openlist_url: normalizeOpenListMode(mode) === "external_remote"
          ? String(connection.url || "")
          : String(connection.url || "http://127.0.0.1:5244"),
        openlist_token: String(connection.token || ""),
        openlist_username: String(connection.username || "admin"),
        openlist_password: String(connection.password || ""),
        managed_openlist_bin: String(managedRuntime.bin || ""),
        managed_openlist_data_dir: String(managedRuntime.data_dir || ".runtime/openlist"),
        managed_openlist_port: String(managedRuntime.port || 5244),
        managed_openlist_docker_image: String((getGroupedConfigValue(["openlist", "managed_docker", "image"], "") || "openlistteam/openlist:latest")),
        managed_openlist_docker_container_name: String((getGroupedConfigValue(["openlist", "managed_docker", "container_name"], "") || "cloudpan-bridge-openlist")),
        managed_openlist_init_username: String(managedInitAdmin.username || "admin"),
        managed_openlist_init_password: String(managedInitAdmin.password || ""),
      };
    }

    function applyOpenListModeSnapshot(mode) {
      const snapshot = readOpenListSnapshotFromGrouped(mode);
      Object.entries(snapshot).forEach(([field, value]) => {
        const el = document.getElementById(field);
        if (el) el.value = value;
      });
      applyOpenListModeUi();
    }

    function persistCurrentOpenListModeSnapshot(mode) {
      const normalized = normalizeOpenListMode(mode);
      const connectionPath = getOpenListConnectionGroupedPath(normalized);
      const connectionPayload = {
        url: String(document.getElementById("openlist_url")?.value || ""),
        token: String(document.getElementById("openlist_token")?.value || ""),
        username: String(document.getElementById("openlist_username")?.value || "admin"),
        password: String(document.getElementById("openlist_password")?.value || ""),
      };
      if (normalized !== "external_remote" && !connectionPayload.url) {
        connectionPayload.url = "http://127.0.0.1:5244";
      }
      setGroupedConfigValue(connectionPath, connectionPayload);
      setGroupedConfigValue(["openlist", "managed_runtime"], {
        bin: String(document.getElementById("managed_openlist_bin")?.value || ""),
        data_dir: String(document.getElementById("managed_openlist_data_dir")?.value || ".runtime/openlist"),
        port: normalizeFormValue("managed_openlist_port", document.getElementById("managed_openlist_port")?.value || 5244),
      });
      setGroupedConfigValue(["openlist", "managed_docker"], {
        enabled: normalized === "managed_docker",
        image: String(document.getElementById("managed_openlist_docker_image")?.value || "openlistteam/openlist:latest"),
        container_name: String(document.getElementById("managed_openlist_docker_container_name")?.value || "cloudpan-bridge-openlist"),
      });
      setGroupedConfigValue(["openlist", "managed_init_admin"], {
        username: String(document.getElementById("managed_openlist_init_username")?.value || "admin"),
        password: String(document.getElementById("managed_openlist_init_password")?.value || ""),
      });
    }

    function applyOpenListModeUi() {
      const mode = normalizeOpenListMode(document.getElementById("openlist_mode")?.value || "external_local");
      const runtimeManaged = isManagedOpenListMode(mode);
      const urlLabel = document.querySelector('label[data-help-key="openlist_url"]');
      if (urlLabel) {
        urlLabel.textContent = runtimeManaged
          ? (currentLang() === "en" ? "Current OpenList URL" : currentLang() === "mix" ? "当前 OpenList 地址 / Current OpenList URL" : "当前 OpenList 地址")
          : (currentLang() === "en" ? "OpenList URL" : currentLang() === "mix" ? "OpenList 地址 / OpenList URL" : "OpenList 地址");
      }
      document.querySelectorAll("[data-managed-only]").forEach((el) => {
        el.classList.toggle("hidden", !runtimeManaged);
      });
      document.querySelectorAll("[data-managed-binary-only]").forEach((el) => {
        el.classList.toggle("hidden", mode !== "managed_binary");
      });
      document.querySelectorAll("[data-managed-docker-only]").forEach((el) => {
        el.classList.toggle("hidden", mode !== "managed_docker");
      });
      document.querySelectorAll("[data-external-only]").forEach((el) => {
        el.classList.toggle("hidden", runtimeManaged);
      });
      const installBtn = document.getElementById("install-runtime");
      if (installBtn) installBtn.classList.toggle("hidden", mode !== "managed_binary");
      const runtimeBtn = document.getElementById("start-runtime");
      if (runtimeBtn) runtimeBtn.classList.toggle("hidden", false);
    }

    function getConfigFieldValue(config, field) {
      const path = CONFIG_GROUPED_PATHS[field];
      const fallback = CONFIG_FIELD_DEFAULTS[field] ?? "";
      if (path && hasGroupedConfigValue(path)) {
        const groupedValue = getGroupedConfigValue(path, fallback);
        if (groupedValue !== undefined && groupedValue !== null && groupedValue !== "") return groupedValue;
      }
      const directValue = config?.[field];
      if (directValue !== undefined && directValue !== null && directValue !== "") return directValue;
      return fallback;
    }

    function readLegacyJsonCache(primaryKey, legacyKeys = [], fallback = {}) {
      try {
        return JSON.parse(getStorageValue(primaryKey, legacyKeys) || JSON.stringify(fallback));
      } catch {
        return { ...(fallback || {}) };
      }
    }

    function syncUiPreferenceCache() {
      const groupedLanguage = getGroupedConfigValue(["ui", "language"], "");
      if (typeof groupedLanguage === "string" && groupedLanguage) {
        localStorage.setItem(UI_LANGUAGE_KEY, groupedLanguage);
      }
      const groupedCoverageFilters = getGroupedConfigValue(["ui", "coverage_filters"], null);
      if (groupedCoverageFilters && typeof groupedCoverageFilters === "object") {
        localStorage.setItem(COVERAGE_FILTERS_KEY, JSON.stringify(groupedCoverageFilters));
      }
      const groupedPanelState = getGroupedConfigValue(["ui", "panel_open_states"], null);
      if (groupedPanelState && typeof groupedPanelState === "object") {
        localStorage.setItem(PANEL_STATE_KEY, JSON.stringify(groupedPanelState));
      }
    }

    const currentLang = () => {
      const groupedLanguage = typeof getGroupedConfigValue(["ui", "language"], "") === "string"
        ? getGroupedConfigValue(["ui", "language"], "")
        : "";
      return groupedLanguage || getStorageValue(UI_LANGUAGE_KEY, LEGACY_UI_LANGUAGE_KEYS) || "zh";
    };

    function getCoverageFilterState() {
      const groupedFilters = hasGroupedConfigValue(["ui", "coverage_filters"])
        ? getGroupedConfigValue(["ui", "coverage_filters"], null)
        : null;
      if (groupedFilters && typeof groupedFilters === "object") return { ...groupedFilters };
      return readLegacyJsonCache(COVERAGE_FILTERS_KEY, [], {});
    }

    function setCoverageFilterState(nextState) {
      localStorage.setItem(COVERAGE_FILTERS_KEY, JSON.stringify(nextState));
      setGroupedConfigValue(["ui", "coverage_filters"], { ...(nextState || {}) });
      scheduleUiPrefsPersist();
    }

    function scheduleUiPrefsPersist() {
      if (uiPrefsPersistTimer) clearTimeout(uiPrefsPersistTimer);
      uiPrefsPersistTimer = setTimeout(async () => {
        try {
          await call("/api/config", {
            method: "POST",
            body: JSON.stringify({
              grouped_config: {
                ui: {
                  language: currentLang(),
                  coverage_filters: getCoverageFilterState(),
                  browser: {
                    current_path: String(currentDirectoryPath || "/"),
                    current_parent_path: currentParentPath ? String(currentParentPath) : "",
                    mounted_source: String(document.getElementById("mounted_source_select")?.value || ""),
                  },
                },
              },
            }),
          });
        } catch (_error) {
        }
      }, 180);
    }

    function currentCoverageFilters() {
      return {
        onlyGaps: Boolean(document.getElementById("coverage-only-gaps")?.checked),
        onlyOnboardingReady: Boolean(document.getElementById("coverage-only-onboarding-ready")?.checked),
        nextAction: String(document.getElementById("coverage-next-action-filter")?.value || ""),
        missingItem: String(document.getElementById("coverage-missing-item-filter")?.value || ""),
        capabilityLevel: String(document.getElementById("coverage-capability-level-filter")?.value || ""),
        profileKey: String(document.getElementById("coverage-profile-key-filter")?.value || ""),
        onboardingStage: String(document.getElementById("coverage-onboarding-stage-filter")?.value || ""),
      };
    }

    function applySavedCoverageFilters() {
      const state = getCoverageFilterState();
      const onlyGaps = document.getElementById("coverage-only-gaps");
      const onlyOnboardingReady = document.getElementById("coverage-only-onboarding-ready");
      const nextAction = document.getElementById("coverage-next-action-filter");
      const missingItem = document.getElementById("coverage-missing-item-filter");
      const capabilityLevel = document.getElementById("coverage-capability-level-filter");
      const profileKey = document.getElementById("coverage-profile-key-filter");
      const onboardingStage = document.getElementById("coverage-onboarding-stage-filter");
      if (onlyGaps) onlyGaps.checked = Boolean(state.onlyGaps);
      if (onlyOnboardingReady) onlyOnboardingReady.checked = Boolean(state.onlyOnboardingReady);
      if (nextAction && typeof state.nextAction === "string") nextAction.value = state.nextAction;
      if (missingItem && typeof state.missingItem === "string") missingItem.value = state.missingItem;
      if (capabilityLevel && typeof state.capabilityLevel === "string") capabilityLevel.value = state.capabilityLevel;
      if (profileKey && typeof state.profileKey === "string") profileKey.value = state.profileKey;
      if (onboardingStage && typeof state.onboardingStage === "string") onboardingStage.value = state.onboardingStage;
    }

    function uniqueSorted(values) {
      return [...new Set((values || []).map((item) => String(item || "").trim()).filter(Boolean))].sort((a, b) => a.localeCompare(b, "zh-CN"));
    }

    function buildSelectOptions(selectId, emptyLabel, options, currentValue = "") {
      const select = document.getElementById(selectId);
      if (!select) return;
      const normalizedOptions = Array.isArray(options) ? options : [];
      select.innerHTML = [
        `<option value="">${escapeHtml(emptyLabel)}</option>`,
        ...normalizedOptions.map((item) => `<option value="${escapeHtml(item.value)}" ${item.disabled ? "disabled" : ""}>${escapeHtml(item.label)}</option>`),
      ].join("");
      const fallbackValue = String(currentValue || "");
      if (fallbackValue && normalizedOptions.some((item) => String(item.value) === fallbackValue)) {
        select.value = fallbackValue;
      } else if (fallbackValue === "") {
        select.value = "";
      }
    }

    function renderTargetSpecificControls() {
      const target = activeTargetKey();
      const isGuangya = target === "guangya";
      const miaochuanTabLabel = document.getElementById("tab-miaochuan-label");
      const miaochuanPanelTitle = document.getElementById("miaochuan-panel-title");
      const captureCardTitle = document.getElementById("capture-card-title");
      const targetAuthPanelTitle = document.getElementById("target-auth-panel-title");
      const targetPathLabel = document.getElementById("target-path-label");
      const capabilityDesc = document.getElementById("capability-desc");
      const targetProfilesDesc = document.getElementById("target-profiles-desc");
      const driverMatrixDesc = document.getElementById("driver-matrix-desc");
      const miaochuanDesc = document.getElementById("miaochuan-desc");
      const diagnoseMiaochuanButton = document.getElementById("diagnose-miaochuan");
      const runMiaochuanButton = document.getElementById("run-miaochuan");
      if (miaochuanTabLabel) {
        miaochuanTabLabel.textContent = isGuangya
          ? t("tab.miaochuan")
          : (currentLang() === "en"
            ? "Flash Ref"
            : currentLang() === "mix"
              ? "秒传参考 / Flash Ref"
              : "秒传参考");
      }
      if (miaochuanPanelTitle) {
        miaochuanPanelTitle.textContent = isGuangya
          ? t("panel.miaochuan")
          : (currentLang() === "en"
            ? "Flash Upload Reference"
            : currentLang() === "mix"
              ? "秒传参考与诊断 / Flash Upload Reference"
              : "秒传参考与诊断");
      }
      if (captureCardTitle) {
        captureCardTitle.textContent = isGuangya
          ? t("card.capture")
          : (currentLang() === "en"
            ? "Target State"
            : currentLang() === "mix"
              ? "目标端状态 / Target State"
              : "目标端状态");
      }
      if (targetAuthPanelTitle) {
        targetAuthPanelTitle.textContent = isGuangya
          ? t("panel.guangya_auth")
          : (currentLang() === "en"
            ? "Target Auth State"
            : currentLang() === "mix"
              ? "目标端鉴权状态 / Target Auth State"
              : "目标端鉴权状态");
      }
      if (targetPathLabel) {
        targetPathLabel.textContent = isGuangya
          ? t("label.target_path")
          : (currentLang() === "en"
            ? "Target Directory"
            : currentLang() === "mix"
              ? "目标端目录 / Target Directory"
              : "目标端目录");
      }
      if (capabilityDesc) {
        capabilityDesc.textContent = isGuangya
          ? t("desc.capability")
          : (currentLang() === "en"
            ? `Show the honest recommendation for the current source driver to ${target}, including whether the current combination is still only profile-level or not writable yet.`
            : currentLang() === "mix"
              ? `这里会根据当前源驱动和目标端 ${target} 给出诚实建议，包括当前组合是否仍只有档案层、还没接通写入。 / Honest recommendation for target ${target}.`
              : `这里会根据当前源驱动和目标端 ${target} 给出诚实建议，包括当前组合是否仍只有档案层、还没接通写入。`);
      }
      if (targetProfilesDesc) {
        targetProfilesDesc.textContent = isGuangya
          ? t("desc.target_profiles")
          : (currentLang() === "en"
            ? `This lists the current target adapter profile for ${target}. At this stage, it may still be profile-only and not a writable adapter.`
            : currentLang() === "mix"
              ? `这里列出当前目标端 ${target} 的档案与降级信息；现阶段它可能仍只是档案层，还不是可写入适配器。 / Profile-level target info for ${target}.`
              : `这里列出当前目标端 ${target} 的档案与降级信息；现阶段它可能仍只是档案层，还不是可写入适配器。`);
      }
      if (driverMatrixDesc) {
        driverMatrixDesc.textContent = isGuangya
          ? t("desc.driver_matrix")
          : (currentLang() === "en"
            ? `This is the current built-in source-driver to ${target} matrix. It reflects this project's real support judgment, not a promise that the combination is already writable.`
            : currentLang() === "mix"
              ? `这是当前内置的“源驱动 -> ${target}”能力矩阵，只表示当前项目的真实支持判断，不等于该组合已经接通可写入。 / Built-in matrix for ${target}.`
              : `这是当前内置的“源驱动 -> ${target}”能力矩阵，只表示当前项目的真实支持判断，不等于该组合已经接通可写入。`);
      }
      if (miaochuanDesc) {
        miaochuanDesc.textContent = isGuangya
          ? t("desc.miaochuan")
          : (currentLang() === "en"
            ? "Flash-upload JSON direct import is currently Guangya-only. For other targets, keep this panel as a reference/diagnosis area and do not treat it as a writable import path."
            : currentLang() === "mix"
              ? "秒传 JSON 直导当前仅适用于 Guangya。切到其他目标端时，这里只保留参考/诊断意义，不应视为可直接写入。 / Flash-upload JSON direct import is Guangya-only for now."
              : "秒传 JSON 直导当前仅适用于 Guangya。切到其他目标端时，这里只保留参考/诊断意义，不应视为可直接写入。");
      }
      if (diagnoseMiaochuanButton) {
        diagnoseMiaochuanButton.textContent = isGuangya
          ? t("btn.diagnose_miaochuan")
          : (currentLang() === "en"
            ? "Diagnose Flash JSON"
            : currentLang() === "mix"
              ? "诊断秒传 JSON / Diagnose Flash JSON"
              : "诊断秒传 JSON");
      }
      if (runMiaochuanButton) {
        runMiaochuanButton.textContent = isGuangya
          ? t("btn.run_miaochuan")
          : (currentLang() === "en"
            ? "Guangya Only"
            : currentLang() === "mix"
              ? "仅 Guangya 可导入 / Guangya Only"
              : "仅 Guangya 可导入");
        runMiaochuanButton.disabled = !isGuangya;
        runMiaochuanButton.title = isGuangya
          ? ""
          : (currentLang() === "en"
            ? "Current flash-upload JSON direct import only supports Guangya."
            : currentLang() === "mix"
              ? "当前秒传 JSON 直导仅支持 Guangya。 / Guangya only."
              : "当前秒传 JSON 直导仅支持 Guangya。");
      }
      document.querySelectorAll("[data-target-only]").forEach((el) => {
        const expected = String(el.getAttribute("data-target-only") || "");
        el.style.display = expected === target ? "" : "none";
      });
      const guide = document.getElementById("target-auth-guide");
      if (guide) {
        guide.textContent = isGuangya
          ? (currentLang() === "en"
            ? "Guangya is the only built-in writable target right now. Keep Authorization, Access Token, Refresh Token, and Device ID complete before large sync jobs."
            : currentLang() === "mix"
              ? "当前只有 Guangya 已正式接通写入。大目录运行前，请先保证 Authorization、Access Token、Refresh Token、Device ID 完整。 / Guangya is the only built-in writable target for now."
              : "当前只有 Guangya 已正式接通写入。大目录运行前，请先保证 Authorization、Access Token、Refresh Token、Device ID 完整。")
          : (currentLang() === "en"
            ? `Target ${target} is not connected as a writable adapter yet. The panel keeps only the target selector and preflight notice to avoid overpromising support.`
            : currentLang() === "mix"
              ? `目标端 ${target} 目前还没有接通可写入适配器，因此这里只保留目标端选择和预检提示，避免误导成已可用。 / Target ${target} is not writable yet.`
              : `目标端 ${target} 目前还没有接通可写入适配器，因此这里只保留目标端选择和预检提示，避免误导成已可用。`);
      }
    }

    function populateTargetOptions() {
      const targetProfiles = providerRegistryPayload?.target_profiles || {};
      const implementationStatus = providerRegistryPayload?.target_implementation_status || {};
      const currentValue = String(
        document.getElementById("target_key")?.value
        || getConfigFieldValue(configCache, "target_key")
        || providerRegistryPayload?.active_target
        || "guangya"
      );
      const options = Object.values(targetProfiles).map((item) => {
        const key = String(item.key || "");
        const selectable = Boolean(implementationStatus?.[key]?.selectable);
        const isCurrent = key === currentValue;
        const baseLabel = currentLang() === "en"
          ? `${item.label || key || "-"}`
          : currentLang() === "mix"
            ? `${item.labelZh || item.label || key || "-"} / ${item.label || key || "-"}`
            : `${item.labelZh || item.label || key || "-"}`;
        const suffix = selectable
          ? ""
          : (currentLang() === "en"
            ? " [profile only]"
            : currentLang() === "mix"
              ? " [仅档案 / profile only]"
              : " [仅档案]");
        return {
          value: key,
          label: `${baseLabel}${suffix}`,
          disabled: !selectable && !isCurrent,
        };
      }).filter((item) => item.value);
      buildSelectOptions("target_key", currentLang() === "en" ? "Select target" : currentLang() === "mix" ? "选择目标端 / Select target" : "选择目标端", options, currentValue);
    }

    function populateCoverageFilterOptions() {
      const sourceProfiles = providerRegistryPayload?.source_profiles || {};
      const auditRows = Array.isArray(coverageAuditCache?.rows) ? coverageAuditCache.rows : [];
      const backlog = Array.isArray(coverageAuditCache?.backlog) ? coverageAuditCache.backlog : [];
      const profileKeys = uniqueSorted([
        ...Object.keys(sourceProfiles || {}),
        ...auditRows.map((item) => item.profileKey),
        ...backlog.map((item) => item.profileKey),
      ]);
      const nextActions = uniqueSorted([
        ...auditRows.map((item) => item.nextAction),
        ...backlog.map((item) => item.nextAction),
      ]);
      const capabilityLevels = uniqueSorted([
        ...auditRows.map((item) => item.capabilityLevel),
        ...backlog.map((item) => item.capabilityLevel),
      ]);
      const onboardingStages = uniqueSorted([
        ...auditRows.map((item) => item.onboardingStage),
        ...backlog.map((item) => item.onboardingStage),
      ]);
      buildSelectOptions(
        "coverage-profile-key-filter",
        currentLang() === "en" ? "All profile keys" : currentLang() === "mix" ? "全部 profile key / All profile keys" : "全部 profile key",
        profileKeys.map((item) => ({ value: item, label: item })),
        String(document.getElementById("coverage-profile-key-filter")?.value || getCoverageFilterState().profileKey || "")
      );
      buildSelectOptions(
        "coverage-next-action-filter",
        currentLang() === "en" ? "All next steps" : currentLang() === "mix" ? "全部下一步 / All next steps" : "全部下一步",
        nextActions.map((item) => ({ value: item, label: coverageNextActionText(item) })),
        String(document.getElementById("coverage-next-action-filter")?.value || getCoverageFilterState().nextAction || "")
      );
      buildSelectOptions(
        "coverage-capability-level-filter",
        currentLang() === "en" ? "All capability levels" : currentLang() === "mix" ? "全部能力等级 / All capability levels" : "全部能力等级",
        capabilityLevels.map((item) => ({ value: item, label: item })),
        String(document.getElementById("coverage-capability-level-filter")?.value || getCoverageFilterState().capabilityLevel || "")
      );
      buildSelectOptions(
        "coverage-onboarding-stage-filter",
        currentLang() === "en" ? "All onboarding stages" : currentLang() === "mix" ? "全部接入阶段 / All onboarding stages" : "全部接入阶段",
        onboardingStages.map((item) => ({ value: item, label: item })),
        String(document.getElementById("coverage-onboarding-stage-filter")?.value || getCoverageFilterState().onboardingStage || "")
      );
      applySavedCoverageFilters();
    }
    const PROVIDER_DRIVER_HINTS = {
      "189cloud": ["189Cloud", "189CloudPC", "189CloudTV"],
      "quark": ["Quark", "QuarkOpen", "QuarkTV"],
      "123pan": ["123Pan"],
      "baidu": ["BaiduNetdisk", "BaiduPhoto"],
      "thunder": ["Thunder", "ThunderX", "ThunderExpert"],
      "guangya": ["guangya"],
    };


  return {
    I18N,
    HELP_TEXT,
    DRIVER_FIELD_I18N,
    DRIVER_HELP_PATTERNS,
    DRIVER_OPTIONS_I18N,
    PROVIDER_DRIVER_HINTS,
  };
})();

