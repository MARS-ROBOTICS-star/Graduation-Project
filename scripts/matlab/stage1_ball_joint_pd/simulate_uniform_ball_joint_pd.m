function sim_result = simulate_uniform_ball_joint_pd(trace, params)
%SIMULATE_UNIFORM_BALL_JOINT_PD Simulate direct-target uniform PD response.

arguments
    trace (1, 1) struct
    params (1, 1) struct
end

num_steps = size(trace.q_desired, 1);
num_joints = size(trace.q_desired, 2);

q_lower = row_vector(params.q_lower);
q_upper = row_vector(params.q_upper);
dt_sim = params.dt_sim;
dt_ctrl = params.dt_ctrl;
decimation = max(1, round(dt_ctrl / dt_sim));
alpha_v = 1 - exp(-dt_ctrl / params.tau_v);

if isfield(params, "initial_condition_from_trace") && params.initial_condition_from_trace
    q = trace.q_actual_old(1, :);
    qdot = trace.qdot_actual_old(1, :);
    qdot_alloc = trace.qdot_cmd_old(1, :);
else
    q = zeros(1, num_joints);
    qdot = zeros(1, num_joints);
    qdot_alloc = zeros(1, num_joints);
end

q_target_new = zeros(num_steps, num_joints);
q_sim_new = zeros(num_steps, num_joints);
qdot_sim_new = zeros(num_steps, num_joints);
qdot_alloc_new = zeros(num_steps, num_joints);
tau_sim_new = zeros(num_steps, num_joints);

for step_index = 1:num_steps
    q_target = min(max(trace.q_desired(step_index, :), q_lower), q_upper);
    tau = zeros(1, num_joints);

    for substep_index = 1:decimation %#ok<NASGU>
        tau_raw = params.Kp .* (q_target - q) - params.Kd .* qdot;
        tau = min(max(tau_raw, -params.tau_max), params.tau_max);
        qddot = (tau - params.B_axis .* qdot - params.tau_load) ./ params.J_axis;
        qdot = min(max(qdot + dt_sim .* qddot, -params.qdot_max), params.qdot_max);
        q = min(max(q + dt_sim .* qdot, q_lower), q_upper);
    end

    qdot_alloc = (1 - alpha_v) .* qdot_alloc + alpha_v .* qdot;

    q_target_new(step_index, :) = q_target;
    q_sim_new(step_index, :) = q;
    qdot_sim_new(step_index, :) = qdot;
    qdot_alloc_new(step_index, :) = qdot_alloc;
    tau_sim_new(step_index, :) = tau;
end

sim_result = struct();
sim_result.t = trace.t(:);
sim_result.q_target_new = q_target_new;
sim_result.q_sim_new = q_sim_new;
sim_result.qdot_sim_new = qdot_sim_new;
sim_result.qdot_alloc_new = qdot_alloc_new;
sim_result.tau_sim_new = tau_sim_new;
sim_result.params = params;
end

function values = row_vector(values)
    values = reshape(values, 1, []);
end
