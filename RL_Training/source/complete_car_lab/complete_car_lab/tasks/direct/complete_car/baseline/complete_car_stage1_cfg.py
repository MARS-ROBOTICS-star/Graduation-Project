"""Stage1: terrain curriculum。"""

from isaaclab.utils import configclass

from ..base.complete_car_cfg import CompleteCarEnvCfg


@configclass
class CompleteCarStage1EnvCfg(CompleteCarEnvCfg):
    stage_name: str = "stage1"

    def __post_init__(self) -> None:
        self.scene.num_envs = 32
        self.commands.num_waypoints_per_episode = 1
        self.commands.resampling_time = self.episode_length_s
        self.commands.goal_distance = 16.0
        self.commands.goal_direction_max_deg = 0.0
        self.commands.goal_heading_delta_max_deg = 0.0
        self.commands.zero_command = False
        self.commands.rel_standing_envs = 0.0
        self.commands.use_terrain_column_targets = True
        self.commands.terrain_goal_min_row_offset = 1
        self.commands.terrain_goal_max_row_offset = 2
        self.commands.terrain_goal_lateral_range_m = 3.0

        self.terrain.enabled = True
        self.terrain.mode = "generator"
        self.curriculum.enabled = True
        self.curriculum.max_init_terrain_level = 5
        self.curriculum.default_terrain_name = "slope down"
        self.curriculum.move_up_distance_ratio = 0.70
        self.curriculum.move_down_command_ratio = 0.5
        self.curriculum.move_up_uses_forward_x = True
        self.terrain.measure_heights = True

        self.rewards.params.reached_target_weight = 0.0
        self.rewards.params.far_from_target_margin = 8.0

        self.resets.root_yaw_range = (0.0, 0.0)

        self.sensors.imu.enabled = False
        self.sensors.stereo_camera.enabled = False
        self.sensors.lidar.enabled = False
        self.sensors.enable_height_scanner = False
        self.sensors.wheel_contact_max_points_per_env = 128

        self.debug.enable_debug_draw = True
        self.debug.visualize_goal_heading = False
        self.debug.create_follow_views = True
        self.debug.follow_view_top_height = 8.0
        self.debug.follow_view_chase_env_index = 0
        super().__post_init__()
