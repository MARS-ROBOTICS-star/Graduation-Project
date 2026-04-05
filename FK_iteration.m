%% Forward kinematics symbolic derivation for the Agile Eye 3-RRR mechanism
clear; clc;

fprintf('=== Agile Eye forward kinematics symbolic derivation ===\n\n');

%% 0) Symbols and simplifier
syms phi theta psi real
syms theta1 theta2 theta3 real

simp = @(expr) simplify(expand(expr), ...
    'Steps', 100, ...
    'IgnoreAnalyticConstraints', true);

Rx = @(ang) [1, 0, 0;
             0, cos(ang), -sin(ang);
             0, sin(ang),  cos(ang)];

Ry = @(ang) [ cos(ang), 0, sin(ang);
              0,        1, 0;
             -sin(ang), 0, cos(ang)];

Rz = @(ang) [cos(ang), -sin(ang), 0;
             sin(ang),  cos(ang), 0;
             0,         0,        1];

fprintf('0) Symbol set ready.\n\n');

%% 1) Base frame, platform frame, and axis definitions
u1 = sym([1; 0; 0]);
u2 = sym([0; 1; 0]);
u3 = sym([0; 0; 1]);

vp1 = sym([ 0; -1;  0]);
vp2 = sym([ 0;  0; -1]);
vp3 = sym([-1;  0;  0]);

R = simp(Rz(phi) * Ry(theta) * Rx(psi));

v1 = simp(R * vp1);
v2 = simp(R * vp2);
v3 = simp(R * vp3);

v1_expected = [sin(phi)*cos(psi) - cos(phi)*sin(theta)*sin(psi);
              -cos(phi)*cos(psi) - sin(phi)*sin(theta)*sin(psi);
              -cos(theta)*sin(psi)];

v2_expected = [-sin(phi)*sin(psi) - cos(phi)*sin(theta)*cos(psi);
                cos(phi)*sin(psi) - sin(phi)*sin(theta)*cos(psi);
               -cos(theta)*cos(psi)];

v3_expected = [-cos(phi)*cos(theta);
               -sin(phi)*cos(theta);
                sin(theta)];

w1 = [0; -sin(theta1);  cos(theta1)];
w2 = [cos(theta2); 0; -sin(theta2)];
w3 = [-sin(theta3); cos(theta3); 0];

fprintf('1) Base joint axes u_i:\n');
disp(u1); disp(u2); disp(u3);

fprintf('1) Platform joint axes in moving frame v_i'':\n');
disp(vp1); disp(vp2); disp(vp3);

fprintf('1) ZYX rotation matrix R = Rz(phi) * Ry(theta) * Rx(psi):\n');
disp(R);

fprintf('1) Platform axes expressed in base frame:\n');
disp('v1 ='); disp(v1);
disp('v2 ='); disp(v2);
disp('v3 ='); disp(v3);

assert_symbolic_zero('v1 expansion', v1 - v1_expected, simp);
assert_symbolic_zero('v2 expansion', v2 - v2_expected, simp);
assert_symbolic_zero('v3 expansion', v3 - v3_expected, simp);

fprintf('1) Intermediate axes after active rotations:\n');
disp('w1 ='); disp(w1);
disp('w2 ='); disp(w2);
disp('w3 ='); disp(w3);

%% 2) Vector constraints w_i^T v_i = 0
eq1 = simp(w1.' * v1);
eq2 = simp(w2.' * v2);
eq3 = simp(w3.' * v3);

eq1_paper = simp( ...
    sin(psi) * (sin(theta1) * sin(theta) * sin(phi) - cos(theta) * cos(theta1)) ...
    + cos(psi) * sin(theta1) * cos(phi));

eq2_paper = simp( ...
    cos(psi) * (cos(theta2) * sin(theta) * cos(phi) - cos(theta) * sin(theta2)) ...
    + sin(psi) * cos(theta2) * sin(phi));

eq3_paper = simp(sin(theta3 - phi) * cos(theta));

fprintf('2) Scalar constraints from w_i^T v_i = 0:\n');
disp('Eq. (9b):'); disp(eq1);
disp('Eq. (9c) raw from w2^T*v2:'); disp(eq2);
disp('Eq. (9c) paper form after multiplying by -1:'); disp(eq2_paper);
disp('Eq. (9d):'); disp(eq3);

assert_symbolic_zero('Eq. (9b)', eq1 - eq1_paper, simp);
assert_symbolic_zero('Eq. (9c) equivalence', eq2 + eq2_paper, simp);
assert_symbolic_zero('Eq. (9d)', eq3 - eq3_paper, simp);

fprintf('2) Forward-kinematics system:\n');
disp(eq1_paper == 0);
disp(eq2_paper == 0);
disp(eq3_paper == 0);

%% 3) Branch A: cos(theta) = 0 -> trivial solutions
branchA1_raw = simp(subs(eq1_paper, theta, sym(pi)/2));
branchA2_raw = simp(subs(eq1_paper, theta, -sym(pi)/2));

branchA1_expected = simp(sin(theta1) * cos(phi - psi));
branchA2_expected = simp(sin(theta1) * cos(phi + psi));

fprintf('3A) Trivial branch: cos(theta) = 0\n');
disp('theta = pi/2 -> reduced constraint:');
disp(branchA1_raw);
disp('theta = -pi/2 -> reduced constraint:');
disp(branchA2_raw);

assert_symbolic_zero('theta = pi/2 branch', branchA1_raw - branchA1_expected, simp);
assert_symbolic_zero('theta = -pi/2 branch', branchA2_raw - branchA2_expected, simp);

fprintf('3A) Generic trivial conditions:\n');
disp(sym(pi)/2);
disp(cos(phi - psi) == 0);
disp(-sym(pi)/2);
disp(cos(phi + psi) == 0);

%% 4) Branch B: sin(theta3 - phi) = 0 -> nontrivial solutions
phi_nontrivial = theta3;

eq1_phi = simp(subs(eq1_paper, phi, phi_nontrivial));
eq2_phi = simp(subs(eq2_paper, phi, phi_nontrivial));

p1 = simp(sin(theta1) * cos(theta3));
p2 = simp(sin(theta1) * sin(theta) * sin(theta3) - cos(theta) * cos(theta1));
p3 = simp(cos(theta2) * sin(theta) * cos(theta3) - cos(theta) * sin(theta2));
p4 = simp(cos(theta2) * sin(theta3));

eq1_linear = simp(p1 * cos(psi) + p2 * sin(psi));
eq2_linear = simp(p3 * cos(psi) + p4 * sin(psi));

fprintf('4) Nontrivial branch: phi = theta3\n');
disp('Eq. (15a):'); disp(eq1_phi);
disp('Eq. (15b):'); disp(eq2_phi);

assert_symbolic_zero('Eq. (15a)', eq1_phi - eq1_linear, simp);
assert_symbolic_zero('Eq. (15b)', eq2_phi - eq2_linear, simp);

fprintf('4) p1...p4:\n');
disp(p1); disp(p2); disp(p3); disp(p4);

det_expr = simp(expand(p1 * p4 - p2 * p3));

q1 = simp(sin(theta1) * cos(theta2) * cos(theta3) * sin(theta3) ...
    - cos(theta1) * sin(theta2));
q2 = simp(sin(theta1) * sin(theta2) * sin(theta3) ...
    + cos(theta1) * cos(theta2) * cos(theta3));

det_expected = simp(cos(theta) * (q1 * cos(theta) + q2 * sin(theta)));

fprintf('4) Determinant elimination p1*p4 - p2*p3:\n');
disp(det_expr);

assert_symbolic_zero('Eq. (17)', det_expr - det_expected, simp);

fprintf('4) q1 and q2:\n');
disp(q1);
disp(q2);

theta_solution = atan2(-q1, q2);
psi_solution = atan2(-p1, p2);

fprintf('4) Nontrivial solution branches:\n');
disp(phi == theta3);
disp(theta == theta_solution);
disp(theta == theta_solution + sym(pi));
disp(psi == psi_solution);
disp(psi == psi_solution + sym(pi));

fprintf('\nDone.\n');

function assert_symbolic_zero(label, expr, simp)
residual = simp(expr);
fprintf('check %s:\n', label);
disp(residual);
end
