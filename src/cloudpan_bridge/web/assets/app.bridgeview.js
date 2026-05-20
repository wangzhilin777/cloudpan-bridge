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
      api_capture_cache_normalized: ["已从抓取缓存归并文件级哈希", "File-level hashes were normalized from the capture cache"],
      bridge_not_registered: ["未注册桥接执行器", "Bridge executor not registered"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function bridgeProviderStageText(ctx, key) {
    const mapping = {
      session_snapshot: ["会话快照阶段", "Session snapshot stage"],
      api_placeholder: ["API 占位阶段", "API placeholder stage"],
      api_capture_cache: ["抓取缓存归并阶段", "Capture-cache normalization stage"],
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
      api_capture_cache_partial: ["已吃到抓取缓存，但快传关键哈希仍未补齐", "The capture cache was consumed, but fast-upload hashes are still incomplete"],
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

  function nextActionHintText(ctx, key) {
    const mapping = {
      manual_review: ["需要人工复核", "Needs manual review"],
      direct_fast_upload_ready: ["可直接执行快传", "Fast upload can run directly"],
      fallback_download_upload_ready: ["可直接走下载补传", "Download-upload fallback is ready"],
      fallback_stream_upload_ready: ["可直接走普通流式上传", "Normal stream upload fallback is ready"],
      defer_to_pending_tree: ["建议先进入待补传目录树", "Prefer deferring into the pending tree first"],
      execute_provider_api_enrich: ["应先执行源端 API 补指纹", "Run source-side API enrichment first"],
      execute_provider_api_for_fast_hashes: ["应优先补齐快传关键哈希", "Prioritize recovering fast-upload hashes first"],
      extend_capture_cache_or_provider_api: ["应继续扩抓取缓存，或切到真实 API enrich", "Extend the capture cache or switch to real provider API enrichment"],
      extend_capture_cache_for_fast_hashes: ["应优先扩抓取缓存里的快传关键哈希", "Prioritize extending fast-upload hashes inside the capture cache"],
      wait_for_fast_hash_or_fallback: ["等待快传关键哈希，或转降级上传", "Wait for fast hashes or fall back to normal upload"],
      fallback_target_does_not_accept_hashes: ["目标端不认这些哈希，应转普通上传", "The target does not accept these hashes, so fall back to normal upload"],
      fallback_target_has_no_fast_upload: ["目标端无秒传能力，应直接走普通上传", "The target has no fast-upload capability, so use normal upload"],
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
      api_capture_cache_ready: ["抓取缓存补指纹已生效", "Capture-cache enrichment is active"],
      capture_missing: ["仍缺关键登录态", "Missing required capture fields"],
      not_registered: ["未注册专用 bridge", "No dedicated bridge registered"],
      unknown: ["需要人工复核", "Needs manual review"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function bridgeHonestyText(ctx, key) {
    const mapping = {
      capture_ready_normalization_only: ["已具备归并能力，但仍只到补指纹层", "Normalization is ready, but still limited to enrichment only"],
      api_prepared_not_executed: ["API 准备态已满足，但真实 provider enrich 未执行", "API preparation is satisfied, but real provider enrich is not executed"],
      capture_cache_snapshot_only: ["已消费抓取缓存，但仍不是在线直连 enrich", "The capture cache is consumed, but this is still not live direct enrichment"],
      waiting_capture: ["仍在等待关键登录态", "Still waiting for required capture fields"],
      openlist_only: ["当前只能依赖 OpenList 元数据", "Currently limited to OpenList metadata only"],
      manual_review: ["需要人工复核", "Needs manual review"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function sourceTargetRouteBucketText(ctx, key) {
    const mapping = {
      openlist_upload_path: ["先走 OpenList 源端再决定写入", "Use the OpenList source path first, then choose the write path"],
      target_upload_only: ["目标端只能普通上传", "The target only supports normal upload"],
      session_bridge_fast_candidate: ["会话桥接已具备快传候选", "Session bridge is ready for fast-upload candidates"],
      api_bridge_fast_candidate: ["API 桥接理论可补齐快传", "API bridge can theoretically recover fast-upload hashes"],
      capture_gap_before_fast: ["先补登录态再谈快传", "Capture fields must be collected before fast upload is realistic"],
      native_hash_candidate: ["OpenList 元数据已接近可快传", "OpenList metadata is already close to fast-upload readiness"],
      provider_candidate_but_fallback_first: ["有 provider 候选，但当前更适合补传", "A provider candidate exists, but fallback is still safer for now"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function sourceTargetRouteFocusText(ctx, key) {
    const mapping = {
      openlist_first: ["先看 OpenList 当前元数据覆盖率", "Inspect current OpenList metadata coverage first"],
      target_fallback_upload: ["按目标端普通上传能力规划执行", "Plan execution around the target's normal upload path"],
      validate_fast_hash_hit_rate: ["先验证快传哈希命中率", "Validate the fast-hash hit rate first"],
      provider_api_enrich: ["优先补齐 provider API enrich", "Prioritize provider API enrichment"],
      collect_provider_capture: ["先补关键登录态字段", "Collect the required capture fields first"],
      inspect_openlist_hash_coverage: ["先确认 OpenList 是否已暴露关键哈希", "Check whether OpenList already exposes the key hashes"],
      pending_tree_or_stream_upload: ["优先待补传树或普通上传", "Prefer the pending tree or normal upload first"],
    };
    const pair = mapping[String(key || "").trim()] || [key || "-", key || "-"];
    return pickText(ctx, pair[0], pair[1]);
  }

  function sourceTargetRouteHonestyText(ctx, key) {
    const mapping = {
      openlist_only_for_now: ["当前仍以 OpenList 执行为主", "Execution still primarily relies on OpenList for now"],
      target_has_no_metadata_fast_upload: ["目标端本身没有元数据秒传", "The target itself has no metadata fast-upload path"],
      session_bridge_ready_but_transport_not_direct: ["会话桥接已 ready，但真实直连传输还没落地", "The session bridge is ready, but true direct transport is not implemented yet"],
      provider_api_not_implemented_yet: ["理论 API enrich 可行，但真实实现尚未接通", "Theoretical API enrichment exists, but the real implementation is not connected yet"],
      capture_missing_before_fast_upload: ["补齐关键登录态前，不应把它当作快传可用", "Do not treat this as fast-upload ready before the required capture fields exist"],
      openlist_metadata_may_already_be_enough: ["可能只靠 OpenList 元数据就够了", "OpenList metadata may already be sufficient"],
      provider_overlap_weak: ["源端与目标端快传哈希重叠较弱", "The overlap between source and target fast hashes is weak"],
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
    bridgeHonestyText,
    sourceTargetRouteBucketText,
    sourceTargetRouteFocusText,
    sourceTargetRouteHonestyText,
    nextActionHintText,
    formatCountMap,
  };
})();
