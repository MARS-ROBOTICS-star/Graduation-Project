function metrics = compute_trace_metrics(trace, sim_result, params)
%COMPUTE_TRACE_METRICS Compute per-trace scalar metrics for one PD candidate.

arguments
    trace (1, 1) struct
    sim_result (1, 1) struct
    params (1, 1) struct
end

old_gap = abs(trace.q_desired - trace.q_target_old);
old_error = abs(trace.q_desired - trace.q_actual_old);
new_error = abs(sim_result.q_target_new - sim_result.q_sim_new);
qdot_abs = abs(sim_result.qdot_sim_new);
tau_abs = abs(sim_result.tau_sim_new);

old_qdot_rms = rms_all(trace.qdot_actual_old);
new_qdot_rms = rms_all(sim_result.qdot_sim_new);

qdot_sign = sign(sim_result.qdot_sim_new);
qdot_sign(abs(sim_result.qdot_sim_new) < 1.0e-4) = 0;
sign_changes = abs(diff(qdot_sign, 1, 1)) > 1;
duration_s = max(trace.t(end) - trace.t(1), params.dt_ctrl);

metrics = struct();
metrics.num_samples = size(trace.q_desired, 1);
metrics.duration_s = duration_s;
metrics.Kp = params.Kp;
metrics.Kd = params.Kd;
metrics.J_axis = params.J_axis;
metrics.B_axis = params.B_axis;
metrics.tau_load = params.tau_load;
metrics.tau_v = params.tau_v;
metrics.old_gap_mean = mean(old_gap, "all");
metrics.old_error_mean = mean(old_error, "all");
metrics.new_error_mean = mean(new_error, "all");
metrics.rms_target_error_new = rms_all(new_error);
metrics.p95_target_error_new = prctile(new_error(:), 95);
metrics.error_reduction_ratio = safe_ratio(metrics.old_error_mean - metrics.new_error_mean, metrics.old_error_mean);
metrics.max_abs_qdot_new = max(qdot_abs, [], "all");
metrics.qdot_limit_rate = mean(qdot_abs(:) > 0.98 * params.qdot_max);
metrics.sat_ratio = mean(tau_abs(:) > 0.98 * params.tau_max);
metrics.max_abs_tau_new = max(tau_abs, [], "all");
metrics.oscillation_score = sum(sign_changes, "all") / duration_s / size(trace.q_desired, 2);
metrics.smoothness_cost = mean(diff(sim_result.qdot_sim_new, 1, 1).^2, "all");
metrics.qdot_alloc_rmse = rms_all(sim_result.qdot_alloc_new - sim_result.qdot_sim_new);
metrics.qdot_alloc_smoothness = mean(diff(sim_result.qdot_alloc_new, 1, 1).^2, "all");
metrics.old_qdot_rms = old_qdot_rms;
metrics.new_qdot_rms = new_qdot_rms;
metrics.new_vs_old_qdot_ratio = safe_ratio(new_qdot_rms, old_qdot_rms);
metrics.risk_score = compute_risk_score(metrics);
end

function value = rms_all(values)
    value = sqrt(mean(values(:).^2));
end

function value = safe_ratio(numerator, denominator)
    value = numerator ./ max(abs(denominator), 1.0e-9);
end

function score = compute_risk_score(metrics)
    saturation_penalty = 2.0 * max(0.0, metrics.sat_ratio - 0.30);
    qdot_penalty = 2.0 * max(0.0, metrics.qdot_limit_rate - 0.30);
    negative_reduction_penalty = 2.0 * max(0.0, -metrics.error_reduction_ratio);
    oscillation_penalty = 0.01 * metrics.oscillation_score;
    smoothness_penalty = 0.20 * metrics.smoothness_cost;
    score = metrics.new_error_mean + saturation_penalty + qdot_penalty + ...
        negative_reduction_penalty + oscillation_penalty + smoothness_penalty;
end
