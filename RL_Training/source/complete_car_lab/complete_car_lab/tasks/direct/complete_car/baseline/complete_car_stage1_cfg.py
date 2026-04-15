"""Stage1: terrain curriculum。"""

from isaaclab.utils import configclass

from ..base.complete_car_cfg import CompleteCarEnvCfg


@configclass
class CompleteCarStage1EnvCfg(CompleteCarEnvCfg):
    stage_name: str = "stage1"

    def __post_init__(self) -> None:
        self.scene.num_envs = 384
        self.terrain.enabled = True
        self.terrain.mode = "generator"
        self.curriculum.enabled = True
        self.curriculum.max_init_terrain_level = 5
        self.curriculum.default_terrain_name = "flat"
        self.terrain.measure_heights = True

        self.sensors.imu.enabled = False
        self.sensors.stereo_camera.enabled = False
        self.sensors.lidar.enabled = False
        self.sensors.enable_height_scanner = False
        super().__post_init__()
