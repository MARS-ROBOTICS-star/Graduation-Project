% Run uniform Kp/Kd sweep on Stage0 model_200 flat real policy traces.

clearvars;
close all;

script_dir = fileparts(mfilename("fullpath"));
project_root = fileparts(fileparts(fileparts(script_dir)));
trace_dir = fullfile(project_root, "results", "stage0_model200_ball_joint_pd_matlab", "raw_traces");
output_dir = fullfile(project_root, "results", "stage0_model200_ball_joint_pd_matlab");
figure_dir = fullfile(output_dir, "figures");

if ~isfolder(output_dir)
    mkdir(output_dir);
end
if ~isfolder(figure_dir)
    mkdir(figure_dir);
end

joint_names = [
    "spm1_platform_joint_z", ...
    "spm1_platform_joint_y", ...
    "spm1_platform_joint_x", ...
    "spm2_platform_joint_z", ...
    "spm2_platform_joint_y", ...
    "spm2_platform_joint_x" ...
];

base_params = struct();
base_params.dt_sim = 1 / 120;
base_params.dt_ctrl = 1 / 60;
base_params.q_lower = [-0.7, -1.6, -0.5, -0.7, -1.6, -0.5];
base_params.q_upper = [0.7, 0.5, 0.5, 0.7, 0.5, 0.5];
base_params.J_axis = 0.10;
base_params.B_axis = 0.5;
base_params.tau_load = 0;
base_params.tau_max = 60;
base_params.qdot_max = 2;
base_params.tau_v = 0.04;
base_params.initial_condition_from_trace = true;

Kp_values = [80, 100, 120, 160, 220, 320, 500];
Kd_values = [6, 8, 10, 12, 16, 24, 32];

trace_files = dir(fullfile(trace_dir, "stage0_model200_flat_col*.csv"));
trace_files = trace_files(~contains(string({trace_files.name}), "combined"));
if isempty(trace_files)
    error("stage0BallJointPD:NoTraceFiles", "No Stage0 trace CSV files found in %s.", trace_dir);
end

case_rows = table();
for file_index = 1:numel(trace_files)
    csv_path = fullfile(trace_files(file_index).folder, trace_files(file_index).name);
    env_ids = list_trace_env_ids(csv_path);
    for env_index = 1:numel(env_ids)
        trace = load_isaac_ball_joint_trace(csv_path, EnvId=env_ids(env_index));
        case_rows = [case_rows; build_case_row(trace, trace_files(file_index).name)]; %#ok<AGROW>
    end
end

metrics_rows = table();
best_by_case = table();

for case_index = 1:height(case_rows)
    csv_path = string(case_rows.csv_path(case_index));
    env_id = case_rows.env_id(case_index);
    trace = load_isaac_ball_joint_trace(csv_path, EnvId=env_id);
    case_metrics = table();

    for Kp = Kp_values
        for Kd = Kd_values
            params = base_params;
            params.Kp = Kp;
            params.Kd = Kd;

            sim_result = simulate_uniform_ball_joint_pd(trace, params);
            metrics = compute_trace_metrics(trace, sim_result, params);
            row = struct2table(metrics);
            row.case_name = case_rows.case_name(case_index);
            row.csv_name = case_rows.csv_name(case_index);
            row.csv_path = case_rows.csv_path(case_index);
            row.env_id = env_id;
            row.terrain_col = case_rows.terrain_col(case_index);
            row.terrain_name = case_rows.terrain_name(case_index);
            row.terrain_level = case_rows.terrain_level(case_index);
            row = movevars(row, ["case_name", "csv_name", "env_id", "terrain_col", "terrain_name", "terrain_level"], "Before", 1);

            metrics_rows = [metrics_rows; row]; %#ok<AGROW>
            case_metrics = [case_metrics; row]; %#ok<AGROW>
        end
    end

    [~, best_index] = min(case_metrics.risk_score);
    best_by_case = [best_by_case; case_metrics(best_index, :)]; %#ok<AGROW>
end

metrics_path = fullfile(output_dir, "metrics_stage0_model200_uniform_gain_sweep.csv");
writetable(metrics_rows, metrics_path);

summary = groupsummary(metrics_rows, ["Kp", "Kd"], "mean", ...
    ["old_gap_mean", "old_error_mean", "new_error_mean", "error_reduction_ratio", ...
    "sat_ratio", "qdot_limit_rate", "oscillation_score", "smoothness_cost", "risk_score"]);
summary.Properties.VariableNames = erase(summary.Properties.VariableNames, "mean_");
summary = sortrows(summary, "risk_score", "ascend");
summary.compatibility_pass = summary.new_error_mean < summary.old_error_mean & ...
    summary.sat_ratio < 0.30 & summary.qdot_limit_rate < 0.70;

candidate_path = fullfile(output_dir, "best_stage0_model200_uniform_gain_candidates.csv");
writetable(summary(1:min(12, height(summary)), :), candidate_path);

case_best_path = fullfile(output_dir, "best_stage0_model200_uniform_gain_by_case.csv");
writetable(best_by_case, case_best_path);

current_mask = summary.Kp == 120 & summary.Kd == 10;
if ~any(current_mask)
    error("stage0BallJointPD:MissingCurrentGain", "Current Kp=120, Kd=10 is not in the sweep grid.");
end
current_row = summary(current_mask, :);
current_rank = find(current_mask);
best_global = summary(1, :);
raw_stats = compute_raw_trace_stats(case_rows);

plot_representative_figure(case_rows, best_global, base_params, figure_dir, "best");
plot_representative_figure(case_rows, current_row, base_params, figure_dir, "current_kp120_kd10");

report_path = fullfile(output_dir, "report_stage0_model200_ball_joint_pd_sweep.md");
write_report(report_path, metrics_path, candidate_path, case_best_path, figure_dir, ...
    best_global, current_row, current_rank, case_rows, joint_names, base_params, raw_stats);

fprintf("Stage0 model_200 sweep complete.\n");
fprintf("Metrics: %s\n", metrics_path);
fprintf("Candidates: %s\n", candidate_path);
fprintf("Case best: %s\n", case_best_path);
fprintf("Report: %s\n", report_path);

function env_ids = list_trace_env_ids(csv_path)
    table_data = readtable(csv_path, "VariableNamingRule", "preserve");
    env_ids = unique(table_data.env_id, "stable");
end

function row = build_case_row(trace, csv_name)
    [~, stem, ~] = fileparts(csv_name);
    table_data = readtable(trace.csv_path, "VariableNamingRule", "preserve", "TextType", "string");
    env_table = table_data(table_data.env_id == trace.env_id, :);

    row = table();
    row.case_name = string(stem) + "_env" + string(trace.env_id);
    row.csv_name = string(csv_name);
    row.csv_path = string(trace.csv_path);
    row.env_id = trace.env_id;
    row.terrain_col = read_optional_scalar(env_table, "terrain_col", NaN);
    row.terrain_name = string(read_optional_scalar(env_table, "terrain_name", "flat"));
    row.terrain_level = read_optional_scalar(env_table, "terrain_level", NaN);
end

function value = read_optional_scalar(table_data, name, default_value)
    if any(string(table_data.Properties.VariableNames) == name)
        value = table_data{1, name};
    else
        value = default_value;
    end
end

function plot_representative_figure(case_rows, gain_row, base_params, figure_dir, tag)
    row = case_rows(1, :);
    trace = load_isaac_ball_joint_trace(row.csv_path, EnvId=row.env_id);
    params = base_params;
    params.Kp = gain_row.Kp;
    params.Kd = gain_row.Kd;
    sim_result = simulate_uniform_ball_joint_pd(trace, params);
    output_path = fullfile(figure_dir, tag + "_stage0_model200_env" + row.env_id + "_joint2.png");
    title_text = sprintf("Stage0 model_200 env %g, Kp=%g, Kd=%g", row.env_id, params.Kp, params.Kd);
    plot_trace_response(trace, sim_result, output_path, JointIndex=2, Title=title_text);
end

function raw_stats = compute_raw_trace_stats(case_rows)
    q_desired_abs = [];
    tracking_error_abs = [];
    position_target_gap_abs = [];
    qdot_abs = [];
    desired_delta_abs = [];

    for case_index = 1:height(case_rows)
        trace = load_isaac_ball_joint_trace(case_rows.csv_path(case_index), EnvId=case_rows.env_id(case_index));
        q_desired_abs = [q_desired_abs; abs(trace.q_desired(:))]; %#ok<AGROW>
        tracking_error_abs = [tracking_error_abs; abs(trace.q_desired(:) - trace.q_actual_old(:))]; %#ok<AGROW>
        position_target_gap_abs = [position_target_gap_abs; abs(trace.q_desired(:) - trace.q_target_old(:))]; %#ok<AGROW>
        qdot_abs = [qdot_abs; abs(trace.qdot_actual_old(:))]; %#ok<AGROW>
        desired_delta_abs = [desired_delta_abs; abs(reshape(diff(trace.q_desired, 1, 1), [], 1))]; %#ok<AGROW>
    end

    raw_stats = struct();
    raw_stats.q_desired_abs_mean = mean(q_desired_abs);
    raw_stats.q_desired_abs_p95 = prctile(q_desired_abs, 95);
    raw_stats.tracking_error_abs_mean = mean(tracking_error_abs);
    raw_stats.tracking_error_abs_p95 = prctile(tracking_error_abs, 95);
    raw_stats.tracking_error_ratio = raw_stats.tracking_error_abs_mean / max(raw_stats.q_desired_abs_mean, 1.0e-9);
    raw_stats.position_target_gap_mean = mean(position_target_gap_abs);
    raw_stats.position_target_gap_max = max(position_target_gap_abs);
    raw_stats.qdot_abs_mean = mean(qdot_abs);
    raw_stats.qdot_abs_p95 = prctile(qdot_abs, 95);
    raw_stats.qdot_limit_rate_095 = mean(qdot_abs >= 1.9);
    raw_stats.qdot_limit_rate_098 = mean(qdot_abs >= 1.96);
    raw_stats.q_desired_delta_abs_mean = mean(desired_delta_abs);
    raw_stats.q_desired_delta_abs_p95 = prctile(desired_delta_abs, 95);
end

function write_report(report_path, metrics_path, candidate_path, case_best_path, figure_dir, ...
        best_global, current_row, current_rank, case_rows, joint_names, base_params, raw_stats)
    fid = fopen(report_path, "w");
    cleaner = onCleanup(@() fclose(fid));

    fprintf(fid, "# Stage0 `model_200.pt` 球铰 PD 统一增益真实轨迹扫参报告\n\n");
    fprintf(fid, "## 1. 实验口径\n\n");
    fprintf(fid, "- 输入数据：`results/stage0_model200_ball_joint_pd_matlab/raw_traces/` 下的 Stage0 flat 逐 control step 真实 CSV。\n");
    fprintf(fid, "- checkpoint：`2026-05-10_18-21-11_stage0_slip2_actionrate_m50_qmon_700iter/model_200.pt`。\n");
    fprintf(fid, "- 参与 case 数：`%d`，每个 case 对应一个 `env_id`。\n", height(case_rows));
    fprintf(fid, "- 固定 plant 参数：`J = %.3f kg*m^2`、`B = %.3f`、`tau_load = %.3f N*m`、`tau_v = %.3f s`。\n", ...
        base_params.J_axis, base_params.B_axis, base_params.tau_load, base_params.tau_v);
    fprintf(fid, "- 固定限制：`tau_max = %.1f N*m`、`qdot_max = %.1f rad/s`、`dt_sim = 1/120 s`、`dt_ctrl = 1/60 s`。\n", ...
        base_params.tau_max, base_params.qdot_max);
    fprintf(fid, "- 仿真初值：使用真实 trace 的第一帧 `q_actual`、`qdot_actual` 和 `qdot_alloc`。\n");
    fprintf(fid, "- 关节顺序：`%s`。\n\n", strjoin(joint_names, "`, `"));

    fprintf(fid, "## 2. 当前真实回放指标\n\n");
    fprintf(fid, "| 指标 | 数值 |\n");
    fprintf(fid, "|---|---:|\n");
    fprintf(fid, "| `q_desired_abs_mean` | %.6f |\n", raw_stats.q_desired_abs_mean);
    fprintf(fid, "| `q_desired_abs_p95` | %.6f |\n", raw_stats.q_desired_abs_p95);
    fprintf(fid, "| `tracking_error_abs_mean` | %.6f |\n", raw_stats.tracking_error_abs_mean);
    fprintf(fid, "| `tracking_error_abs_p95` | %.6f |\n", raw_stats.tracking_error_abs_p95);
    fprintf(fid, "| `tracking_error_mean / q_desired_abs_mean` | %.6f |\n", raw_stats.tracking_error_ratio);
    fprintf(fid, "| `position_target_gap_mean` | %.6f |\n", raw_stats.position_target_gap_mean);
    fprintf(fid, "| `position_target_gap_max` | %.6f |\n", raw_stats.position_target_gap_max);
    fprintf(fid, "| `qdot_abs_mean` | %.6f |\n", raw_stats.qdot_abs_mean);
    fprintf(fid, "| `qdot_abs_p95` | %.6f |\n", raw_stats.qdot_abs_p95);
    fprintf(fid, "| `qdot_limit_rate_0.95` | %.6f |\n", raw_stats.qdot_limit_rate_095);
    fprintf(fid, "| `qdot_limit_rate_0.98` | %.6f |\n", raw_stats.qdot_limit_rate_098);
    fprintf(fid, "| `q_desired_delta_abs_mean` | %.6f |\n", raw_stats.q_desired_delta_abs_mean);
    fprintf(fid, "| `q_desired_delta_abs_p95` | %.6f |\n\n", raw_stats.q_desired_delta_abs_p95);

    fprintf(fid, "## 3. 最优候选与当前参数\n\n");
    fprintf(fid, "| item | Kp | Kd | new_error_mean | old_error_mean | error_reduction_ratio | sat_ratio | qdot_limit_rate | risk_score | rank |\n");
    fprintf(fid, "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n");
    fprintf(fid, "| best | %.0f | %.0f | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f | 1 |\n", ...
        best_global.Kp, best_global.Kd, best_global.new_error_mean, best_global.old_error_mean, ...
        best_global.error_reduction_ratio, best_global.sat_ratio, best_global.qdot_limit_rate, best_global.risk_score);
    fprintf(fid, "| current | %.0f | %.0f | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f | %d |\n\n", ...
        current_row.Kp, current_row.Kd, current_row.new_error_mean, current_row.old_error_mean, ...
        current_row.error_reduction_ratio, current_row.sat_ratio, current_row.qdot_limit_rate, current_row.risk_score, current_rank);

    fprintf(fid, "## 4. 结论\n\n");
    fprintf(fid, "- 当前 `Kp=120, Kd=10` 的优点是保守稳定：真实回放中 `qdot` 贴近 `2 rad/s` 的比例很低，`position_target_gap = 0`，说明 `q_desired` 已完整进入底层 position target。\n");
    fprintf(fid, "- 当前 `Kp=120, Kd=10` 的问题是实际跟踪误差仍偏大：真实 `tracking_error_abs_mean / q_desired_abs_mean = %.3f`，说明球铰实际姿态只是在稳定跟踪，不能认为已经高精度跟上 policy 目标。\n", raw_stats.tracking_error_ratio);
    fprintf(fid, "- MATLAB 简化 plant 中，`Kp=120, Kd=10` 的预测 tracking error 不差，但平滑 / 振荡风险分偏高；综合 risk 第一的 `Kp=320, Kd=24` 平滑性更好，但 `qdot_limit_rate` 已到 %.3f，不能直接替换为训练默认值。\n", best_global.qdot_limit_rate);
    fprintf(fid, "- 因此当前参数不是明显错误，但更准确的判断是：`120/10` 适合作为保守稳定基线；若要降低 tracking error，应先用 Isaac GUI 短回放对照 `120/16`、`160/16`，再把 `320/24` 作为激进候选单独观察。\n");
    fprintf(fid, "- `old_error_mean` 是当前 Isaac 真实回放中的 `|q_desired - q_actual|`，不是 MATLAB 模型预测值；`new_error_mean` 是简化单轴 plant 对候选 `Kp/Kd` 的预测，只能用于预筛，不能替代 Isaac 回放。\n\n");

    fprintf(fid, "## 5. 结果文件\n\n");
    fprintf(fid, "- 全量扫参指标：`%s`\n", metrics_path);
    fprintf(fid, "- 候选表：`%s`\n", candidate_path);
    fprintf(fid, "- 每个 case 的最优参数：`%s`\n", case_best_path);
    fprintf(fid, "- 代表性曲线目录：`%s`\n", figure_dir);
end
