% Initialize the Stage1 ball-joint PD Simulink workspace.
%
% If trace_csv_path exists in the workspace and points to a CSV file, this
% script loads that IsaacLab control-step trace. Otherwise it creates a
% deterministic demo trace for Simulink sanity checks.

script_dir = fileparts(mfilename("fullpath"));
project_root = fileparts(fileparts(fileparts(script_dir)));
trace_root = fullfile(project_root, "results", "stage1_ball_joint_pd_matlab", "raw_traces");

joint_names = [
    "spm1_platform_joint_z", ...
    "spm1_platform_joint_y", ...
    "spm1_platform_joint_x", ...
    "spm2_platform_joint_z", ...
    "spm2_platform_joint_y", ...
    "spm2_platform_joint_x" ...
];

dt_sim = 1 / 120;
dt_ctrl = 1 / 60;
stop_time_s = 20;

q_lower = [-0.7, -1.6, -0.5, -0.7, -1.6, -0.5];
q_upper = [0.7, 0.5, 0.5, 0.7, 0.5, 0.5];

Kp = 120;
Kd = 10;
J_axis = 0.10;
B_axis = 0.5;
tau_load = 0;
tau_max = 60;
qdot_max = 2;
tau_v = 0.04;
alpha_v = 1 - exp(-dt_ctrl / tau_v);

planner_gain = 8;
planner_qdot_limits = [1.5, 1.5, 1.5, 1.5, 1.5, 1.5];

if exist("trace_csv_path", "var") == 1 && strlength(string(trace_csv_path)) > 0 && isfile(trace_csv_path)
    if exist("trace_env_id", "var") == 1 && ~isempty(trace_env_id)
        trace = load_isaac_ball_joint_trace(trace_csv_path, EnvId=trace_env_id);
    else
        trace = load_isaac_ball_joint_trace(trace_csv_path);
        trace_env_id = trace.env_id;
    end
    t = trace.t(:);
    q_desired = trace.q_desired;
    q_target_old = trace.q_target_old;
    q_actual_old = trace.q_actual_old;
    qdot_actual_old = trace.qdot_actual_old;
    qdot_cmd_old = trace.qdot_cmd_old;
    stop_time_s = t(end);
else
    trace_csv_path = "";
    trace_env_id = [];
    t = (0:dt_ctrl:stop_time_s)';
    q_desired = build_demo_q_desired(t, q_lower, q_upper);
    [q_target_old, q_actual_old, qdot_actual_old, qdot_cmd_old] = emulate_old_planner_trace( ...
        q_desired, q_lower, q_upper, planner_gain, planner_qdot_limits, Kp, Kd, ...
        J_axis, B_axis, tau_load, tau_max, qdot_max, dt_ctrl);
end

q_desired_ts = timeseries(q_desired, t, "Name", "q_desired");
q_target_old_ts = timeseries(q_target_old, t, "Name", "q_target_old");
q_actual_old_ts = timeseries(q_actual_old, t, "Name", "q_actual_old");
qdot_actual_old_ts = timeseries(qdot_actual_old, t, "Name", "qdot_actual_old");
qdot_cmd_old_ts = timeseries(qdot_cmd_old, t, "Name", "qdot_cmd_old");

function q_desired = build_demo_q_desired(t, q_lower, q_upper)
    q_desired = zeros(numel(t), 6);

    q_desired(:, 2) = q_desired(:, 2) + 0.18 * (t >= 2.0);
    q_desired(:, 2) = q_desired(:, 2) - 0.35 * (t >= 6.0);
    q_desired(:, 2) = q_desired(:, 2) + 0.22 * (t >= 10.0);
    q_desired(:, 5) = q_desired(:, 5) - 0.20 * (t >= 3.5);
    q_desired(:, 5) = q_desired(:, 5) + 0.40 * (t >= 8.0);
    q_desired(:, 5) = q_desired(:, 5) - 0.25 * (t >= 13.0);

    sine_gate = double(t >= 11.0);
    q_desired(:, 1) = 0.12 * sin(2 * pi * 0.7 * t) .* sine_gate;
    q_desired(:, 4) = -0.10 * sin(2 * pi * 0.5 * t) .* sine_gate;
    q_desired(:, 3) = 0.08 * sin(2 * pi * 1.0 * t) .* double(t >= 14.0);
    q_desired(:, 6) = -0.08 * sin(2 * pi * 1.0 * t) .* double(t >= 14.0);

    q_desired = min(max(q_desired, q_lower), q_upper);
end

function [q_target_old, q_actual_old, qdot_actual_old, qdot_cmd_old] = emulate_old_planner_trace( ...
        q_desired, q_lower, q_upper, planner_gain, planner_qdot_limits, Kp, Kd, ...
        J_axis, B_axis, tau_load, tau_max, qdot_max, dt)

    num_steps = size(q_desired, 1);
    q_target_old = zeros(num_steps, 6);
    q_actual_old = zeros(num_steps, 6);
    qdot_actual_old = zeros(num_steps, 6);
    qdot_cmd_old = zeros(num_steps, 6);
    q = zeros(1, 6);
    qdot = zeros(1, 6);

    for k = 1:num_steps
        qdot_cmd = min(max(planner_gain .* (q_desired(k, :) - q), -planner_qdot_limits), planner_qdot_limits);
        q_target = min(max(q + dt .* qdot_cmd, q_lower), q_upper);

        tau_raw = Kp .* (q_target - q) - Kd .* qdot;
        tau = min(max(tau_raw, -tau_max), tau_max);
        qddot = (tau - B_axis .* qdot - tau_load) ./ J_axis;
        qdot = min(max(qdot + dt .* qddot, -qdot_max), qdot_max);
        q = min(max(q + dt .* qdot, q_lower), q_upper);

        q_target_old(k, :) = q_target;
        q_actual_old(k, :) = q;
        qdot_actual_old(k, :) = qdot;
        qdot_cmd_old(k, :) = qdot_cmd;
    end
end
