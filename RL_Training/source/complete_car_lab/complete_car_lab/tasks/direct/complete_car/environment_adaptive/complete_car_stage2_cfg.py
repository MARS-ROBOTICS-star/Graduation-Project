"""Stage2: 环境自适应 / 感知增强。"""

from isaaclab.utils import configclass

from ..base.complete_car_cfg import CompleteCarEnvCfg


@configclass
class CompleteCarStage2EnvCfg(CompleteCarEnvCfg):
    stage_name: str = "stage2"

    def __post_init__(self) -> None:
        self.scene.num_envs = 256
        self.terrain.enabled = True
        self.terrain.mode = "generator"
        self.terrain.curriculum = True
        self.terrain.flat_only_reset = False
        self.terrain.max_init_terrain_level = 5

        self.sensors.imu.enabled = True
        self.sensors.stereo_camera.enabled = True
        self.sensors.stereo_camera.data_types = ["rgb", "distance_to_image_plane"]
        self.sensors.lidar.enabled = True
        self.sensors.enable_height_scanner = False

        self.observations.noise.enabled = True
        self.observations.noise.level = 0.5
        super().__post_init__()
