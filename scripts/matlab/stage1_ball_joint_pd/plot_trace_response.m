function plot_trace_response(trace, sim_result, output_path, options)
%PLOT_TRACE_RESPONSE Save a compact, white-background response figure.

arguments
    trace (1, 1) struct
    sim_result (1, 1) struct
    output_path (1, 1) string
    options.JointIndex (1, 1) double = 2
    options.Title (1, 1) string = "Stage1 ball-joint PD response"
    options.FontSize (1, 1) double = 15
end

joint_index = options.JointIndex;
colors = response_plot_colors();
fig = figure("Visible", "off", "Color", "white", "Position", [100, 100, 1280, 880]);
set(fig, "InvertHardcopy", "off");
tiledlayout(fig, 3, 1, "TileSpacing", "compact", "Padding", "compact");

nexttile;
plot(trace.t, trace.q_desired(:, joint_index), "Color", colors.desired, "LineWidth", 2.0);
hold on;
plot(trace.t, trace.q_target(:, joint_index), "--", "Color", colors.trace_target, "LineWidth", 1.7);
plot(trace.t, trace.q_actual(:, joint_index), "Color", colors.trace_actual, "LineWidth", 1.7);
plot(sim_result.t, sim_result.q_target_new(:, joint_index), ":", "Color", colors.new_target, "LineWidth", 2.0);
plot(sim_result.t, sim_result.q_sim_new(:, joint_index), "Color", colors.new_sim, "LineWidth", 2.0);
style_response_axes(gca, options.FontSize);
ylabel("Angle (rad)");
title(options.Title, "Interpreter", "none", "FontSize", options.FontSize + 1, "FontWeight", "bold");
legend("q desired", "Isaac target", "Isaac actual", "sim target", "sim actual", ...
    "Location", "eastoutside", "Box", "off", "FontSize", options.FontSize - 2);

nexttile;
plot(trace.t, trace.qdot_actual(:, joint_index), "Color", colors.trace_target, "LineWidth", 1.7);
hold on;
plot(trace.t, trace.qdot_alloc(:, joint_index), "--", "Color", colors.trace_actual, "LineWidth", 1.7);
plot(sim_result.t, sim_result.qdot_sim_new(:, joint_index), "Color", colors.new_target, "LineWidth", 2.0);
plot(sim_result.t, sim_result.qdot_alloc_new(:, joint_index), "Color", colors.new_sim, "LineWidth", 2.0);
style_response_axes(gca, options.FontSize);
ylabel("Velocity (rad/s)");
legend("Isaac qdot actual", "Isaac qdot alloc", "sim qdot", "sim qdot alloc", ...
    "Location", "eastoutside", "Box", "off", "FontSize", options.FontSize - 2);

nexttile;
plot(sim_result.t, sim_result.tau_sim_new(:, joint_index), "Color", colors.torque, "LineWidth", 2.0);
style_response_axes(gca, options.FontSize);
ylabel("Torque (N*m)");
xlabel("Time (s)");
legend("new tau", "Location", "eastoutside", "Box", "off", "FontSize", options.FontSize - 2);

export_response_figure(fig, output_path);
close(fig);
end

function colors = response_plot_colors()
    colors.desired = [0.05, 0.05, 0.05];
    colors.trace_target = [0.50, 0.50, 0.50];
    colors.trace_actual = [0.84, 0.37, 0.00];
    colors.new_target = [0.00, 0.45, 0.70];
    colors.new_sim = [0.00, 0.62, 0.45];
    colors.torque = [0.49, 0.18, 0.56];
end

function style_response_axes(ax, font_size)
    ax.Color = "white";
    ax.FontName = "Arial";
    ax.FontSize = font_size;
    ax.LineWidth = 1.0;
    ax.Box = "on";
    ax.XColor = [0.05, 0.05, 0.05];
    ax.YColor = [0.05, 0.05, 0.05];
    ax.GridColor = [0.78, 0.78, 0.78];
    ax.GridAlpha = 0.45;
    ax.MinorGridColor = [0.88, 0.88, 0.88];
    ax.MinorGridAlpha = 0.25;
    grid(ax, "on");
end

function export_response_figure(fig, output_path)
    [output_dir, ~, extension] = fileparts(output_path);
    if strlength(output_dir) > 0 && ~isfolder(output_dir)
        mkdir(output_dir);
    end

    if extension == ".svg"
        exportgraphics(fig, output_path, "ContentType", "vector", "BackgroundColor", "white");
    else
        exportgraphics(fig, output_path, "Resolution", 300, "BackgroundColor", "white");
    end
end
