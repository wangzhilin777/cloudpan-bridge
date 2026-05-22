    const CONFIG_FIELDS = [
      "source_path", "target_path", "openlist_mode", "managed_openlist_bin", "managed_openlist_data_dir",
      "managed_openlist_port", "managed_openlist_docker_image", "managed_openlist_docker_container_name",
      "openlist_url", "openlist_token", "openlist_username", "openlist_password",
      "managed_openlist_init_username", "managed_openlist_init_password",
      "target_key", "source_provider_preference", "guangya_phone", "guangya_authorization", "guangya_access_token", "guangya_refresh_token",
      "guangya_device_id", "local_target_root", "webdav_target_url", "webdav_target_username", "webdav_target_password", "s3_target_endpoint", "s3_target_bucket", "s3_target_prefix", "s3_target_access_key", "s3_target_secret_key", "s3_target_region", "seafile_target_url", "seafile_target_token", "seafile_target_username", "seafile_target_password", "seafile_target_repo_id", "seafile_target_repo_name", "azureblob_target_account_url", "azureblob_target_container", "azureblob_target_prefix", "azureblob_target_account_name", "azureblob_target_account_key", "smb_target_url", "smb_target_username", "smb_target_password", "ftp_target_url", "ftp_target_username", "ftp_target_password", "sftp_target_url", "sftp_target_username", "sftp_target_password", "delete_removed", "target_delete_removed", "openlist_page_size", "openlist_request_interval_ms", "queue_interval_ms",
      "auto_download_threshold_mb", "rate_limit_mode", "log_file", "temp_dir", "state_file",
      "app_admin_username", "app_admin_password"
    ];
    const CONFIG_GROUPED_PATHS = {
      source_path: ["sync", "source_path"],
      target_path: ["sync", "target_path"],
      openlist_mode: ["openlist", "mode"],
      managed_openlist_bin: ["openlist", "managed_runtime", "bin"],
      managed_openlist_data_dir: ["openlist", "managed_runtime", "data_dir"],
      managed_openlist_port: ["openlist", "managed_runtime", "port"],
      managed_openlist_docker_image: ["openlist", "managed_docker", "image"],
      managed_openlist_docker_container_name: ["openlist", "managed_docker", "container_name"],
      openlist_url: ["openlist", "url"],
      openlist_token: ["openlist", "token"],
      openlist_username: ["openlist", "username"],
      openlist_password: ["openlist", "password"],
      managed_openlist_init_username: ["openlist", "managed_init_admin", "username"],
      managed_openlist_init_password: ["openlist", "managed_init_admin", "password"],
      target_key: ["targets", "active_target"],
      source_provider_preference: ["source_session", "provider_preference"],
      guangya_phone: ["targets", "guangya", "phone"],
      guangya_authorization: ["targets", "guangya", "authorization"],
      guangya_access_token: ["targets", "guangya", "access_token"],
      guangya_refresh_token: ["targets", "guangya", "refresh_token"],
      guangya_device_id: ["targets", "guangya", "device_id"],
      local_target_root: ["targets", "localfs", "root"],
      webdav_target_url: ["targets", "webdav", "url"],
      webdav_target_username: ["targets", "webdav", "username"],
      webdav_target_password: ["targets", "webdav", "password"],
      s3_target_endpoint: ["targets", "s3", "endpoint"],
      s3_target_bucket: ["targets", "s3", "bucket"],
      s3_target_prefix: ["targets", "s3", "prefix"],
      s3_target_access_key: ["targets", "s3", "access_key"],
      s3_target_secret_key: ["targets", "s3", "secret_key"],
      s3_target_region: ["targets", "s3", "region"],
      seafile_target_url: ["targets", "seafile", "url"],
      seafile_target_token: ["targets", "seafile", "token"],
      seafile_target_username: ["targets", "seafile", "username"],
      seafile_target_password: ["targets", "seafile", "password"],
      seafile_target_repo_id: ["targets", "seafile", "repo_id"],
      seafile_target_repo_name: ["targets", "seafile", "repo_name"],
      azureblob_target_account_url: ["targets", "azureblob", "account_url"],
      azureblob_target_container: ["targets", "azureblob", "container"],
      azureblob_target_prefix: ["targets", "azureblob", "prefix"],
      azureblob_target_account_name: ["targets", "azureblob", "account_name"],
      azureblob_target_account_key: ["targets", "azureblob", "account_key"],
      smb_target_url: ["targets", "smb", "url"],
      smb_target_username: ["targets", "smb", "username"],
      smb_target_password: ["targets", "smb", "password"],
      ftp_target_url: ["targets", "ftp", "url"],
      ftp_target_username: ["targets", "ftp", "username"],
      ftp_target_password: ["targets", "ftp", "password"],
      sftp_target_url: ["targets", "sftp", "url"],
      sftp_target_username: ["targets", "sftp", "username"],
      sftp_target_password: ["targets", "sftp", "password"],
      delete_removed: ["sync", "delete_removed"],
      target_delete_removed: ["sync", "target_delete_removed"],
      openlist_page_size: ["sync", "openlist_page_size"],
      openlist_request_interval_ms: ["sync", "openlist_request_interval_ms"],
      queue_interval_ms: ["sync", "queue_interval_ms"],
      auto_download_threshold_mb: ["sync", "auto_download_threshold_mb"],
      rate_limit_mode: ["sync", "rate_limit_mode"],
      temp_dir: ["state", "temp_dir"],
      state_file: ["state", "state_file"],
      log_file: ["state", "log_file"],
      app_admin_username: ["app", "admin_username"],
      app_admin_password: ["app", "admin_password"],
    };
    const CONFIG_FIELD_DEFAULTS = {
      openlist_mode: "external_local",
      managed_openlist_port: 5244,
      managed_openlist_docker_image: "openlistteam/openlist:latest",
      managed_openlist_docker_container_name: "cloudpan-bridge-openlist",
      managed_openlist_init_username: "admin",
      target_key: "guangya",
      source_provider_preference: "auto",
      delete_removed: false,
      target_delete_removed: false,
      rate_limit_mode: "safe",
    };
    const PANEL_STATE_KEY = "cloudpan-bridge-panel-state";
    const LEGACY_PANEL_STATE_KEYS = ["cloud2guangya-tabs"];
    const UI_LANGUAGE_KEY = "cloudpan-bridge-ui-language";
    const LEGACY_UI_LANGUAGE_KEYS = ["cloud2guangya-ui-language"];
    const AUTO_GUANGYA_CAPTURE_KEY = "cloudpan-bridge-auto-guangya-capture";
    const LEGACY_AUTO_GUANGYA_CAPTURE_KEYS = ["cloud2guangya-auto-guangya-capture"];
    const COVERAGE_FILTERS_KEY = "cloudpan-bridge-coverage-filters";
    const RATE_PRESETS = {
      default: { openlist_page_size: 100, openlist_request_interval_ms: 800, queue_interval_ms: 3000 },
      safe: { openlist_page_size: 80, openlist_request_interval_ms: 1200, queue_interval_ms: 5000 },
      balanced: { openlist_page_size: 120, openlist_request_interval_ms: 700, queue_interval_ms: 2500 },
      fast: { openlist_page_size: 200, openlist_request_interval_ms: 300, queue_interval_ms: 1000 },
      "189cloud": { openlist_page_size: 60, openlist_request_interval_ms: 1200, queue_interval_ms: 5000 },
      "quark": { openlist_page_size: 80, openlist_request_interval_ms: 1000, queue_interval_ms: 3500 },
      "123pan": { openlist_page_size: 100, openlist_request_interval_ms: 900, queue_interval_ms: 3000 },
      "baidu": { openlist_page_size: 50, openlist_request_interval_ms: 1500, queue_interval_ms: 6000 },
      "thunder": { openlist_page_size: 80, openlist_request_interval_ms: 1000, queue_interval_ms: 3500 },
      "aliyun": { openlist_page_size: 120, openlist_request_interval_ms: 700, queue_interval_ms: 2500 }
    };
    const { I18N, HELP_TEXT, DRIVER_FIELD_I18N, DRIVER_HELP_PATTERNS, DRIVER_OPTIONS_I18N, PROVIDER_DRIVER_HINTS } = window.CloudPanBridgeData || {};
    const workflowView = window.CloudPanBridgeWorkflow || {};
    const capabilityView = window.CloudPanBridgeCapabilityView || {};
    const driverCaptureView = window.CloudPanBridgeDriverCapture || {};
    const sourceOpsView = window.CloudPanBridgeSourceOps || {};
    const pendingView = window.CloudPanBridgePendingUi || {};
    const registryView = window.CloudPanBridgeRegistryView || {};
    const statusView = window.CloudPanBridgeStatusView || {};
    const runtimeView = window.CloudPanBridgeRuntimeView || {};
    const FALLBACK_PROVIDER_DEFINITIONS = [
      { key: "aliyundriveopen", label: "AliyunDrive Open", label_zh: "阿里云盘 Open", login_url: "https://www.alipan.com/", recommended_drivers: ["AliyundriveOpen"], source_profile: { label: "AliyunDrive Open", label_zh: "阿里云盘 Open" } },
      { key: "123pan", label: "123Pan", label_zh: "123 云盘", login_url: "https://www.123pan.com/", recommended_drivers: ["123Open"], source_profile: { label: "123Pan", label_zh: "123 云盘" } },
      { key: "139yun", label: "139Yun", label_zh: "139 云盘", login_url: "https://yun.139.com/", recommended_drivers: ["139Yun"], source_profile: { label: "139Yun", label_zh: "139 云盘" } },
      { key: "quark", label: "Quark", label_zh: "夸克网盘", login_url: "https://pan.quark.cn/", recommended_drivers: ["Quark"], source_profile: { label: "Quark", label_zh: "夸克网盘" } },
      { key: "thunder", label: "Thunder", label_zh: "迅雷云盘", login_url: "https://pan.xunlei.com/", recommended_drivers: ["Thunder"], source_profile: { label: "Thunder", label_zh: "迅雷云盘" } },
      { key: "baidu", label: "Baidu", label_zh: "百度网盘", login_url: "https://pan.baidu.com/", recommended_drivers: ["Baidu"], source_profile: { label: "Baidu", label_zh: "百度网盘" } },
      { key: "onedrive", label: "OneDrive", label_zh: "OneDrive", login_url: "https://onedrive.live.com/", recommended_drivers: ["OneDrive"], source_profile: { label: "OneDrive", label_zh: "OneDrive" } },
      { key: "pikpak", label: "PikPak", label_zh: "PikPak", login_url: "https://mypikpak.com/", recommended_drivers: ["PikPak"], source_profile: { label: "PikPak", label_zh: "PikPak" } },
      { key: "189cloud", label: "189Cloud", label_zh: "天翼云盘", login_url: "https://cloud.189.cn/", recommended_drivers: ["189Cloud"], source_profile: { label: "189Cloud", label_zh: "天翼云盘" } },
    ];
    let configCache = {};
    let providerRegistryPayload = null;
    let driverGuideRegistry = {};
    let capabilityAssessmentCache = null;
    let coverageAuditCache = null;
    let targetPreflightCache = null;
    let targetPreflightByKey = new Map();
    let driverCaptureBlueprint = null;
    let providerDefinitions = [...FALLBACK_PROVIDER_DEFINITIONS];
    let providerSnapshots = {};
    let storageRecords = [];
    let sourceAnalyzeCache = null;
    let latestPendingItems = [];
    let pendingSelection = new Set();
    let pendingSelectionTouched = false;
    let pendingExpanded = new Set(["/"]);
    let pendingDirectoryFiles = new Map();
    let currentDirectoryPath = "/";
    let currentParentPath = null;
    let currentDriverGuide = null;
    let currentProviderGuide = null;
    let driversCache = [];
    let currentDriverInfo = null;
    const POPULAR_PROVIDER_KEYS = ["aliyundriveopen", "123pan", "139yun", "quark", "thunder", "baidu", "onedrive", "pikpak", "189cloud"];
    const POPULAR_TARGET_KEYS = ["guangya", "openlist", "localfs", "webdav", "s3", "seafile", "azureblob", "smb", "ftp", "sftp"];
    let mirrorInputsInitialized = false;
    let targetChangeSeq = 0;

    function workflowContext() {
      return {
        currentDriverContext,
        normalizeDriverKey,
        providerRegistryPayload,
        capabilityAssessmentCache,
        sourceAnalyzeCache,
        currentLang,
        strategyQuickActions,
        escapeHtml,
        capabilityLevelText,
        strategyModeText,
        formatBytes,
        setSourceAnalyzeCache: (value) => {
          sourceAnalyzeCache = value;
        },
        currentDirectoryPath,
        configCache,
        getGroupedConfigValue,
        activeTargetKey,
        translateDriverText,
        renderOverviewRouteSummary,
        applyWorkflowGates,
      };
    }

    function driverCaptureContext() {
      return {
        currentLang,
        normalizeDriverKey,
        escapeHtml,
        guideTextPair,
        t,
        call,
        setNotice,
        renderCapabilitySummary,
        RATE_PRESETS,
        PROVIDER_DRIVER_HINTS,
        getProviderDefinitions: () => providerDefinitions,
        getProviderSnapshots: () => providerSnapshots,
        getDriverCaptureBlueprint: () => driverCaptureBlueprint,
        getDriverGuideRegistry: () => driverGuideRegistry,
        getStorageRecords: () => storageRecords,
        getCurrentDriverGuide: () => currentDriverGuide,
        setCurrentDriverGuide: (value) => {
          currentDriverGuide = value;
        },
        getCurrentProviderGuide: () => currentProviderGuide,
        setCurrentProviderGuide: (value) => {
          currentProviderGuide = value;
        },
      };
    }

    function pendingUiContext() {
      return {
        currentLang,
        escapeHtml,
        formatBytes,
        setLatestPendingItems: (items) => {
          latestPendingItems = items;
        },
        getPendingState: () => ({
          selection: new Set(pendingSelection),
          selectionTouched: pendingSelectionTouched,
          expanded: new Set(pendingExpanded),
          directoryFiles: new Map(pendingDirectoryFiles),
        }),
        setPendingState: (state) => {
          pendingSelection = new Set(state.selection || []);
          pendingSelectionTouched = !!state.selectionTouched;
          pendingExpanded = new Set(state.expanded || ["/"]);
          pendingDirectoryFiles = new Map(state.directoryFiles || []);
        },
      };
    }

    function registryViewContext() {
      return {
        currentLang,
        escapeHtml,
        capabilityLevelText,
        coverageNextActionText,
        currentCoverageFilters,
        getProviderRegistryPayload: () => providerRegistryPayload,
        getCoverageAuditCache: () => coverageAuditCache,
      };
    }

    function statusViewContext() {
      return {
        escapeHtml,
        getConfigCache: () => configCache,
        getCurrentDirectoryPath: () => currentDirectoryPath,
        normalizeOpenListMode,
        getOpenListModeLabel,
      };
    }

    function runtimeViewContext() {
      return {
        currentLang,
        escapeHtml,
        getOpenListModeLabel,
        applyOpenListModeUi,
      };
    }

    function sourceOpsContext() {
      return {
        currentLang,
        escapeHtml,
        formatBytes,
        call,
        refreshStatus,
        browseDirectory,
        renderSourceDriverSummary,
        renderCapabilitySummary,
        applyWorkflowGates,
        applyProviderSelectionFromDriver,
        renderDriverGuide,
        renderProviderCapturePanel,
        getGroupedConfigValue,
        setGroupedConfigValue,
        scheduleUiPrefsPersist,
        driverFieldLabel,
        driverFieldHelp,
        driverFieldOptions,
        getCurrentDirectoryPath: () => currentDirectoryPath,
        getCurrentParentPath: () => currentParentPath,
        setCurrentDirectory: (path, parentPath) => {
          currentDirectoryPath = path;
          currentParentPath = parentPath;
        },
        setStorageRecords: (items) => {
          storageRecords = items;
        },
        setCurrentDriverInfo: (info) => {
          currentDriverInfo = info;
        },
      };
    }

    const getDriverGuide = (driver) => driverCaptureView.getDriverGuide(driverCaptureContext(), driver);
    const getGuideForProviderDefinition = (definition) => driverCaptureView.getGuideForProviderDefinition(driverCaptureContext(), definition);
    const guideDocCandidates = (guide) => driverCaptureView.guideDocCandidates(driverCaptureContext(), guide);
    const renderGuideIntoDialog = (guide, titleText) => driverCaptureView.renderGuideIntoDialog(driverCaptureContext(), guide, titleText);
    const renderDriverGuide = (driver) => driverCaptureView.renderDriverGuide(driverCaptureContext(), driver);
    const applyDriverGuideDefaults = () => driverCaptureView.applyDriverGuideDefaults(driverCaptureContext());
    const toggleDriverGuideDialog = (visible) => driverCaptureView.toggleDriverGuideDialog(driverCaptureContext(), visible);
    const chooseRatePreset = (driver, mode) => driverCaptureView.chooseRatePreset(driverCaptureContext(), driver, mode);
    const inferProviderFromDriver = (driver) => driverCaptureView.inferProviderFromDriver(driverCaptureContext(), driver);
    const renderProviderOptions = (definitions) => driverCaptureView.renderProviderOptions(driverCaptureContext(), definitions);
    const renderProviderCapturePanel = () => driverCaptureView.renderProviderCapturePanel(driverCaptureContext());
    const applyProviderSelectionFromDriver = (driver) => driverCaptureView.applyProviderSelectionFromDriver(driverCaptureContext(), driver);
    const applyCapturedProviderFields = () => driverCaptureView.applyCapturedProviderFields(driverCaptureContext());
    const applyRatePresetForMount = (mountPath) => driverCaptureView.applyRatePresetForMount(driverCaptureContext(), mountPath);
    const renderPendingTree = (items) => pendingView.renderPendingTree(pendingUiContext(), items);
    const renderAboutRegistry = () => registryView.renderAboutRegistry(registryViewContext());
    const renderLogs = (records) => statusView.renderLogs(statusViewContext(), records);
    const renderOverviewRouteSummary = (syncState = {}, runtimeState = {}) => statusView.renderOverviewRouteSummary(statusViewContext(), syncState, runtimeState);
    const renderSync = (sync) => runtimeView.renderSync(runtimeViewContext(), sync);
    const renderRuntime = (runtime) => runtimeView.renderRuntime(runtimeViewContext(), runtime);
    const renderCapture = (capture, targetStateSummary = null) => runtimeView.renderCapture(runtimeViewContext(), capture, targetStateSummary);
    let authState = { enabled: false, authenticated: true, username: "" };
    let appBootstrapped = false;
    let eventsBound = false;
    let autoRefreshTimer = null;
    let panelStatePersistTimer = null;

    function escapeHtml(text) {
      return String(text ?? "").replace(/[&<>"']/g, (ch) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#39;"
      }[ch]));
    }

    function formatBytes(bytes) {
      const num = Number(bytes || 0);
      if (!num) return "0 B";
      const units = ["B", "KB", "MB", "GB", "TB"];
      let value = num;
      let index = 0;
      while (value >= 1024 && index < units.length - 1) {
        value /= 1024;
        index += 1;
      }
      return `${value.toFixed(value >= 10 || index === 0 ? 0 : 1)} ${units[index]}`;
    }

    async function call(url, options = {}) {
      const response = await fetch(url, {
        headers: { "content-type": "application/json", ...(options.headers || {}) },
        credentials: "same-origin",
        ...options,
      });
      if (!response.ok) {
        let detail = response.statusText;
        try {
          const data = await response.json();
          detail = data.detail || data.message || JSON.stringify(data);
        } catch {}
        if (response.status === 401) {
          updateAuthUi({ ...(authState || {}), authenticated: false });
          showAuthDialog(detail || "控制台登录已失效，请重新登录。");
        }
        throw new Error(detail);
      }
      const contentType = response.headers.get("content-type") || "";
      if (contentType.includes("application/json")) return response.json();
      return response.text();
    }

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
      grouped.ui.browser = grouped.ui.browser || {};
      grouped.openlist = grouped.openlist || {};
      grouped.openlist.managed_runtime = grouped.openlist.managed_runtime || {};
      grouped.openlist.managed_docker = grouped.openlist.managed_docker || {};
      grouped.openlist.managed_init_admin = grouped.openlist.managed_init_admin || {};
      grouped.openlist.connections = grouped.openlist.connections || {};
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
      if (normalized === "managed_binary" || normalized === "managed_docker") return ["openlist", "connections", normalized];
      return ["openlist", "connections", "external_local"];
    }

    const currentLang = () => {
      const groupedLanguage = typeof getGroupedConfigValue(["ui", "language"], "") === "string"
        ? getGroupedConfigValue(["ui", "language"], "")
        : "";
      return groupedLanguage || getStorageValue(UI_LANGUAGE_KEY, LEGACY_UI_LANGUAGE_KEYS) || "zh";
    };

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

    function buildManagedLocalUrl(portValue) {
      const port = Number.parseInt(String(portValue ?? ""), 10);
      const safePort = Number.isFinite(port) && port > 0 ? port : 5244;
      return `http://127.0.0.1:${safePort}`;
    }

    function readOpenListSnapshotFromGrouped(mode) {
      const connectionPath = getOpenListConnectionGroupedPath(mode);
      const connection = getGroupedConfigValue(connectionPath, {}) || {};
      const managedRuntime = getGroupedConfigValue(["openlist", "managed_runtime"], {}) || {};
      const managedInitAdmin = getGroupedConfigValue(["openlist", "managed_init_admin"], {}) || {};
      const managedPort = String(managedRuntime.port || 5244);
      const managedUrl = buildManagedLocalUrl(managedPort);
      return {
        openlist_url: normalizeOpenListMode(mode) === "external_remote"
          ? String(connection.url || "")
          : isManagedOpenListMode(mode)
            ? managedUrl
            : String(connection.url || "http://127.0.0.1:5244"),
        openlist_token: String(connection.token || ""),
        openlist_username: String(connection.username || "admin"),
        openlist_password: String(connection.password || ""),
        managed_openlist_bin: String(managedRuntime.bin || ""),
        managed_openlist_data_dir: String(managedRuntime.data_dir || ".runtime/openlist"),
        managed_openlist_port: managedPort,
        managed_openlist_docker_image: String(getGroupedConfigValue(["openlist", "managed_docker", "image"], "openlistteam/openlist:latest") || "openlistteam/openlist:latest"),
        managed_openlist_docker_container_name: String(getGroupedConfigValue(["openlist", "managed_docker", "container_name"], "cloudpan-bridge-openlist") || "cloudpan-bridge-openlist"),
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
      if (isManagedOpenListMode(normalized)) {
        connectionPayload.url = buildManagedLocalUrl(document.getElementById("managed_openlist_port")?.value || 5244);
      }
      if (normalized !== "external_remote" && !connectionPayload.url) {
        connectionPayload.url = isManagedOpenListMode(normalized)
          ? buildManagedLocalUrl(document.getElementById("managed_openlist_port")?.value || 5244)
          : "http://127.0.0.1:5244";
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
      const modeSummary = document.getElementById("openlist-mode-summary");
      const modeChip = document.getElementById("openlist-mode-chip");
      const urlLabel = document.querySelector('label[data-help-key="openlist_url"]');
      if (urlLabel) {
        urlLabel.textContent = runtimeManaged
          ? (currentLang() === "en" ? "Current OpenList URL" : currentLang() === "mix" ? "当前 OpenList 地址 / Current OpenList URL" : "当前 OpenList 地址")
          : (currentLang() === "en" ? "OpenList URL" : currentLang() === "mix" ? "OpenList 地址 / OpenList URL" : "OpenList 地址");
      }
      document.querySelectorAll("[data-openlist-section]").forEach((el) => {
        const expected = String(el.getAttribute("data-openlist-section") || "");
        el.classList.toggle("hidden", expected !== mode);
        el.classList.toggle("is-active", expected === mode);
      });
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
      document.querySelectorAll("[data-openlist-mode-group]").forEach((el) => {
        const groups = String(el.getAttribute("data-openlist-mode-group") || "")
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean);
        const visible = groups.includes("always") || groups.includes(mode);
        el.classList.toggle("hidden", !visible);
      });
      const installBtn = document.getElementById("install-runtime");
      if (installBtn) installBtn.classList.toggle("hidden", mode !== "managed_binary");
      const modeHelpText = mode === "external_remote"
        ? (currentLang() === "en" ? "Remote OpenList mode. Only fill the remote URL and credentials." : currentLang() === "mix" ? "当前为远程 OpenList 模式，只需要远程地址和凭证。 / Remote OpenList mode." : "当前为远程 OpenList 模式，只需要远程地址和凭证。")
        : mode === "external_local"
          ? (currentLang() === "en" ? "Local external mode. Fill the local instance credentials only." : currentLang() === "mix" ? "当前为本机外部模式，只需要本机实例凭证。 / Local external mode." : "当前为本机外部模式，只需要本机实例凭证。")
          : mode === "managed_docker"
            ? (currentLang() === "en" ? "Managed Docker placeholder mode. Save image and startup parameters here." : currentLang() === "mix" ? "当前为 Docker 托管预留模式，可先保存镜像和启动参数。 / Managed Docker placeholder mode." : "当前为 Docker 托管预留模式，可先保存镜像和启动参数。")
            : (currentLang() === "en" ? "Managed binary mode. Configure the binary path, data dir, and port." : currentLang() === "mix" ? "当前为本机二进制托管模式，请配置可执行文件、数据目录和端口。 / Managed binary mode." : "当前为本机二进制托管模式，请配置可执行文件、数据目录和端口。");
      if (modeSummary) {
        modeSummary.textContent = mode === "external_local"
          ? (currentLang() === "en" ? "Current mode: connect an existing local OpenList instance." : currentLang() === "mix" ? "当前模式：连接本机已有 OpenList 实例。 / Existing local OpenList." : "当前模式：连接本机已有 OpenList 实例。")
          : mode === "external_remote"
            ? (currentLang() === "en" ? "Current mode: connect an existing remote OpenList instance." : currentLang() === "mix" ? "当前模式：连接远程 OpenList 实例。 / Existing remote OpenList." : "当前模式：连接远程 OpenList 实例。")
            : mode === "managed_docker"
              ? (currentLang() === "en" ? "Current mode: managed Docker placeholder mode." : currentLang() === "mix" ? "当前模式：Docker 托管预留模式。 / Managed Docker placeholder mode." : "当前模式：Docker 托管预留模式。")
              : (currentLang() === "en" ? "Current mode: managed local binary runtime." : currentLang() === "mix" ? "当前模式：本机二进制托管模式。 / Managed local binary runtime." : "当前模式：本机二进制托管模式。");
      }
      if (modeChip) {
        const labels = {
          external_local: currentLang() === "en" ? "Active mode: Existing local instance" : currentLang() === "mix" ? "当前模式：本机已有实例 / Existing local instance" : "当前模式：本机已有实例",
          external_remote: currentLang() === "en" ? "Active mode: Existing remote instance" : currentLang() === "mix" ? "当前模式：远程已有实例 / Existing remote instance" : "当前模式：远程已有实例",
          managed_binary: currentLang() === "en" ? "Active mode: Managed local binary" : currentLang() === "mix" ? "当前模式：本机二进制托管 / Managed local binary" : "当前模式：本机二进制托管",
          managed_docker: currentLang() === "en" ? "Active mode: Managed Docker placeholder" : currentLang() === "mix" ? "当前模式：Docker 托管预留 / Managed Docker placeholder" : "当前模式：Docker 托管预留",
        };
        modeChip.textContent = labels[mode] || labels.external_local;
      }
      const runtimeNotice = document.getElementById("runtime-action-notice");
      if (runtimeNotice && !runtimeNotice.textContent.trim()) {
        setNotice("runtime-action-notice", modeHelpText, runtimeManaged ? "warn" : "success");
      }
    }

    function initializeMirroredInputs() {
      if (mirrorInputsInitialized) return;
      mirrorInputsInitialized = true;
      const syncMirrorFromPrimary = (key) => {
        const primary = document.getElementById(key);
        if (!primary) return;
        document.querySelectorAll(`[data-openlist-mirror="${key}"]`).forEach((mirror) => {
          if (mirror.value !== primary.value) mirror.value = primary.value;
        });
      };
      document.querySelectorAll("[data-openlist-mirror]").forEach((mirror) => {
        const key = String(mirror.getAttribute("data-openlist-mirror") || "");
        const primary = document.getElementById(key);
        if (!key || !primary) return;
        if (mirror.value !== primary.value) mirror.value = primary.value;
        mirror.addEventListener("input", () => {
          if (primary.value !== mirror.value) primary.value = mirror.value;
        });
        mirror.addEventListener("change", () => {
          if (primary.value !== mirror.value) primary.value = mirror.value;
        });
      });
      CONFIG_FIELDS.forEach((field) => {
        const primary = document.getElementById(field);
        if (!primary) return;
        primary.addEventListener("input", () => syncMirrorFromPrimary(field));
        primary.addEventListener("change", () => syncMirrorFromPrimary(field));
        syncMirrorFromPrimary(field);
      });
    }

    function syncMirroredInputs() {
      document.querySelectorAll("[data-openlist-mirror]").forEach((mirror) => {
        const key = String(mirror.getAttribute("data-openlist-mirror") || "");
        const primary = document.getElementById(key);
        if (primary && mirror.value !== primary.value) mirror.value = primary.value;
      });
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
      if (panelStatePersistTimer) clearTimeout(panelStatePersistTimer);
      panelStatePersistTimer = setTimeout(async () => {
        if (authState.enabled && !authState.authenticated) return;
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
                  panel_open_states: getPanelState(),
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

    function getPanelState() {
      const groupedState = hasGroupedConfigValue(["ui", "panel_open_states"])
        ? getGroupedConfigValue(["ui", "panel_open_states"], null)
        : null;
      if (groupedState && typeof groupedState === "object") return { ...groupedState };
      return readLegacyJsonCache(PANEL_STATE_KEY, LEGACY_PANEL_STATE_KEYS, {});
    }

    function setPanelState(nextState) {
      localStorage.setItem(PANEL_STATE_KEY, JSON.stringify(nextState));
      setGroupedConfigValue(["ui", "panel_open_states"], { ...(nextState || {}) });
    }

    function schedulePanelStatePersist() {
      if (panelStatePersistTimer) clearTimeout(panelStatePersistTimer);
      panelStatePersistTimer = setTimeout(async () => {
        if (authState.enabled && !authState.authenticated) return;
        try {
          await call("/api/config", {
            method: "POST",
            body: JSON.stringify({
              grouped_config: {
                ui: {
                  panel_open_states: { ...getPanelState() },
                },
              },
            }),
          });
        } catch (_error) {
        }
      }, 180);
    }

    function updatePanelState(patch) {
      const nextState = { ...getPanelState(), ...(patch || {}) };
      setPanelState(nextState);
      configCache = { ...(configCache || {}) };
      schedulePanelStatePersist();
      return nextState;
    }

    function setAuthNotice(message) {
      const notice = document.getElementById("auth-notice");
      if (notice) notice.textContent = message || t("notice.auth_idle");
      const inline = document.getElementById("auth-lock-summary");
      if (inline && message) inline.textContent = message;
    }

    function showAuthDialog(message = "") {
      const dialog = document.getElementById("auth-dialog");
      if (!dialog) return;
      if (message) setAuthNotice(message);
      dialog.classList.remove("hidden");
      document.getElementById("auth-username")?.focus();
    }

    function hideAuthDialog() {
      const dialog = document.getElementById("auth-dialog");
      if (dialog) dialog.classList.add("hidden");
    }

    function stopAutoRefresher() {
      if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
        autoRefreshTimer = null;
      }
    }

    function startAutoRefresher() {
      stopAutoRefresher();
      autoRefreshTimer = setInterval(async () => {
        if (authState.enabled && !authState.authenticated) return;
        try {
          await refreshStatus();
        } catch (_error) {
        }
      }, 5000);
    }

    function computeWorkflowState() {
      const targetKey = activeTargetKey();
      const sourcePath = String(document.getElementById("source_path")?.value || configCache?.source_path || "/").trim() || "/";
      const targetPath = String(document.getElementById("target_path")?.value || configCache?.target_path || "/").trim() || "/";
      const mountedSource = String(document.getElementById("mounted_source_select")?.value || getGroupedConfigValue(["ui", "browser", "mounted_source"], "") || "").trim();
      const openlistUrl = String(document.getElementById("effective_openlist_url")?.value || configCache?.effective_openlist_url || configCache?.openlist_url || "").trim();
      const sourceReady = sourcePath !== "/" && Boolean(sourcePath);
      const connectionReady = Boolean(openlistUrl) || storageRecords.length > 0 || Boolean(mountedSource);
      const targetConfigured = Boolean(targetPreflightCache?.configured);
      const taskReady = connectionReady && sourceReady && targetConfigured && Boolean(targetPath);
      const executionReady = taskReady;
      const guangyaMiaochuanReady = targetKey === "guangya" && targetConfigured;
      let currentStep = "connect";
      if (!connectionReady) currentStep = "connect";
      else if (!sourceReady) currentStep = "source";
      else if (!targetConfigured) currentStep = "target";
      else if (!taskReady) currentStep = "task";
      else currentStep = "execute";
      return {
        connectionReady,
        sourceReady,
        targetConfigured,
        taskReady,
        executionReady,
        guangyaMiaochuanReady,
        currentStep,
        sourcePath,
        targetPath,
        targetKey,
        openlistUrl,
      };
    }

    function renderWorkflowRoadmap() {
      const root = document.getElementById("workflow-roadmap");
      if (!root) return;
      const state = computeWorkflowState();
      const steps = [
        {
          key: "connect",
          title: currentLang() === "en" ? "1. Connect OpenList" : currentLang() === "mix" ? "1. 连接 OpenList / Connect OpenList" : "1. 连接 OpenList",
          ready: state.connectionReady,
          detail: state.connectionReady
            ? (currentLang() === "en" ? `Ready: ${state.openlistUrl || "OpenList reachable"}` : currentLang() === "mix" ? `已就绪 / Ready: ${state.openlistUrl || "OpenList reachable"}` : `已就绪: ${state.openlistUrl || "可访问"}`)
            : (currentLang() === "en" ? "Finish OpenList login or runtime startup first." : currentLang() === "mix" ? "先完成 OpenList 登录或托管启动。 / Finish OpenList login first." : "先完成 OpenList 登录或托管启动。"),
        },
        {
          key: "source",
          title: currentLang() === "en" ? "2. Pick Source" : currentLang() === "mix" ? "2. 选择源目录 / Pick Source" : "2. 选择源目录",
          ready: state.sourceReady,
          detail: state.sourceReady
            ? (currentLang() === "en" ? `Ready: ${state.sourcePath}` : currentLang() === "mix" ? `已选源目录 / Ready: ${state.sourcePath}` : `已选源目录: ${state.sourcePath}`)
            : (currentLang() === "en" ? "Open the source browser and write a concrete source_path." : currentLang() === "mix" ? "去“源端”页选择具体目录并写回 source_path。 / Pick a concrete directory first." : "去“源端”页选择具体目录并写回 source_path。"),
        },
        {
          key: "target",
          title: currentLang() === "en" ? "3. Configure Target" : currentLang() === "mix" ? "3. 配置目标端 / Configure Target" : "3. 配置目标端",
          ready: state.targetConfigured,
          detail: state.targetConfigured
            ? (currentLang() === "en" ? `Ready: ${state.targetKey}` : currentLang() === "mix" ? `已就绪 / Ready: ${state.targetKey}` : `已就绪: ${state.targetKey}`)
            : (currentLang() === "en" ? "Complete target credentials until preflight becomes configured." : currentLang() === "mix" ? "补齐目标端凭证，直到预检显示 configured。 / Finish target credentials first." : "补齐目标端凭证，直到预检显示 configured。"),
        },
        {
          key: "task",
          title: currentLang() === "en" ? "4. Configure Task" : currentLang() === "mix" ? "4. 配置任务 / Configure Task" : "4. 配置任务",
          ready: state.taskReady,
          detail: state.taskReady
            ? (currentLang() === "en" ? `Ready: ${state.sourcePath} -> ${state.targetKey}:${state.targetPath}` : currentLang() === "mix" ? `任务已确认 / Ready: ${state.sourcePath} -> ${state.targetKey}:${state.targetPath}` : `任务已确认: ${state.sourcePath} -> ${state.targetKey}:${state.targetPath}`)
            : (currentLang() === "en" ? "Confirm source_path, target_path, and sync strategy in the Task tab." : currentLang() === "mix" ? "去“任务”页确认 source_path、target_path 和同步策略。 / Confirm task settings first." : "去“任务”页确认 source_path、target_path 和同步策略。"),
        },
        {
          key: "execute",
          title: currentLang() === "en" ? "5. Execute" : currentLang() === "mix" ? "5. 执行同步 / Execute" : "5. 执行同步",
          ready: state.executionReady,
          detail: state.executionReady
            ? (currentLang() === "en" ? "Ready: direct sync, queue, leaf mode, and pending recovery are available." : currentLang() === "mix" ? "可执行：可开始直接同步、队列、最底层模式和待补传恢复。 / Execution ready." : "可执行：可开始直接同步、队列、最底层模式和待补传恢复。")
            : (currentLang() === "en" ? "After task settings are ready, switch to Run for actual execution." : currentLang() === "mix" ? "任务确认后，再去“执行”页启动正式同步。 / Open Run after task is ready." : "任务确认后，再去“执行”页启动正式同步。"),
        },
      ];
      root.innerHTML = steps.map((step) => {
        const cls = [
          "workflow-card",
          step.ready ? "is-ready" : "",
          state.currentStep === step.key ? "is-current" : "",
          !step.ready && state.currentStep !== step.key ? "is-locked" : "",
        ].filter(Boolean).join(" ");
        return `<div class="${cls}"><strong>${escapeHtml(step.title)}</strong><div class="mono">${escapeHtml(step.detail)}</div></div>`;
      }).join("");
    }

    function applyWorkflowGates() {
      const locked = Boolean(authState.enabled && !authState.authenticated);
      const state = computeWorkflowState();
      const tabRules = {
        overview: true,
        mounts: true,
        source: state.connectionReady,
        config: state.connectionReady,
        task: state.connectionReady && state.sourceReady,
        execute: state.executionReady,
      };
      document.querySelectorAll(".tab").forEach((tab) => {
        const tabId = tab.dataset.tab;
        if (!tabId) return;
        const enabled = !locked && Boolean(tabRules[tabId]);
        tab.disabled = !enabled;
        tab.classList.toggle("is-gated", !enabled);
        if (!enabled) {
          if (locked) tab.title = currentLang() === "en" ? "Login to the console first." : currentLang() === "mix" ? "请先登录控制台。 / Login to the console first." : "请先登录控制台。";
          else if (tabId === "source") tab.title = currentLang() === "en" ? "Complete OpenList connection first." : currentLang() === "mix" ? "请先完成 OpenList 连接。 / Complete OpenList connection first." : "请先完成 OpenList 连接。";
          else if (tabId === "task") tab.title = currentLang() === "en" ? "Pick a concrete source directory first." : currentLang() === "mix" ? "请先选定具体源目录。 / Pick a concrete source directory first." : "请先选定具体源目录。";
          else if (tabId === "execute") tab.title = currentLang() === "en" ? "Confirm the task configuration first." : currentLang() === "mix" ? "请先确认任务配置。 / Confirm task configuration first." : "请先确认任务配置。";
        } else {
          tab.removeAttribute("title");
        }
      });
      if (!locked) {
        const active = document.querySelector(".tab.active");
        const activeId = active?.dataset?.tab || "overview";
        if (!tabRules[activeId]) activateTab("overview");
      }
      renderWorkflowRoadmap();
      renderOverviewNextStep();
    }

    function updateAuthUi(state = {}) {
      authState = {
        enabled: Boolean(state.enabled),
        authenticated: Boolean(state.authenticated),
        username: String(state.username || ""),
      };
      document.body.classList.toggle("auth-locked", authState.enabled && !authState.authenticated);
      document.getElementById("auth-lock-panel")?.classList.toggle("hidden", !(authState.enabled && !authState.authenticated));
      document.getElementById("open-auth-login")?.classList.toggle("hidden", !authState.enabled || authState.authenticated);
      document.getElementById("open-auth-login-inline")?.classList.toggle("hidden", !authState.enabled || authState.authenticated);
      document.getElementById("logout-auth")?.classList.toggle("hidden", !authState.enabled || !authState.authenticated);
      const badge = document.getElementById("auth-status-badge");
      if (badge) {
        badge.textContent = !authState.enabled
          ? (currentLang() === "en" ? "Console unlocked" : currentLang() === "mix" ? "控制台未加锁 / Console unlocked" : "控制台未加锁")
          : authState.authenticated
            ? (currentLang() === "en" ? `Logged in: ${authState.username || "admin"}` : currentLang() === "mix" ? `已登录: ${authState.username || "admin"} / Logged in` : `已登录: ${authState.username || "admin"}`)
            : (currentLang() === "en" ? "Console locked" : currentLang() === "mix" ? "控制台已加锁 / Console locked" : "控制台已加锁");
      }
      applyWorkflowGates();
    }

    async function ensureAuthorizedAndBootstrap(force = false) {
      const status = await fetch("/api/auth/status", { credentials: "same-origin" }).then((response) => response.json());
      updateAuthUi(status || {});
      if (authState.enabled && !authState.authenticated) {
        appBootstrapped = false;
        stopAutoRefresher();
        showAuthDialog(currentLang() === "en" ? "Console login is required before loading the rest of the workspace." : currentLang() === "mix" ? "需要先登录控制台后再继续加载其它页面。 / Console login required." : "需要先登录控制台后再继续加载其它页面。");
        return false;
      }
      hideAuthDialog();
      if (!appBootstrapped || force) {
        await loadConfig();
        try {
          await refreshStatus();
        } catch (error) {
          console.warn("early refreshStatus failed", error);
        }
        try {
          await attemptAutoOpenListLogin();
        } catch (error) {
          console.warn("attemptAutoOpenListLogin failed", error);
        }
        try {
          await loadProviderRegistry();
        } catch (error) {
          console.warn("loadProviderRegistry failed", error);
          setNotice("provider-capture-summary", currentLang() === "en"
            ? `Provider registry unavailable: ${error.message}`
            : currentLang() === "mix"
              ? `源网盘注册表暂不可用 / Provider registry unavailable: ${error.message}`
              : `源网盘注册表暂不可用: ${error.message}`);
        }
        try {
          await refreshStatus();
        } catch (error) {
          console.warn("refreshStatus failed", error);
          setNotice("runtime-action-notice", currentLang() === "en"
            ? `Status refresh failed: ${error.message}`
            : currentLang() === "mix"
              ? `状态刷新失败 / Status refresh failed: ${error.message}`
              : `状态刷新失败: ${error.message}`);
        }
        startAutoRefresher();
        appBootstrapped = true;
        void (async () => {
          try {
            await loadDrivers();
          } catch (error) {
            console.warn("loadDrivers failed", error);
            const select = document.getElementById("driver-select");
            if (select && !select.innerHTML.trim()) {
              select.innerHTML = `<option value="">${escapeHtml(currentLang() === "en" ? "Driver list unavailable" : currentLang() === "mix" ? "驱动列表暂不可用 / Driver list unavailable" : "驱动列表暂不可用")}</option>`;
            }
            document.getElementById("driver-fields").innerHTML = `<div class='subtle'>${escapeHtml(currentLang() === "en" ? `OpenList driver list unavailable: ${error.message}` : currentLang() === "mix" ? `OpenList 驱动列表暂不可用 / Driver list unavailable: ${error.message}` : `OpenList 驱动列表暂不可用: ${error.message}`)}</div>`;
          }
          try {
            await refreshStorages();
          } catch (error) {
            console.warn("refreshStorages failed", error);
            setNotice("dir-notice", currentLang() === "en"
              ? `Mounted source list unavailable: ${error.message}`
              : currentLang() === "mix"
                ? `挂载源列表暂不可用 / Mounted source list unavailable: ${error.message}`
                : `挂载源列表暂不可用: ${error.message}`);
          }
          try {
            await ensureDirectoryBrowserReady(true);
          } catch (error) {
            console.warn("ensureDirectoryBrowserReady failed", error);
          }
        })();
      } else {
        applyWorkflowGates();
      }
      return true;
    }

    function normalizeTabId(tabId) {
      if (tabId === "sync") return "task";
      if (tabId === "pending" || tabId === "miaochuan") return "execute";
      if (tabId === "about") return "overview";
      return tabId || "overview";
    }

    function setDetailsOpen(id, open = true) {
      const el = document.getElementById(id);
      if (el && typeof el.open === "boolean") el.open = open;
    }

    function mountedSourceSelectIds() {
      return ["mounted_source_select", "mounted_source_select_source"];
    }

    function syncMountedSourceSelectors(value) {
      const normalized = String(value || "").trim();
      mountedSourceSelectIds().forEach((id) => {
        const select = document.getElementById(id);
        if (!select) return;
        if (!normalized) {
          select.value = "";
          return;
        }
        const matched = Array.from(select.options || []).some((option) => String(option.value || "") === normalized);
        if (matched) select.value = normalized;
      });
    }

    function toggleDialog(id, visible) {
      const dialog = document.getElementById(id);
      if (!dialog) return;
      dialog.classList.toggle("hidden", !visible);
    }

    function activateTab(tabId) {
      const normalizedTabId = normalizeTabId(tabId);
      document.querySelectorAll(".tab").forEach((tab) => {
        tab.classList.toggle("active", tab.dataset.tab === normalizedTabId);
      });
      document.querySelectorAll(".tab-panel").forEach((panel) => {
        panel.classList.toggle("active", panel.dataset.panel === normalizedTabId);
      });
      updatePanelState({ activeTab: normalizedTabId });
    }

    function renderOverviewNextStep() {
      const root = document.getElementById("overview-next-step");
      if (!root) return;
      const state = computeWorkflowState();
      let text = "";
      let tone = "";
      if (!state.connectionReady) {
        text = currentLang() === "en"
          ? "Start from Connections: complete OpenList login or runtime startup first."
          : currentLang() === "mix"
            ? "下一步：先去“连接”完成 OpenList 登录或托管启动。 / Start from Connections first."
            : "下一步：先去“连接”完成 OpenList 登录或托管启动。";
        tone = "warn";
      } else if (!state.sourceReady) {
        text = currentLang() === "en"
          ? "Open Source and choose a concrete source directory, then write it back to source_path."
          : currentLang() === "mix"
            ? "下一步：去“源端”选一个具体目录，并写回 source_path。 / Pick a concrete source directory next."
            : "下一步：去“源端”选一个具体目录，并写回 source_path。";
      } else if (!state.targetConfigured) {
        text = currentLang() === "en"
          ? "Open Target and finish the active target credentials until preflight becomes ready."
          : currentLang() === "mix"
            ? "下一步：去“目标端”补齐当前目标端配置，直到预检显示可执行。 / Finish target configuration next."
            : "下一步：去“目标端”补齐当前目标端配置，直到预检显示可执行。";
        tone = "warn";
      } else if (!state.taskReady) {
        text = currentLang() === "en"
          ? "Open Task and confirm source_path, target_path, and sync strategy before execution."
          : currentLang() === "mix"
            ? "下一步：去“任务”确认 source_path、target_path 和同步策略。 / Confirm task settings next."
            : "下一步：去“任务”确认 source_path、target_path 和同步策略。";
      } else {
        text = currentLang() === "en"
          ? "Everything is ready. Open Run to start a dry-run, direct sync, queue run, or pending recovery."
          : currentLang() === "mix"
            ? "当前已经可以执行。去“执行”页开始 dry-run、直接同步、队列或补传。 / Ready to run."
            : "当前已经可以执行。去“执行”页开始 dry-run、直接同步、队列或补传。";
        tone = "success";
      }
      setNotice("overview-next-step", text, tone);
    }

    function t(key) {
      const lang = currentLang();
      if (lang === "mix") {
        const zh = I18N.zh[key] || key;
        const en = I18N.en[key] || key;
        return `${zh} / ${en}`;
      }
      return I18N[lang]?.[key] || I18N.zh[key] || key;
    }

    function helpText(key) {
      const lang = currentLang();
      if (lang === "mix") {
        const zh = HELP_TEXT.zh[key] || "";
        const en = HELP_TEXT.en[key] || "";
        return zh && en ? `${zh} / ${en}` : (zh || en || "");
      }
      return HELP_TEXT[lang]?.[key] || HELP_TEXT.zh[key] || HELP_TEXT.en[key] || "";
    }

    function applyHelpTips() {
      document.querySelectorAll("[data-help-key]").forEach((el) => {
        const key = el.getAttribute("data-help-key");
        if (!key) return;
        const text = helpText(key).trim();
        if (text) {
          el.setAttribute("title", text);
          const iconEligible = ["LABEL", "H2", "H3"].includes(el.tagName) || el.classList.contains("help-anchor");
          if (iconEligible && !el.querySelector(".help-tip")) {
            const tip = document.createElement("span");
            tip.className = "help-tip";
            tip.tabIndex = 0;
            tip.textContent = "?";
            el.appendChild(tip);
          }
          const tip = el.querySelector(".help-tip");
          if (tip) {
            tip.setAttribute("title", text);
            tip.setAttribute("aria-label", text);
          }
          if (["BUTTON", "LABEL", "H2", "H3", "SPAN", "DIV"].includes(el.tagName)) {
            el.style.cursor = "help";
          }
        } else {
          el.removeAttribute("title");
          const tip = el.querySelector(".help-tip");
          if (tip) tip.remove();
        }
      });
    }

    function applyI18n() {
      document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (!key) return;
        if (el.dataset.noticeManual === "1") return;
        if (el.classList.contains("subtle")) el.innerHTML = t(key);
        else el.textContent = t(key);
      });
      document.querySelectorAll("[data-i18n-option]").forEach((el) => {
        const key = el.getAttribute("data-i18n-option");
        if (key) el.textContent = t(key);
      });
      document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
        const key = el.getAttribute("data-i18n-placeholder");
        if (key) el.setAttribute("placeholder", t(key));
      });
      const toggleLogs = document.getElementById("toggle-logs");
      if (toggleLogs) {
        const key = document.getElementById("log-drawer").classList.contains("hidden") ? "btn.toggle_logs_show" : "btn.toggle_logs_hide";
        toggleLogs.textContent = t(key);
      }
      populateTargetOptions();
      populateCoverageFilterOptions();
      if (storageRecords.length) populateMountedSources(storageRecords);
      if (providerDefinitions.length) {
        renderProviderOptions(providerDefinitions);
        renderProviderCapturePanel();
        renderProviderQuickPicks();
      }
      applyOpenListModeUi();
      applyHelpTips();
      renderTargetSpecificControls();
      renderCapabilitySummary();
      renderAboutRegistry();
      renderOverviewNextStep();
    }

    function initTabs() {
      document.querySelectorAll(".tab").forEach((tab) => {
        tab.addEventListener("click", () => activateTab(tab.dataset.tab));
      });
      activateTab(normalizeTabId(getPanelState().activeTab || "overview"));
      applySavedCoverageFilters();
      const langSelect = document.getElementById("ui_language");
      langSelect.value = currentLang();
      langSelect.addEventListener("change", () => {
        setGroupedConfigValue(["ui", "language"], langSelect.value);
        localStorage.setItem(UI_LANGUAGE_KEY, langSelect.value);
        scheduleUiPrefsPersist();
        applyI18n();
      });
    }

    function setNoticeTone(id, tone = "") {
      const el = document.getElementById(id);
      if (!el) return;
      el.classList.remove("is-success", "is-warn", "is-error");
      if (tone === "success") el.classList.add("is-success");
      else if (tone === "warn") el.classList.add("is-warn");
      else if (tone === "error") el.classList.add("is-error");
    }

    function setNotice(id, message, tone = "") {
      const el = document.getElementById(id);
      if (!el) return;
      el.textContent = message;
      el.dataset.noticeManual = "1";
      setNoticeTone(id, tone);
    }

    function persistNotice(id, message, delays = [0, 400, 1200], tone = "") {
      delays.forEach((delay) => {
        window.setTimeout(() => setNotice(id, message, tone), delay);
      });
    }

    function translateDriverText(zh, en) {
      return currentLang() === "en" ? en : currentLang() === "mix" ? `${zh} / ${en}` : zh;
    }

    function normalizeDriverKey(value) {
      return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "");
    }

    function humanizeDriverFieldName(value) {
      return String(value || "")
        .replace(/[_-]+/g, " ")
        .replace(/([a-z])([A-Z])/g, "$1 $2")
        .replace(/\s+/g, " ")
        .trim()
        .replace(/\b\w/g, (m) => m.toUpperCase());
    }

    function driverFieldLabel(name) {
      const key = normalizeDriverKey(name);
      const mapped = DRIVER_FIELD_I18N[key];
      if (!mapped) return humanizeDriverFieldName(name);
      return translateDriverText(mapped.zh, mapped.en);
    }

    function driverFieldHelp(text) {
      const raw = String(text || "").trim();
      if (!raw) return "";
      const normalized = raw.toLowerCase();
      const matched = DRIVER_HELP_PATTERNS.find((item) => item.includes.every((part) => normalized.includes(part)));
      if (matched) return translateDriverText(matched.zh, matched.en);
      return currentLang() === "en" ? raw : currentLang() === "mix" ? `${raw}` : raw;
    }

    function driverFieldOptions(text) {
      const raw = String(text || "").trim();
      if (!raw) return "";
      const mapped = DRIVER_OPTIONS_I18N[raw];
      if (mapped) return translateDriverText(mapped.zh, mapped.en);
      return raw;
    }

    function guideTextPair(pair) {
      if (!pair) return "";
      return translateDriverText(pair.zh || "", pair.en || "");
    }

    function activeTargetKey() {
      return String(document.getElementById("target_key")?.value || document.getElementById("target_key_config")?.value || providerRegistryPayload?.active_target || "guangya");
    }

    function formatTargetProfileLabel(profile) {
      const zh = String(profile?.label_zh || profile?.labelZh || profile?.label || profile?.key || "-");
      const en = String(profile?.label || profile?.key || zh || "-");
      return currentLang() === "en" ? en : currentLang() === "mix" ? `${zh} / ${en}` : zh;
    }

    function getTargetProfileNames(profile) {
      const zh = String(profile?.label_zh || profile?.labelZh || profile?.label || profile?.key || "-");
      const en = String(profile?.label || profile?.key || zh || "-");
      return { zh, en };
    }

    function populateTargetOptions() {
      const targetProfiles = providerRegistryPayload?.target_profiles || {};
      const implementationStatus = providerRegistryPayload?.target_implementation_status || {};
      const currentValue = String(
        document.getElementById("target_key")?.value
        || document.getElementById("target_key_config")?.value
        || getConfigFieldValue(configCache, "target_key")
        || providerRegistryPayload?.active_target
        || "guangya"
      );
      const fallbackProfiles = [
        { key: "guangya", label: "Guangya", label_zh: "光鸭云盘" },
        { key: "openlist", label: "OpenList", label_zh: "OpenList 挂载目标" },
        { key: "localfs", label: "LocalFS", label_zh: "本地目录目标" },
        { key: "webdav", label: "WebDAV", label_zh: "WebDAV 目标端" },
        { key: "s3", label: "S3", label_zh: "S3 / 对象存储目标" },
        { key: "seafile", label: "Seafile", label_zh: "Seafile 目标端" },
        { key: "azureblob", label: "Azure Blob", label_zh: "Azure Blob 目标" },
        { key: "smb", label: "SMB", label_zh: "SMB 共享目标" },
        { key: "ftp", label: "FTP", label_zh: "FTP 目标端" },
        { key: "sftp", label: "SFTP", label_zh: "SFTP 目标端" },
      ];
      const profileList = Object.keys(targetProfiles).length ? Object.values(targetProfiles) : fallbackProfiles;
      const options = profileList.map((item) => {
        const key = String(item.key || "");
        const selectable = Boolean(implementationStatus?.[key]?.selectable ?? true);
        const isCurrent = key === currentValue;
        const suffix = selectable
          ? ""
          : (currentLang() === "en"
            ? " [planned]"
            : currentLang() === "mix"
              ? " [规划中 / planned]"
              : " [规划中]");
        return {
          value: key,
          label: `${formatTargetProfileLabel(item)}${suffix}`,
          disabled: !selectable && !isCurrent,
        };
      }).filter((item) => item.value);
      const emptyLabel = currentLang() === "en" ? "Select target" : currentLang() === "mix" ? "选择目标端 / Select target" : "选择目标端";
      buildSelectOptions("target_key", emptyLabel, options, currentValue);
      buildSelectOptions("target_key_config", emptyLabel, options, currentValue);
      renderTargetQuickPicks(profileList, currentValue);
    }

    function renderTargetQuickPicks(profileList = [], currentValue = "guangya") {
      const root = document.getElementById("target-quick-picks");
      if (!root) return;
      const implementationStatus = providerRegistryPayload?.target_implementation_status || {};
      const cards = profileList
        .filter((item) => POPULAR_TARGET_KEYS.includes(String(item.key || "")))
        .sort((a, b) => POPULAR_TARGET_KEYS.indexOf(String(a.key || "")) - POPULAR_TARGET_KEYS.indexOf(String(b.key || "")))
        .map((item) => {
          const key = String(item.key || "");
          const selectable = Boolean(implementationStatus?.[key]?.selectable ?? true);
          const hint = selectable
            ? (currentLang() === "en" ? "click to switch" : currentLang() === "mix" ? "点击切换 / click to switch" : "点击切换")
            : (currentLang() === "en" ? "planned" : currentLang() === "mix" ? "规划中 / planned" : "规划中");
          return `<button class="quick-pick ${key === currentValue ? "is-active" : ""}" data-target-quick="${escapeHtml(key)}" ${selectable ? "" : "disabled"}><strong>${escapeHtml(formatTargetProfileLabel(item))}</strong><small>${escapeHtml(hint)}</small></button>`;
        });
      root.innerHTML = cards.join("");
    }

    function renderTargetPreflightNotice({ targetKey = "", payload = null, loading = false, error = null } = {}) {
      const root = document.getElementById("target-preflight-notice");
      if (!root) return;
      if (loading) {
        setNotice(
          "target-preflight-notice",
          currentLang() === "en"
            ? `Checking target ${targetKey || activeTargetKey() || "guangya"}...`
            : currentLang() === "mix"
              ? `正在检查目标端 ${targetKey || activeTargetKey() || "guangya"} ... / Checking target...`
              : `正在检查目标端 ${targetKey || activeTargetKey() || "guangya"} ...`,
          "warn",
        );
        return;
      }
      if (error) {
        setNotice(
          "target-preflight-notice",
          currentLang() === "en"
            ? `Target preflight failed: ${error.message}`
            : currentLang() === "mix"
              ? `目标端预检失败 / Target preflight failed: ${error.message}`
              : `目标端预检失败: ${error.message}`,
          "error",
        );
        return;
      }
      const resolvedPayload = payload || {};
      const capability = resolvedPayload?.adapter_capability || {};
      const missingFields = Array.isArray(resolvedPayload?.missing_fields) ? resolvedPayload.missing_fields : [];
      const implemented = !!resolvedPayload?.implemented;
      const selectable = !!resolvedPayload?.selectable;
      const configured = !!resolvedPayload?.configured;
      const targetProfile = providerRegistryPayload?.target_profiles?.[targetKey] || { key: targetKey, label: targetKey, label_zh: targetKey };
      const stateLabel = error
        ? (currentLang() === "en" ? "Connection error" : currentLang() === "mix" ? "连接异常 / Connection error" : "连接异常")
        : configured
          ? (currentLang() === "en" ? "Connected" : currentLang() === "mix" ? "已连接 / Connected" : "已连接")
          : missingFields.length
            ? (currentLang() === "en" ? "Not ready" : currentLang() === "mix" ? "未就绪 / Not ready" : "未就绪")
            : (currentLang() === "en" ? "Pending check" : currentLang() === "mix" ? "待检查 / Pending check" : "待检查");
      const statusText = configured
        ? (currentLang() === "en" ? "This target is ready for execution." : currentLang() === "mix" ? "当前目标端已配置完成，可以继续执行。 / Ready for execution." : "当前目标端已配置完成，可以继续执行。")
        : missingFields.length
          ? (currentLang() === "en" ? `Still missing ${missingFields.length} required field(s).` : currentLang() === "mix" ? `还有 ${missingFields.length} 个必填项未完成。 / Missing ${missingFields.length} required field(s).` : `还有 ${missingFields.length} 个必填项未完成。`)
          : (currentLang() === "en" ? "Target fields still need to be confirmed." : currentLang() === "mix" ? "目标端字段还需要确认。 / Target fields still need confirmation." : "目标端字段还需要确认。");
      const nextHint = !implemented
        ? (currentLang() === "en" ? "This target is still not implemented in the current build." : currentLang() === "mix" ? "当前版本还没真正实现这个目标端。 / Not implemented in this build." : "当前版本还没真正实现这个目标端。")
        : !selectable
          ? (currentLang() === "en" ? "This target is listed but not selectable yet." : currentLang() === "mix" ? "这个目标端已列出，但暂时还不能选择。 / Listed but not selectable yet." : "这个目标端已列出，但暂时还不能选择。")
          : configured
            ? (currentLang() === "en" ? "You can keep the details collapsed unless you need to update credentials." : currentLang() === "mix" ? "如果不需要改凭证，下面的连接字段可以继续保持收起。 / You can keep details collapsed." : "如果不需要改凭证，下面的连接字段可以继续保持收起。")
            : (currentLang() === "en" ? "Expand the connection details below only when you need to complete the missing fields." : currentLang() === "mix" ? "只有补字段或排查连接问题时，才需要展开下面的连接详情。 / Expand details only when needed." : "只有补字段或排查连接问题时，才需要展开下面的连接详情。");
      root.innerHTML = `
        <div><strong>${escapeHtml(formatTargetProfileLabel(targetProfile))}</strong></div>
        <div class="summary-pill ${configured ? "" : "warn"}">${escapeHtml(stateLabel)}</div>
        <div>${escapeHtml(statusText)}</div>
        <div class="mono">${currentLang() === "en" ? "Missing fields" : currentLang() === "mix" ? "缺少字段 / Missing fields" : "缺少字段"}: ${escapeHtml(missingFields.join(", ") || "-")}</div>
        <div class="subtle">${escapeHtml(nextHint)}</div>
      `;
      setNoticeTone("target-preflight-notice", configured ? "success" : "warn");
    }

    function renderProviderQuickPicks() {
      const root = document.getElementById("provider-quick-picks");
      if (!root) return;
      const currentValue = String(document.getElementById("provider-select")?.value || "");
      const quickKeys = POPULAR_PROVIDER_KEYS.filter((key) => providerDefinitions.some((item) => item.key === key));
      if (!quickKeys.length) {
        root.innerHTML = `<div class="notice">${escapeHtml(currentLang() === "en" ? "Common provider quick picks will appear here after the provider registry loads." : currentLang() === "mix" ? "载入源网盘注册表后，这里会显示常用网盘快捷入口。 / Common provider quick picks appear here after registry load." : "载入源网盘注册表后，这里会显示常用网盘快捷入口。")}</div>`;
        return;
      }
      root.innerHTML = quickKeys.map((key) => {
        const item = providerDefinitions.find((entry) => entry.key === key);
        const profile = item?.source_profile || {};
        const zh = String(profile.label_zh || item?.label_zh || item?.labelZh || item?.label || key);
        const en = String(profile.label || item?.label || key);
        const label = currentLang() === "en" ? en : currentLang() === "mix" ? `${zh} / ${en}` : zh;
        const hint = currentLang() === "en"
          ? "select and prepare mount"
          : currentLang() === "mix"
            ? "切换并准备挂载 / select and prepare mount"
            : "切换并准备挂载";
        return `<button class="quick-pick ${currentValue === key ? "is-active" : ""}" data-provider-quick="${escapeHtml(key)}"><strong>${escapeHtml(label)}</strong><small>${escapeHtml(hint)}</small></button>`;
      }).join("");
    }

    function renderTargetSpecificControls() {
      const target = activeTargetKey();
      const isGuangya = target === "guangya";
      const targetProfile = providerRegistryPayload?.target_profiles?.[target] || {};
      const targetStatus = providerRegistryPayload?.target_implementation_status?.[target] || {};
      const preflight = targetPreflightCache || {};
      const targetName = formatTargetProfileLabel(targetProfile);
      const targetNames = getTargetProfileNames(targetProfile);
      const writable = preflight?.write_mode && preflight.write_mode !== "unavailable";
      const fastUploadHashes = Array.isArray(preflight?.fast_upload_hashes) ? preflight.fast_upload_hashes : [];
      const fallbackModes = Array.isArray(preflight?.fallback_modes) ? preflight.fallback_modes : [];
      const miaochuanTabLabel = document.getElementById("tab-miaochuan-label");
      const miaochuanPanelTitle = document.getElementById("miaochuan-panel-title");
      const captureCardTitle = document.getElementById("capture-card-title");
      const targetModeChip = document.getElementById("target-mode-chip");
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
          : (currentLang() === "en" ? "Fast Upload" : currentLang() === "mix" ? "快传能力 / Fast Upload" : "快传能力");
      }
      if (miaochuanPanelTitle) {
        miaochuanPanelTitle.textContent = isGuangya
          ? t("panel.miaochuan")
          : (currentLang() === "en" ? "Target Fast Upload Reference" : currentLang() === "mix" ? "目标端快传参考 / Target Fast Upload Reference" : "目标端快传参考");
      }
      if (captureCardTitle) {
        captureCardTitle.textContent = isGuangya
          ? t("card.capture")
          : (currentLang() === "en" ? "Target State" : currentLang() === "mix" ? "目标端状态 / Target State" : "目标端状态");
      }
      if (targetAuthPanelTitle) {
        targetAuthPanelTitle.textContent = isGuangya
          ? t("panel.guangya_auth")
          : (currentLang() === "en" ? "Target Credentials" : currentLang() === "mix" ? "目标端连接参数 / Target Credentials" : "目标端连接参数");
      }
      if (targetPathLabel) {
        targetPathLabel.textContent = isGuangya
          ? t("label.target_path")
          : (currentLang() === "en" ? "Target Directory" : currentLang() === "mix" ? "目标端目录 / Target Directory" : "目标端目录");
      }
      if (capabilityDesc) {
        capabilityDesc.textContent = isGuangya
          ? t("desc.capability")
          : (currentLang() === "en"
            ? `Show the real source-to-${targetName} recommendation, including whether this target is already writable and whether it only supports regular upload fallback.`
            : currentLang() === "mix"
              ? `这里会显示当前源端到 ${targetName} 的真实建议，包括是否已接通写入、以及是否仅支持普通上传降级。 / Honest source-to-target recommendation for ${targetName}.`
              : `这里会显示当前源端到 ${targetName} 的真实建议，包括是否已接通写入、以及是否仅支持普通上传降级。`);
      }
      if (targetProfilesDesc) {
        targetProfilesDesc.textContent = isGuangya
          ? t("desc.target_profiles")
          : (currentLang() === "en"
            ? `${targetName} is a built-in target in this build. Whether it can fast upload depends on the capability check below.`
            : currentLang() === "mix"
              ? `${targetName} 已纳入当前版本目标端；是否能快传，以这里的能力检查为准。 / ${targetName} is supported as a target in this build.`
              : `${targetName} 已纳入当前版本目标端；是否能快传，以这里的能力检查为准。`);
      }
      if (driverMatrixDesc) {
        driverMatrixDesc.textContent = isGuangya
          ? t("desc.driver_matrix")
          : (currentLang() === "en"
            ? `This matrix reflects the real source-driver to ${targetName} support status. It does not overpromise cross-cloud fast upload when only regular upload is available.`
            : currentLang() === "mix"
              ? `这是当前“源驱动 -> ${targetName}”的真实支持状态；如果只能普通上传，就不会误导成已支持跨盘秒传。 / Real matrix for ${targetName}.`
              : `这是当前“源驱动 -> ${targetName}”的真实支持状态；如果只能普通上传，就不会误导成已支持跨盘秒传。`);
      }
      if (miaochuanDesc) {
        miaochuanDesc.textContent = isGuangya
          ? t("desc.miaochuan")
          : (currentLang() === "en"
            ? "Flash-upload JSON direct import remains Guangya-only. Other targets can still sync files, but currently through regular upload and fallback flows."
            : currentLang() === "mix"
              ? "秒传 JSON 直导仍然只支持 Guangya。其它目标端可以写入，但当前主要走普通上传和降级补传。 / Flash JSON direct import remains Guangya-only."
              : "秒传 JSON 直导仍然只支持 Guangya。其它目标端可以写入，但当前主要走普通上传和降级补传。");
      }
      if (diagnoseMiaochuanButton) {
        diagnoseMiaochuanButton.textContent = isGuangya
          ? t("btn.diagnose_miaochuan")
          : (currentLang() === "en" ? "Diagnose Fast Upload" : currentLang() === "mix" ? "诊断快传能力 / Diagnose Fast Upload" : "诊断快传能力");
      }
      if (runMiaochuanButton) {
        runMiaochuanButton.textContent = isGuangya
          ? t("btn.run_miaochuan")
          : (currentLang() === "en" ? "Guangya JSON Only" : currentLang() === "mix" ? "仅 Guangya 支持 JSON 直导 / Guangya JSON Only" : "仅 Guangya 支持 JSON 直导");
        runMiaochuanButton.disabled = !isGuangya;
        runMiaochuanButton.title = isGuangya
          ? ""
          : (currentLang() === "en"
            ? "JSON direct import is only available for Guangya right now."
            : currentLang() === "mix"
              ? "JSON 直导目前仅 Guangya 可用。 / Guangya only."
              : "JSON 直导目前仅 Guangya 可用。");
      }
      document.querySelectorAll("[data-target-only]").forEach((el) => {
        const expected = String(el.getAttribute("data-target-only") || "");
        el.classList.toggle("hidden", expected !== target);
      });
      document.querySelectorAll("[data-target-section]").forEach((el) => {
        const expected = String(el.getAttribute("data-target-section") || "");
        el.classList.toggle("hidden", expected !== target);
        el.classList.toggle("is-active", expected === target);
      });
      document.querySelectorAll("[data-target-quick]").forEach((el) => {
        el.classList.toggle("is-active", String(el.getAttribute("data-target-quick") || "") === target);
      });
      if (targetModeChip) {
        targetModeChip.textContent = currentLang() === "en"
          ? `Active target: ${targetNames.en}`
          : currentLang() === "mix"
            ? `当前目标端：${targetNames.zh} / Active target: ${targetNames.en}`
            : `当前目标端：${targetNames.zh}`;
      }
      const popularSummary = document.getElementById("target-popular-summary");
      if (popularSummary) {
        const popularText = {
          guangya: currentLang() === "en"
            ? "Common target: Guangya cloud drive. Best when you want metadata fast upload first and fallback reupload second."
            : currentLang() === "mix"
              ? "常用目标端：光鸭云盘。适合优先秒传、未命中再补传。 / Guangya is best for metadata fast upload first."
              : "常用目标端：光鸭云盘。适合优先秒传、未命中再补传。",
          localfs: currentLang() === "en"
            ? "Common target: local folder. Suitable for local export, debugging, and fallback landing."
            : currentLang() === "mix"
              ? "常用目标端：本地目录。适合导出、联调和本地落盘。 / Local folder target."
              : "常用目标端：本地目录。适合导出、联调和本地落盘。",
          webdav: currentLang() === "en"
            ? "Common target: WebDAV. Suitable for NAS, private cloud, and third-party WebDAV services."
            : currentLang() === "mix"
              ? "常用目标端：WebDAV。适合 NAS、私有云和第三方 WebDAV。 / WebDAV target."
              : "常用目标端：WebDAV。适合 NAS、私有云和第三方 WebDAV。",
          s3: currentLang() === "en"
            ? "Common target: S3 or compatible object storage."
            : currentLang() === "mix"
              ? "常用目标端：S3 / 对象存储。 / S3 or compatible object storage."
              : "常用目标端：S3 / 对象存储。",
          seafile: currentLang() === "en"
            ? "Common target: Seafile team library."
            : currentLang() === "mix"
              ? "常用目标端：Seafile 团队资料库。 / Seafile team library."
              : "常用目标端：Seafile 团队资料库。",
          azureblob: currentLang() === "en"
            ? "Common target: Azure Blob container."
            : currentLang() === "mix"
              ? "常用目标端：Azure Blob 容器。 / Azure Blob container."
              : "常用目标端：Azure Blob 容器。",
          smb: currentLang() === "en"
            ? "Common target: SMB share."
            : currentLang() === "mix"
              ? "常用目标端：SMB 共享。 / SMB share."
              : "常用目标端：SMB 共享。",
          ftp: currentLang() === "en"
            ? "Common target: FTP server directory."
            : currentLang() === "mix"
              ? "常用目标端：FTP 目录。 / FTP server directory."
              : "常用目标端：FTP 目录。",
          sftp: currentLang() === "en"
            ? "Common target: SFTP server directory."
            : currentLang() === "mix"
              ? "常用目标端：SFTP 目录。 / SFTP server directory."
              : "常用目标端：SFTP 目录。",
          openlist: currentLang() === "en"
            ? "Common target: OpenList mount target. Good for normal upload into another mounted storage."
            : currentLang() === "mix"
              ? "常用目标端：OpenList 挂载目标。适合写入另一个已挂载存储。 / OpenList mount target."
              : "常用目标端：OpenList 挂载目标。适合写入另一个已挂载存储。",
        };
        popularSummary.textContent = popularText[target] || popularText.guangya;
      }
      const guide = document.getElementById("target-auth-guide");
      if (guide) {
        const authMode = String(preflight?.auth_mode || targetProfile?.auth_mode || "-");
        guide.innerHTML = `
          <div><strong>${escapeHtml(targetName)}</strong></div>
          <div class="subtle">${escapeHtml(guideTextPair(targetProfile?.description) || "")}</div>
          <div class="mono">${currentLang() === "en" ? "Auth mode" : currentLang() === "mix" ? "鉴权 / Auth mode" : "鉴权"}: ${escapeHtml(authMode)}</div>
          <div class="subtle">${preflight?.auto_create_dir
            ? (currentLang() === "en" ? "Can create target directories automatically." : currentLang() === "mix" ? "支持自动建目录。 / Auto directory creation supported." : "支持自动建目录。")
            : (currentLang() === "en" ? "Target directories may need to exist in advance." : currentLang() === "mix" ? "目标目录可能需要提前存在。 / Target directory may need to exist first." : "目标目录可能需要提前存在。")}</div>
        `;
      }
      const summary = document.getElementById("target-auth-summary");
      if (summary) {
        const missingFields = Array.isArray(preflight?.missing_fields) ? preflight.missing_fields : [];
        const readyText = writable
          ? (currentLang() === "en" ? "Ready to execute" : currentLang() === "mix" ? "可直接执行 / Ready to execute" : "可直接执行")
          : (currentLang() === "en" ? "Needs configuration" : currentLang() === "mix" ? "还需配置 / Needs configuration" : "还需配置");
        summary.innerHTML = `
          <div class="summary-pill ${writable ? "" : "warn"}">${escapeHtml(readyText)}</div>
          <div>${writable
            ? (currentLang() === "en" ? "Connection looks healthy and this target can continue into execution." : currentLang() === "mix" ? "连接状态正常，可以继续执行。 / Connection looks healthy." : "连接状态正常，可以继续执行。")
            : (currentLang() === "en" ? `There are still ${missingFields.length || 0} required field(s) to complete.` : currentLang() === "mix" ? `还有 ${missingFields.length || 0} 个必填项需要补齐。 / Required fields are still missing.` : `还有 ${missingFields.length || 0} 个必填项需要补齐。`)}</div>
          <div class="mono">${currentLang() === "en" ? "Write mode" : currentLang() === "mix" ? "写入方式 / Write mode" : "写入方式"}: ${escapeHtml(preflight?.write_mode || "-")}</div>
          <div class="subtle">${escapeHtml(preflight?.message || "")}</div>
        `;
      }
    }

    async function loadProviderRegistry() {
      const data = await call("/api/provider/registry");
      providerRegistryPayload = data || providerRegistryPayload;
      driverGuideRegistry = data?.guides || {};
      providerDefinitions = Array.isArray(data?.provider_catalog) ? data.provider_catalog : providerDefinitions;
      populateTargetOptions();
      populateSourceProfileOverrideOptions();
      populateCoverageFilterOptions();
      renderProviderOptions(providerDefinitions);
      renderProviderCapturePanel();
      renderProviderQuickPicks();
      renderSourceDriverSummary();
      await refreshTargetPreflight();
      renderCapabilitySummary();
      renderAboutRegistry();
      await refreshCapabilityAssessment();
    }

    async function refreshCapabilityAssessment() {
      const context = currentDriverContext();
      if (!context.driver) {
        capabilityAssessmentCache = null;
        renderCapabilitySummary();
        renderTaskModeSummary();
        return;
      }
      try {
        capabilityAssessmentCache = await call("/api/provider/capability_assess", {
          method: "POST",
          body: JSON.stringify({
            driver: context.driver,
            mount_path: context.mountPath,
            target: activeTargetKey(),
            analysis_summary: sourceAnalyzeCache?.summary || {},
          }),
        });
      } catch (_error) {
        capabilityAssessmentCache = null;
      }
      renderCapabilitySummary();
      renderTaskModeSummary();
    }

    function buildCoverageAuditPayload(filters) {
      const payload = {
        target: activeTargetKey(),
        only_gaps: filters.onlyGaps,
        only_onboarding_ready: filters.onlyOnboardingReady,
        next_action: filters.nextAction,
        missing_item: filters.missingItem,
        capability_level: filters.capabilityLevel,
        profile_key: filters.profileKey,
        onboarding_stage: filters.onboardingStage,
      };
      if (Array.isArray(driversCache) && driversCache.length) {
        payload.drivers = driversCache;
      }
      return payload;
    }

    async function refreshCoverageAudit() {
      const filters = currentCoverageFilters();
      try {
        coverageAuditCache = await call("/api/provider/coverage_audit", {
          method: "POST",
          body: JSON.stringify(buildCoverageAuditPayload(filters)),
        });
      } catch (_error) {
        coverageAuditCache = null;
      }
      populateCoverageFilterOptions();
      renderAboutRegistry();
    }

    async function refreshTargetPreflight(expectedTarget = null) {
      const requestedTarget = String(expectedTarget || activeTargetKey() || "guangya");
      try {
        const payload = await call(`/api/target/preflight?target=${encodeURIComponent(requestedTarget)}`);
        if (requestedTarget !== String(activeTargetKey() || "guangya")) return;
        targetPreflightCache = payload || null;
        targetPreflightByKey.set(requestedTarget, payload || null);
        renderTargetPreflightNotice({ targetKey: requestedTarget, payload });
      } catch (error) {
        if (requestedTarget !== String(activeTargetKey() || "guangya")) return;
        targetPreflightCache = null;
        renderTargetPreflightNotice({ targetKey: requestedTarget, error });
      }
      applyWorkflowGates();
    }

    function downloadTextFile(filename, text, mimeType = "text/plain;charset=utf-8") {
      const blob = new Blob([text], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 500);
    }

    function currentDriverContext() {
      const selectedMount = document.getElementById("mounted_source_select")?.value || "";
      const overrideMap = getGroupedConfigValue(["source_session", "mount_provider_mapping"], {}) || {};
      const overrideProfile = typeof overrideMap === "object" && overrideMap
        ? String(overrideMap[selectedMount] || "")
        : "";
      const selectedStorage = storageRecords.find((item) => String(item.mount_path || item.mountPath || item.path || "/") === String(selectedMount));
      const mountedDriver = selectedStorage?.driver || selectedStorage?.driver_name || selectedStorage?.driverName || "";
      const driver = overrideProfile || mountedDriver || document.getElementById("driver-select")?.value || "";
      return {
        driver,
        overrideProfile,
        mountedDriver,
        mountPath: selectedMount || document.getElementById("source_path")?.value || "/",
      };
    }

    function populateSourceProfileOverrideOptions() {
      const select = document.getElementById("source_profile_override");
      if (!select) return;
      const profiles = Object.values(providerRegistryPayload?.source_profiles || {});
      const current = currentDriverContext();
      const options = [
        `<option value="">${currentLang() === "en" ? "Auto detect from mount driver" : currentLang() === "mix" ? "自动按挂载驱动识别 / Auto detect from mount driver" : "自动按挂载驱动识别"}</option>`,
        ...profiles.map((profile) => {
          const key = String(profile?.key || "");
          const label = escapeHtml(translateDriverText(profile?.label_zh || key, profile?.label || key) || key);
          const selected = current.overrideProfile === key ? "selected" : "";
          return `<option value="${escapeHtml(key)}" ${selected}>${label} [${escapeHtml(key)}]</option>`;
        }),
      ];
      select.innerHTML = options.join("");
      if (current.overrideProfile) select.value = current.overrideProfile;
    }

    async function saveSourceProfileOverrideSelection(value = "") {
      const selectedMount = String(document.getElementById("mounted_source_select")?.value || "").trim();
      if (!selectedMount) {
        setNotice("source-profile-override-notice", currentLang() === "en"
          ? "Choose a mounted source first, then save an override."
          : currentLang() === "mix"
            ? "请先选择已挂载源目录，再保存覆盖。 / Choose a mounted source first."
            : "请先选择已挂载源目录，再保存覆盖。");
        return false;
      }
      const map = { ...(getGroupedConfigValue(["source_session", "mount_provider_mapping"], {}) || {}) };
      const normalized = String(value || "").trim();
      if (normalized) map[selectedMount] = normalized;
      else delete map[selectedMount];
      setGroupedConfigValue(["source_session", "mount_provider_mapping"], map);
      const result = await call("/api/provider/source_mapping", {
        method: "POST",
        body: JSON.stringify({
          mount_path: selectedMount,
          profile_key: normalized,
        }),
      });
      if (result?.items && typeof result.items === "object") {
        setGroupedConfigValue(["source_session", "mount_provider_mapping"], result.items);
      }
      populateSourceProfileOverrideOptions();
      renderSourceDriverSummary();
      await refreshCapabilityAssessment();
      setNotice("source-profile-override-notice", normalized
        ? (currentLang() === "en"
            ? `Saved override: ${selectedMount} -> ${normalized}`
            : currentLang() === "mix"
              ? `已保存覆盖：${selectedMount} -> ${normalized} / Override saved`
              : `已保存覆盖：${selectedMount} -> ${normalized}`)
        : (currentLang() === "en"
            ? `Override cleared for ${selectedMount}`
            : currentLang() === "mix"
              ? `已清除覆盖：${selectedMount} / Override cleared`
              : `已清除覆盖：${selectedMount}`));
      return true;
    }

    function capabilityLevelText(level) {
      const normalized = String(level || "").toLowerCase();
      const mapping = {
        fast_upload_supported: {
          zh: "可稳定秒传",
          en: "Stable fast upload",
        },
        fast_upload_partial: {
          zh: "部分可秒传",
          en: "Partial fast upload",
        },
        relay_supported: {
          zh: "可中转流传输",
          en: "Relay streaming supported",
        },
        download_upload_only: {
          zh: "仅补传/下载上传",
          en: "Download-upload only",
        },
        unsupported: {
          zh: "暂不支持",
          en: "Unsupported",
        },
      };
      const text = mapping[normalized] || mapping.unsupported;
      return currentLang() === "en" ? text.en : currentLang() === "mix" ? `${text.zh} / ${text.en}` : text.zh;
    }

    const strategyModeText = (mode) => capabilityView.strategyModeText({
      currentLang,
    }, mode);
    const coverageNextActionText = (action) => capabilityView.coverageNextActionText({
      currentLang,
    }, action);
    const strategyQuickActions = (mode, strategy) => capabilityView.strategyQuickActions({
      currentLang,
      activeTargetKey,
    }, mode, strategy);
    const performCapabilityQuickAction = (actionKey) => capabilityView.performCapabilityQuickAction({
      activateTab,
    }, actionKey);

    function renderCapabilitySummary() {
      workflowView.renderCapabilitySummary?.({
        ...workflowContext(),
        root: document.getElementById("capability-summary"),
        quickActionsRoot: document.getElementById("capability-quick-actions"),
      });
    }

    function toggleDrawer(forceVisible = null) {
      const drawer = document.getElementById("log-drawer");
      const hidden = forceVisible === null ? !drawer.classList.contains("hidden") : !forceVisible;
      drawer.classList.toggle("hidden", hidden);
      updatePanelState({ logsVisible: !hidden });
      applyI18n();
    }

    function getConfigFromForm() {
      const payload = { ...configCache };
      const currentMode = normalizeOpenListMode(document.getElementById("openlist_mode")?.value || "external_local");
      for (const field of CONFIG_FIELDS) {
        const el = document.getElementById(field);
        if (!el) continue;
        payload[field] = normalizeFormValue(field, el.value);
      }
      payload.grouped_config = payload.grouped_config && typeof payload.grouped_config === "object" ? payload.grouped_config : {};
      configCache = payload;
      syncConfigFieldsToGrouped(payload);
      persistCurrentOpenListModeSnapshot(currentMode);
      setGroupedConfigValue(["openlist", "mode"], currentMode);
      setGroupedConfigValue(["openlist", "url"], String(document.getElementById("openlist_url")?.value || ""));
      setGroupedConfigValue(["openlist", "token"], String(document.getElementById("openlist_token")?.value || ""));
      setGroupedConfigValue(["openlist", "username"], String(document.getElementById("openlist_username")?.value || "admin"));
      setGroupedConfigValue(["openlist", "password"], String(document.getElementById("openlist_password")?.value || ""));
      setGroupedConfigValue(["ui", "panel_open_states"], getPanelState());
      payload.grouped_config = configCache.grouped_config;
      payload.openlist_mode = currentMode;
      return payload;
    }

    function applyConfigToForm(config, options = {}) {
      const restoreActiveTab = options.restoreActiveTab !== false;
      configCache = { ...(config || {}) };
      syncUiPreferenceCache();
      const groupedMountedSource = getGroupedConfigValue(["ui", "browser", "mounted_source"], "");
      if (typeof groupedMountedSource === "string" && groupedMountedSource) {
        syncMountedSourceSelectors(groupedMountedSource);
      }
      const panelState = getGroupedConfigValue(["ui", "panel_open_states"], {});
      if (panelState && typeof panelState === "object") {
        setPanelState({ ...panelState });
        if (restoreActiveTab && panelState.activeTab) activateTab(panelState.activeTab);
      }
      for (const field of CONFIG_FIELDS) {
        const el = document.getElementById(field);
        if (!el) continue;
        const value = getConfigFieldValue(config, field);
        if (el.type === "checkbox") {
          el.checked = Boolean(value);
        } else {
          el.value = value ?? "";
        }
      }
      applyOpenListModeSnapshot(config?.openlist_mode || document.getElementById("openlist_mode")?.value || "external_local");
      document.getElementById("effective_openlist_url").value = config?.effective_openlist_url || "";
      syncMirroredInputs();
      applySavedCoverageFilters();
      populateSourceProfileOverrideOptions();
      const langSelect = document.getElementById("ui_language");
      if (langSelect) langSelect.value = currentLang();
    }

    async function saveConfig(options = {}) {
      const payload = getConfigFromForm();
      await call("/api/config", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      configCache = payload;
      if (options?.silent) return;
      providerRegistryPayload = {
        ...(providerRegistryPayload || {}),
        active_target: String(payload.target_key || "guangya"),
      };
      await loadProviderRegistry();
      await refreshCoverageAudit();
      await refreshTargetPreflight();
      setNotice("sync-notice", "配置已保存");
      setNotice("dir-notice", "配置已保存");
    }

    async function loadConfig(options = {}) {
      const data = await call("/api/config");
      applyConfigToForm(data, options);
      applyI18n();
      syncMirroredInputs();
      return data;
    }

    async function getRuntimeStatus() {
      return await call("/api/openlist/runtime/status");
    }

    async function installManagedRuntimeWithPrompt(runtimeStatus = null) {
      const status = runtimeStatus || await getRuntimeStatus();
      if (!status?.install_required) return status;
      const message = currentLang() === "en"
        ? "No local OpenList runtime was found. Download it now? If you cancel, switch to an external local or remote mode."
        : currentLang() === "mix"
          ? "当前未检测到本机 OpenList 运行时，是否现在拉取？如果取消，请改用外部本机或远程模式。 / Download now?"
          : "当前未检测到本机 OpenList 运行时，是否现在拉取？如果取消，请改用外部本机或远程模式。";
      const accepted = window.confirm(message);
      if (!accepted) {
        setNotice("runtime-action-notice", currentLang() === "en" ? "Runtime installation was declined. Switch to an external mode to continue." : currentLang() === "mix" ? "已拒绝拉取本机运行时，请改用外部模式。 / Runtime install declined." : "已拒绝拉取本机运行时，请改用外部模式。");
        return status;
      }
      const installed = await call("/api/openlist/runtime/install", { method: "POST" });
      renderRuntime(installed);
      await loadConfig();
      return installed;
    }

    async function ensureDirectoryBrowserReady(force = false) {
      const sourcePath = String(document.getElementById("source_path").value || "/").trim() || "/";
      const browserPath = String(getGroupedConfigValue(["ui", "browser", "current_path"], "") || "").trim();
      const restorePath = browserPath || sourcePath;
      if (!force && currentDirectoryPath && currentDirectoryPath !== "/" && currentDirectoryPath === restorePath) {
        return;
      }
      try {
        await browseDirectory(restorePath);
        setNotice("dir-notice", `已恢复目录浏览位置: ${restorePath}`);
      } catch (error) {
        await browseDirectory("/");
        setNotice("dir-notice", `恢复目录浏览位置失败，已回退到根目录: ${error.message}`);
      }
    }

    async function browseDirectory(path) {
      const data = await call("/api/openlist/list_dirs", {
        method: "POST",
        body: JSON.stringify({
          openlist_url: document.getElementById("openlist_url").value,
          openlist_username: document.getElementById("openlist_username").value,
          openlist_password: document.getElementById("openlist_password").value,
          openlist_token: document.getElementById("openlist_token").value,
          path,
        }),
      });
      renderDirectoryBrowser(data);
    }

    function renderDirectoryBrowser(data) {
      sourceOpsView.renderDirectoryBrowser?.(sourceOpsContext(), data);
    }

    function renderSourceAnalyze(data) {
      workflowView.renderSourceAnalyze?.(workflowContext(), data);
    }

    function renderMiaochuanDiagnosis(data) {
      sourceOpsView.renderMiaochuanDiagnosis?.(sourceOpsContext(), data);
    }

    function populateMountedSources(items) {
      sourceOpsView.populateMountedSources?.(sourceOpsContext(), items);
      populateOpenListTargetMounts(items);
    }

    function renderQueue(items) {
      sourceOpsView.renderQueue?.(sourceOpsContext(), items);
    }

    function renderStorages(payload) {
      sourceOpsView.renderStorages?.(sourceOpsContext(), payload);
      const content = payload?.data?.content || payload?.data || [];
      populateOpenListTargetMounts(Array.isArray(content) ? content : []);
    }

    function populateOpenListTargetMounts(items = []) {
      const list = Array.isArray(items) ? items : [];
      const selects = ["openlist_target_mount_select", "openlist_target_mount_select_task"]
        .map((id) => document.getElementById(id))
        .filter(Boolean);
      if (!selects.length) return;
      if (!list.length) {
        selects.forEach((select) => {
          select.innerHTML = `<option value="">${currentLang() === "en" ? "No OpenList mounts" : currentLang() === "mix" ? "暂无 OpenList 挂载 / No OpenList mounts" : "暂无 OpenList 挂载"}</option>`;
        });
        return;
      }
      const targetPath = String(document.getElementById("target_path")?.value || "").trim();
      const html = list.map((item) => {
        const mountPath = String(item.mount_path || item.mountPath || item.path || "/");
        const driver = String(item.driver || item.driver_name || item.driverName || "-");
        const selected = targetPath.startsWith(mountPath) ? "selected" : "";
        return `<option value="${escapeHtml(mountPath)}" ${selected}>${escapeHtml(mountPath)} | ${escapeHtml(driver)}</option>`;
      }).join("");
      selects.forEach((select) => {
        select.innerHTML = html;
      });
    }

    function syncOpenListTargetMountSelectors(value) {
      const normalized = String(value || "").trim();
      ["openlist_target_mount_select", "openlist_target_mount_select_task"].forEach((id) => {
        const select = document.getElementById(id);
        if (!select || !normalized) return;
        const matched = Array.from(select.options || []).some((option) => String(option.value || "") === normalized);
        if (matched) select.value = normalized;
      });
    }

    function applySelectedOpenListTargetMount(selectId, noticeId = "target-preflight-notice") {
      const select = document.getElementById(selectId);
      const targetPath = document.getElementById("target_path");
      const value = String(select?.value || "").trim();
      if (!targetPath || !value) {
        setNotice(
          noticeId,
          currentLang() === "en"
            ? "Pick an OpenList mount first."
            : currentLang() === "mix"
              ? "请先选择一个 OpenList 挂载。 / Pick an OpenList mount first."
              : "请先选择一个 OpenList 挂载。",
          "warn"
        );
        return;
      }
      targetPath.value = value;
      syncOpenListTargetMountSelectors(value);
      setNotice(
        noticeId,
        currentLang() === "en"
          ? `Target directory set to ${value}`
          : currentLang() === "mix"
            ? `已写入目标目录：${value} / Target directory applied.`
            : `已写入目标目录：${value}`,
        "success"
      );
    }

    async function loadDrivers() {
      await loadProviderRegistry();
      const data = await call("/api/openlist/drivers");
      driversCache = Array.isArray(data?.items) ? data.items : [];
      const select = document.getElementById("driver-select");
      const sourceProfiles = providerRegistryPayload?.source_profiles || {};
      const formatDriverOptionLabel = (driver) => {
        const normalized = normalizeDriverKey(driver);
        const matchedProfile = Object.values(sourceProfiles).find((profile) =>
          Array.isArray(profile?.driver_aliases) && profile.driver_aliases.some((alias) => normalizeDriverKey(alias) === normalized)
        );
        if (!matchedProfile) return String(driver || "");
        const zh = String(matchedProfile.label_zh || matchedProfile.label || driver || "");
        const en = String(matchedProfile.label || driver || "");
        if (currentLang() === "en") return `${en} [${driver}]`;
        if (currentLang() === "mix") return `${zh} / ${en} [${driver}]`;
        return `${zh} [${driver}]`;
      };
      select.innerHTML = driversCache.map((driver) => `<option value="${escapeHtml(driver)}">${escapeHtml(formatDriverOptionLabel(driver))}</option>`).join("");
      if (driversCache.length) {
        await loadDriverInfo(select.value);
      } else {
        document.getElementById("driver-fields").innerHTML = `<div class='subtle'>${currentLang() === "en" ? "No drivers loaded." : currentLang() === "mix" ? "未获取到驱动列表 / No drivers loaded." : "未获取到驱动列表。"}</div>`;
      }
      applyProviderSelectionFromDriver(select.value || "");
      renderProviderQuickPicks();
      await refreshCoverageAudit();
    }

    function renderDriverFields(info) {
      sourceOpsView.renderDriverFields?.(sourceOpsContext(), info);
    }

    async function loadDriverInfo(driver) {
      if (!driver) return;
      const info = await call(`/api/openlist/driver_info?driver=${encodeURIComponent(driver)}`);
      renderDriverFields(info);
      try {
        driverCaptureBlueprint = await call(`/api/provider/driver_blueprint?driver=${encodeURIComponent(driver)}`);
      } catch (_error) {
        driverCaptureBlueprint = null;
      }
      renderDriverGuide(info?.name || "");
      renderProviderOptions(providerDefinitions);
      applyProviderSelectionFromDriver(driver);
      renderCapabilitySummary();
      await refreshCapabilityAssessment();
    }

    async function refreshStorages() {
      const data = await call("/api/openlist/storages");
      renderStorages(data);
    }

    async function attemptAutoOpenListLogin() {
      const token = String(document.getElementById("openlist_token").value || "").trim();
      const username = String(document.getElementById("openlist_username").value || "").trim();
      const password = String(document.getElementById("openlist_password").value || "");
      if (token || !username || !password) return false;
      try {
        await call("/api/openlist/login", {
          method: "POST",
          body: JSON.stringify({
            openlist_url: document.getElementById("openlist_url").value,
            openlist_username: username,
            openlist_password: password,
            openlist_token: token,
          }),
        });
        await loadConfig();
        setNotice("sync-notice", "已自动完成 OpenList 登录并写回 Token。");
        return true;
      } catch (error) {
        setNotice("sync-notice", `OpenList 自动登录失败: ${error.message}`);
        return false;
      }
    }

    async function attemptAutoGuangyaCapture() {
      if (activeTargetKey() !== "guangya") return false;
      const values = [
        document.getElementById("guangya_authorization").value,
        document.getElementById("guangya_access_token").value,
        document.getElementById("guangya_refresh_token").value,
        document.getElementById("guangya_device_id").value,
      ].map((item) => String(item || "").trim());
      const hasAll = values.every(Boolean);
      if (hasAll || getSessionStorageValue(AUTO_GUANGYA_CAPTURE_KEY, LEGACY_AUTO_GUANGYA_CAPTURE_KEYS) === "1") return false;
      try {
        await call("/api/guangya/capture/start", { method: "POST" });
        sessionStorage.setItem(AUTO_GUANGYA_CAPTURE_KEY, "1");
        setNotice("sync-notice", "检测到光鸭登录信息不完整，已自动启动一次抓取窗口。");
        return true;
      } catch (error) {
        setNotice("sync-notice", `自动启动光鸭抓取失败: ${error.message}`);
        return false;
      }
    }

    function renderSourceDriverSummary() {
      workflowView.renderSourceDriverSummary?.(workflowContext());
    }

    function renderTaskModeSummary() {
      workflowView.renderTaskModeSummary?.(workflowContext());
    }

    function renderWorkflowSummaries(syncState = {}, runtimeState = {}) {
      workflowView.renderWorkflowSummaries?.(workflowContext(), syncState, runtimeState);
    }

    async function refreshStatus() {
      const data = await call("/api/status");
      window.__cpbStatusCache = data || {};
      renderSync(data.sync || {});
      renderRuntime(data.openlist_runtime || {});
      renderCapture(data.guangya_capture || {}, data.active_target_state || null);
       providerDefinitions = Array.isArray(data.provider_definitions) ? data.provider_definitions : providerDefinitions;
       providerSnapshots = data.provider_captures || {};
       renderProviderOptions(providerDefinitions);
       renderProviderCapturePanel();
       renderProviderQuickPicks();
      renderQueue(data.sync?.source_queue || []);
      renderPendingTree(data.sync?.persistent_pending || []);
      if (data.sync?.directory_browser) renderDirectoryBrowser(data.sync.directory_browser);
      renderLogs(data.logs || []);
      renderWorkflowSummaries(data.sync || {}, data.openlist_runtime || {});
    }

    async function analyzeCurrentSource() {
      await saveConfig();
      const sourcePath = document.getElementById("source_path").value || currentDirectoryPath || "/";
      const data = await call("/api/source/analyze", {
        method: "POST",
        body: JSON.stringify({ source_path: sourcePath, limit: 80 }),
      });
      renderSourceAnalyze(data);
      renderCapabilitySummary();
      await refreshCapabilityAssessment();
      setNotice("source-analyze-notice", currentLang() === "en"
        ? `Analysis finished: ${data.summary?.total ?? 0} files scanned.`
        : currentLang() === "mix"
          ? `分析完成，共扫描 ${data.summary?.total ?? 0} 个文件。 / Analysis finished.`
          : `分析完成，共扫描 ${data.summary?.total ?? 0} 个文件。`);
    }

    async function buildCurrentSourceMiaochuan() {
      await saveConfig();
      const sourcePath = document.getElementById("source_path").value || currentDirectoryPath || "/";
      const data = await call("/api/source/miaochuan_preview", {
        method: "POST",
        body: JSON.stringify({ source_path: sourcePath }),
      });
      document.getElementById("miaochuan_payload").value = data.payload_text || "";
      renderSourceAnalyze({
        source_path: data.source_path,
        summary: data.summary,
        plan_total: data.plan_total,
        removed_total: data.removed_total,
        entries: (data.payload?.files || []).slice(0, 80).map((item) => ({
          path: item.path,
          provider: item.provider,
          hashType: item.hashType,
          size: Number(item.size || 0),
          md5: item.etag || "",
          gcid: item.gcid || "",
          sourceId: item.sourceId || "",
        })),
        truncated: Array.isArray(data.payload?.files) && data.payload.files.length > 80,
      });
      activateTab("execute");
      setDetailsOpen("execute-miaochuan-details", true);
      setDetailsOpen("execute-capability-details", true);
      const count = data.payload?.totalFilesCount ?? 0;
      setNotice(
        "miaochuan-notice",
        currentLang() === "en"
          ? `Generated flash-upload JSON from current source directory: ${count} files ready.`
          : currentLang() === "mix"
            ? `已生成当前源目录秒传 JSON，共 ${count} 个文件可直导。 / Flash-upload JSON generated.`
            : `已生成当前源目录秒传 JSON，共 ${count} 个文件可直导。`
      );
      setNotice(
        "source-analyze-notice",
        currentLang() === "en"
          ? `Flash-upload JSON generated: ${count} files ready.`
          : currentLang() === "mix"
            ? `秒传 JSON 已生成，共 ${count} 个文件。 / Flash-upload JSON generated.`
            : `秒传 JSON 已生成，共 ${count} 个文件。`
      );
      await diagnoseMiaochuanPayload();
    }

    async function diagnoseMiaochuanPayload() {
      const payloadText = String(document.getElementById("miaochuan_payload").value || "").trim();
      if (!payloadText) {
        renderMiaochuanDiagnosis(null);
        throw new Error(currentLang() === "en"
          ? "Please paste or generate flash-upload JSON first."
          : currentLang() === "mix"
            ? "请先粘贴或生成秒传 JSON。 / Please paste or generate flash-upload JSON first."
            : "请先粘贴或生成秒传 JSON。");
      }
      const data = await call("/api/miaochuan/diagnose", {
        method: "POST",
        body: JSON.stringify({ miaochuan_payload: payloadText }),
      });
      renderMiaochuanDiagnosis(data);
      setNotice(
        "miaochuan-notice",
        currentLang() === "en"
          ? `Diagnosis finished: ${data.total ?? 0} files, ${formatBytes(data.total_size || 0)} total.`
          : currentLang() === "mix"
            ? `诊断完成，共 ${data.total ?? 0} 个文件，合计 ${formatBytes(data.total_size || 0)}。 / Diagnosis finished.`
            : `诊断完成，共 ${data.total ?? 0} 个文件，合计 ${formatBytes(data.total_size || 0)}。`
      );
      return data;
    }

    async function runSyncMode(mode, extra = {}, noticeId = "sync-notice") {
      await saveConfig();
      await call("/api/sync/start", {
        method: "POST",
        body: JSON.stringify({ mode, ...extra }),
      });
      setNotice(noticeId, `已启动任务: ${mode}`);
      await refreshStatus();
    }

    function withBusy(buttonId, message, handler) {
      return async () => {
        const button = document.getElementById(buttonId);
        const oldText = button?.textContent || "";
        if (button) {
          button.disabled = true;
          button.textContent = message;
        }
        try {
          await handler();
        } catch (error) {
          setNotice("sync-notice", `失败: ${error.message}`, "error");
          setNotice("dir-notice", `失败: ${error.message}`, "error");
          setNotice("miaochuan-notice", `失败: ${error.message}`, "error");
          setNotice("runtime-action-notice", `失败: ${error.message}`, "error");
        } finally {
          if (button) {
            button.disabled = false;
            button.textContent = oldText;
          }
        }
      };
    }

    function bindEvents() {
      if (eventsBound) return;
      eventsBound = true;

      const byId = (id) => document.getElementById(id);
      const bindClick = (id, handler) => {
        const el = byId(id);
        if (!el) {
          console.warn(`bindEvents: missing element #${id}`);
          return;
        }
        el.onclick = handler;
      };
      const bindChange = (id, handler) => {
        const el = byId(id);
        if (!el) {
          console.warn(`bindEvents: missing element #${id}`);
          return;
        }
        el.addEventListener("change", handler);
      };
      const bindEvent = (id, eventName, handler) => {
        const el = byId(id);
        if (!el) {
          console.warn(`bindEvents: missing element #${id}`);
          return;
        }
        el.addEventListener(eventName, handler);
      };

      bindClick("open-auth-login", () => {
        setAuthNotice(currentLang() === "en" ? "Enter the console credentials." : currentLang() === "mix" ? "请输入控制台账号密码。 / Enter the console credentials." : "请输入控制台账号密码。");
        showAuthDialog();
      });
      bindClick("open-help-center", () => toggleDialog("help-center-dialog", true));
      bindClick("open-help-center-target", () => toggleDialog("help-center-dialog", true));
      bindClick("close-help-center", () => toggleDialog("help-center-dialog", false));
      bindClick("open-advanced-settings", () => toggleDialog("advanced-settings-dialog", true));
      bindClick("open-advanced-settings-mounts", () => toggleDialog("advanced-settings-dialog", true));
      bindClick("close-advanced-settings", () => toggleDialog("advanced-settings-dialog", false));
      bindClick("save-config-advanced", withBusy("save-config-advanced", "保存中...", saveConfig));
      bindClick("open-auth-login-inline", () => {
        setAuthNotice(currentLang() === "en" ? "Enter the console credentials." : currentLang() === "mix" ? "请输入控制台账号密码。 / Enter the console credentials." : "请输入控制台账号密码。");
        showAuthDialog();
      });
      bindClick("close-auth-dialog", () => {
        if (authState.enabled && !authState.authenticated) return;
        hideAuthDialog();
      });
      bindClick("submit-auth-login", withBusy("submit-auth-login", "登录中...", async () => {
        await call("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({
            username: document.getElementById("auth-username").value,
            password: document.getElementById("auth-password").value,
          }),
        });
        document.getElementById("auth-password").value = "";
        setAuthNotice(currentLang() === "en" ? "Login succeeded. Loading the console..." : currentLang() === "mix" ? "登录成功，正在载入控制台... / Login succeeded." : "登录成功，正在载入控制台...");
        await ensureAuthorizedAndBootstrap(true);
      }));
      bindEvent("auth-login-form", "submit", (event) => {
        event.preventDefault();
        document.getElementById("submit-auth-login")?.click();
      });
      bindEvent("auth-password", "keydown", (event) => {
        if (event.key === "Enter") document.getElementById("submit-auth-login")?.click();
      });
      bindEvent("auth-dialog", "click", (event) => {
        if (event.target?.id !== "auth-dialog") return;
        if (authState.enabled && !authState.authenticated) return;
        hideAuthDialog();
      });
      bindEvent("advanced-settings-dialog", "click", (event) => {
        if (event.target?.id === "advanced-settings-dialog") toggleDialog("advanced-settings-dialog", false);
      });
      bindEvent("help-center-dialog", "click", (event) => {
        if (event.target?.id === "help-center-dialog") toggleDialog("help-center-dialog", false);
      });
      bindClick("logout-auth", withBusy("logout-auth", "退出中...", async () => {
        await call("/api/auth/logout", { method: "POST" });
        updateAuthUi({ ...(authState || {}), authenticated: false });
        appBootstrapped = false;
        stopAutoRefresher();
        showAuthDialog(currentLang() === "en" ? "You have been logged out." : currentLang() === "mix" ? "已退出登录。 / You have been logged out." : "已退出登录。");
      }));
      bindClick("toggle-logs", () => toggleDrawer());
      bindClick("capability-quick-actions", (event) => {
        const target = event.target?.closest?.("[data-capability-action]");
        if (!target) return;
        performCapabilityQuickAction(target.getAttribute("data-capability-action"));
      });
      bindClick("reload-all", withBusy("reload-all", "重载中...", async () => {
        await loadConfig();
        await ensureDirectoryBrowserReady(true);
        await refreshStatus();
        await refreshStorages();
      }));
      bindClick("jump-connect", () => activateTab("mounts"));
      bindClick("jump-source", () => activateTab("source"));
      bindClick("jump-target", () => activateTab("config"));
      bindClick("jump-execute", () => activateTab("execute"));
      bindClick("save-config-top", withBusy("save-config-top", "保存中...", saveConfig));
      bindClick("save-config-overview", withBusy("save-config-overview", "保存中...", saveConfig));
      bindClick("save-config-bottom", withBusy("save-config-bottom", "保存中...", saveConfig));
      bindClick("apply-openlist-target-mount", () => applySelectedOpenListTargetMount("openlist_target_mount_select", "target-preflight-notice"));
      bindClick("apply-openlist-target-mount-task", () => applySelectedOpenListTargetMount("openlist_target_mount_select_task", "sync-notice"));
      const handleMountedSourceChange = (nextValueRaw) => {
        const nextValue = String(nextValueRaw || "");
        syncMountedSourceSelectors(nextValue);
        applyRatePresetForMount(nextValue);
        setGroupedConfigValue(["ui", "browser", "mounted_source"], nextValue);
        scheduleUiPrefsPersist();
        const selected = storageRecords.find((item) => String(item.mount_path || item.mountPath || item.path || "/") === nextValue);
        if (selected) applyProviderSelectionFromDriver(selected.driver || selected.driver_name || selected.driverName || "");
        renderProviderQuickPicks();
        populateSourceProfileOverrideOptions();
        renderSourceDriverSummary();
      };
      bindChange("mounted_source_select", (event) => {
        handleMountedSourceChange(event.target.value);
      });
      bindChange("mounted_source_select_source", (event) => {
        handleMountedSourceChange(event.target.value);
      });
      bindChange("provider-select", () => {
        renderProviderCapturePanel();
        renderProviderQuickPicks();
      });
      const handleTargetChange = async (nextTargetRaw) => {
        const nextTarget = String(nextTargetRaw || "guangya");
        const seq = ++targetChangeSeq;
        const taskSelect = document.getElementById("target_key");
        const configSelect = document.getElementById("target_key_config");
        if (taskSelect && taskSelect.value !== nextTarget) taskSelect.value = nextTarget;
        if (configSelect && configSelect.value !== nextTarget) configSelect.value = nextTarget;
        providerRegistryPayload = {
          ...(providerRegistryPayload || {}),
          active_target: nextTarget,
        };
        setGroupedConfigValue(["targets", "active_target"], nextTarget);
        const cachedPreflight = targetPreflightByKey.get(nextTarget);
        if (cachedPreflight) {
          targetPreflightCache = cachedPreflight;
          renderTargetPreflightNotice({ targetKey: nextTarget, payload: cachedPreflight });
        } else {
          renderTargetPreflightNotice({ targetKey: nextTarget, loading: true });
        }
        renderTargetSpecificControls();
        renderCapabilitySummary();
        renderAboutRegistry();
        await refreshTargetPreflight(nextTarget);
        if (seq !== targetChangeSeq) return;
        renderTargetSpecificControls();
        renderCapabilitySummary();
        renderAboutRegistry();
        await refreshCapabilityAssessment();
        if (seq !== targetChangeSeq) return;
        await refreshCoverageAudit();
        if (seq !== targetChangeSeq) return;
        if (nextTarget === "guangya") {
          await attemptAutoGuangyaCapture();
        }
      };
      bindChange("target_key", async (event) => {
        await handleTargetChange(event.target?.value || "guangya");
      });
      bindChange("target_key_config", async (event) => {
        await handleTargetChange(event.target?.value || "guangya");
      });
      bindChange("rate_limit_mode", () => {
        const selected = document.getElementById("mounted_source_select").value || document.getElementById("source_path").value || "/";
        applyRatePresetForMount(selected);
      });
      ["source_path", "target_path", "auto_download_threshold_mb", "source_provider_preference"].forEach((fieldId) => {
        bindChange(fieldId, () => {
          renderWorkflowSummaries(window.__cpbStatusCache?.sync || {}, window.__cpbStatusCache?.openlist_runtime || {});
        });
      });
      ["delete_removed", "target_delete_removed"].forEach((fieldId) => {
        bindChange(fieldId, () => {
          renderTaskModeSummary();
        });
      });
      bindChange("openlist_mode", async (event) => {
        const nextMode = normalizeOpenListMode(event.target.value || "external_local");
        persistCurrentOpenListModeSnapshot(getGroupedConfigValue(["openlist", "mode"], "external_local"));
        setGroupedConfigValue(["openlist", "mode"], nextMode);
        applyOpenListModeSnapshot(nextMode);
        await saveConfig();
        await refreshStatus();
      });
      bindChange("managed_openlist_port", () => {
        const mode = normalizeOpenListMode(document.getElementById("openlist_mode")?.value || "external_local");
        if (!isManagedOpenListMode(mode)) return;
        const nextUrl = buildManagedLocalUrl(document.getElementById("managed_openlist_port")?.value || 5244);
        const openlistUrlInput = document.getElementById("openlist_url");
        if (openlistUrlInput) openlistUrlInput.value = nextUrl;
        syncMirroredInputs();
      });
      bindClick("use-mounted-source", withBusy("use-mounted-source", "处理中...", async () => {
        const selected = document.getElementById("mounted_source_select").value || "/";
        setGroupedConfigValue(["ui", "browser", "mounted_source"], selected);
        syncMountedSourceSelectors(selected);
        document.getElementById("source_path").value = selected;
        await browseDirectory(selected);
        await saveConfig();
        setNotice("dir-notice", `已切换到挂载源目录: ${selected}`);
      }));
      bindClick("browse-mounted-source", withBusy("browse-mounted-source", "处理中...", async () => {
        const selected = document.getElementById("mounted_source_select_source")?.value
          || document.getElementById("mounted_source_select")?.value
          || "/";
        setGroupedConfigValue(["ui", "browser", "mounted_source"], selected);
        syncMountedSourceSelectors(selected);
        document.getElementById("source_path").value = selected;
        await browseDirectory(selected);
        await saveConfig();
        setNotice("dir-notice", `已从挂载源开始浏览: ${selected}`);
      }));
      bindClick("save-source-profile-override", withBusy("save-source-profile-override", "保存中...", async () => {
        const select = document.getElementById("source_profile_override");
        await saveSourceProfileOverrideSelection(select?.value || "");
      }));
      bindClick("clear-source-profile-override", withBusy("clear-source-profile-override", "清除中...", async () => {
        const select = document.getElementById("source_profile_override");
        if (select) select.value = "";
        await saveSourceProfileOverrideSelection("");
      }));

      bindClick("install-runtime", withBusy("install-runtime", "拉取中...", async () => {
        persistCurrentOpenListModeSnapshot(document.getElementById("openlist_mode")?.value || "external_local");
        await saveConfig({ silent: true });
        const installed = await installManagedRuntimeWithPrompt(await getRuntimeStatus());
        if (installed) {
          renderRuntime(installed);
          await loadConfig({ restoreActiveTab: false });
          await refreshStatus();
        }
      }));
      bindClick("start-runtime", withBusy("start-runtime", "启动中...", async () => {
        persistCurrentOpenListModeSnapshot(document.getElementById("openlist_mode")?.value || "external_local");
        await saveConfig({ silent: true });
        const status = await getRuntimeStatus();
        const maybeInstalled = await installManagedRuntimeWithPrompt(status);
        if (maybeInstalled?.install_required) {
          renderRuntime(maybeInstalled);
          return;
        }
        const data = await call("/api/openlist/runtime/start", { method: "POST" });
        const readyMessage = currentLang() === "en"
          ? `OpenList runtime is ready: ${data.active_url || "-"}`
          : currentLang() === "mix"
            ? `OpenList runtime 已就绪: ${data.active_url || "-"} / Runtime ready`
            : `OpenList runtime 已就绪: ${data.active_url || "-"}`;
        persistNotice("runtime-action-notice", readyMessage);
        persistNotice("sync-notice", readyMessage);
        renderRuntime(data);
        await loadConfig({ restoreActiveTab: false });
        await refreshStatus();
        persistNotice("runtime-action-notice", readyMessage, [0, 800, 2000]);
        persistNotice("sync-notice", readyMessage, [0, 800, 2000]);
      }));
      bindClick("start-runtime-docker", () => document.getElementById("start-runtime")?.click());
      bindClick("login-openlist", withBusy("login-openlist", currentLang() === "en" ? "Signing in..." : currentLang() === "mix" ? "登录中... / Signing in..." : "登录中...", async () => {
        setNotice("runtime-action-notice", currentLang() === "en" ? "Signing in to OpenList and writing back token..." : currentLang() === "mix" ? "正在登录 OpenList 并写回 Token... / Signing in to OpenList..." : "正在登录 OpenList 并写回 Token...", "warn");
        await call("/api/openlist/login", {
          method: "POST",
          body: JSON.stringify({
            openlist_url: document.getElementById("openlist_url").value,
            openlist_username: document.getElementById("openlist_username").value,
            openlist_password: document.getElementById("openlist_password").value,
            openlist_token: document.getElementById("openlist_token").value,
          }),
        });
        const loginNotice = currentLang() === "en"
          ? "OpenList login succeeded and token was written back."
          : currentLang() === "mix"
            ? "OpenList 登录成功并已写回 Token。 / Login succeeded and token saved."
            : "OpenList 登录成功并已写回 Token。";
        const syncNotice = currentLang() === "en"
          ? "OpenList connection is ready."
          : currentLang() === "mix"
            ? "OpenList 连接已就绪。 / OpenList connection is ready."
            : "OpenList 连接已就绪。";
        persistNotice("runtime-action-notice", loginNotice, [0], "success");
        persistNotice("sync-notice", syncNotice, [0], "success");
        await loadConfig({ restoreActiveTab: false });
        await ensureDirectoryBrowserReady(true);
        await refreshStorages();
        await refreshStatus();
        persistNotice("runtime-action-notice", loginNotice, [0, 400, 1200], "success");
        persistNotice("sync-notice", syncNotice, [0, 400, 1200], "success");
      }));
      bindClick("login-openlist-remote", async () => {
        const primaryUrl = document.getElementById("openlist_url");
        const primaryToken = document.getElementById("openlist_token");
        const primaryUsername = document.getElementById("openlist_username");
        const primaryPassword = document.getElementById("openlist_password");
        const remoteUrl = document.querySelector('[data-openlist-mirror="openlist_url"]');
        const remoteToken = document.querySelector('[data-openlist-mirror="openlist_token"]');
        const remoteUsername = document.querySelector('[data-openlist-mirror="openlist_username"]');
        const remotePassword = document.querySelector('[data-openlist-mirror="openlist_password"]');
        if (primaryUrl && remoteUrl) primaryUrl.value = remoteUrl.value;
        if (primaryToken && remoteToken) primaryToken.value = remoteToken.value;
        if (primaryUsername && remoteUsername) primaryUsername.value = remoteUsername.value;
        if (primaryPassword && remotePassword) primaryPassword.value = remotePassword.value;
        setNotice("runtime-action-notice", currentLang() === "en" ? "Remote mode fields synced. Starting OpenList login..." : currentLang() === "mix" ? "已同步远程模式字段，开始登录 OpenList... / Remote fields synced." : "已同步远程模式字段，开始登录 OpenList...", "warn");
        document.getElementById("login-openlist")?.click();
      });
      bindClick("capture-guangya", withBusy("capture-guangya", "启动抓取中...", async () => {
        await call("/api/guangya/capture/start", { method: "POST" });
        setNotice("sync-notice", "已打开光鸭登录抓取窗口，请在浏览器中完成登录。");
        await refreshStatus();
      }));
      const runDirectOverviewButton = document.getElementById("run-direct-overview");
      if (runDirectOverviewButton) {
        runDirectOverviewButton.onclick = withBusy("run-direct-overview", "启动中...", () => runSyncMode("direct"));
      }

      bindClick("browse-root", withBusy("browse-root", "载入中...", async () => {
        await browseDirectory("/");
        setNotice("dir-notice", "已打开挂载根目录。");
      }));
      bindClick("analyze-source", withBusy("analyze-source", "分析中...", async () => {
        await analyzeCurrentSource();
      }));
      bindClick("build-source-miaochuan", withBusy("build-source-miaochuan", "生成中...", async () => {
        await buildCurrentSourceMiaochuan();
      }));
      bindClick("browse-up", withBusy("browse-up", "返回中...", async () => {
        await browseDirectory(currentParentPath || "/");
        setNotice("dir-notice", `当前浏览: ${currentDirectoryPath}`);
      }));
      bindClick("browse-refresh", withBusy("browse-refresh", "刷新中...", async () => {
        await browseDirectory(currentDirectoryPath || "/");
        setNotice("dir-notice", `已刷新: ${currentDirectoryPath}`);
      }));
      bindClick("use-current-dir", withBusy("use-current-dir", "写入中...", async () => {
        document.getElementById("source_path").value = currentDirectoryPath || "/";
        await saveConfig();
        setNotice("dir-notice", `已写入 source_path: ${currentDirectoryPath}`);
      }));

      bindClick("add-current-queue", withBusy("add-current-queue", "加入中...", async () => {
        await call("/api/queue/add", {
          method: "POST",
          body: JSON.stringify({ source_path: currentDirectoryPath || "/" }),
        });
        await refreshStatus();
        setNotice("dir-notice", `已加入队列: ${currentDirectoryPath}`);
      }));
      bindClick("add-leaf-queue", withBusy("add-leaf-queue", "扫描中...", async () => {
        const result = await call("/api/queue/add_leaf_units", {
          method: "POST",
          body: JSON.stringify({ source_path: currentDirectoryPath || "/" }),
        });
        await refreshStatus();
        setNotice("dir-notice", `已加入 ${result.added || 0} 个最底层目录。`);
      }));
      bindClick("run-leaf-direct", withBusy("run-leaf-direct", "启动中...", async () => {
        await saveConfig();
        await call("/api/leaf/run_stream", {
          method: "POST",
          body: JSON.stringify({ source_path: currentDirectoryPath || "/" }),
        });
        setNotice("dir-notice", `已开始最底层目录边扫边秒传: ${currentDirectoryPath}`);
        await refreshStatus();
      }));
      bindClick("run-leaf-full", withBusy("run-leaf-full", "启动中...", async () => {
        await saveConfig();
        await call("/api/leaf/run_stream_full", {
          method: "POST",
          body: JSON.stringify({ source_path: currentDirectoryPath || "/" }),
        });
        setNotice("dir-notice", `已开始最底层目录边扫边同步+补传: ${currentDirectoryPath}`);
        await refreshStatus();
      }));

      bindClick("run-dry", withBusy("run-dry", "启动中...", () => runSyncMode("dry_run")));
      bindClick("run-direct", withBusy("run-direct", "启动中...", () => runSyncMode("direct")));
      bindClick("run-next-queue", withBusy("run-next-queue", "启动中...", async () => {
        await saveConfig();
        const result = await call("/api/queue/run_next", { method: "POST" });
        setNotice("sync-notice", `开始执行队列目录: ${result.source_path || "-"}`);
        await refreshStatus();
      }));
      bindClick("run-all-queue", withBusy("run-all-queue", "启动中...", async () => {
        await saveConfig();
        await call("/api/queue/run_all", { method: "POST" });
        setNotice("sync-notice", "已开始连续执行整个队列。");
        await refreshStatus();
      }));

      bindClick("pending-select-all", () => {
        for (const item of latestPendingItems) {
          if (item?.path) pendingSelection.add(item.path);
        }
        pendingSelectionTouched = true;
        renderPendingTree(latestPendingItems);
      });
      bindClick("pending-clear-all", () => {
        pendingSelection.clear();
        pendingSelectionTouched = true;
        renderPendingTree(latestPendingItems);
      });
      bindClick("pending-run-selected", withBusy("pending-run-selected", "启动中...", async () => {
        await saveConfig();
        await call("/api/sync/start", {
          method: "POST",
          body: JSON.stringify({ mode: "download_selected", selected_paths: [...pendingSelection] }),
        });
        setNotice("sync-notice", `已开始补传 ${pendingSelection.size} 个文件。`);
        await refreshStatus();
      }));
      bindClick("pending-run-stream", withBusy("pending-run-stream", "启动中...", async () => {
        await saveConfig();
        await call("/api/pending/run_selected_stream", {
          method: "POST",
          body: JSON.stringify({ selected_paths: [...pendingSelection] }),
        });
        setNotice("sync-notice", "已开始按勾选目录最底层顺序补传。");
        await refreshStatus();
      }));

      bindClick("diagnose-miaochuan", withBusy("diagnose-miaochuan", "诊断中...", async () => {
        await diagnoseMiaochuanPayload();
      }));
      bindClick("run-miaochuan", withBusy("run-miaochuan", "提交中...", async () => {
        await saveConfig();
        await call("/api/miaochuan/import", {
          method: "POST",
          body: JSON.stringify({
            target_key: activeTargetKey(),
            miaochuan_payload: document.getElementById("miaochuan_payload").value,
            guangya_authorization: document.getElementById("guangya_authorization").value,
          }),
        });
        setNotice("miaochuan-notice", "已开始执行秒传 JSON 直导。");
        await refreshStatus();
      }));

      bindClick("refresh-storages", withBusy("refresh-storages", "刷新中...", refreshStorages));
      bindClick("refresh-drivers", withBusy("refresh-drivers", "刷新中...", loadDrivers));
      bindChange("driver-select", async (event) => {
        await loadDriverInfo(event.target.value);
      });
      bindClick("show-driver-guide", () => toggleDriverGuideDialog(true));
      bindClick("show-provider-guide", () => {
        const select = document.getElementById("provider-select");
        const definition = [...providerDefinitions, ...(driverCaptureBlueprint ? [driverCaptureBlueprint] : [])]
          .find((item) => item.key === select?.value);
        currentProviderGuide = getGuideForProviderDefinition(definition);
        const title = definition?.label
          ? `${definition.label} ${currentLang() === "en" ? "Guide" : currentLang() === "mix" ? "接入流程 / Guide" : "接入流程"}`
          : (currentLang() === "en" ? "Provider Access Guide" : currentLang() === "mix" ? "网盘接入流程 / Provider Access Guide" : "网盘接入流程");
        renderGuideIntoDialog(currentProviderGuide, title);
        toggleDriverGuideDialog(true);
      });
      bindClick("close-driver-guide", () => toggleDriverGuideDialog(false));
      bindEvent("driver-guide-dialog", "click", (event) => {
        if (event.target?.id === "driver-guide-dialog") toggleDriverGuideDialog(false);
      });
      bindChange("coverage-only-gaps", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      bindChange("coverage-only-onboarding-ready", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      bindChange("coverage-next-action-filter", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      bindChange("coverage-missing-item-filter", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      bindChange("coverage-capability-level-filter", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      bindChange("coverage-profile-key-filter", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      bindChange("coverage-onboarding-stage-filter", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      bindClick("export-coverage-json", async () => {
        await refreshCoverageAudit();
        if (!coverageAuditCache) return;
        downloadTextFile("cloudpan-bridge-coverage-audit.json", JSON.stringify(coverageAuditCache, null, 2), "application/json;charset=utf-8");
      });
      bindClick("export-coverage-md", async () => {
        const filters = currentCoverageFilters();
        const markdown = await call("/api/provider/coverage_audit_markdown", {
          method: "POST",
          body: JSON.stringify(buildCoverageAuditPayload(filters)),
          headers: { "content-type": "application/json" },
        });
        downloadTextFile("cloudpan-bridge-coverage-audit.md", markdown, "text/markdown;charset=utf-8");
      });
      bindClick("export-coverage-scaffold", async () => {
        const filters = currentCoverageFilters();
        const scaffold = await call("/api/provider/coverage_scaffold", {
          method: "POST",
          body: JSON.stringify(buildCoverageAuditPayload(filters)),
        });
        downloadTextFile("cloudpan-bridge-coverage-scaffold.json", JSON.stringify(scaffold, null, 2), "application/json;charset=utf-8");
      });
      bindClick("export-coverage-scaffold-md", async () => {
        const filters = currentCoverageFilters();
        const markdown = await call("/api/provider/coverage_scaffold_markdown", {
          method: "POST",
          body: JSON.stringify(buildCoverageAuditPayload(filters)),
          headers: { "content-type": "application/json" },
        });
        downloadTextFile("cloudpan-bridge-coverage-scaffold.md", markdown, "text/markdown;charset=utf-8");
      });
      bindClick("open-driver-doc", () => {
        const candidates = guideDocCandidates(currentDriverGuide);
        if (candidates.length) window.open(candidates[0], "_blank", "noopener,noreferrer");
      });
      bindClick("apply-driver-defaults", () => applyDriverGuideDefaults());
      bindClick("apply-driver-defaults-dialog", () => applyDriverGuideDefaults());
      bindClick("start-provider-capture", withBusy("start-provider-capture", "抓取中...", async () => {
        const provider = document.getElementById("provider-select").value;
        const loginUrl = document.getElementById("provider-login-url").value;
        const definition = [...providerDefinitions, ...(driverCaptureBlueprint ? [driverCaptureBlueprint] : [])].find((item) => item.key === provider);
        const captureMode = String(definition?.capture_mode || "browser");
        await call("/api/provider/capture/start", {
          method: "POST",
          body: JSON.stringify({
            provider,
            driver: document.getElementById("driver-select").value,
            login_url: loginUrl,
          }),
        });
        if (captureMode === "manual") {
          if (loginUrl) window.open(loginUrl, "_blank", "noopener,noreferrer");
          setNotice("driver-notice", currentLang() === "en"
            ? `This provider uses manual credentials. Opened the guide link if available; fill the required fields manually in the mount form.`
            : currentLang() === "mix"
              ? `该来源使用手动凭证模式，已尝试打开说明链接，请按要求手动填写挂载字段。 / Manual credential mode.`
              : `该来源使用手动凭证模式，已尝试打开说明链接，请按要求手动填写挂载字段。`);
        } else {
          setNotice("driver-notice", currentLang() === "en"
            ? `Opened login capture for ${provider}. Finish login in the browser window, then return here.`
            : currentLang() === "mix"
              ? `已打开 ${provider} 登录抓取窗口 / Finish login in the browser window, then return here.`
              : `已打开 ${provider} 登录抓取窗口，请在浏览器里完成登录后回到这里。`);
        }
        await refreshStatus();
      }));
      bindClick("apply-provider-fields", withBusy("apply-provider-fields", "回填中...", async () => {
        await applyCapturedProviderFields();
      }));
      bindClick("create-storage", withBusy("create-storage", "创建中...", async () => {
        const values = {};
        document.querySelectorAll("[data-driver-field]").forEach((el) => {
          values[el.getAttribute("data-driver-field")] = el.value;
        });
        await call("/api/openlist/storage/create", {
          method: "POST",
          body: JSON.stringify({
            driver: document.getElementById("driver-select").value,
            values,
          }),
        });
        await refreshStorages();
        setNotice("driver-notice", "挂载已创建。");
      }));

      bindClick("provider-quick-picks", (event) => {
        const target = event.target?.closest?.("[data-provider-quick]");
        if (!target) return;
        const nextProvider = String(target.getAttribute("data-provider-quick") || "");
        const select = document.getElementById("provider-select");
        if (!select || !nextProvider) return;
        select.value = nextProvider;
        renderProviderCapturePanel();
        renderProviderQuickPicks();
      });
      bindClick("target-quick-picks", async (event) => {
        const target = event.target?.closest?.("[data-target-quick]");
        if (!target) return;
        const nextTarget = String(target.getAttribute("data-target-quick") || "");
        if (!nextTarget) return;
        await handleTargetChange(nextTarget);
      });
      bindClick("clear-logs", withBusy("clear-logs", "清理中...", async () => {
        await call("/api/logs/clear", { method: "POST" });
        await refreshStatus();
      }));
    }

    async function bootstrap() {
      initTabs();
      initializeMirroredInputs();
      bindEvents();
      try {
        applyI18n();
      } catch (error) {
        console.error("applyI18n failed during bootstrap", error);
        document.getElementById("logs").textContent = `界面翻译初始化失败: ${error.message}`;
      }
      const panelState = getPanelState();
      toggleDrawer(panelState.logsVisible !== false);
      await ensureAuthorizedAndBootstrap(true);
    }

    bootstrap().catch((error) => {
      document.getElementById("logs").textContent = `初始化失败: ${error.message}`;
    });
  
