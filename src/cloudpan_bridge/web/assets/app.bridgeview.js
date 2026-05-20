(function () {
  function pickText(ctx, zh, en) {
    return ctx.currentLang() === "en" ? en : ctx.currentLang() === "mix" ? `${zh} / ${en}` : zh;
  }

  function bridgePendingReasonText(ctx, key) {
    const mapping = {
      provider_api_bridge_not_executed_yet: ["源端已进入 API 准备态，但当前版本还没真正执行直连补指纹", "Source bridge is API-ready, but the real provider enrichment has not executed yet"],
      non_fast_hashes_only_after_session_snapshot: ["源端只补出了非快传关键指纹，暂时还不能直接快传", "Only non-fast fingerprints were recovered, so direct fast upload is still unavailable"],
      bridge_not_registered: ["当前源端还没有注册 bridge executor", "No bridge executor is registered for this source yet"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function bridgeExecutionStateText(ctx, key) {
    const mapping = {
      session_snapshot_normalized: ["已按会话快照归并指纹", "Session snapshot normalized"],
      api_bridge_prepared_but_not_executed: ["已准备 API 桥接，但尚未真正执行", "API bridge prepared but not executed"],
      bridge_not_registered: ["未注册桥接执行器", "Bridge executor not registered"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function bridgeProviderStageText(ctx, key) {
    const mapping = {
      session_snapshot: ["会话快照阶段", "Session snapshot stage"],
      api_placeholder: ["API 占位阶段", "API placeholder stage"],
      none: ["未进入桥接阶段", "No bridge stage"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function transferReasonCodeText(ctx, key) {
    const mapping = {
      fast_hash_ready: ["已具备目标端快传指纹", "Target-ready fast-upload fingerprint is available"],
      small_file_auto_fallback: ["命中小文件自动补传阈值", "Matched the small-file auto fallback threshold"],
      full_download_fallback_allowed: ["当前模式允许完整下载补传", "The current run mode allows full download-upload fallback"],
      full_stream_fallback_allowed: ["当前模式允许普通流式上传", "The current run mode allows normal stream upload"],
      fallback_available_but_deferred: ["目标端可降级上传，但本轮先只记录待补传", "Fallback upload is available, but this run keeps it as pending only"],
      provider_api_bridge_not_executed_yet: ["源端 API 桥接未真正执行，当前只看到候选哈希", "The source API bridge is not executed yet, so only candidate hashes are visible"],
      non_fast_hashes_only_after_session_snapshot: ["源端只补出非快传关键指纹", "Only non-fast fingerprints were recovered from the source"],
      target_hash_not_supported: ["源端候选哈希存在，但目标端不认这些哈希", "Candidate hashes exist, but the target does not recognize them"],
      target_no_fast_capability: ["当前目标端本身不支持元数据秒传", "The current target does not provide metadata-based fast upload"],
      no_auto_fallback: ["当前未允许自动降级补传", "Automatic fallback is not enabled for this run"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function transferModeText(ctx, key) {
    const mapping = {
      fast_upload: ["优先快传", "Fast upload first"],
      stream_upload: ["普通流式上传", "Normal stream upload"],
      download_upload: ["下载后上传", "Download then upload"],
      record_pending_only: ["仅记录待补传", "Record as pending only"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function bridgeTransportHintText(ctx, key) {
    const mapping = {
      cookie_or_session_snapshot: ["Cookie 或会话快照", "Cookie or session snapshot"],
      cookie_snapshot: ["Cookie 快照", "Cookie snapshot"],
      cookie_plus_bdstoken: ["Cookie + bdstoken", "Cookie + bdstoken"],
      authorization_plus_device_id: ["Authorization + device_id", "Authorization + device_id"],
      refresh_token_or_authorization: ["Refresh Token 或 Authorization", "Refresh token or Authorization"],
      openlist_only: ["仅 OpenList 元数据", "OpenList metadata only"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function bridgeExpectationText(ctx, hashes) {
    const items = Array.isArray(hashes) ? hashes.filter(Boolean) : [];
    if (!items.length) return "-";
    return items.join(", ");
  }

  function bridgeMaturityText(ctx, key) {
    const mapping = {
      session_snapshot_ready: ["会话快照已就绪", "Session snapshot ready"],
      api_capture_ready_pending_provider_enrich: ["API 准备态已就绪", "API preparation ready"],
      capture_missing: ["仍缺关键登录态", "Missing required capture fields"],
      not_registered: ["未注册专用 bridge", "No dedicated bridge registered"],
      unknown: ["需要人工复核", "Needs manual review"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function formatCountMap(ctx, counts, formatter) {
    return Object.entries(counts || {}).map(([key, value]) => `${formatter(ctx, key)}: ${value}`).join(" | ") || "-";
  }

  window.CloudPanBridgeBridgeView = {
    bridgePendingReasonText,
    bridgeExecutionStateText,
    bridgeProviderStageText,
    transferReasonCodeText,
    transferModeText,
    bridgeTransportHintText,
    bridgeExpectationText,
    bridgeMaturityText,
    formatCountMap,
  };
})();
