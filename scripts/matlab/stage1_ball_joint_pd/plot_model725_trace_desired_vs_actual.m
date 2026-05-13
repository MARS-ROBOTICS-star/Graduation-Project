% Plot q_desired and Isaac q_actual from the model_725 30 Hz trace directly.
%
% Optional variables before running:
%   trace_csv_path : CSV path to inspect.
%   trace_env_id   : env_id inside the CSV.
%   export_png     : true/false, whether to save a PNG copy.
%   Kp, Kd         : gains used to estimate the ball-joint PD torque.
%   tau_max        : torque limit used by the PD drive.

script_dir = fileparts(mfilename("fullpath"));
project_root = fileparts(fileparts(fileparts(script_dir)));
trace_root = fullfile(project_root, "results", ...
    "stage1_model725_allcols_30hz_fine_pd_2026-05-12", "raw_traces");

if exist("trace_csv_path", "var") ~= 1 || strlength(string(trace_csv_path)) == 0
    trace_csv_path = fullfile(trace_root, "model725_allcols_30hz_col05_stairs_down.csv");
end

if exist("trace_env_id", "var") == 1 && ~isempty(trace_env_id)
    trace = load_isaac_ball_joint_trace(trace_csv_path, EnvId=trace_env_id);
else
    trace = load_isaac_ball_joint_trace(trace_csv_path);
    trace_env_id = trace.env_id;
end

if exist("export_png", "var") ~= 1
    export_png = true;
end

if exist("Kp", "var") ~= 1
    Kp = 170;
end
if exist("Kd", "var") ~= 1
    Kd = 30;
end
if exist("tau_max", "var") ~= 1
    tau_max = 60;
end
q_lower = [-0.7, -1.6, -0.5, -0.7, -1.6, -0.5];
q_upper = [0.7, 0.5, 0.5, 0.7, 0.5, 0.5];
q_target = min(max(trace.q_desired, q_lower), q_upper);
tau_raw = Kp .* (q_target - trace.q_actual) - Kd .* trace.qdot_actual;
tau_estimated = min(max(tau_raw, -tau_max), tau_max);

joint_titles = [
    "J1 spm1 z yaw", ...
    "J2 spm1 y pitch", ...
    "J3 spm1 x roll", ...
    "J4 spm2 z yaw", ...
    "J5 spm2 y pitch", ...
    "J6 spm2 x roll" ...
];

fig = figure("Color", "white", "Name", "model_725 q_desired vs Isaac actual", ...
    "Position", [80, 80, 1500, 900]);
tiledlayout(fig, 3, 2, "TileSpacing", "compact", "Padding", "compact");

for joint_index = 1:6
    ax = nexttile;
    plot(trace.t, trace.q_desired(:, joint_index), "Color", [0.05, 0.05, 0.05], "LineWidth", 1.8);
    hold on;
    plot(trace.t, trace.q_actual(:, joint_index), "Color", [0.00, 0.45, 0.70], "LineWidth", 1.6);
    grid(ax, "on");
    ax.Box = "on";
    ax.FontName = "Arial";
    ax.FontSize = 12;
    title(joint_titles(joint_index), "Interpreter", "none");
    xlabel("Time (s)");
    ylabel("Angle (rad)");
    legend("q desired", "Isaac actual", "Location", "best", "Box", "off");
end

sgtitle(sprintf("model_725 30 Hz trace: %s, env_id=%g", ...
    get_file_name(trace_csv_path), trace_env_id), "Interpreter", "none");

torque_fig = figure("Color", "white", "Name", "model_725 estimated ball-joint torque", ...
    "Position", [120, 120, 1500, 900]);
tiledlayout(torque_fig, 3, 2, "TileSpacing", "compact", "Padding", "compact");

for joint_index = 1:6
    ax = nexttile;
    plot(trace.t, tau_estimated(:, joint_index), "Color", [0.49, 0.18, 0.56], "LineWidth", 1.5);
    hold on;
    yline(tau_max, "--", "Color", [0.65, 0.65, 0.65], "LineWidth", 1.0);
    yline(-tau_max, "--", "Color", [0.65, 0.65, 0.65], "LineWidth", 1.0);
    grid(ax, "on");
    ax.Box = "on";
    ax.FontName = "Arial";
    ax.FontSize = 12;
    title(joint_titles(joint_index), "Interpreter", "none");
    xlabel("Time (s)");
    ylabel("Torque (N*m)");
    legend("estimated PD torque", "limit", "Location", "best", "Box", "off");
end

sgtitle(sprintf("Estimated ball-joint PD torque: Kp=%g, Kd=%g, tau_max=%g N*m", ...
    Kp, Kd, tau_max), "Interpreter", "none");

if export_png
    output_dir = fullfile(project_root, ...
        "results", "stage1_model725_allcols_30hz_fine_pd_2026-05-12", "trace_figures");
    if ~isfolder(output_dir)
        mkdir(output_dir);
    end
    output_name = sprintf("desired_vs_isaac_actual_env%g_%s.png", ...
        trace_env_id, erase(get_file_name(trace_csv_path), ".csv"));
    output_path = fullfile(output_dir, output_name);
    exportgraphics(fig, output_path, "Resolution", 200, "BackgroundColor", "white");
    fprintf("Saved trace figure: %s\n", output_path);

    torque_output_name = sprintf("estimated_torque_kp%g_kd%g_env%g_%s.png", ...
        Kp, Kd, trace_env_id, erase(get_file_name(trace_csv_path), ".csv"));
    torque_output_path = fullfile(output_dir, torque_output_name);
    exportgraphics(torque_fig, torque_output_path, "Resolution", 200, "BackgroundColor", "white");
    fprintf("Saved torque figure: %s\n", torque_output_path);
end

function name = get_file_name(path_value)
    [~, base_name, extension] = fileparts(path_value);
    name = string(base_name) + string(extension);
end
