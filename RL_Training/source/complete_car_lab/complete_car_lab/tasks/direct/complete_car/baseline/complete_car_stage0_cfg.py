"""Stage0: 平地 baseline。"""

from isaaclab.utils import configclass

from ..base.complete_car_cfg import CompleteCarEnvCfg


@configclass
class CompleteCarStage0EnvCfg(CompleteCarEnvCfg):
    stage_name: str = "stage0"

    def __post_init__(self) -> None:
        self.scene.num_envs = 64
        self.terrain.enabled = False
        self.terrain.mode = "plane"
        self.curriculum.enabled = False
        self.terrain.measure_heights = False

        self.sensors.imu.enabled = False
        self.sensors.stereo_camera.enabled = False
        self.sensors.lidar.enabled = False
        self.sensors.enable_height_scanner = False
        super().__post_init__()
