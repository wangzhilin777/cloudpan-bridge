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
    let configCache = {};
    let providerRegistryPayload = null;
    let driverGuideRegistry = {};
    let capabilityAssessmentCache = null;
    let coverageAuditCache = null;
    let targetPreflightCache = null;
    let driverCaptureBlueprint = null;
    let providerDefinitions = [];
    let providerSnapshots = {};
    let storageRecords = [];
    let sourceAnalyzeCache = null;
    let latestPendingItems = [];
    let pendingSelection = new Set();
    let pendingSelectionTouched = false;
    let currentDirectoryPath = "/";
    let currentParentPath = null;
    let authState = { enabled: false, authenticated: true, username: "" };
    let appBootstrapped = false;
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
      if (notice) notice.textContent = message || "等待登录。";
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
        pending: state.connectionReady && state.targetConfigured,
        miaochuan: state.connectionReady && state.targetConfigured && state.guangyaMiaochuanReady,
        about: true,
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
          else if (tabId === "pending" || tabId === "miaochuan") tab.title = currentLang() === "en" ? "Complete target configuration first." : currentLang() === "mix" ? "请先完成目标端配置。 / Complete target configuration first." : "请先完成目标端配置。";
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
          ? (currentLang() === "en" ? "Console auth disabled" : currentLang() === "mix" ? "控制台未加锁 / Console auth disabled" : "控制台未加锁")
          : authState.authenticated
            ? (currentLang() === "en" ? `Logged in as ${authState.username || "admin"}` : currentLang() === "mix" ? `已登录 / ${authState.username || "admin"}` : `已登录: ${authState.username || "admin"}`)
            : (currentLang() === "en" ? "Login required" : currentLang() === "mix" ? "需要登录 / Login required" : "需要登录");
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
        await loadProviderRegistry();
        await refreshStorages();
        await ensureDirectoryBrowserReady(true);
        await refreshStatus();
        startAutoRefresher();
        appBootstrapped = true;
      } else {
        applyWorkflowGates();
      }
      return true;
    }

    function normalizeTabId(tabId) {
      if (tabId === "sync") return "task";
      return tabId || "overview";
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
          if (["BUTTON", "LABEL", "H2", "H3", "SPAN", "DIV"].includes(el.tagName)) {
            el.style.cursor = "help";
          }
        } else {
          el.removeAttribute("title");
        }
      });
    }

    function applyI18n() {
      document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (!key) return;
        if (el.classList.contains("subtle")) el.innerHTML = t(key);
        else el.textContent = t(key);
      });
      document.querySelectorAll("[data-i18n-option]").forEach((el) => {
        const key = el.getAttribute("data-i18n-option");
        if (key) el.textContent = t(key);
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
      }
      applyHelpTips();
      renderTargetSpecificControls();
      renderCapabilitySummary();
      renderAboutRegistry();
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

    function setNotice(id, message) {
      const el = document.getElementById(id);
      if (el) el.textContent = message;
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
      return String(document.getElementById("target_key")?.value || providerRegistryPayload?.active_target || "guangya");
    }

    async function loadProviderRegistry() {
      const data = await call("/api/provider/registry");
      providerRegistryPayload = data || providerRegistryPayload;
      driverGuideRegistry = data?.guides || {};
      populateTargetOptions();
      populateSourceProfileOverrideOptions();
      populateCoverageFilterOptions();
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

    async function refreshTargetPreflight() {
      const root = document.getElementById("target-preflight-notice");
      if (!root) return;
      try {
        const payload = await call(`/api/target/preflight?target=${encodeURIComponent(activeTargetKey())}`);
        targetPreflightCache = payload || null;
        const implemented = payload?.implemented ? "true" : "false";
        const selectable = payload?.selectable ? "true" : "false";
        const configured = payload?.configured ? "true" : "false";
        const capability = payload?.adapter_capability || {};
        const missingFields = Array.isArray(payload?.missing_fields) ? payload.missing_fields : [];
        root.innerHTML = `
          <div class="mono">target=${escapeHtml(payload?.target_key || "-")} | implemented=${implemented} | selectable=${selectable} | configured=${configured}</div>
          <div class="mono">fast_upload=${capability?.supports_fast_upload ? "true" : "false"} | hashes=${escapeHtml((capability?.fast_upload_hashes || []).join(", ") || "-")} | fallback=${escapeHtml((capability?.fallback_modes || []).join(", ") || "-")}</div>
          <div class="mono">write_mode=${escapeHtml(capability?.write_mode || "-")} | auto_create_dir=${capability?.auto_create_dir ? "true" : "false"} | supports_delete=${capability?.supports_delete ? "true" : "false"}</div>
          <div class="mono">missing=${escapeHtml(missingFields.join(", ") || "-")}</div>
          <div>${escapeHtml(payload?.message || "")}</div>
        `;
      } catch (error) {
        targetPreflightCache = null;
        root.textContent = currentLang() === "en"
          ? `Target preflight failed: ${error.message}`
          : currentLang() === "mix"
            ? `目标端预检失败 / Target preflight failed: ${error.message}`
            : `目标端预检失败: ${error.message}`;
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

    function strategyModeText(mode) {
      const mapping = {
        analyze_first: {
          zh: "先分析再决定",
          en: "Analyze first",
        },
        direct_metadata_first: {
          zh: "优先直接秒传/元数据导入",
          en: "Direct metadata-first sync",
        },
        leaf_metadata_then_pending: {
          zh: "最底层边扫边秒传，再进待补传树",
          en: "Leaf sync first, pending tree next",
        },
        stream_relay_first: {
          zh: "优先中转流传输",
          en: "Relay streaming first",
        },
        pending_tree_first: {
          zh: "优先待补传树分目录补传",
          en: "Pending-tree-first reupload",
        },
        manual_verify_first: {
          zh: "先人工核对能力与登录态",
          en: "Manual verification first",
        },
      };
      const text = mapping[String(mode || "").toLowerCase()] || mapping.analyze_first;
      return currentLang() === "en" ? text.en : currentLang() === "mix" ? `${text.zh} / ${text.en}` : text.zh;
    }

    function coverageNextActionText(action) {
      const mapping = {
        add_profile_first: { zh: "先补 source profile", en: "Add source profile first" },
        add_guide: { zh: "补接入流程说明", en: "Add setup guide" },
        add_capture_spec: { zh: "补登录抓取定义", en: "Add capture spec" },
        assess_target_capability: { zh: "补目标能力判断", en: "Assess target capability" },
        covered: { zh: "当前已覆盖", en: "Already covered" },
      };
      const text = mapping[String(action || "").toLowerCase()] || mapping.add_profile_first;
      return currentLang() === "en" ? text.en : currentLang() === "mix" ? `${text.zh} / ${text.en}` : text.zh;
    }

    function strategyQuickActions(mode, strategy) {
      const actions = [];
      const isGuangya = activeTargetKey() === "guangya";
      const push = (key, labelZh, labelEn) => actions.push({
        key,
        label: currentLang() === "en" ? labelEn : currentLang() === "mix" ? `${labelZh} / ${labelEn}` : labelZh,
      });
      if (strategy?.shouldAnalyzeFirst) push("analyze", "先分析当前目录", "Analyze current directory");
      if (mode === "direct_metadata_first") {
        if (isGuangya) push("to-miaochuan", "去秒传页", "Open flash-upload tab");
        else push("to-execute", "去执行页", "Open execution tab");
        push("run-direct", "直接同步当前目录", "Run direct sync");
      } else if (mode === "leaf_metadata_then_pending") {
        push("run-leaf-direct", "最底层边扫边秒传", "Run leaf scan sync");
        push("to-pending", "查看待补传树", "Open pending tree");
      } else if (mode === "pending_tree_first") {
        push("to-pending", "去补传页", "Open pending tab");
        push("run-leaf-full", "最底层边扫边同步+补传", "Run leaf sync with fallback");
      } else if (mode === "stream_relay_first") {
        push("to-execute", "去执行页", "Open execution tab");
        push("run-direct", "直接同步当前目录", "Run direct sync");
      } else if (mode === "manual_verify_first") {
        push("to-mounts", "去挂载与驱动说明", "Open mounts and guides");
        push("to-about", "查看能力矩阵说明", "Open capability reference");
      }
      return actions;
    }

    function performCapabilityQuickAction(actionKey) {
      const actions = {
        analyze: () => {
          activateTab("source");
          document.getElementById("analyze-source")?.click();
        },
        "to-miaochuan": () => activateTab("miaochuan"),
        "to-pending": () => activateTab("pending"),
        "to-task": () => activateTab("task"),
        "to-execute": () => activateTab("execute"),
        "to-mounts": () => activateTab("mounts"),
        "to-about": () => activateTab("about"),
        "run-direct": () => {
          activateTab("execute");
          document.getElementById("run-direct")?.click();
        },
        "run-leaf-direct": () => {
          activateTab("execute");
          document.getElementById("run-leaf-direct")?.click();
        },
        "run-leaf-full": () => {
          activateTab("execute");
          document.getElementById("run-leaf-full")?.click();
        },
      };
      actions[actionKey]?.();
    }

    function renderCapabilitySummary() {
      const root = document.getElementById("capability-summary");
      const quickActionsRoot = document.getElementById("capability-quick-actions");
      if (!root || !quickActionsRoot) return;
      const context = currentDriverContext();
      const normalized = normalizeDriverKey(context.driver || "");
      const matrix = providerRegistryPayload?.driver_matrix || {};
      const capability = matrix[normalized] || null;
      const assessment = capabilityAssessmentCache && normalizeDriverKey(capabilityAssessmentCache.driver || "") === normalized
        ? capabilityAssessmentCache
        : null;
      if (!capability) {
        quickActionsRoot.innerHTML = "";
        root.innerHTML = currentLang() === "en"
          ? "No capability matrix matched for the current driver yet. Treat it conservatively and verify hash availability first."
          : currentLang() === "mix"
            ? "当前驱动暂未命中内置能力矩阵，建议按保守模式处理，先验证哈希可用性。 / Treat it conservatively first."
            : "当前驱动暂未命中内置能力矩阵，建议按保守模式处理，先验证哈希可用性。";
        return;
      }
      const sourceProfile = capability.sourceProfile || {};
      const targetProfile = capability.targetProfile || {};
      const notes = capability.notes || {};
      const assessedLevel = assessment?.assessedLevel || capability.level;
      const sourceMappingContext = assessment?.sourceMappingContext || providerRegistryPayload?.current_source_context || {};
      const rationale = assessment?.rationale || {};
      const strategy = assessment?.strategy || {};
      const likelyHashes = Array.isArray(sourceProfile.likelyHashes) ? sourceProfile.likelyHashes : [];
      const analysisSummary = sourceAnalyzeCache?.summary || {};
      const analysisLine = sourceAnalyzeCache
        ? `${currentLang() === "en" ? "Current analysis" : currentLang() === "mix" ? "当前分析 / Current analysis" : "当前分析"}: MD5=${analysisSummary.md5_ready ?? 0}, GCID=${analysisSummary.gcid_ready ?? 0}, ${currentLang() === "en" ? "Fast fingerprints" : currentLang() === "mix" ? "可快传指纹 / Fast fingerprints" : "可快传指纹"}=${analysisSummary.fast_upload_ready ?? 0}/${analysisSummary.total ?? 0}`
        : `${currentLang() === "en" ? "Current analysis" : currentLang() === "mix" ? "当前分析 / Current analysis" : "当前分析"}: ${currentLang() === "en" ? "not run yet" : currentLang() === "mix" ? "尚未运行 / not run yet" : "尚未运行"}`;
      const recommendedFlow = currentLang() === "en"
        ? (capability.recommendedFlowEn || capability.recommendedFlow || "")
        : currentLang() === "mix"
          ? `${capability.recommendedFlow || ""} / ${capability.recommendedFlowEn || ""}`.trim()
          : (capability.recommendedFlow || "");
      const notesText = currentLang() === "en"
        ? (notes.en || "")
        : currentLang() === "mix"
          ? `${notes.zh || ""} / ${notes.en || ""}`.trim()
          : (notes.zh || "");
      const rationaleText = currentLang() === "en"
        ? (rationale.en || "")
        : currentLang() === "mix"
          ? `${rationale.zh || ""} / ${rationale.en || ""}`.trim()
          : (rationale.zh || "");
      const throttleHintText = currentLang() === "en"
        ? (strategy?.throttleHint?.en || "")
        : currentLang() === "mix"
          ? `${strategy?.throttleHint?.zh || ""} / ${strategy?.throttleHint?.en || ""}`.trim()
          : (strategy?.throttleHint?.zh || "");
      const suggestedActions = Array.isArray(strategy?.suggestedActions) ? strategy.suggestedActions : [];
      const supportsFingerprintEnrichment = !!sourceProfile.supportsFingerprintEnrichment;
      const suggestedText = suggestedActions.length
        ? suggestedActions.map((item, index) => {
            const text = currentLang() === "en"
              ? (item?.en || "")
              : currentLang() === "mix"
                ? `${item?.zh || ""} / ${item?.en || ""}`.trim()
                : (item?.zh || "");
            return `${index + 1}. ${text}`;
          }).join("<br>")
        : "-";
      const executionFlags = [
        `${currentLang() === "en" ? "Analyze first" : currentLang() === "mix" ? "先分析 / Analyze first" : "先分析"}=${strategy?.shouldAnalyzeFirst ? "yes" : "no"}`,
        `${currentLang() === "en" ? "Prefer leaf mode" : currentLang() === "mix" ? "叶子目录优先 / Prefer leaf mode" : "叶子目录优先"}=${strategy?.preferLeafMode ? "yes" : "no"}`,
        `${currentLang() === "en" ? "Prefer pending tree" : currentLang() === "mix" ? "待补传树优先 / Prefer pending tree" : "待补传树优先"}=${strategy?.preferPendingTree ? "yes" : "no"}`,
      ].join(" | ");
      const quickActions = strategyQuickActions(strategy?.recommendedMode || "analyze_first", strategy);
      quickActionsRoot.innerHTML = quickActions.map((item) => (
        `<button class="secondary" type="button" data-capability-action="${escapeHtml(item.key)}">${escapeHtml(item.label)}</button>`
      )).join("");
      root.innerHTML = `
        <div><strong>${escapeHtml(context.driver || "-")}</strong> -> <strong>${escapeHtml(targetProfile.labelZh || targetProfile.label || "Guangya")}</strong></div>
        <div class="mono">${currentLang() === "en" ? "Source mapping" : currentLang() === "mix" ? "源映射 / Source mapping" : "源映射"}: requested=${escapeHtml(sourceMappingContext.requested_driver || context.mountedDriver || context.driver || "-")} | override=${escapeHtml(sourceMappingContext.source_profile_override || context.overrideProfile || "-")} | effective=${escapeHtml(sourceMappingContext.effective_driver || context.driver || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Capability level" : currentLang() === "mix" ? "静态等级 / Capability level" : "静态等级"}: ${escapeHtml(capabilityLevelText(capability.level))}</div>
        <div class="mono">${currentLang() === "en" ? "Runtime assessment" : currentLang() === "mix" ? "动态判断 / Runtime assessment" : "动态判断"}: ${escapeHtml(capabilityLevelText(assessedLevel))}</div>
        <div class="mono">${currentLang() === "en" ? "Execution mode" : currentLang() === "mix" ? "执行模式 / Execution mode" : "执行模式"}: ${escapeHtml(strategyModeText(strategy?.recommendedMode || "analyze_first"))}</div>
        <div class="mono">${currentLang() === "en" ? "Likely hashes" : currentLang() === "mix" ? "常见哈希 / Likely hashes" : "常见哈希"}: ${escapeHtml(likelyHashes.join(", ") || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Fingerprint enrichment" : currentLang() === "mix" ? "补指纹能力 / Fingerprint enrichment" : "补指纹能力"}: ${supportsFingerprintEnrichment ? (currentLang() === "en" ? "declared" : currentLang() === "mix" ? "已声明 / declared" : "已声明") : (currentLang() === "en" ? "unknown" : currentLang() === "mix" ? "未知 / unknown" : "未知")}</div>
        <div class="mono">${currentLang() === "en" ? "Recommended rate profile" : currentLang() === "mix" ? "推荐频率 / Recommended rate profile" : "推荐频率"}: ${escapeHtml(sourceProfile.recommendedRateProfile || "-")}</div>
        <div class="mono">${escapeHtml(analysisLine)}</div>
        <div class="mono">${currentLang() === "en" ? "Suggested path" : currentLang() === "mix" ? "建议路径 / Suggested path" : "建议路径"}: ${escapeHtml(recommendedFlow || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Runtime rationale" : currentLang() === "mix" ? "动态理由 / Runtime rationale" : "动态理由"}: ${escapeHtml(rationaleText || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Throttle hint" : currentLang() === "mix" ? "节奏建议 / Throttle hint" : "节奏建议"}: ${escapeHtml(throttleHintText || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Execution flags" : currentLang() === "mix" ? "执行偏好 / Execution flags" : "执行偏好"}: ${escapeHtml(executionFlags)}</div>
        <div class="mono">${currentLang() === "en" ? "Suggested actions" : currentLang() === "mix" ? "建议动作 / Suggested actions" : "建议动作"}:<br>${suggestedText}</div>
        <div class="mono">${currentLang() === "en" ? "Notes" : currentLang() === "mix" ? "说明 / Notes" : "说明"}: ${escapeHtml(notesText || "-")}</div>
      `;
    }

    function renderAboutRegistry() {
      const summaryRoot = document.getElementById("about-summary");
      const sourceRoot = document.getElementById("about-source-profiles");
      const targetRoot = document.getElementById("about-target-profiles");
      const matrixRoot = document.getElementById("about-driver-matrix");
      const coverageRoot = document.getElementById("about-coverage-audit");
      const coverageBacklogRoot = document.getElementById("about-coverage-backlog");
      const coverageActionStatsRoot = document.getElementById("about-coverage-action-stats");
      const coveragePlanRoot = document.getElementById("about-coverage-plan");
      if (!summaryRoot || !sourceRoot || !targetRoot || !matrixRoot || !coverageRoot || !coverageBacklogRoot || !coverageActionStatsRoot || !coveragePlanRoot) return;
      const sourceProfiles = Object.values(providerRegistryPayload?.source_profiles || {});
      const targetProfiles = Object.values(providerRegistryPayload?.target_profiles || {});
      const driverMatrix = Object.values(providerRegistryPayload?.driver_matrix || {});
      summaryRoot.innerHTML = `
        <div><strong>CloudPan Bridge</strong></div>
        <div class="mono">${currentLang() === "en" ? "Master plan" : currentLang() === "mix" ? "主计划 / Master plan" : "主计划"}: docs/cloudpan-bridge-master-plan.md</div>
        <div class="mono">${currentLang() === "en" ? "Research plan" : currentLang() === "mix" ? "调研计划 / Research plan" : "调研计划"}: docs/cloudpan-bridge-research-plan.md</div>
        <div class="mono">${currentLang() === "en" ? "Source profiles" : currentLang() === "mix" ? "源端 profiles / Source profiles" : "源端 profiles"}: ${sourceProfiles.length}</div>
        <div class="mono">${currentLang() === "en" ? "Target profiles" : currentLang() === "mix" ? "目标端 profiles / Target profiles" : "目标端 profiles"}: ${targetProfiles.length}</div>
        <div class="mono">${currentLang() === "en" ? "Driver matrix rows" : currentLang() === "mix" ? "矩阵条目 / Driver matrix rows" : "矩阵条目"}: ${driverMatrix.length}</div>
      `;

      if (!sourceProfiles.length) {
        sourceRoot.textContent = currentLang() === "en" ? "No source profiles loaded." : currentLang() === "mix" ? "暂无源端 profiles / No source profiles loaded." : "暂无源端 profiles";
      } else {
        sourceRoot.innerHTML = sourceProfiles.map((item) => `
          <div class="row-item">
            <div>
              <div>${escapeHtml(item.labelZh || item.label || item.key || "-")}</div>
              <div class="mono">key=${escapeHtml(item.key || "-")} | ${currentLang() === "en" ? "rate" : currentLang() === "mix" ? "频率 / rate" : "频率"}=${escapeHtml(item.recommendedRateProfile || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "login mode" : currentLang() === "mix" ? "登录模式 / login mode" : "登录模式"}=${escapeHtml(item.loginMode || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "hashes" : currentLang() === "mix" ? "哈希 / hashes" : "哈希"}=${escapeHtml((item.likelyHashes || []).join(", ") || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "supported hash fields" : currentLang() === "mix" ? "支持哈希字段 / supported hash fields" : "支持哈希字段"}=${escapeHtml((item.hashFieldsSupported || []).join(", ") || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "fingerprint enrichment" : currentLang() === "mix" ? "补指纹能力 / fingerprint enrichment" : "补指纹能力"}=${item.supportsFingerprintEnrichment ? (currentLang() === "en" ? "declared" : currentLang() === "mix" ? "已声明 / declared" : "已声明") : (currentLang() === "en" ? "unknown" : currentLang() === "mix" ? "未知 / unknown" : "未知")}</div>
              <div class="mono">${currentLang() === "en" ? "download links" : currentLang() === "mix" ? "下载链路 / download links" : "下载链路"}=${escapeHtml(item.downloadLinkSupported || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "aliases" : currentLang() === "mix" ? "驱动别名 / aliases" : "驱动别名"}=${escapeHtml((item.driverAliases || []).join(", ") || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "capture strategy" : currentLang() === "mix" ? "抓取策略 / capture strategy" : "抓取策略"}=${escapeHtml((currentLang() === "en" ? item.captureStrategyEn : currentLang() === "mix" ? `${item.captureStrategy || ""} / ${item.captureStrategyEn || ""}`.trim() : item.captureStrategy) || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "default mount values" : currentLang() === "mix" ? "默认挂载值 / default mount values" : "默认挂载值"}=${escapeHtml(JSON.stringify(item.defaultMountValues || {}))}</div>
              <div class="mono">${currentLang() === "en" ? "doc links" : currentLang() === "mix" ? "文档链接 / doc links" : "文档链接"}=${escapeHtml((item.docLinks || []).join(", ") || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "risk notes" : currentLang() === "mix" ? "风险说明 / risk notes" : "风险说明"}=${escapeHtml((currentLang() === "en" ? item.riskNotes?.en : currentLang() === "mix" ? `${item.riskNotes?.zh || ""} / ${item.riskNotes?.en || ""}`.trim() : item.riskNotes?.zh) || "-")}</div>
            </div>
          </div>
        `).join("");
      }

      if (!targetProfiles.length) {
        targetRoot.textContent = currentLang() === "en" ? "No target profiles loaded." : currentLang() === "mix" ? "暂无目标端 profiles / No target profiles loaded." : "暂无目标端 profiles";
      } else {
        const targetImplementationStatus = providerRegistryPayload?.target_implementation_status || {};
        targetRoot.innerHTML = targetProfiles.map((item) => `
          <div class="row-item">
            <div>
              <div>${escapeHtml(item.labelZh || item.label || item.key || "-")}</div>
              <div class="mono">key=${escapeHtml(item.key || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "implemented" : currentLang() === "mix" ? "已实现 / implemented" : "已实现"}=${targetImplementationStatus?.[item.key || ""]?.implemented ? "true" : "false"} | ${currentLang() === "en" ? "selectable" : currentLang() === "mix" ? "可选 / selectable" : "可选"}=${targetImplementationStatus?.[item.key || ""]?.selectable ? "true" : "false"}</div>
              <div class="mono">${currentLang() === "en" ? "auth mode" : currentLang() === "mix" ? "鉴权模式 / auth mode" : "鉴权模式"}=${escapeHtml(item.authMode || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "token refresh" : currentLang() === "mix" ? "刷新方式 / token refresh" : "刷新方式"}=${escapeHtml(item.tokenRefresh || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "auto create dir" : currentLang() === "mix" ? "自动建目录 / auto create dir" : "自动建目录"}=${item.autoCreateDir ? "true" : "false"}</div>
              <div class="mono">${currentLang() === "en" ? "fast hashes" : currentLang() === "mix" ? "快传指纹 / fast hashes" : "快传指纹"}=${escapeHtml((item.fastUploadHashes || []).join(", ") || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "fallback" : currentLang() === "mix" ? "降级方式 / fallback" : "降级方式"}=${escapeHtml((item.fallbackModes || []).join(", ") || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "research notes" : currentLang() === "mix" ? "调研备注 / research notes" : "调研备注"}=${escapeHtml((currentLang() === "en" ? item.researchNotes?.en : currentLang() === "mix" ? `${item.researchNotes?.zh || ""} / ${item.researchNotes?.en || ""}`.trim() : item.researchNotes?.zh) || "-")}</div>
            </div>
          </div>
        `).join("");
      }

      if (!driverMatrix.length) {
        matrixRoot.textContent = currentLang() === "en" ? "No matrix rows loaded." : currentLang() === "mix" ? "暂无矩阵条目 / No matrix rows loaded." : "暂无矩阵条目";
      } else {
        matrixRoot.innerHTML = driverMatrix
          .sort((a, b) => String(a.driver || "").localeCompare(String(b.driver || ""), "zh-CN"))
          .map((item) => {
            const sourceProfile = item.sourceProfile || {};
            const flow = currentLang() === "en"
              ? (item.recommendedFlowEn || item.recommendedFlow || "")
              : currentLang() === "mix"
                ? `${item.recommendedFlow || ""} / ${item.recommendedFlowEn || ""}`.trim()
                : (item.recommendedFlow || "");
            return `
              <div class="row-item">
                <div>
                  <div>${escapeHtml(item.driver || "-")}</div>
                  <div class="mono">${currentLang() === "en" ? "profile" : currentLang() === "mix" ? "profile / 档案" : "档案"}=${escapeHtml(sourceProfile.key || "-")} | ${currentLang() === "en" ? "level" : currentLang() === "mix" ? "等级 / level" : "等级"}=${escapeHtml(capabilityLevelText(item.level))}</div>
                  <div class="mono">${currentLang() === "en" ? "suggested path" : currentLang() === "mix" ? "建议路径 / suggested path" : "建议路径"}=${escapeHtml(flow || "-")}</div>
                </div>
              </div>
            `;
          }).join("");
      }

      const auditRows = Array.isArray(coverageAuditCache?.rows) ? coverageAuditCache.rows : [];
      const auditTotals = coverageAuditCache?.totals || {};
      const gapBuckets = coverageAuditCache?.gapBuckets || {};
      const backlog = Array.isArray(coverageAuditCache?.backlog) ? coverageAuditCache.backlog : [];
      const executionPlan = coverageAuditCache?.executionPlan || {};
      const filters = currentCoverageFilters();
      const filteredAuditRows = auditRows.filter((item) => {
        if (filters.onlyGaps && (!Array.isArray(item.missingItems) || !item.missingItems.length)) return false;
        if (filters.onlyOnboardingReady && !item.onboardingReady) return false;
        if (filters.nextAction && String(item.nextAction || "") !== filters.nextAction) return false;
        if (filters.missingItem && (!Array.isArray(item.missingItems) || !item.missingItems.includes(filters.missingItem))) return false;
        if (filters.capabilityLevel && String(item.capabilityLevel || "") !== filters.capabilityLevel) return false;
        if (filters.profileKey && String(item.profileKey || "") !== filters.profileKey) return false;
        if (filters.onboardingStage && String(item.onboardingStage || "") !== filters.onboardingStage) return false;
        return true;
      });
      const filteredBacklog = backlog.filter((item) => {
        if (filters.onlyGaps && (!Array.isArray(item.missingItems) || !item.missingItems.length)) return false;
        if (filters.onlyOnboardingReady && !item.onboardingReady) return false;
        if (filters.nextAction && String(item.nextAction || "") !== filters.nextAction) return false;
        if (filters.missingItem && (!Array.isArray(item.missingItems) || !item.missingItems.includes(filters.missingItem))) return false;
        if (filters.capabilityLevel && String(item.capabilityLevel || "") !== filters.capabilityLevel) return false;
        if (filters.profileKey && String(item.profileKey || "") !== filters.profileKey) return false;
        if (filters.onboardingStage && String(item.onboardingStage || "") !== filters.onboardingStage) return false;
        return true;
      });
      const planWaves = Array.isArray(executionPlan?.waves) ? executionPlan.waves.filter((item) => {
        if (filters.nextAction && String(item.nextAction || "") !== filters.nextAction) return false;
        if (filters.onboardingStage && String(item.onboardingStage || "") !== filters.onboardingStage) return false;
        if (filters.capabilityLevel && Array.isArray(item.capabilityLevels) && item.capabilityLevels.length && !item.capabilityLevels.includes(filters.capabilityLevel)) return false;
        if (filters.profileKey && Array.isArray(item.profileKeys) && item.profileKeys.length && !item.profileKeys.includes(filters.profileKey)) return false;
        if (filters.missingItem && Array.isArray(item.missingItems) && item.missingItems.length && !item.missingItems.includes(filters.missingItem)) return false;
        return true;
      }) : [];
      if (!auditRows.length) {
        coverageBacklogRoot.textContent = currentLang() === "en"
          ? "The prioritized backlog will appear after OpenList driver coverage is available."
          : currentLang() === "mix"
            ? "OpenList 驱动覆盖可用后，这里会显示优先级 backlog。 / The prioritized backlog will appear after driver coverage is available."
            : "OpenList 驱动覆盖可用后，这里会显示优先级 backlog。";
        coverageActionStatsRoot.textContent = currentLang() === "en"
          ? "The next-action stats will appear after OpenList driver coverage is available."
          : currentLang() === "mix"
            ? "OpenList 驱动覆盖可用后，这里会显示下一步动作统计。 / The next-action stats will appear after driver coverage is available."
            : "OpenList 驱动覆盖可用后，这里会显示下一步动作统计。";
        coverageRoot.textContent = currentLang() === "en"
          ? "Coverage audit will appear after OpenList driver coverage is available."
          : currentLang() === "mix"
            ? "OpenList 驱动覆盖可用后，这里会显示覆盖审计结果。 / Coverage audit will appear after driver coverage is available."
            : "OpenList 驱动覆盖可用后，这里会显示覆盖审计结果。";
        coveragePlanRoot.textContent = currentLang() === "en"
          ? "Execution waves will appear after OpenList driver coverage is available."
          : currentLang() === "mix"
            ? "OpenList 驱动覆盖可用后，这里会显示执行波次建议。 / Execution waves will appear after driver coverage is available."
            : "OpenList 驱动覆盖可用后，这里会显示执行波次建议。";
      } else {
        const actionCounts = filteredAuditRows.reduce((acc, item) => {
          const key = String(item.nextAction || "unknown");
          acc[key] = (acc[key] || 0) + 1;
          return acc;
        }, {});
        coverageBacklogRoot.innerHTML = filteredBacklog.length
          ? filteredBacklog.slice(0, 12).map((item, index) => `
              <div class="mono">${index + 1}. ${escapeHtml(item.driver || "-")} | P${item.priorityRank ?? "-"} | ${escapeHtml(coverageNextActionText(item.nextAction || ""))} | ${escapeHtml((item.missingItems || []).join(", ") || "-")}</div>
            `).join("")
          : (currentLang() === "en"
            ? "No backlog items match the current filter."
            : currentLang() === "mix"
              ? "当前筛选条件下没有 backlog 项。 / No backlog items match the current filter."
              : "当前筛选条件下没有 backlog 项。");
        coverageActionStatsRoot.innerHTML = Object.keys(actionCounts).length
          ? Object.entries(actionCounts).map(([key, count]) => (
              `<div class="mono">${escapeHtml(coverageNextActionText(key))}: ${count}</div>`
            )).join("")
          : (currentLang() === "en"
            ? "No next-action stats match the current filter."
            : currentLang() === "mix"
              ? "当前筛选条件下没有下一步动作统计。 / No next-action stats match the current filter."
              : "当前筛选条件下没有下一步动作统计。");
        coveragePlanRoot.innerHTML = planWaves.length
          ? planWaves.map((wave, index) => `
              <div class="mono">${index + 1}. P${wave.priorityRank ?? "-"} | ${escapeHtml(coverageNextActionText(wave.nextAction || ""))} | ${escapeHtml(wave.onboardingStage || "-")} | ${currentLang() === "en" ? "count" : currentLang() === "mix" ? "数量 / count" : "数量"}=${wave.count ?? 0}</div>
              <div class="mono">${currentLang() === "en" ? "drivers" : currentLang() === "mix" ? "驱动 / drivers" : "驱动"}=${escapeHtml((wave.drivers || []).join(", ") || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "missing items" : currentLang() === "mix" ? "缺口 / missing items" : "缺口"}=${escapeHtml((wave.missingItems || []).join(", ") || "-")}</div>
              <div class="mono">${currentLang() === "en" ? "profiles" : currentLang() === "mix" ? "profiles / 档案" : "档案"}=${escapeHtml((wave.profileKeys || []).join(", ") || "-")}</div>
            `).join("")
          : (currentLang() === "en"
            ? "No execution waves match the current filter."
            : currentLang() === "mix"
              ? "当前筛选条件下没有执行波次建议。 / No execution waves match the current filter."
              : "当前筛选条件下没有执行波次建议。");
        coverageRoot.innerHTML = `
          <div class="subtle" style="margin-bottom:10px;">
            ${currentLang() === "en"
              ? `Total=${auditTotals.total ?? 0}, profile=${auditTotals.profile ?? 0}, guide=${auditTotals.guide ?? 0}, capture=${auditTotals.capture ?? 0}, capability=${auditTotals.capability ?? 0}`
              : currentLang() === "mix"
                ? `总数 / Total=${auditTotals.total ?? 0}, profile=${auditTotals.profile ?? 0}, guide=${auditTotals.guide ?? 0}, capture=${auditTotals.capture ?? 0}, capability=${auditTotals.capability ?? 0}`
                : `总数=${auditTotals.total ?? 0}，profile=${auditTotals.profile ?? 0}，guide=${auditTotals.guide ?? 0}，capture=${auditTotals.capture ?? 0}，capability=${auditTotals.capability ?? 0}`}
          </div>
          <div class="subtle" style="margin-bottom:10px;">
            ${currentLang() === "en"
              ? `fully covered=${gapBuckets.fullyCovered ?? 0}, missing profile=${gapBuckets.missingProfile ?? 0}, missing guide=${gapBuckets.missingGuide ?? 0}, missing capture=${gapBuckets.missingCapture ?? 0}, missing capability=${gapBuckets.missingCapability ?? 0}`
              : currentLang() === "mix"
                ? `完全覆盖 / fully covered=${gapBuckets.fullyCovered ?? 0}, 缺 profile / missing profile=${gapBuckets.missingProfile ?? 0}, 缺 guide / missing guide=${gapBuckets.missingGuide ?? 0}, 缺 capture / missing capture=${gapBuckets.missingCapture ?? 0}, 缺 capability / missing capability=${gapBuckets.missingCapability ?? 0}`
                : `完全覆盖=${gapBuckets.fullyCovered ?? 0}，缺 profile=${gapBuckets.missingProfile ?? 0}，缺 guide=${gapBuckets.missingGuide ?? 0}，缺 capture=${gapBuckets.missingCapture ?? 0}，缺 capability=${gapBuckets.missingCapability ?? 0}`}
          </div>
          <div class="subtle" style="margin-bottom:10px;">
            ${currentLang() === "en"
              ? `Visible rows=${filteredAuditRows.length}`
              : currentLang() === "mix"
                ? `当前可见条目 / Visible rows=${filteredAuditRows.length}`
                : `当前可见条目=${filteredAuditRows.length}`}
          </div>
          ${filteredAuditRows.map((item) => `
            <div class="row-item">
              <div>
                <div>${escapeHtml(item.driver || "-")}</div>
                <div class="mono">profile=${item.hasProfile ? "yes" : "no"} | guide=${item.hasGuide ? "yes" : "no"} | capture=${item.hasCapture ? "yes" : "no"} | capability=${item.hasCapability ? "yes" : "no"}</div>
                <div class="mono">${currentLang() === "en" ? "inference" : currentLang() === "mix" ? "推断状态 / inference" : "推断状态"}=profile:${item.profileIsDynamic ? "dynamic" : "static"} | capture:${item.captureIsDynamic ? "dynamic" : "static"} | capability:${item.capabilityIsDynamic ? "dynamic" : "static"}</div>
                <div class="mono">${currentLang() === "en" ? "level" : currentLang() === "mix" ? "等级 / level" : "等级"}=${escapeHtml(capabilityLevelText(item.capabilityLevel || "unsupported"))} | score=${item.coverageScore ?? 0}/4 | P${item.priorityRank ?? "-"}</div>
                <div class="mono">onboardingReady=${item.onboardingReady ? "yes" : "no"} | onboardingStage=${escapeHtml(item.onboardingStage || "-")}</div>
                <div class="mono">canonicalDriver=${escapeHtml(item.canonicalDriverKey || "generic")} | matchedGuide=${escapeHtml(item.matchedGuideKey || "-")}</div>
                <div class="mono">profileKey=${escapeHtml(item.profileKey || "generic")}</div>
                <div class="mono">${currentLang() === "en" ? "dynamic required keys" : currentLang() === "mix" ? "动态必需键 / dynamic required keys" : "动态必需键"}=${escapeHtml((item.dynamicRequiredKeys || []).join(", ") || "-")}</div>
                <div class="mono">${currentLang() === "en" ? "dynamic matched fields" : currentLang() === "mix" ? "动态字段命中 / dynamic matched fields" : "动态字段命中"}=${escapeHtml((item.dynamicMatchedFields || []).join(", ") || "-")}</div>
                <div class="mono">guideDoc=${escapeHtml(item.guideDocUrl || "-")}</div>
                <div class="mono">captureSpec=${escapeHtml(item.captureSpecKey || "-")} | alias=${escapeHtml(item.captureMatchedAlias || "-")}</div>
                <div class="mono">captureLogin=${escapeHtml(item.captureLoginUrl || "-")}</div>
                <div class="mono">${currentLang() === "en" ? "missing items" : currentLang() === "mix" ? "缺口 / missing items" : "缺口"}=${escapeHtml((item.missingItems || []).join(", ") || "-")}</div>
                <div class="mono">${currentLang() === "en" ? "next step" : currentLang() === "mix" ? "下一步 / next step" : "下一步"}=${escapeHtml(coverageNextActionText(item.nextAction || ""))}</div>
              </div>
            </div>
          `).join("")}
        `;
      }
    }

    function getDriverGuide(driver) {
      const normalized = normalizeDriverKey(driver);
      if (driverCaptureBlueprint?.driver && normalizeDriverKey(driverCaptureBlueprint.driver) === normalized && driverCaptureBlueprint.guide) {
        return driverCaptureBlueprint.guide;
      }
      return driverGuideRegistry[normalized] || null;
    }

    function getGuideForProviderDefinition(definition) {
      if (definition?.guide) return definition.guide;
      const sourceProfile = definition?.source_profile || {};
      const aliases = Array.isArray(sourceProfile.driverAliases) ? sourceProfile.driverAliases : [];
      const recommendedDrivers = Array.isArray(definition?.recommended_drivers) ? definition.recommended_drivers : [];
      const candidates = [...recommendedDrivers, ...aliases, sourceProfile.key || "", definition?.key || ""];
      for (const item of candidates) {
        const guide = getDriverGuide(item);
        if (guide) return guide;
      }
      return null;
    }

    function guideDocCandidates(guide) {
      const list = Array.isArray(guide?.docUrlCandidates) ? guide.docUrlCandidates : [];
      const merged = [];
      if (guide?.docUrl) merged.push(guide.docUrl);
      merged.push(...list);
      return [...new Set(merged.map((item) => String(item || "").trim()).filter(Boolean))];
    }

    function renderGuideIntoDialog(guide, titleText) {
      currentDriverGuide = guide;
      const summary = document.getElementById("driver-guide-summary");
      const stepsRoot = document.getElementById("driver-guide-steps");
      const title = document.getElementById("driver-guide-title");
      const openDocButton = document.getElementById("open-driver-doc");
      const candidatesRoot = document.getElementById("driver-guide-doc-candidates");
      if (!guide) {
        const empty = currentLang() === "en"
          ? "This provider currently has no built-in special guide. You can still use the captured fields and the official docs manually."
          : currentLang() === "mix"
            ? "当前 provider 暂无内置专属流程说明，可先用抓取结果与动态字段，再手动参考官方文档。 / No built-in special guide yet."
            : "当前 provider 暂无内置专属流程说明，可先用抓取结果与动态字段，再手动参考官方文档。";
        if (summary) summary.textContent = empty;
        if (stepsRoot) stepsRoot.innerHTML = "";
        if (candidatesRoot) candidatesRoot.textContent = currentLang() === "en"
          ? "No official doc candidates yet."
          : currentLang() === "mix"
            ? "当前没有官方文档候选链路。 / No official doc candidates yet."
            : "当前没有官方文档候选链路。";
        if (title) title.textContent = titleText || (currentLang() === "en" ? "Provider Access Guide" : currentLang() === "mix" ? "网盘接入流程 / Provider Access Guide" : "网盘接入流程");
        if (openDocButton) openDocButton.disabled = true;
        return;
      }
      const summaryText = guideTextPair(guide.summary);
      if (summary) summary.textContent = summaryText;
      if (title) title.textContent = titleText || (currentLang() === "en" ? "Provider Access Guide" : currentLang() === "mix" ? "网盘接入流程 / Provider Access Guide" : "网盘接入流程");
      const zhSteps = Array.isArray(guide.steps?.zh) ? guide.steps.zh : [];
      const enSteps = Array.isArray(guide.steps?.en) ? guide.steps.en : [];
      const steps = currentLang() === "en" ? enSteps : currentLang() === "mix" ? zhSteps.map((item, index) => `${item}\n\n${enSteps[index] || ""}`) : zhSteps;
      if (stepsRoot) {
        stepsRoot.innerHTML = steps.map((item, index) => `
          <div class="guide-step">
            <strong>${index + 1}.</strong> ${escapeHtml(item)}
          </div>
        `).join("");
      }
      const candidates = guideDocCandidates(guide);
      if (candidatesRoot) {
        candidatesRoot.innerHTML = candidates.length
          ? `
            <div style="margin-bottom:8px;">${currentLang() === "en" ? "Official doc candidates" : currentLang() === "mix" ? "官方文档候选 / Official doc candidates" : "官方文档候选"}</div>
            ${candidates.map((item, index) => `<div class="mono"><a href="${escapeHtml(item)}" target="_blank" rel="noopener noreferrer">${escapeHtml(index === 0 ? item : `${index + 1}. ${item}`)}</a></div>`).join("")}
          `
          : (currentLang() === "en"
            ? "No official doc candidates yet."
            : currentLang() === "mix"
              ? "当前没有官方文档候选链路。 / No official doc candidates yet."
              : "当前没有官方文档候选链路。");
      }
      if (openDocButton) openDocButton.disabled = !candidates.length;
    }

    function renderDriverGuide(driver) {
      const guide = getDriverGuide(driver);
      currentDriverGuide = guide;
      const inline = document.getElementById("driver-guide-inline");
      if (!guide) {
        const empty = currentLang() === "en"
          ? "This driver currently has no built-in special guide. You can still use the dynamic fields below or check the OpenList docs manually."
          : currentLang() === "mix"
            ? "当前驱动暂时没有内置专属流程说明，可先用下方动态字段，也可以手动查 OpenList 文档。 / No built-in special guide yet."
            : "当前驱动暂时没有内置专属流程说明，可先用下方动态字段，也可以手动查 OpenList 文档。";
        if (inline) inline.textContent = empty;
        renderGuideIntoDialog(null, currentLang() === "en" ? "Driver Access Guide" : currentLang() === "mix" ? "驱动接入流程 / Driver Access Guide" : "驱动接入流程");
        return;
      }
      const summaryText = guideTextPair(guide.summary);
      if (inline) {
        inline.innerHTML = `
          <div>${escapeHtml(summaryText)}</div>
          <div class="mono">${currentLang() === "en" ? "Official doc" : currentLang() === "mix" ? "官方文档 / Official doc" : "官方文档"}: ${escapeHtml(guide.docUrl || "")}</div>
        `;
      }
      renderGuideIntoDialog(guide, `${driver} ${currentLang() === "en" ? "Guide" : currentLang() === "mix" ? "接入流程 / Guide" : "接入流程"}`);
    }

    function applyDriverGuideDefaults() {
      if (!currentDriverGuide?.defaults) {
        setNotice("driver-notice", currentLang() === "en"
          ? "No built-in recommended defaults for this driver."
          : currentLang() === "mix"
            ? "当前驱动没有内置推荐默认值。 / No built-in recommended defaults."
            : "当前驱动没有内置推荐默认值。");
        return;
      }
      let changed = 0;
      const inputs = [...document.querySelectorAll("[data-driver-field]")];
      for (const [fieldName, value] of Object.entries(currentDriverGuide.defaults)) {
        const input = inputs.find((item) => normalizeDriverKey(item.getAttribute("data-driver-field") || "") === normalizeDriverKey(fieldName));
        if (input) {
          input.value = String(value);
          changed += 1;
        }
      }
      setNotice("driver-notice", currentLang() === "en"
        ? `Applied ${changed} recommended default values.`
        : currentLang() === "mix"
          ? `已套用 ${changed} 个推荐默认值。 / Applied ${changed} recommended defaults.`
          : `已套用 ${changed} 个推荐默认值。`);
    }

    function toggleDriverGuideDialog(visible) {
      const dialog = document.getElementById("driver-guide-dialog");
      if (!dialog) return;
      dialog.classList.toggle("hidden", !visible);
    }

    function chooseRatePreset(driver, mode) {
      const normalizedDriver = String(driver || "").toLowerCase();
      if (mode === "custom") return null;
      for (const [key, preset] of Object.entries(RATE_PRESETS)) {
        if (key === "default" || key === "safe" || key === "balanced" || key === "fast") continue;
        if (normalizedDriver.includes(key)) return preset;
      }
      return RATE_PRESETS[mode] || RATE_PRESETS.default;
    }

    function inferProviderFromDriver(driver) {
      const text = String(driver || "").toLowerCase();
      const fromDefinitions = (providerDefinitions || []).find((item) => {
        const list = Array.isArray(item?.recommended_drivers) ? item.recommended_drivers : [];
        return list.some((name) => String(name || "").toLowerCase() === text);
      });
      if (fromDefinitions?.key) return fromDefinitions.key;
      if (!text) return "189cloud";
      if (text.includes("quark")) return "quark";
      if (text.includes("123")) return "123pan";
      if (text.includes("baidu")) return "baidu";
      if (text.includes("thunder") || text.includes("xunlei")) return "thunder";
      if (text.includes("189")) return "189cloud";
      if (text.includes("aliyun") || text.includes("alipan")) return "aliyundriveopen";
      if (text.includes("onedrive")) return "onedrive";
      if (text.includes("pikpak")) return "pikpak";
      if (text.includes("139")) return "139yun";
      if (text.includes("guangya")) return "guangya";
      if (driverCaptureBlueprint?.key) return driverCaptureBlueprint.key;
      return "189cloud";
    }

    function maskValue(value) {
      const text = String(value || "");
      if (!text) return "";
      if (text.length <= 12) return `${text.slice(0, 2)}***${text.slice(-2)}`;
      return `${text.slice(0, 6)}***${text.slice(-4)}`;
    }

    function fieldStatus(value) {
      if (value) return currentLang() === "en" ? "captured" : currentLang() === "mix" ? "已抓取 / captured" : "已抓取";
      return currentLang() === "en" ? "missing" : currentLang() === "mix" ? "未抓取 / missing" : "未抓取";
    }

    function normalizeProviderFieldValue(fieldName, captured, provider) {
      const key = String(fieldName || "").toLowerCase();
      const data = captured || {};
      if (key.includes("cookie")) return data.cookie_header || "";
      if (key.includes("bdstoken")) return data.bdstoken || "";
      if (key.includes("refresh")) return data.refresh_token || "";
      if (key.includes("access") || key.endsWith("token")) return data.access_token || data.token || "";
      if (key.includes("auth")) return data.authorization || "";
      if (key.includes("device") || key === "did") return data.device_id || data.did || "";
      if (key === "dt") return data.dt || "";
      if (key.includes("captcha")) return data.captcha_token || "";
      if (key.includes("client")) return data.client_id || "";
      if (key.includes("session")) return data.session_key || "";
      if (provider === "quark" && key.includes("cookie")) return data.cookie_header || "";
      return "";
    }

    function renderProviderOptions(definitions) {
      const select = document.getElementById("provider-select");
      if (!select) return;
      const items = [...(Array.isArray(definitions) ? definitions : [])];
      if (driverCaptureBlueprint?.key && !items.some((item) => item.key === driverCaptureBlueprint.key)) {
        items.push(driverCaptureBlueprint);
      }
      if (!items.length) {
        select.innerHTML = `<option value="">${currentLang() === "en" ? "No providers" : currentLang() === "mix" ? "暂无 provider / No providers" : "暂无 provider"}</option>`;
        return;
      }
      const current = select.value || inferProviderFromDriver(document.getElementById("driver-select")?.value || "");
      select.innerHTML = items.map((item) => {
        const selected = item.key === current ? "selected" : "";
        return `<option value="${escapeHtml(item.key)}" ${selected}>${escapeHtml(item.label)}</option>`;
      }).join("");
    }

    function renderProviderCapturePanel() {
      const select = document.getElementById("provider-select");
      if (!select) return;
      const items = [...providerDefinitions];
      if (driverCaptureBlueprint?.key && !items.some((item) => item.key === driverCaptureBlueprint.key)) {
        items.push(driverCaptureBlueprint);
      }
      const provider = select.value || items[0]?.key || "189cloud";
      const definition = items.find((item) => item.key === provider);
      currentProviderGuide = getGuideForProviderDefinition(definition);
      const snapshot = providerSnapshots?.[provider] || {};
      const captured = snapshot.captured || {};
      const captureMode = String(definition?.capture_mode || "browser");
      const requiredKeys = Array.isArray(definition?.required_keys) ? definition.required_keys : [];
      const recommended = Array.isArray(definition?.recommended_drivers) && definition.recommended_drivers.length
        ? definition.recommended_drivers
        : (PROVIDER_DRIVER_HINTS[provider] || []);
      const profile = definition?.source_profile || {};
      const loginModeText = currentLang() === "en"
        ? (profile.loginMode || "")
        : currentLang() === "mix"
          ? `${profile.loginMode || ""} / ${profile.loginMode || ""}`.trim()
          : (profile.loginMode || "");
      const hashText = Array.isArray(profile.hashFieldsSupported) ? profile.hashFieldsSupported.join(", ") : "";
      const docLinks = Array.isArray(profile.docLinks) ? profile.docLinks : [];
      const rateText = profile.recommendedRateProfile || "";
      const lines = requiredKeys.length
        ? requiredKeys.map((key) => `<div class="mono">${escapeHtml(key)}: ${fieldStatus(captured[key])}${captured[key] ? ` | ${escapeHtml(maskValue(captured[key]))}` : ""}</div>`).join("")
        : `<div class="mono">${currentLang() === "en" ? "No required fields declared." : currentLang() === "mix" ? "未声明必需字段 / No required fields declared." : "未声明必需字段。"}</div>`;
      document.getElementById("provider-driver-hint").innerHTML = `
        <div>${escapeHtml(definition?.description || "")}</div>
        <div class="mono">${currentLang() === "en" ? "Login URL" : currentLang() === "mix" ? "登录地址 / Login URL" : "登录地址"}: ${escapeHtml(definition?.login_url || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Recommended drivers" : currentLang() === "mix" ? "建议驱动 / Recommended drivers" : "建议驱动"}: ${escapeHtml(recommended.join(", ") || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Login mode" : currentLang() === "mix" ? "登录模式 / Login mode" : "登录模式"}: ${escapeHtml(loginModeText || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Recommended rate" : currentLang() === "mix" ? "推荐频率 / Recommended rate" : "推荐频率"}: ${escapeHtml(rateText || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Hash fields" : currentLang() === "mix" ? "哈希字段 / Hash fields" : "哈希字段"}: ${escapeHtml(hashText || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Docs" : currentLang() === "mix" ? "文档 / Docs" : "文档"}: ${docLinks.length ? docLinks.map((link) => `<a href="${escapeHtml(link)}" target="_blank" rel="noreferrer">${escapeHtml(link)}</a>`).join("<br>") : "-"}</div>
        <div class="mono">${currentLang() === "en" ? "Built-in guide" : currentLang() === "mix" ? "内置流程说明 / Built-in guide" : "内置流程说明"}: ${currentProviderGuide ? (currentLang() === "en" ? "available" : currentLang() === "mix" ? "可查看 / available" : "可查看") : (currentLang() === "en" ? "not available" : currentLang() === "mix" ? "暂无 / not available" : "暂无")}</div>
      `;
      const loginUrlInput = document.getElementById("provider-login-url");
      if (loginUrlInput) {
        loginUrlInput.value = definition?.login_url || "";
      }
      const startButton = document.getElementById("start-provider-capture");
      if (startButton) {
        startButton.textContent = captureMode === "manual"
          ? (currentLang() === "en"
            ? "Open guide / manual credentials"
            : currentLang() === "mix"
              ? "查看说明并手动填写 / Open guide"
              : "查看说明并手动填写")
          : t("btn.start_provider_capture");
      }
      document.getElementById("provider-capture-summary").innerHTML = `
        <div class="badge">${escapeHtml(snapshot.status || "idle")}</div>
        <div class="mono">${escapeHtml(snapshot.message || "")}</div>
        <div class="mono">${currentLang() === "en" ? "Capture mode" : currentLang() === "mix" ? "接入模式 / Capture mode" : "接入模式"}: ${escapeHtml(captureMode === "manual" ? (currentLang() === "en" ? "manual credentials" : currentLang() === "mix" ? "手动凭证 / manual credentials" : "手动凭证") : (currentLang() === "en" ? "browser capture" : currentLang() === "mix" ? "网页登录抓取 / browser capture" : "网页登录抓取"))}</div>
        ${lines}
        ${captured.cookie_header ? `<div class="mono">cookie_header: ${escapeHtml(maskValue(captured.cookie_header))}</div>` : ""}
      `;
    }

    function applyProviderSelectionFromDriver(driver) {
      const select = document.getElementById("provider-select");
      if (!select) return;
      const provider = inferProviderFromDriver(driver);
      if ([...select.options].some((item) => item.value === provider)) {
        select.value = provider;
        renderProviderCapturePanel();
      }
      renderCapabilitySummary();
    }

    async function applyCapturedProviderFields() {
      const provider = document.getElementById("provider-select")?.value || "";
      const driver = document.getElementById("driver-select")?.value || "";
      const data = await call("/api/provider/capture/prefill", {
        method: "POST",
        body: JSON.stringify({ provider, driver }),
      });
      const values = data?.values || {};
      let changed = 0;
      document.querySelectorAll("[data-driver-field]").forEach((el) => {
        const fieldName = el.getAttribute("data-driver-field") || "";
        const nextValue = values[fieldName] || "";
        if (nextValue && !el.value) {
          el.value = nextValue;
          changed += 1;
        }
      });
      const missingRequired = Array.isArray(data?.missing_required) ? data.missing_required : [];
      const missingText = missingRequired.length
        ? (currentLang() === "en"
          ? ` Missing required fields: ${missingRequired.join(", ")}`
          : currentLang() === "mix"
            ? ` 缺少必填字段 / Missing required fields: ${missingRequired.join(", ")}`
            : ` 缺少必填字段: ${missingRequired.join(", ")}`)
        : "";
      setNotice(
        "driver-notice",
        changed
          ? (currentLang() === "en"
            ? `Applied ${changed} captured values to the mount form.${missingText}`
            : currentLang() === "mix"
              ? `已写入 ${changed} 个抓取字段 / Applied ${changed} values.${missingText}`
              : `已写入 ${changed} 个抓取字段到当前挂载表单。${missingText}`)
          : (currentLang() === "en"
            ? `No matching captured values were found for the current mount form.${missingText}`
            : currentLang() === "mix"
              ? `当前挂载表单没有可匹配字段 / No matching captured values were found.${missingText}`
              : `当前挂载表单没有可匹配的抓取字段。${missingText}`)
      );
    }

    function applyRatePresetForMount(mountPath) {
      const mode = String(document.getElementById("rate_limit_mode").value || "safe");
      if (mode === "custom") return;
      const selected = storageRecords.find((item) => {
        const current = item.mount_path || item.mountPath || item.path || "/";
        return String(current) === String(mountPath);
      });
      const driver = selected?.driver || selected?.driver_name || selected?.driverName || "";
      const preset = chooseRatePreset(driver, mode);
      if (!preset) return;
      document.getElementById("openlist_page_size").value = String(preset.openlist_page_size);
      document.getElementById("openlist_request_interval_ms").value = String(preset.openlist_request_interval_ms);
      document.getElementById("queue_interval_ms").value = String(preset.queue_interval_ms);
      setNotice("sync-notice", `已按 ${driver || "默认驱动"} 应用 ${mode} 频率策略。`);
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

    function applyConfigToForm(config) {
      configCache = { ...(config || {}) };
      syncUiPreferenceCache();
      const groupedMountedSource = getGroupedConfigValue(["ui", "browser", "mounted_source"], "");
      if (typeof groupedMountedSource === "string" && groupedMountedSource) {
        const mountedSelect = document.getElementById("mounted_source_select");
        if (mountedSelect) mountedSelect.value = groupedMountedSource;
      }
      const panelState = getGroupedConfigValue(["ui", "panel_open_states"], {});
      if (panelState && typeof panelState === "object") {
        setPanelState({ ...panelState });
        if (panelState.activeTab) activateTab(panelState.activeTab);
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
      applySavedCoverageFilters();
      populateSourceProfileOverrideOptions();
      const langSelect = document.getElementById("ui_language");
      if (langSelect) langSelect.value = currentLang();
    }

    async function saveConfig() {
      const payload = getConfigFromForm();
      await call("/api/config", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      configCache = payload;
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

    async function loadConfig() {
      const data = await call("/api/config");
      applyConfigToForm(data);
      applyI18n();
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
      currentDirectoryPath = data?.path || "/";
      currentParentPath = data?.parent_path || null;
      document.getElementById("dir-current").textContent = `当前浏览: ${currentDirectoryPath}`;
      setGroupedConfigValue(["ui", "browser", "current_path"], currentDirectoryPath || "/");
      setGroupedConfigValue(["ui", "browser", "current_parent_path"], currentParentPath || "");
      scheduleUiPrefsPersist();
      renderSourceDriverSummary();
      const root = document.getElementById("dir-browser-list");
      const dirs = Array.isArray(data?.directories) ? data.directories : [];
      if (!dirs.length) {
        root.innerHTML = `<div class="subtle">这个目录下没有子目录，可以直接把它设为同步源目录。</div>`;
        return;
      }
      root.innerHTML = dirs.map((item) => `
        <div class="row-item">
          <div>
            <div>${escapeHtml(item.name || "")}</div>
            <div class="mono">${escapeHtml(item.path || "")}</div>
          </div>
          <button class="secondary" data-open-dir="${escapeHtml(item.path || "/")}">进入</button>
        </div>
      `).join("");
      root.querySelectorAll("[data-open-dir]").forEach((button) => {
        button.addEventListener("click", async () => {
          await browseDirectory(button.getAttribute("data-open-dir") || "/");
        });
      });
    }

    function renderSync(sync) {
      const running = sync?.running ? (currentLang() === "en" ? "running" : currentLang() === "mix" ? "运行中 / running" : "运行中") : (currentLang() === "en" ? "idle" : currentLang() === "mix" ? "空闲 / idle" : "空闲");
      const summary = sync?.last_summary || {};
      const queue = sync?.queue_runner || {};
      const task = sync?.current_task || {};
      const mapping = sync?.current_source_context || queue?.source_mapping_context || {};
      document.getElementById("sync-summary").innerHTML = `
        <div class="badge">${escapeHtml(running)}</div>
        <div class="mono">${currentLang() === "en" ? "Last error" : currentLang() === "mix" ? "最近错误 / Last error" : "最近错误"}: ${escapeHtml(sync?.last_error || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Current task" : currentLang() === "mix" ? "当前任务 / Current task" : "当前任务"}: ${escapeHtml(task.mode || "-")} | ${escapeHtml(task.source_path || "-")} -> ${escapeHtml(task.target_key || "-")}:${escapeHtml(task.target_path || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Source mapping" : currentLang() === "mix" ? "源映射 / Source mapping" : "源映射"}: mount=${escapeHtml(mapping.mount_path || "-")} | requested=${escapeHtml(mapping.requested_driver || "-")} | override=${escapeHtml(mapping.source_profile_override || "-")} | effective=${escapeHtml(mapping.effective_driver || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Current queue source" : currentLang() === "mix" ? "当前队列目录 / Current queue source" : "当前队列目录"}: ${escapeHtml(queue.current_source || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Remaining" : currentLang() === "mix" ? "待处理剩余 / Remaining" : "待处理剩余"}: ${queue.remaining ?? "-"}</div>
        <div class="mono">${currentLang() === "en" ? "Last summary" : currentLang() === "mix" ? "最近结果 / Last summary" : "最近结果"}: total=${summary.total ?? 0}, direct=${summary.direct_success ?? 0}, downloaded=${summary.downloaded_success ?? 0}, failed=${summary.failed ?? 0}</div>
      `;
    }

    function renderRuntime(runtime) {
      const runtimeMode = runtime?.mode_label || getOpenListModeLabel(runtime?.mode || document.getElementById("openlist_mode")?.value);
      const canInstall = Boolean(runtime?.install_required);
      const yesText = currentLang() === "en" ? "yes" : currentLang() === "mix" ? "是 / yes" : "是";
      const noText = currentLang() === "en" ? "no" : currentLang() === "mix" ? "否 / no" : "否";
      document.getElementById("runtime-summary").innerHTML = `
        <div class="badge">${escapeHtml(runtimeMode || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Configured" : currentLang() === "mix" ? "配置地址 / Configured" : "配置地址"}: ${escapeHtml(runtime?.configured_url || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Active" : currentLang() === "mix" ? "实际地址 / Active" : "实际地址"}: ${escapeHtml(runtime?.active_url || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Running" : currentLang() === "mix" ? "运行状态 / Running" : "运行状态"}: ${runtime?.running ? yesText : noText} ${runtime?.pid ? `(pid ${runtime.pid})` : ""}</div>
        <div class="mono">${currentLang() === "en" ? "Binary" : currentLang() === "mix" ? "可执行文件 / Binary" : "可执行文件"}: ${escapeHtml(runtime?.binary || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Data dir" : currentLang() === "mix" ? "数据目录 / Data dir" : "数据目录"}: ${escapeHtml(runtime?.data_dir || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Docker CLI" : currentLang() === "mix" ? "Docker CLI / Docker CLI" : "Docker CLI"}: ${escapeHtml(runtime?.docker_cli || "-")} ${runtime?.docker_available ? "" : `(${currentLang() === "en" ? "missing" : currentLang() === "mix" ? "未检测到 / missing" : "未检测到"})`}</div>
        <div class="mono">${currentLang() === "en" ? "Docker daemon" : currentLang() === "mix" ? "Docker daemon / Docker daemon" : "Docker daemon"}: ${runtime?.docker_daemon_available ? yesText : noText}</div>
        <div class="mono">${currentLang() === "en" ? "Docker image" : currentLang() === "mix" ? "Docker 镜像 / Docker image" : "Docker 镜像"}: ${escapeHtml(runtime?.docker_image || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Docker container" : currentLang() === "mix" ? "Docker 容器 / Docker container" : "Docker 容器"}: ${escapeHtml(runtime?.docker_container_name || "-")} ${runtime?.docker_container_exists ? "" : `(${currentLang() === "en" ? "not created" : currentLang() === "mix" ? "未创建 / not created" : "未创建"})`}</div>
        <div class="mono">${currentLang() === "en" ? "Install required" : currentLang() === "mix" ? "需要拉取 / Install required" : "需要拉取"}: ${canInstall ? yesText : noText}</div>
        <div class="mono">${escapeHtml(runtime?.message || "")}</div>
        ${runtime?.suggested_action ? `<div class="mono">${escapeHtml(runtime.suggested_action)}</div>` : ""}
      `;
      const noticeEl = document.getElementById("runtime-action-notice");
      if (noticeEl) {
        noticeEl.textContent = runtime?.message || (currentLang() === "en" ? "Runtime status is ready." : currentLang() === "mix" ? "运行时状态已更新。 / Runtime status is ready." : "运行时状态已更新。");
      }
      const installBtn = document.getElementById("install-runtime");
      if (installBtn) installBtn.disabled = !canInstall;
      applyOpenListModeUi();
    }

    function renderCapture(capture, targetStateSummary = null) {
      const captured = capture?.captured || {};
      const missing = !captured.authorization && !captured.access_token && !captured.refresh_token;
      const activeTarget = String(targetStateSummary?.target_key || activeTargetKey() || "guangya");
      const targetFields = Array.isArray(targetStateSummary?.fields) ? targetStateSummary.fields : [];
      const isGuangya = activeTarget === "guangya";
      const nonGuangyaBadge = targetStateSummary?.has_state
        ? (currentLang() === "en" ? "configured" : currentLang() === "mix" ? "已配置 / configured" : "已配置")
        : (currentLang() === "en" ? "empty" : currentLang() === "mix" ? "未配置 / empty" : "未配置");
      const nonGuangyaMessage = currentLang() === "en"
        ? `Current target is ${activeTarget}. Guangya capture details are hidden because this target is not using Guangya auth fields.`
        : currentLang() === "mix"
          ? `当前目标端为 ${activeTarget}，这里不再展示 Guangya 抓取细节，因为该目标端不使用 Guangya 鉴权字段。 / Guangya capture details are hidden.`
          : `当前目标端为 ${activeTarget}，这里不再展示 Guangya 抓取细节，因为该目标端不使用 Guangya 鉴权字段。`;
      const targetStateLine = targetStateSummary
        ? `<div class="mono">${currentLang() === "en" ? "Active target state" : currentLang() === "mix" ? "当前目标端状态 / Active target state" : "当前目标端状态"}: ${escapeHtml(activeTarget)} | ${currentLang() === "en" ? "fields" : currentLang() === "mix" ? "字段 / fields" : "字段"}=${targetStateSummary.field_count ?? 0} | ${escapeHtml(targetFields.join(", ") || "-")}</div>`
        : "";
      document.getElementById("capture-summary").innerHTML = `
        <div class="badge">${escapeHtml(isGuangya ? (capture?.status || "idle") : nonGuangyaBadge)}</div>
        <div class="mono">${escapeHtml(isGuangya ? (capture?.message || "") : nonGuangyaMessage)}</div>
        ${targetStateLine}
        ${isGuangya ? `<div class="mono">Authorization: ${captured.authorization ? (currentLang() === "en" ? "captured" : currentLang() === "mix" ? "已抓取 / captured" : "已抓取") : (currentLang() === "en" ? "missing" : currentLang() === "mix" ? "未抓取 / missing" : "未抓取")}</div>` : ""}
        ${isGuangya ? `<div class="mono">Access Token: ${captured.access_token ? (currentLang() === "en" ? "captured" : currentLang() === "mix" ? "已抓取 / captured" : "已抓取") : (currentLang() === "en" ? "missing" : currentLang() === "mix" ? "未抓取 / missing" : "未抓取")}</div>` : ""}
        ${isGuangya ? `<div class="mono">Refresh Token: ${captured.refresh_token ? (currentLang() === "en" ? "captured" : currentLang() === "mix" ? "已抓取 / captured" : "已抓取") : (currentLang() === "en" ? "missing" : currentLang() === "mix" ? "未抓取 / missing" : "未抓取")}</div>` : ""}
        ${isGuangya && missing ? `<div class="mono">${currentLang() === "en" ? "Hint: click Guangya capture to auto-fill the login data." : currentLang() === "mix" ? "提示 / Hint: 点击光鸭抓取按钮自动回填登录信息。" : "提示: 需要点击“打开光鸭登录并自动抓取”完成自动回填。"}</div>` : ""}
      `;
    }

    function renderSourceAnalyze(data) {
      sourceAnalyzeCache = data || null;
      const root = document.getElementById("source-analyze-summary");
      const summary = data?.summary || {};
      const decision = data?.fastUploadDecision || {};
      const entries = Array.isArray(data?.entries) ? data.entries : [];
      if (!data) {
        root.textContent = currentLang() === "en" ? "No analysis result" : currentLang() === "mix" ? "暂无分析结果 / No analysis result" : "暂无分析结果";
        return;
      }
      const providerCounts = Object.entries(summary.provider_counts || {}).map(([key, value]) => `${key}: ${value}`).join(" | ") || "-";
      const hashCounts = Object.entries(summary.hash_type_counts || {}).map(([key, value]) => `${key}: ${value}`).join(" | ") || "-";
      const recommendation = summary.missing_md5 > 0
        ? (summary.gcid_ready > 0
          ? (currentLang() === "en"
            ? "Some files do not have MD5 but do have GCID. Prefer metadata sync first, then inspect pending items carefully."
            : currentLang() === "mix"
              ? "部分文件没有 MD5 但有 GCID，建议先走元数据秒传，再重点检查待补传。 / Prefer metadata sync first, then inspect pending items carefully."
              : "部分文件没有 MD5 但有 GCID，建议先走元数据秒传，再重点检查待补传。")
          : (currentLang() === "en"
            ? "Some files do not have MD5. Avoid aggressive auto-download and inspect source/provider compatibility first."
            : currentLang() === "mix"
              ? "部分文件没有 MD5，建议先确认源端兼容性，不要过激进地自动补传。 / Avoid aggressive auto-download first."
              : "部分文件没有 MD5，建议先确认源端兼容性，不要过激进地自动补传。"))
        : (currentLang() === "en"
          ? "Most files are MD5-ready. This directory is suitable for normal metadata-first sync."
          : currentLang() === "mix"
            ? "大多数文件已具备 MD5，适合正常先秒传再补传。 / This directory looks good for metadata-first sync."
            : "大多数文件已具备 MD5，适合正常先秒传再补传。");
      root.innerHTML = `
        <div class="row-item">
          <div>
            <div>${escapeHtml(data.source_path || "-")}</div>
            <div class="mono">${currentLang() === "en" ? "Total files" : currentLang() === "mix" ? "文件总数 / Total files" : "文件总数"}: ${summary.total ?? 0} | ${currentLang() === "en" ? "Plan total" : currentLang() === "mix" ? "待同步 / Plan total" : "待同步"}: ${data.plan_total ?? 0} | ${currentLang() === "en" ? "Removed" : currentLang() === "mix" ? "源端已删除 / Removed" : "源端已删除"}: ${data.removed_total ?? 0}</div>
            <div class="mono">${currentLang() === "en" ? "MD5 ready" : currentLang() === "mix" ? "具备 MD5 / MD5 ready" : "具备 MD5"}: ${summary.md5_ready ?? 0} | GCID: ${summary.gcid_ready ?? 0} | ${currentLang() === "en" ? "Missing MD5" : currentLang() === "mix" ? "缺少 MD5 / Missing MD5" : "缺少 MD5"}: ${summary.missing_md5 ?? 0}</div>
            <div class="mono">${currentLang() === "en" ? "Fast upload decision" : currentLang() === "mix" ? "秒传决策 / Fast upload decision" : "秒传决策"}: ${escapeHtml(decision.level || "-")} | ${escapeHtml(decision.bucket || "-")}</div>
            <div class="mono">provider: ${escapeHtml(providerCounts)}</div>
            <div class="mono">hash: ${escapeHtml(hashCounts)}</div>
            <div class="mono">${escapeHtml((currentLang() === "en" ? decision?.rationale?.en : currentLang() === "mix" ? `${decision?.rationale?.zh || ""} / ${decision?.rationale?.en || ""}`.trim() : decision?.rationale?.zh) || "-")}</div>
            <div class="mono">${escapeHtml(recommendation)}</div>
          </div>
        </div>
        ${entries.map((item) => `
          <div class="row-item">
            <div>
              <div>${escapeHtml(item.path || "")}</div>
              <div class="mono">provider=${escapeHtml(item.provider || "-")} | hashType=${escapeHtml(item.hashType || "-")} | size=${escapeHtml(String(item.size ?? 0))}</div>
              <div class="mono">md5=${escapeHtml(item.md5 || "-")} | gcid=${escapeHtml(item.gcid || "-")} | sourceId=${escapeHtml(item.sourceId || "-")}</div>
            </div>
          </div>
        `).join("")}
        ${data.truncated ? `<div class="subtle">${currentLang() === "en" ? "Only the first preview rows are shown here. Full export has been written to the local export file." : currentLang() === "mix" ? "这里只展示前几条样本，完整结果已写入本地导出文件。 / Only preview rows are shown here." : "这里只展示前几条样本，完整结果已写入本地导出文件。"}</div>` : ""}
      `;
    }

    function renderMiaochuanDiagnosis(data) {
      const root = document.getElementById("miaochuan-diagnosis");
      if (!data) {
        root.textContent = currentLang() === "en"
          ? "No diagnosis result"
          : currentLang() === "mix"
            ? "暂无诊断结果 / No diagnosis result"
            : "暂无诊断结果";
        return;
      }
      const providerCounts = Object.entries(data.provider_counts || {})
        .map(([key, value]) => `${key}: ${value}`)
        .join(" | ") || "-";
      const sample = Array.isArray(data.sample) ? data.sample : [];
      root.innerHTML = `
        <div class="row-item">
          <div>
            <div>${currentLang() === "en" ? "Flash Upload JSON Diagnosis" : currentLang() === "mix" ? "秒传 JSON 诊断 / Flash Upload JSON Diagnosis" : "秒传 JSON 诊断"}</div>
            <div class="mono">${currentLang() === "en" ? "Total files" : currentLang() === "mix" ? "文件总数 / Total files" : "文件总数"}: ${data.total ?? 0}</div>
            <div class="mono">${currentLang() === "en" ? "Total size" : currentLang() === "mix" ? "总大小 / Total size" : "总大小"}: ${formatBytes(data.total_size || 0)}</div>
            <div class="mono">MD5: ${data.md5_count ?? 0} | GCID: ${data.gcid_count ?? 0}</div>
            <div class="mono">provider: ${escapeHtml(providerCounts)}</div>
          </div>
        </div>
        ${sample.map((item) => `
          <div class="row-item">
            <div>
              <div>${escapeHtml(item.path || "-")}</div>
              <div class="mono">provider=${escapeHtml(item.provider || "unknown")} | hashType=${escapeHtml(item.hashType || "-")} | size=${formatBytes(item.size || 0)}</div>
              <div class="mono">md5=${escapeHtml(item.etag || "-")} | gcid=${escapeHtml(item.gcid || "-")}</div>
            </div>
          </div>
        `).join("")}
        ${sample.length === 0 ? `<div class="subtle">${currentLang() === "en" ? "No sample rows available." : currentLang() === "mix" ? "没有可展示的样本行。 / No sample rows available." : "没有可展示的样本行。"}</div>` : ""}
      `;
    }

    function populateMountedSources(items) {
      const select = document.getElementById("mounted_source_select");
      const list = Array.isArray(items) ? items : [];
      if (!list.length) {
        select.innerHTML = `<option value="">${currentLang() === "en" ? "No mounts" : currentLang() === "mix" ? "暂无挂载 / No mounts" : "暂无挂载"}</option>`;
        return;
      }
      const sourcePath = String(document.getElementById("source_path").value || "").trim();
      const mountedSource = String(getGroupedConfigValue(["ui", "browser", "mounted_source"], "") || "").trim();
      select.innerHTML = list.map((item) => {
        const mountPath = item.mount_path || item.mountPath || item.path || "/";
        const driver = item.driver || item.driver_name || item.driverName || "-";
        const selected = mountedSource
          ? (mountedSource === String(mountPath) ? "selected" : "")
          : (sourcePath.startsWith(String(mountPath)) ? "selected" : "");
        return `<option value="${escapeHtml(mountPath)}" ${selected}>${escapeHtml(mountPath)} | ${escapeHtml(driver)}</option>`;
      }).join("");
    }

    function renderQueue(items) {
      const root = document.getElementById("queue-list");
      const list = Array.isArray(items) ? items : [];
      if (!list.length) {
        root.textContent = currentLang() === "en" ? "No queued directories" : currentLang() === "mix" ? "暂无目录队列 / No queued directories" : "暂无目录队列";
        return;
      }
      root.innerHTML = list.map((item) => `
        <div class="row-item">
          <div>
            <div>${escapeHtml(item.source_path)}</div>
            <div class="mono">${currentLang() === "en" ? "Status" : currentLang() === "mix" ? "状态 / Status" : "状态"}: ${escapeHtml(item.last_status || "idle")} ${item.last_run_at ? `| ${currentLang() === "en" ? "Last run" : currentLang() === "mix" ? "上次 / Last run" : "上次"}: ${escapeHtml(item.last_run_at)}` : ""}</div>
          </div>
          <button class="secondary" data-remove-queue="${escapeHtml(item.source_path)}">${currentLang() === "en" ? "Remove" : currentLang() === "mix" ? "移除 / Remove" : "移除"}</button>
        </div>
      `).join("");
      root.querySelectorAll("[data-remove-queue]").forEach((button) => {
        button.addEventListener("click", async () => {
          await call("/api/queue/remove", {
            method: "POST",
            body: JSON.stringify({ source_path: button.getAttribute("data-remove-queue") || "" }),
          });
          await refreshStatus();
        });
      });
    }

    function buildPendingTree(items) {
      const root = { name: "/", path: "/", directories: new Map(), files: [] };
      for (const item of items) {
        const path = String(item?.path || "");
        const parts = path.split("/").filter(Boolean);
        let cursor = root;
        let current = "";
        for (let index = 0; index < parts.length - 1; index += 1) {
          const part = parts[index];
          current += `/${part}`;
          if (!cursor.directories.has(part)) {
            cursor.directories.set(part, { name: part, path: current, directories: new Map(), files: [] });
          }
          cursor = cursor.directories.get(part);
        }
        cursor.files.push(item);
      }
      return root;
    }

    function collectNodeFilePaths(node) {
      let result = [];
      for (const file of node.files || []) {
        if (file?.path) result.push(file.path);
      }
      for (const child of node.directories?.values() || []) {
        result = result.concat(collectNodeFilePaths(child));
      }
      return result;
    }

    function refreshPendingDirectoryMap(root) {
      pendingDirectoryFiles = new Map();
      function walk(node) {
        pendingDirectoryFiles.set(node.path, collectNodeFilePaths(node));
        for (const child of node.directories?.values() || []) walk(child);
      }
      walk(root);
    }

    function renderPendingNode(node) {
      const childDirs = [...(node.directories?.values() || [])].sort((a, b) => a.path.localeCompare(b.path, "zh-CN"));
      const files = [...(node.files || [])].sort((a, b) => String(a.path || "").localeCompare(String(b.path || ""), "zh-CN"));
      const allPaths = collectNodeFilePaths(node);
      const checkedCount = allPaths.filter((path) => pendingSelection.has(path)).length;
      const expanded = pendingExpanded.has(node.path);
      return `
        <div class="tree-node">
          <div class="tree-row">
            <button type="button" class="tree-toggle ${childDirs.length ? "" : "empty"}" data-toggle-node="${escapeHtml(node.path)}">${childDirs.length ? (expanded ? "-" : "+") : ""}</button>
            <input type="checkbox" data-select-dir="${escapeHtml(node.path)}" ${allPaths.length && checkedCount === allPaths.length ? "checked" : ""}>
            <div class="tree-label">
              <div>${escapeHtml(node.name || "/")}</div>
              <div class="mono">${escapeHtml(node.path)} | ${allPaths.length} 个文件</div>
            </div>
          </div>
          ${expanded ? `
            <div>
              ${childDirs.map((child) => renderPendingNode(child)).join("")}
              ${files.map((file) => `
                <label class="tree-row">
                  <span class="tree-toggle empty"></span>
                  <input type="checkbox" data-select-file="${escapeHtml(file.path || "")}" ${pendingSelection.has(file.path) ? "checked" : ""}>
                  <div class="tree-label">
                    <div>${escapeHtml((file.path || "").split("/").filter(Boolean).pop() || file.path || "")}</div>
                    <div class="mono">${escapeHtml(file.path || "")} | ${formatBytes(file.size)} | ${escapeHtml(file.reason || "-")}</div>
                  </div>
                </label>
              `).join("")}
            </div>
          ` : ""}
        </div>
      `;
    }

    function syncPendingCheckboxState(root) {
      root.querySelectorAll("[data-select-dir]").forEach((box) => {
        const dir = box.getAttribute("data-select-dir");
        const paths = pendingDirectoryFiles.get(dir) || [];
        const count = paths.filter((path) => pendingSelection.has(path)).length;
        box.checked = paths.length > 0 && count === paths.length;
        box.indeterminate = count > 0 && count < paths.length;
      });
    }

    function bindPendingEvents(items) {
      const root = document.getElementById("pending-tree");
      root.querySelectorAll("[data-toggle-node]").forEach((button) => {
        button.addEventListener("click", () => {
          const node = button.getAttribute("data-toggle-node");
          if (!node) return;
          if (pendingExpanded.has(node)) pendingExpanded.delete(node);
          else pendingExpanded.add(node);
          renderPendingTree(items);
        });
      });
      root.querySelectorAll("[data-select-file]").forEach((box) => {
        box.addEventListener("change", () => {
          const path = box.getAttribute("data-select-file");
          if (!path) return;
          if (box.checked) pendingSelection.add(path);
          else pendingSelection.delete(path);
          pendingSelectionTouched = true;
          syncPendingCheckboxState(root);
        });
      });
      root.querySelectorAll("[data-select-dir]").forEach((box) => {
        box.addEventListener("change", () => {
          const dir = box.getAttribute("data-select-dir");
          const paths = pendingDirectoryFiles.get(dir) || [];
          for (const path of paths) {
            if (box.checked) pendingSelection.add(path);
            else pendingSelection.delete(path);
          }
          pendingSelectionTouched = true;
          renderPendingTree(items);
        });
      });
    }

    function renderPendingTree(items) {
      const root = document.getElementById("pending-tree");
      const list = Array.isArray(items) ? items : [];
      latestPendingItems = list;
      if (!list.length) {
        root.textContent = currentLang() === "en" ? "No pending reupload files" : currentLang() === "mix" ? "暂无待补传文件 / No pending reupload files" : "暂无待补传文件";
        pendingSelection = new Set();
        pendingDirectoryFiles = new Map();
        pendingExpanded = new Set(["/"]);
        return;
      }
      const available = new Set(list.map((item) => item?.path).filter(Boolean));
      pendingSelection = new Set([...pendingSelection].filter((path) => available.has(path)));
      if (!pendingSelectionTouched && pendingSelection.size === 0) {
        pendingSelection = new Set(available);
      }
      const tree = buildPendingTree(list);
      refreshPendingDirectoryMap(tree);
      if (pendingExpanded.size <= 1) {
        for (const item of list) {
          const parts = String(item.path || "").split("/").filter(Boolean);
          let current = "";
          for (let index = 0; index < Math.min(parts.length - 1, 2); index += 1) {
            current += `/${parts[index]}`;
            pendingExpanded.add(current);
          }
        }
      }
      const children = [...tree.directories.values()].sort((a, b) => a.path.localeCompare(b.path, "zh-CN"));
      root.innerHTML = `
        <div class="subtle" style="margin-bottom:10px;">${currentLang() === "en" ? `Total ${list.length} pending files. Expand, collapse, and select by real directory tree.` : currentLang() === "mix" ? `共 ${list.length} 个待补传文件 / Total ${list.length} pending files. 可按目录树展开、折叠和联动勾选。` : `共 ${list.length} 个待补传文件，可按目录树展开、折叠和联动勾选。`}</div>
        ${children.map((child) => renderPendingNode(child)).join("")}
      `;
      bindPendingEvents(list);
      syncPendingCheckboxState(root);
    }

    function renderStorages(payload) {
      const root = document.getElementById("storage-list");
      const content = payload?.data?.content || payload?.data || [];
      const list = Array.isArray(content) ? content : [];
      storageRecords = list;
      populateMountedSources(list);
      const selectedMount = document.getElementById("mounted_source_select")?.value || "";
      const selectedStorage = list.find((item) => String(item.mount_path || item.mountPath || item.path || "/") === String(selectedMount));
      if (selectedStorage) applyProviderSelectionFromDriver(selectedStorage.driver || selectedStorage.driver_name || selectedStorage.driverName || "");
      if (!list.length) {
        root.textContent = currentLang() === "en" ? "No mounts" : currentLang() === "mix" ? "暂无挂载 / No mounts" : "暂无挂载";
        renderCapabilitySummary();
        applyWorkflowGates();
        return;
      }
      root.innerHTML = list.map((item) => {
        const mountPath = item.mount_path || item.mountPath || item.path || "/";
        const driver = item.driver || item.driver_name || item.driverName || "-";
        return `
          <div class="row-item">
            <div>
              <div>${escapeHtml(mountPath)}</div>
              <div class="mono">driver: ${escapeHtml(driver)} | ${currentLang() === "en" ? "status" : currentLang() === "mix" ? "状态 / status" : "状态"}: ${escapeHtml(String(item.status ?? "-"))}</div>
            </div>
          </div>
        `;
      }).join("");
      renderCapabilitySummary();
      applyWorkflowGates();
    }

    async function loadDrivers() {
      await loadProviderRegistry();
      const data = await call("/api/openlist/drivers");
      driversCache = Array.isArray(data?.items) ? data.items : [];
      const select = document.getElementById("driver-select");
      select.innerHTML = driversCache.map((driver) => `<option value="${escapeHtml(driver)}">${escapeHtml(driver)}</option>`).join("");
      if (driversCache.length) {
        await loadDriverInfo(select.value);
      } else {
        document.getElementById("driver-fields").innerHTML = `<div class='subtle'>${currentLang() === "en" ? "No drivers loaded." : currentLang() === "mix" ? "未获取到驱动列表 / No drivers loaded." : "未获取到驱动列表。"}</div>`;
      }
      applyProviderSelectionFromDriver(select.value || "");
      await refreshCoverageAudit();
    }

    function renderDriverFields(info) {
      currentDriverInfo = info;
      const fields = [...(info?.common || []), ...(info?.additional || [])];
      const root = document.getElementById("driver-fields");
      document.getElementById("driver-notice").textContent = currentLang() === "en"
        ? `${info?.name || "-"}: ${fields.length} fields generated from OpenList driver metadata.`
        : currentLang() === "mix"
          ? `${info?.name || "-"}：共 ${fields.length} 个字段 / ${fields.length} fields generated from OpenList driver metadata.`
          : `${info?.name || "-"}：共 ${fields.length} 个字段，已按 OpenList 驱动描述动态生成。`;
      root.innerHTML = fields.map((field) => {
        const type = String(field.type || "string").toLowerCase();
        const id = `driver-field-${field.name}`;
        if (type === "bool") {
          return `
            <div>
              <label>${escapeHtml(driverFieldLabel(field.name))} ${field.required ? (currentLang() === "en" ? "(Required)" : currentLang() === "mix" ? "(必填 / Required)" : "(必填)") : ""}</label>
              <select id="${escapeHtml(id)}" data-driver-field="${escapeHtml(field.name)}">
                <option value="">${currentLang() === "en" ? "Default" : currentLang() === "mix" ? "默认 / Default" : "默认"}</option>
                <option value="true" ${String(field.default) === "True" || String(field.default) === "true" ? "selected" : ""}>${currentLang() === "en" ? "true" : currentLang() === "mix" ? "是 / true" : "是"}</option>
                <option value="false" ${String(field.default) === "False" || String(field.default) === "false" ? "selected" : ""}>${currentLang() === "en" ? "false" : currentLang() === "mix" ? "否 / false" : "否"}</option>
              </select>
              <div class="mono">${escapeHtml(driverFieldHelp(field.help || ""))}</div>
            </div>
          `;
        }
        return `
          <div>
            <label>${escapeHtml(driverFieldLabel(field.name))} ${field.required ? (currentLang() === "en" ? "(Required)" : currentLang() === "mix" ? "(必填 / Required)" : "(必填)") : ""}</label>
            <input id="${escapeHtml(id)}" data-driver-field="${escapeHtml(field.name)}" value="${escapeHtml(field.default || "")}">
            <div class="mono">${escapeHtml(driverFieldHelp(field.help || "") || driverFieldOptions(field.options || "") || String(field.options || ""))}</div>
          </div>
        `;
      }).join("");
      renderDriverGuide(info?.name || "");
      renderProviderCapturePanel();
      renderCapabilitySummary();
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

    function renderLogs(records) {
      const root = document.getElementById("logs");
      root.textContent = (records || []).map((row) => `[${row.ts}] [${row.level}] ${row.message}`).join("\n");
      root.scrollTop = root.scrollHeight;
    }

    function renderOverviewRouteSummary(syncState = {}, runtimeState = {}) {
      const root = document.getElementById("overview-route-summary");
      if (!root) return;
      const currentTask = syncState?.current_task || {};
      const currentSourceContext = syncState?.current_source_context || {};
      const sourcePath = String(currentTask.source_path || document.getElementById("source_path")?.value || configCache?.source_path || currentDirectoryPath || "/").trim() || "/";
      const targetKey = String(currentTask.target_key || document.getElementById("target_key")?.value || configCache?.target_key || "guangya").trim() || "guangya";
      const targetPath = String(currentTask.target_path || document.getElementById("target_path")?.value || configCache?.target_path || "/").trim() || "/";
      const mode = normalizeOpenListMode(document.getElementById("openlist_mode")?.value || configCache?.openlist_mode || "external_local");
      const queueSize = Array.isArray(syncState?.source_queue) ? syncState.source_queue.length : 0;
      const pendingSize = Array.isArray(syncState?.persistent_pending) ? syncState.persistent_pending.length : 0;
      const activeUrl = String(document.getElementById("effective_openlist_url")?.value || runtimeState?.active_url || configCache?.openlist_url || "-").trim() || "-";
      const sourceRuntime = window.__cpbStatusCache?.source_runtime || {};
      root.innerHTML = `
        <div class="mono">OpenList Mode: ${escapeHtml(getOpenListModeLabel(mode))}</div>
        <div class="mono">OpenList URL: ${escapeHtml(activeUrl)}</div>
        <div class="mono">Source: ${escapeHtml(sourcePath)}</div>
        <div class="mono">Target: ${escapeHtml(targetKey)} -> ${escapeHtml(targetPath)}</div>
        <div class="mono">Source Mapping: mount=${escapeHtml(currentSourceContext.mount_path || "-")} | effective=${escapeHtml(currentSourceContext.effective_driver || "-")}</div>
        <div class="mono">Source Route: pref=${escapeHtml(sourceRuntime.requested_provider_preference || "-")} | selected=${escapeHtml(sourceRuntime.selected_source_mode || "-")} | provider=${escapeHtml(sourceRuntime.selected_provider_key || "-")}</div>
        <div class="mono">Queue: ${queueSize} | Pending: ${pendingSize}</div>
      `;
    }

    function renderSourceDriverSummary() {
      const root = document.getElementById("source-driver-summary");
      if (!root) return;
      const context = currentDriverContext();
      const backendContext = providerRegistryPayload?.current_source_context || {};
      const assessedContext = capabilityAssessmentCache?.sourceMappingContext || {};
      const runtimeContext = window.__cpbStatusCache?.sync?.current_source_context || {};
      const sourcePath = String(document.getElementById("source_path")?.value || configCache?.source_path || "/").trim() || "/";
      const browsingPath = String(currentDirectoryPath || "/").trim() || "/";
      const selectedMount = String(document.getElementById("mounted_source_select")?.value || "").trim();
      const rateMode = String(document.getElementById("rate_limit_mode")?.value || configCache?.rate_limit_mode || "safe").trim() || "safe";
      const sourceRuntime = window.__cpbStatusCache?.source_runtime || {};
      root.innerHTML = `
        <div class="mono">driver=${escapeHtml(context.driver || "-")} | mount=${escapeHtml(selectedMount || "-")} | rate=${escapeHtml(rateMode)}</div>
        <div class="mono">mounted_driver=${escapeHtml(context.mountedDriver || "-")} | override=${escapeHtml(context.overrideProfile || "-")}</div>
        <div class="mono">backend_effective=${escapeHtml(assessedContext.effective_driver || backendContext.effective_driver || "-")} | backend_override=${escapeHtml(assessedContext.source_profile_override || backendContext.source_profile_override || "-")}</div>
        <div class="mono">runtime_mount=${escapeHtml(runtimeContext.mount_path || "-")} | runtime_effective=${escapeHtml(runtimeContext.effective_driver || "-")}</div>
        <div class="mono">route_pref=${escapeHtml(sourceRuntime.requested_provider_preference || "-")} | route_selected=${escapeHtml(sourceRuntime.selected_source_mode || "-")} | route_provider=${escapeHtml(sourceRuntime.selected_provider_key || "-")}</div>
        <div class="mono">source_path=${escapeHtml(sourcePath)} | browsing=${escapeHtml(browsingPath)}</div>
        ${sourceRuntime.selection_reason ? `<div>${escapeHtml(sourceRuntime.selection_reason)}</div>` : ""}
        ${sourceRuntime.fallback_reason ? `<div>${escapeHtml(sourceRuntime.fallback_reason)}</div>` : ""}
      `;
    }

    function renderTaskModeSummary() {
      const root = document.getElementById("task-mode-summary");
      if (!root) return;
      const sourcePath = String(document.getElementById("source_path")?.value || configCache?.source_path || "/").trim() || "/";
      const targetKey = activeTargetKey();
      const targetPath = String(document.getElementById("target_path")?.value || configCache?.target_path || "/").trim() || "/";
      const autoThreshold = String(document.getElementById("auto_download_threshold_mb")?.value || configCache?.auto_download_threshold_mb || "0").trim() || "0";
      const deleteRemoved = Boolean(document.getElementById("delete_removed")?.checked);
      const deleteRealTarget = Boolean(document.getElementById("target_delete_removed")?.checked);
      const sourcePreference = String(document.getElementById("source_provider_preference")?.value || configCache?.source_provider_preference || "auto").trim() || "auto";
      const recommendedMode = String(capabilityAssessmentCache?.strategy?.recommendedMode || "-");
      const assessedLevel = capabilityLevelText(capabilityAssessmentCache?.assessedLevel || capabilityAssessmentCache?.level || "unsupported");
      const rationale = capabilityAssessmentCache?.rationale
        ? translateDriverText(capabilityAssessmentCache.rationale.zh || "", capabilityAssessmentCache.rationale.en || "")
        : "";
      const sourceRuntime = window.__cpbStatusCache?.source_runtime || {};
      root.innerHTML = `
        <div class="mono">source=${escapeHtml(sourcePath)} -> target=${escapeHtml(targetKey)}:${escapeHtml(targetPath)}</div>
        <div class="mono">recommended=${escapeHtml(recommendedMode)} | level=${escapeHtml(assessedLevel)} | auto_small_mb=${escapeHtml(autoThreshold)}</div>
        <div class="mono">source_route_pref=${escapeHtml(sourcePreference)} | selected=${escapeHtml(sourceRuntime.selected_source_mode || "-")} | provider=${escapeHtml(sourceRuntime.selected_provider_key || "-")}</div>
        <div class="mono">delete_state=${deleteRemoved ? "on" : "off"} | delete_target=${deleteRealTarget ? "on" : "off"}</div>
        ${sourceRuntime.selection_reason ? `<div>${escapeHtml(sourceRuntime.selection_reason)}</div>` : ""}
        ${sourceRuntime.fallback_reason ? `<div>${escapeHtml(sourceRuntime.fallback_reason)}</div>` : ""}
        ${rationale ? `<div>${escapeHtml(rationale)}</div>` : ""}
      `;
    }

    function renderWorkflowSummaries(syncState = {}, runtimeState = {}) {
      renderOverviewRouteSummary(syncState, runtimeState);
      renderSourceDriverSummary();
      renderTaskModeSummary();
      applyWorkflowGates();
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
      activateTab("miaochuan");
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
          setNotice("sync-notice", `失败: ${error.message}`);
          setNotice("dir-notice", `失败: ${error.message}`);
          setNotice("miaochuan-notice", `失败: ${error.message}`);
        } finally {
          if (button) {
            button.disabled = false;
            button.textContent = oldText;
          }
        }
      };
    }

    function bindEvents() {
      document.getElementById("open-auth-login").onclick = () => {
        setAuthNotice("请输入控制台账号密码。");
        showAuthDialog();
      };
      document.getElementById("open-auth-login-inline").onclick = () => {
        setAuthNotice("请输入控制台账号密码。");
        showAuthDialog();
      };
      document.getElementById("submit-auth-login").onclick = withBusy("submit-auth-login", "登录中...", async () => {
        await call("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({
            username: document.getElementById("auth-username").value,
            password: document.getElementById("auth-password").value,
          }),
        });
        document.getElementById("auth-password").value = "";
        setAuthNotice("登录成功，正在载入控制台...");
        await ensureAuthorizedAndBootstrap(true);
      });
      document.getElementById("auth-password").addEventListener("keydown", (event) => {
        if (event.key === "Enter") document.getElementById("submit-auth-login")?.click();
      });
      document.getElementById("auth-dialog").addEventListener("click", (event) => {
        if (event.target?.id !== "auth-dialog") return;
        if (authState.enabled && !authState.authenticated) return;
        hideAuthDialog();
      });
      document.getElementById("logout-auth").onclick = withBusy("logout-auth", "退出中...", async () => {
        await call("/api/auth/logout", { method: "POST" });
        updateAuthUi({ ...(authState || {}), authenticated: false });
        appBootstrapped = false;
        stopAutoRefresher();
        showAuthDialog("已退出登录。");
      });
      document.getElementById("toggle-logs").onclick = () => toggleDrawer();
      document.getElementById("capability-quick-actions").onclick = (event) => {
        const target = event.target?.closest?.("[data-capability-action]");
        if (!target) return;
        performCapabilityQuickAction(target.getAttribute("data-capability-action"));
      };
      document.getElementById("reload-all").onclick = withBusy("reload-all", "重载中...", async () => {
        await loadConfig();
        await ensureDirectoryBrowserReady(true);
        await refreshStatus();
        await refreshStorages();
      });
      document.getElementById("save-config-top").onclick = withBusy("save-config-top", "保存中...", saveConfig);
      document.getElementById("save-config-overview").onclick = withBusy("save-config-overview", "保存中...", saveConfig);
      document.getElementById("save-config-bottom").onclick = withBusy("save-config-bottom", "保存中...", saveConfig);
      document.getElementById("mounted_source_select").addEventListener("change", (event) => {
        applyRatePresetForMount(event.target.value);
        setGroupedConfigValue(["ui", "browser", "mounted_source"], String(event.target.value || ""));
        scheduleUiPrefsPersist();
        const selected = storageRecords.find((item) => String(item.mount_path || item.mountPath || item.path || "/") === String(event.target.value || ""));
        if (selected) applyProviderSelectionFromDriver(selected.driver || selected.driver_name || selected.driverName || "");
        populateSourceProfileOverrideOptions();
        renderSourceDriverSummary();
      });
      document.getElementById("provider-select").addEventListener("change", () => {
        renderProviderCapturePanel();
      });
      document.getElementById("target_key").addEventListener("change", async (event) => {
        const nextTarget = String(event.target?.value || "guangya");
        providerRegistryPayload = {
          ...(providerRegistryPayload || {}),
          active_target: nextTarget,
        };
        await refreshTargetPreflight();
        renderTargetSpecificControls();
        renderCapabilitySummary();
        renderAboutRegistry();
        await refreshCapabilityAssessment();
        await refreshCoverageAudit();
        if (nextTarget === "guangya") {
          await attemptAutoGuangyaCapture();
        }
      });
      document.getElementById("rate_limit_mode").addEventListener("change", () => {
        const selected = document.getElementById("mounted_source_select").value || document.getElementById("source_path").value || "/";
        applyRatePresetForMount(selected);
      });
      ["source_path", "target_path", "auto_download_threshold_mb", "source_provider_preference"].forEach((fieldId) => {
        document.getElementById(fieldId)?.addEventListener("change", () => {
          renderWorkflowSummaries(window.__cpbStatusCache?.sync || {}, window.__cpbStatusCache?.openlist_runtime || {});
        });
      });
      ["delete_removed", "target_delete_removed"].forEach((fieldId) => {
        document.getElementById(fieldId)?.addEventListener("change", () => {
          renderTaskModeSummary();
        });
      });
      document.getElementById("openlist_mode").addEventListener("change", async (event) => {
        const nextMode = normalizeOpenListMode(event.target.value || "external_local");
        persistCurrentOpenListModeSnapshot(getGroupedConfigValue(["openlist", "mode"], "external_local"));
        setGroupedConfigValue(["openlist", "mode"], nextMode);
        applyOpenListModeSnapshot(nextMode);
        await saveConfig();
        await refreshStatus();
      });
      document.getElementById("use-mounted-source").onclick = withBusy("use-mounted-source", "处理中...", async () => {
        const selected = document.getElementById("mounted_source_select").value || "/";
        setGroupedConfigValue(["ui", "browser", "mounted_source"], selected);
        document.getElementById("source_path").value = selected;
        await saveConfig();
        await browseDirectory(selected);
        setNotice("dir-notice", `已切换到挂载源目录: ${selected}`);
      });
      document.getElementById("save-source-profile-override").onclick = withBusy("save-source-profile-override", "保存中...", async () => {
        const select = document.getElementById("source_profile_override");
        await saveSourceProfileOverrideSelection(select?.value || "");
      });
      document.getElementById("clear-source-profile-override").onclick = withBusy("clear-source-profile-override", "清除中...", async () => {
        const select = document.getElementById("source_profile_override");
        if (select) select.value = "";
        await saveSourceProfileOverrideSelection("");
      });

      document.getElementById("install-runtime").onclick = withBusy("install-runtime", "拉取中...", async () => {
        const installed = await installManagedRuntimeWithPrompt(await getRuntimeStatus());
        if (installed) {
          renderRuntime(installed);
          await refreshStatus();
        }
      });
      document.getElementById("start-runtime").onclick = withBusy("start-runtime", "启动中...", async () => {
        const status = await getRuntimeStatus();
        const maybeInstalled = await installManagedRuntimeWithPrompt(status);
        if (maybeInstalled?.install_required) {
          renderRuntime(maybeInstalled);
          return;
        }
        const data = await call("/api/openlist/runtime/start", { method: "POST" });
        renderRuntime(data);
        await loadConfig();
        setNotice("sync-notice", `OpenList runtime 已就绪: ${data.active_url || "-"}`);
      });
      document.getElementById("login-openlist").onclick = withBusy("login-openlist", "登录中...", async () => {
        await call("/api/openlist/login", {
          method: "POST",
          body: JSON.stringify({
            openlist_url: document.getElementById("openlist_url").value,
            openlist_username: document.getElementById("openlist_username").value,
            openlist_password: document.getElementById("openlist_password").value,
            openlist_token: document.getElementById("openlist_token").value,
          }),
        });
        await loadConfig();
        await ensureDirectoryBrowserReady(true);
        await refreshStatus();
        await refreshStorages();
      });
      document.getElementById("capture-guangya").onclick = withBusy("capture-guangya", "启动抓取中...", async () => {
        await call("/api/guangya/capture/start", { method: "POST" });
        setNotice("sync-notice", "已打开光鸭登录抓取窗口，请在浏览器中完成登录。");
        await refreshStatus();
      });
      const runDirectOverviewButton = document.getElementById("run-direct-overview");
      if (runDirectOverviewButton) {
        runDirectOverviewButton.onclick = withBusy("run-direct-overview", "启动中...", () => runSyncMode("direct"));
      }

      document.getElementById("browse-root").onclick = withBusy("browse-root", "载入中...", async () => {
        await browseDirectory("/");
        setNotice("dir-notice", "已打开挂载根目录。");
      });
      document.getElementById("analyze-source").onclick = withBusy("analyze-source", "分析中...", async () => {
        await analyzeCurrentSource();
      });
      document.getElementById("build-source-miaochuan").onclick = withBusy("build-source-miaochuan", "生成中...", async () => {
        await buildCurrentSourceMiaochuan();
      });
      document.getElementById("browse-up").onclick = withBusy("browse-up", "返回中...", async () => {
        await browseDirectory(currentParentPath || "/");
        setNotice("dir-notice", `当前浏览: ${currentDirectoryPath}`);
      });
      document.getElementById("browse-refresh").onclick = withBusy("browse-refresh", "刷新中...", async () => {
        await browseDirectory(currentDirectoryPath || "/");
        setNotice("dir-notice", `已刷新: ${currentDirectoryPath}`);
      });
      document.getElementById("use-current-dir").onclick = withBusy("use-current-dir", "写入中...", async () => {
        document.getElementById("source_path").value = currentDirectoryPath || "/";
        await saveConfig();
        setNotice("dir-notice", `已写入 source_path: ${currentDirectoryPath}`);
      });

      document.getElementById("add-current-queue").onclick = withBusy("add-current-queue", "加入中...", async () => {
        await call("/api/queue/add", {
          method: "POST",
          body: JSON.stringify({ source_path: currentDirectoryPath || "/" }),
        });
        await refreshStatus();
        setNotice("dir-notice", `已加入队列: ${currentDirectoryPath}`);
      });
      document.getElementById("add-leaf-queue").onclick = withBusy("add-leaf-queue", "扫描中...", async () => {
        const result = await call("/api/queue/add_leaf_units", {
          method: "POST",
          body: JSON.stringify({ source_path: currentDirectoryPath || "/" }),
        });
        await refreshStatus();
        setNotice("dir-notice", `已加入 ${result.added || 0} 个最底层目录。`);
      });
      document.getElementById("run-leaf-direct").onclick = withBusy("run-leaf-direct", "启动中...", async () => {
        await saveConfig();
        await call("/api/leaf/run_stream", {
          method: "POST",
          body: JSON.stringify({ source_path: currentDirectoryPath || "/" }),
        });
        setNotice("dir-notice", `已开始最底层目录边扫边秒传: ${currentDirectoryPath}`);
        await refreshStatus();
      });
      document.getElementById("run-leaf-full").onclick = withBusy("run-leaf-full", "启动中...", async () => {
        await saveConfig();
        await call("/api/leaf/run_stream_full", {
          method: "POST",
          body: JSON.stringify({ source_path: currentDirectoryPath || "/" }),
        });
        setNotice("dir-notice", `已开始最底层目录边扫边同步+补传: ${currentDirectoryPath}`);
        await refreshStatus();
      });

      document.getElementById("run-dry").onclick = withBusy("run-dry", "启动中...", () => runSyncMode("dry_run"));
      document.getElementById("run-direct").onclick = withBusy("run-direct", "启动中...", () => runSyncMode("direct"));
      document.getElementById("run-next-queue").onclick = withBusy("run-next-queue", "启动中...", async () => {
        await saveConfig();
        const result = await call("/api/queue/run_next", { method: "POST" });
        setNotice("sync-notice", `开始执行队列目录: ${result.source_path || "-"}`);
        await refreshStatus();
      });
      document.getElementById("run-all-queue").onclick = withBusy("run-all-queue", "启动中...", async () => {
        await saveConfig();
        await call("/api/queue/run_all", { method: "POST" });
        setNotice("sync-notice", "已开始连续执行整个队列。");
        await refreshStatus();
      });

      document.getElementById("pending-select-all").onclick = () => {
        for (const item of latestPendingItems) {
          if (item?.path) pendingSelection.add(item.path);
        }
        pendingSelectionTouched = true;
        renderPendingTree(latestPendingItems);
      };
      document.getElementById("pending-clear-all").onclick = () => {
        pendingSelection.clear();
        pendingSelectionTouched = true;
        renderPendingTree(latestPendingItems);
      };
      document.getElementById("pending-run-selected").onclick = withBusy("pending-run-selected", "启动中...", async () => {
        await saveConfig();
        await call("/api/sync/start", {
          method: "POST",
          body: JSON.stringify({ mode: "download_selected", selected_paths: [...pendingSelection] }),
        });
        setNotice("sync-notice", `已开始补传 ${pendingSelection.size} 个文件。`);
        await refreshStatus();
      });
      document.getElementById("pending-run-stream").onclick = withBusy("pending-run-stream", "启动中...", async () => {
        await saveConfig();
        await call("/api/pending/run_selected_stream", {
          method: "POST",
          body: JSON.stringify({ selected_paths: [...pendingSelection] }),
        });
        setNotice("sync-notice", "已开始按勾选目录最底层顺序补传。");
        await refreshStatus();
      });

      document.getElementById("diagnose-miaochuan").onclick = withBusy("diagnose-miaochuan", "诊断中...", async () => {
        await diagnoseMiaochuanPayload();
      });
      document.getElementById("run-miaochuan").onclick = withBusy("run-miaochuan", "提交中...", async () => {
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
      });

      document.getElementById("refresh-storages").onclick = withBusy("refresh-storages", "刷新中...", refreshStorages);
      document.getElementById("refresh-drivers").onclick = withBusy("refresh-drivers", "刷新中...", loadDrivers);
      document.getElementById("driver-select").addEventListener("change", async (event) => {
        await loadDriverInfo(event.target.value);
      });
      document.getElementById("show-driver-guide").onclick = () => toggleDriverGuideDialog(true);
      document.getElementById("show-provider-guide").onclick = () => {
        const select = document.getElementById("provider-select");
        const definition = [...providerDefinitions, ...(driverCaptureBlueprint ? [driverCaptureBlueprint] : [])]
          .find((item) => item.key === select?.value);
        currentProviderGuide = getGuideForProviderDefinition(definition);
        const title = definition?.label
          ? `${definition.label} ${currentLang() === "en" ? "Guide" : currentLang() === "mix" ? "接入流程 / Guide" : "接入流程"}`
          : (currentLang() === "en" ? "Provider Access Guide" : currentLang() === "mix" ? "网盘接入流程 / Provider Access Guide" : "网盘接入流程");
        renderGuideIntoDialog(currentProviderGuide, title);
        toggleDriverGuideDialog(true);
      };
      document.getElementById("close-driver-guide").onclick = () => toggleDriverGuideDialog(false);
      document.getElementById("driver-guide-dialog").addEventListener("click", (event) => {
        if (event.target?.id === "driver-guide-dialog") toggleDriverGuideDialog(false);
      });
      document.getElementById("coverage-only-gaps").addEventListener("change", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      document.getElementById("coverage-only-onboarding-ready").addEventListener("change", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      document.getElementById("coverage-next-action-filter").addEventListener("change", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      document.getElementById("coverage-missing-item-filter").addEventListener("change", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      document.getElementById("coverage-capability-level-filter").addEventListener("change", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      document.getElementById("coverage-profile-key-filter").addEventListener("change", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      document.getElementById("coverage-onboarding-stage-filter").addEventListener("change", () => {
        setCoverageFilterState(currentCoverageFilters());
        renderAboutRegistry();
      });
      document.getElementById("export-coverage-json").onclick = async () => {
        await refreshCoverageAudit();
        if (!coverageAuditCache) return;
        downloadTextFile("cloudpan-bridge-coverage-audit.json", JSON.stringify(coverageAuditCache, null, 2), "application/json;charset=utf-8");
      };
      document.getElementById("export-coverage-md").onclick = async () => {
        const filters = currentCoverageFilters();
        const markdown = await call("/api/provider/coverage_audit_markdown", {
          method: "POST",
          body: JSON.stringify(buildCoverageAuditPayload(filters)),
          headers: { "content-type": "application/json" },
        });
        downloadTextFile("cloudpan-bridge-coverage-audit.md", markdown, "text/markdown;charset=utf-8");
      };
      document.getElementById("export-coverage-scaffold").onclick = async () => {
        const filters = currentCoverageFilters();
        const scaffold = await call("/api/provider/coverage_scaffold", {
          method: "POST",
          body: JSON.stringify(buildCoverageAuditPayload(filters)),
        });
        downloadTextFile("cloudpan-bridge-coverage-scaffold.json", JSON.stringify(scaffold, null, 2), "application/json;charset=utf-8");
      };
      document.getElementById("export-coverage-scaffold-md").onclick = async () => {
        const filters = currentCoverageFilters();
        const markdown = await call("/api/provider/coverage_scaffold_markdown", {
          method: "POST",
          body: JSON.stringify(buildCoverageAuditPayload(filters)),
          headers: { "content-type": "application/json" },
        });
        downloadTextFile("cloudpan-bridge-coverage-scaffold.md", markdown, "text/markdown;charset=utf-8");
      };
      document.getElementById("open-driver-doc").onclick = () => {
        const candidates = guideDocCandidates(currentDriverGuide);
        if (candidates.length) window.open(candidates[0], "_blank", "noopener,noreferrer");
      };
      document.getElementById("apply-driver-defaults").onclick = () => applyDriverGuideDefaults();
      document.getElementById("apply-driver-defaults-dialog").onclick = () => applyDriverGuideDefaults();
      document.getElementById("start-provider-capture").onclick = withBusy("start-provider-capture", "抓取中...", async () => {
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
      });
      document.getElementById("apply-provider-fields").onclick = withBusy("apply-provider-fields", "回填中...", async () => {
        await applyCapturedProviderFields();
      });
      document.getElementById("create-storage").onclick = withBusy("create-storage", "创建中...", async () => {
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
      });

      document.getElementById("clear-logs").onclick = withBusy("clear-logs", "清理中...", async () => {
        await call("/api/logs/clear", { method: "POST" });
        await refreshStatus();
      });
    }

    async function bootstrap() {
      initTabs();
      applyI18n();
      bindEvents();
      const panelState = getPanelState();
      toggleDrawer(panelState.logsVisible !== false);
      await ensureAuthorizedAndBootstrap(true);
    }

    bootstrap().catch((error) => {
      document.getElementById("logs").textContent = `初始化失败: ${error.message}`;
    });
  
