function trace = load_isaac_ball_joint_trace(csv_path, options)
%LOAD_ISAAC_BALL_JOINT_TRACE Load one Stage1 control-step ball-joint trace.
%
% The expected CSV field names follow the scheme documented in
% docs/Stage1球铰PD控制MATLAB真实轨迹仿真实验方案.md.

arguments
    csv_path (1, 1) string
    options.EnvId (1, 1) double = NaN
end

if ~isfile(csv_path)
    error("stage1BallJointPD:MissingTrace", "Trace CSV does not exist: %s", csv_path);
end

joint_names = [
    "spm1_platform_joint_z", ...
    "spm1_platform_joint_y", ...
    "spm1_platform_joint_x", ...
    "spm2_platform_joint_z", ...
    "spm2_platform_joint_y", ...
    "spm2_platform_joint_x" ...
];

table_data = readtable(csv_path, "VariableNamingRule", "preserve", "TextType", "string");
variables = string(table_data.Properties.VariableNames);

require_columns(variables, "time_s");
if any(variables == "env_id")
    env_ids = unique(table_data{:, "env_id"}, "stable");
    if isnan(options.EnvId)
        selected_env_id = env_ids(1);
    else
        selected_env_id = options.EnvId;
        if ~any(env_ids == selected_env_id)
            error("stage1BallJointPD:MissingEnvId", ...
                "Trace CSV %s does not contain env_id = %g.", csv_path, selected_env_id);
        end
    end
    table_data = table_data(table_data{:, "env_id"} == selected_env_id, :);
else
    selected_env_id = NaN;
end

if any(variables == "step")
    table_data = sortrows(table_data, "step");
else
    table_data = sortrows(table_data, "time_s");
end

trace = struct();
trace.csv_path = csv_path;
trace.env_id = selected_env_id;
trace.t = table_data{:, "time_s"};
trace.q_desired = read_joint_matrix(table_data, variables, "q_desired_", joint_names);
trace.q_target_old = read_joint_matrix_first_available(table_data, variables, ...
    ["q_position_target_old_", "q_position_target_"], joint_names);
trace.q_actual_old = read_joint_matrix(table_data, variables, "q_actual_", joint_names);
trace.qdot_actual_old = read_joint_matrix(table_data, variables, "qdot_actual_", joint_names);
trace.qdot_cmd_old = read_joint_matrix_first_available(table_data, variables, ...
    ["qdot_cmd_old_", "qdot_alloc_", "qdot_actual_"], joint_names);

if any(diff(trace.t) <= 0)
    error("stage1BallJointPD:InvalidTraceTime", "time_s must be strictly increasing in %s.", csv_path);
end
end

function values = read_joint_matrix_first_available(table_data, variables, prefixes, joint_names)
    for prefix = string(prefixes)
        column_names = prefix + joint_names;
        if all(ismember(column_names, variables))
            values = read_joint_matrix(table_data, variables, prefix, joint_names);
            return;
        end
    end
    missing_columns = prefixes(1) + joint_names;
    error("stage1BallJointPD:MissingColumns", ...
        "Trace CSV is missing required columns: %s", strjoin(missing_columns, ", "));
end

function values = read_joint_matrix(table_data, variables, prefix, joint_names)
    column_names = prefix + joint_names;
    require_columns(variables, column_names);
    values = zeros(height(table_data), numel(joint_names));
    for joint_index = 1:numel(joint_names)
        values(:, joint_index) = table_data{:, column_names(joint_index)};
    end
end

function require_columns(variables, required_columns)
    missing_columns = setdiff(string(required_columns), variables);
    if ~isempty(missing_columns)
        error("stage1BallJointPD:MissingColumns", ...
            "Trace CSV is missing required columns: %s", strjoin(missing_columns, ", "));
    end
end
