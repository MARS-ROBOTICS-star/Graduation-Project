% Initialize the Stage1 ball-joint PD Simulink workspace.
%
% This script loads the same 30 Hz model_725 trace family used by the latest
% Kp/Kd fine sweep. Set trace_csv_path and trace_env_id before running this
% script to inspect a different terrain column or environment.

script_dir = fileparts(mfilename("fullpath"));
project_root = fileparts(fileparts(fileparts(script_dir)));
trace_root = fullfile(project_root, "results", ...
    "stage1_model725_allcols_30hz_fine_pd_2026-05-12", "raw_traces");
default_trace_csv_path = fullfile(trace_root, "model725_allcols_30hz_col05_stairs_down.csv");

joint_names = [
    "spm1_platform_joint_z", ...
    "spm1_platform_joint_y", ...
    "spm1_platform_joint_x", ...
    "spm2_platform_joint_z", ...
    "spm2_platform_joint_y", ...
    "spm2_platform_joint_x" ...
];

dt_sim = 1 / 120;
dt_ctrl = 1 / 30;

q_lower = [-0.7, -1.6, -0.5, -0.7, -1.6, -0.5];
q_upper = [0.7, 0.5, 0.5, 0.7, 0.5, 0.5];

Kp = 170;
Kd = 30;
J_axis = 0.10;
B_axis = 0.5;
tau_load = 0;
tau_max = 60;
qdot_max = 2;
tau_v = 0.04;
alpha_v = 1 - exp(-dt_ctrl / tau_v);

if exist("trace_csv_path", "var") ~= 1 || strlength(string(trace_csv_path)) == 0
    trace_csv_path = default_trace_csv_path;
end
if ~isfile(trace_csv_path)
    error("stage1BallJointPD:MissingTrace", ...
        "Trace CSV does not exist: %s", string(trace_csv_path));
end

if exist("trace_env_id", "var") == 1 && ~isempty(trace_env_id)
    trace = load_isaac_ball_joint_trace(trace_csv_path, EnvId=trace_env_id);
else
    trace = load_isaac_ball_joint_trace(trace_csv_path);
    trace_env_id = trace.env_id;
end
t = trace.t(:);
q_desired = trace.q_desired;
q_target_trace = trace.q_target;
q_actual_trace = trace.q_actual;
qdot_actual_trace = trace.qdot_actual;
qdot_alloc_trace = trace.qdot_alloc;
stop_time_s = t(end);

q_desired_ts = timeseries(q_desired, t, "Name", "q_desired");
q_target_trace_ts = timeseries(q_target_trace, t, "Name", "q_target_trace");
q_actual_trace_ts = timeseries(q_actual_trace, t, "Name", "q_actual_trace");
qdot_actual_trace_ts = timeseries(qdot_actual_trace, t, "Name", "qdot_actual_trace");
qdot_alloc_trace_ts = timeseries(qdot_alloc_trace, t, "Name", "qdot_alloc_trace");
