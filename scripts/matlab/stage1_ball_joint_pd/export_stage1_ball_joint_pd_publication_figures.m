% Export publication-ready white-background figures for the Simulink model.

init_stage1_ball_joint_pd_workspace;

model_name = "stage1_ball_joint_pd_uniform";
model_file = fullfile(script_dir, model_name + ".slx");
if ~bdIsLoaded(model_name)
    load_system(model_file);
end

set_param(model_name, "SimulationCommand", "update");

trace.t = timeseries_time(q_desired_ts);
trace.q_desired = timeseries_matrix(q_desired_ts);
trace.q_target_old = timeseries_matrix(q_target_old_ts);
trace.q_actual_old = timeseries_matrix(q_actual_old_ts);
trace.qdot_actual_old = timeseries_matrix(qdot_actual_old_ts);
trace.qdot_cmd_old = timeseries_matrix(qdot_cmd_old_ts);

params = struct();
params.Kp = Kp;
params.Kd = Kd;
params.J_axis = J_axis;
params.B_axis = B_axis;
params.tau_load = tau_load;
params.tau_max = tau_max;
params.qdot_max = qdot_max;
params.tau_v = tau_v;
params.dt_sim = dt_sim;
params.dt_ctrl = dt_ctrl;
params.q_lower = q_lower;
params.q_upper = q_upper;
sim_result = simulate_uniform_ball_joint_pd(trace, params);

output_dir = fullfile(project_root, "results", "stage1_ball_joint_pd_matlab", "publication_figures");
if ~isfolder(output_dir)
    mkdir(output_dir);
end

if exist("export_svg", "var") ~= 1
    export_svg = false;
end

joint_titles = [
    "J1 spm1 z yaw", ...
    "J2 spm1 y pitch", ...
    "J3 spm1 x roll", ...
    "J4 spm2 z yaw", ...
    "J5 spm2 y pitch", ...
    "J6 spm2 x roll" ...
];
joint_file_names = [
    "j1_spm1_z_yaw", ...
    "j2_spm1_y_pitch", ...
    "j3_spm1_x_roll", ...
    "j4_spm2_z_yaw", ...
    "j5_spm2_y_pitch", ...
    "j6_spm2_x_roll" ...
];

for joint_index = 1:6
    title_text = sprintf("%s, Kp=%g, Kd=%g, tau_v=%.2f s", ...
        joint_titles(joint_index), Kp, Kd, tau_v);
    png_path = string(fullfile(output_dir, "stage1_ball_joint_pd_" + joint_file_names(joint_index) + ".png"));
    svg_path = string(fullfile(output_dir, "stage1_ball_joint_pd_" + joint_file_names(joint_index) + ".svg"));

    plot_trace_response(trace, sim_result, png_path, JointIndex=joint_index, Title=title_text, FontSize=15);
    if export_svg
        plot_trace_response(trace, sim_result, svg_path, JointIndex=joint_index, Title=title_text, FontSize=15);
    end
end

fprintf("Exported publication PNG figures to: %s\n", output_dir);

function time = timeseries_time(ts)
    time = ts.Time(:);
end

function data = timeseries_matrix(ts)
    data = squeeze(ts.Data);
    if isvector(data)
        data = data(:);
    end
    if size(data, 1) ~= numel(ts.Time) && size(data, 2) == numel(ts.Time)
        data = data.';
    end
end
