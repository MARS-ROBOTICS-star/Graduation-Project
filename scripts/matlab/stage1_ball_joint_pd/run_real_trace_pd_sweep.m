% Run uniform Kp/Kd sweep on exported Stage1 real policy traces.

clearvars;
close all;

script_dir = fileparts(mfilename("fullpath"));
project_root = fileparts(fileparts(fileparts(script_dir)));
trace_dir = fullfile(project_root, "results", "stage1_ball_joint_pd_matlab", "raw_traces");
output_dir = fullfile(project_root, "results", "stage1_ball_joint_pd_matlab");
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
base_params.dt_ctrl = 1 / 30;
base_params.q_lower = [-0.7, -1.6, -0.5, -0.7, -1.6, -0.5];
base_params.q_upper = [0.7, 0.5, 0.5, 0.7, 0.5, 0.5];
base_params.J_axis = 0.10;
base_params.B_axis = 0.5;
base_params.tau_load = 0;
base_params.tau_max = 60;
base_params.qdot_max = 2;
base_params.tau_v = 0.05;

Kp_values = [120, 160, 220, 320, 500, 800, 1000];
Kd_values = [10, 16, 24, 32, 48, 64];

trace_files = dir(fullfile(trace_dir, "sec14_model699_flat_stairs_down_obstacles_col*.csv"));
trace_files = trace_files(~contains(string({trace_files.name}), "combined"));
if isempty(trace_files)
    error("stage1BallJointPD:NoTraceFiles", "No per-column trace CSV files found in %s.", trace_dir);
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
best_sims = containers.Map("KeyType", "char", "ValueType", "any");

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
    best_row = case_metrics(best_index, :);
    best_by_case = [best_by_case; best_row]; %#ok<AGROW>

    params = base_params;
    params.Kp = best_row.Kp;
    params.Kd = best_row.Kd;
    best_sims(char(best_row.case_name)) = simulate_uniform_ball_joint_pd(trace, params);
end

metrics_path = fullfile(output_dir, "metrics_uniform_gain_sweep.csv");
writetable(metrics_rows, metrics_path);

summary = groupsummary(metrics_rows, ["Kp", "Kd"], "mean", ...
    ["old_gap_mean", "old_error_mean", "new_error_mean", "error_reduction_ratio", ...
    "sat_ratio", "qdot_limit_rate", "oscillation_score", "smoothness_cost", "risk_score"]);
summary.Properties.VariableNames = erase(summary.Properties.VariableNames, "mean_");
summary = sortrows(summary, "risk_score", "ascend");

summary.compatibility_pass = summary.new_error_mean < summary.old_error_mean & ...
    summary.sat_ratio < 0.30 & summary.qdot_limit_rate < 0.70;

best_candidates = summary(1:min(10, height(summary)), :);
candidate_path = fullfile(output_dir, "best_uniform_gain_candidates.csv");
writetable(best_candidates, candidate_path);

case_best_path = fullfile(output_dir, "best_uniform_gain_by_case.csv");
writetable(best_by_case, case_best_path);

best_global = summary(1, :);
plot_representative_figures(case_rows, best_global, base_params, figure_dir);
report_path = fullfile(output_dir, "report_stage1_ball_joint_pd_matlab.md");
write_report(report_path, metrics_path, candidate_path, case_best_path, figure_dir, ...
    best_global, best_candidates, case_rows, joint_names, base_params);

fprintf("Sweep complete.\n");
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
    row = table();
    row.case_name = string(stem) + "_env" + string(trace.env_id);
    row.csv_name = string(csv_name);
    row.csv_path = string(trace.csv_path);
    row.env_id = trace.env_id;
    row.terrain_col = NaN;
    row.terrain_name = "";
    row.terrain_level = NaN;

    table_data = readtable(trace.csv_path, "VariableNamingRule", "preserve", "TextType", "string");
    env_table = table_data(table_data.env_id == trace.env_id, :);
    if any(string(env_table.Properties.VariableNames) == "terrain_col")
        row.terrain_col = env_table.terrain_col(1);
    end
    if any(string(env_table.Properties.VariableNames) == "terrain_name")
        row.terrain_name = string(env_table.terrain_name(1));
    end
    if any(string(env_table.Properties.VariableNames) == "terrain_level")
        row.terrain_level = env_table.terrain_level(1);
    end
end

function plot_representative_figures(case_rows, best_global, base_params, figure_dir)
    terrain_priority = ["flat", "stairs down", "discrete obstacles"];
    joint_index_by_terrain = [2, 2, 2];

    for terrain_index = 1:numel(terrain_priority)
        mask = case_rows.terrain_name == terrain_priority(terrain_index);
        if ~any(mask)
            continue;
        end
        row = case_rows(find(mask, 1, "first"), :);
        trace = load_isaac_ball_joint_trace(row.csv_path, EnvId=row.env_id);
        params = base_params;
        params.Kp = best_global.Kp;
        params.Kd = best_global.Kd;
        sim_result = simulate_uniform_ball_joint_pd(trace, params);
        safe_name = matlab.lang.makeValidName(row.case_name);
        output_path = fullfile(figure_dir, "best_global_" + safe_name + "_joint" + joint_index_by_terrain(terrain_index) + ".png");
        title_text = sprintf("%s env %g, Kp=%g, Kd=%g", row.terrain_name, row.env_id, params.Kp, params.Kd);
        plot_trace_response(trace, sim_result, output_path, ...
            JointIndex=joint_index_by_terrain(terrain_index), Title=title_text);
    end
end

function write_report(report_path, metrics_path, candidate_path, case_best_path, figure_dir, ...
        best_global, best_candidates, case_rows, joint_names, base_params)
    fid = fopen(report_path, "w");
    cleaner = onCleanup(@() fclose(fid));

    fprintf(fid, "# Stage1 球铰 PD 统一增益 MATLAB 真实轨迹扫参报告\n\n");
    fprintf(fid, "## 1. 实验口径\n\n");
    fprintf(fid, "- 输入数据：`results/stage1_ball_joint_pd_matlab/raw_traces/` 下的逐 control step 真实 CSV。\n");
    fprintf(fid, "- 轨迹覆盖：flat、stairs down、discrete obstacles；每个地形列 CSV 中所有 `env_id` 均参与统计。\n");
    fprintf(fid, "- 固定 plant 参数：`J = %.3f kg*m^2`、`B = %.3f`、`tau_load = %.3f N*m`、`tau_v = %.3f s`。\n", ...
        base_params.J_axis, base_params.B_axis, base_params.tau_load, base_params.tau_v);
    fprintf(fid, "- 固定限制：`tau_max = %.1f N*m`、`qdot_max = %.1f rad/s`、`dt_sim = 1/120 s`、`dt_ctrl = 1/30 s`。\n", ...
        base_params.tau_max, base_params.qdot_max);
    fprintf(fid, "- 扫描变量：统一 `Kp/Kd`，六个球铰轴共享同一组增益。\n\n");

    fprintf(fid, "## 2. 轨迹与关节顺序\n\n");
    fprintf(fid, "- 参与 case 数：`%d`。\n", height(case_rows));
    fprintf(fid, "- 关节顺序：`%s`。\n\n", strjoin(joint_names, "`, `"));

    fprintf(fid, "## 3. 综合推荐\n\n");
    fprintf(fid, "当前综合风险分最低的统一增益为：\n\n");
    fprintf(fid, "| Kp | Kd | new_error_mean | old_error_mean | error_reduction_ratio | sat_ratio | qdot_limit_rate | risk_score |\n");
    fprintf(fid, "|---:|---:|---:|---:|---:|---:|---:|---:|\n");
    fprintf(fid, "| %.0f | %.0f | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f |\n\n", ...
        best_global.Kp, best_global.Kd, best_global.new_error_mean, best_global.old_error_mean, ...
        best_global.error_reduction_ratio, best_global.sat_ratio, best_global.qdot_limit_rate, best_global.risk_score);

    fprintf(fid, "前 `5` 个候选如下：\n\n");
    fprintf(fid, "| rank | Kp | Kd | new_error_mean | error_reduction_ratio | sat_ratio | qdot_limit_rate | risk_score |\n");
    fprintf(fid, "|---:|---:|---:|---:|---:|---:|---:|---:|\n");
    top_n = min(5, height(best_candidates));
    for index = 1:top_n
        fprintf(fid, "| %d | %.0f | %.0f | %.6f | %.6f | %.6f | %.6f | %.6f |\n", ...
            index, best_candidates.Kp(index), best_candidates.Kd(index), best_candidates.new_error_mean(index), ...
            best_candidates.error_reduction_ratio(index), best_candidates.sat_ratio(index), ...
            best_candidates.qdot_limit_rate(index), best_candidates.risk_score(index));
    end
    fprintf(fid, "\n");

    fprintf(fid, "## 4. 结果文件\n\n");
    fprintf(fid, "- 全量扫参指标：`%s`\n", metrics_path);
    fprintf(fid, "- 综合候选表：`%s`\n", candidate_path);
    fprintf(fid, "- 每个 case 的最优参数：`%s`\n", case_best_path);
    fprintf(fid, "- 代表性曲线目录：`%s`\n\n", figure_dir);

    fprintf(fid, "## 5. 解释边界\n\n");
    fprintf(fid, "本报告只评价简化单轴 PD plant 在真实 policy 目标轨迹下的时域响应。它不能替代 Isaac 中三车体、轮地接触和地形相互作用的短回放验证。候选增益进入代码前，仍需要做 flat、stairs down、discrete obstacles 的 Isaac 短验证。\n");
end
