# Stage1 方向通过地形任务设计草案

日期：2026-04-25

状态：设计草案，尚未接入训练代码。

## 1. 设计目标

Stage1 的目标不应继续定义为“精确到达 waypoint”。

当前混合地形训练更合理的任务定义是：

> 小车在当前地形通道内，朝指定前进方向稳定通过一段地形。

因此 Stage1 中的目标点应改为“方向引导点”，而不是必须命中的终点。

本设计要解决两个具体问题：

1. 目标点不能生成到其它地形列，避免小车被奖励引导到其它地形。
2. reset 出生点、出生朝向和目标点必须共同受当前地形通道边界约束，避免边缘 tile 上小车被引导出地图。

## 2. 当前地形几何

Stage1 terrain generator 当前关键尺寸如下：

| 参数 | 数值 | 含义 |
|---|---:|---|
| `terrain_length` | `8.0 m` | 单个 tile 在前进方向 `$x$` 上的长度 |
| `terrain_width` | `8.0 m` | 单个 tile 在横向 `$y$` 上的宽度 |
| `num_rows` | `20` | 难度层数，row 越大难度越高 |
| `num_cols` | `10` | 地形列数 |
| 地图总有效长度 | `160 m` | `$20 \times 8 m$` |
| 地图总有效宽度 | `80 m` | `$10 \times 8 m$` |

坐标约定：

- row 方向对应世界坐标 `$+x$`，也是建议的前进方向。
- col 方向对应世界坐标 `$+y$`。
- 第 `r` 行、第 `c` 列 tile 的边界为：

$$
x_{\min}=8r,\quad x_{\max}=8(r+1)
$$

$$
y_{\min}=8c,\quad y_{\max}=8(c+1)
$$

例如：

| tile | `$x_{\min}$` | `$x_{\max}$` | `$y_{\min}$` | `$y_{\max}$` |
|---|---:|---:|---:|---:|
| row 0, col 0 | `0 m` | `8 m` | `0 m` | `8 m` |
| row 0, col 1 | `0 m` | `8 m` | `8 m` | `16 m` |
| row 5, col 2 | `40 m` | `48 m` | `16 m` | `24 m` |
| row 19, col 9 | `152 m` | `160 m` | `72 m` | `80 m` |

## 3. 两列同地形通道

如果 Stage1 采用“每两列为同一种地形”的训练地图，则训练边界不应使用单列 tile，而应使用两列合并后的地形通道。

列分组：

| 通道编号 | 列范围 | `$y_{\min}$` | `$y_{\max}$` | 通道宽度 |
|---:|---|---:|---:|---:|
| 0 | col 0-1 | `0 m` | `16 m` | `16 m` |
| 1 | col 2-3 | `16 m` | `32 m` | `16 m` |
| 2 | col 4-5 | `32 m` | `48 m` | `16 m` |
| 3 | col 6-7 | `48 m` | `64 m` | `16 m` |
| 4 | col 8-9 | `64 m` | `80 m` | `16 m` |

对任意当前列 `c`：

$$
c_{\mathrm{left}}=2\left\lfloor c/2 \right\rfloor
$$

$$
c_{\mathrm{right}}=c_{\mathrm{left}}+1
$$

$$
y_{\mathrm{band,min}}=8c_{\mathrm{left}}
$$

$$
y_{\mathrm{band,max}}=8(c_{\mathrm{right}}+1)
$$

示意图：

```text
俯视图：x 向右，y 向上

y
^
|   col 9  +----------------------------------+
|          |                                  |
|   col 8  +========== terrain band 4 ========+
|          |                                  |
|   col 7  +----------------------------------+
|          |                                  |
|   col 6  +========== terrain band 3 ========+
|          |                                  |
|   col 5  +----------------------------------+
|          |                                  |
|   col 4  +========== terrain band 2 ========+
|          |                                  |
|   col 3  +----------------------------------+
|          |                                  |
|   col 2  +========== terrain band 1 ========+
|          |                                  |
|   col 1  +----------------------------------+
|          |                                  |
|   col 0  +========== terrain band 0 ========+
|
+--------------------------------------------------> x
    row 0        row 1        row 2        ...
```

## 4. 统一边界参数

建议 Stage1 第一版使用以下固定数值：

| 参数 | 数值 | 含义 |
|---|---:|---|
| `rear_margin` | `1.0 m` | reset 时距离 tile 后边界的最小距离 |
| `front_margin` | `1.0 m` | 通过判定和目标点距离 tile 前边界的安全距离 |
| `side_margin` | `2.0 m` | 目标点和正常行驶区域距离通道左右边界的安全距离 |
| `yaw_clearance_margin` | `1.0 m` | 给 reset yaw 扰动额外预留的横向余量 |
| `target_y_offset_max` | `1.0 m` | 目标点相对出生 `$y$` 的最大横向偏移 |
| `reset_yaw_max_deg` | `5.0°` | 出生朝向最大扰动角 |
| `episode_length_s` | `16.0 s` | Stage1 当前默认回合时长，第一版可保持不变 |

单个 tile 的有效前进距离：

$$
d_{\mathrm{pass}}=8.0-1.0-1.0=6.0\ \mathrm{m}
$$

如果要求 `16 s` 内通过 `6 m`，平均前进速度只需：

$$
v_{\mathrm{avg}}=6.0/16.0=0.375\ \mathrm{m/s}
$$

如果课程升级阈值设为 `5 m`，平均速度要求为：

$$
v_{\mathrm{upgrade}}=5.0/16.0=0.3125\ \mathrm{m/s}
$$

这比直接追 `20 m` waypoint 更适合 Stage1 地形通过训练。

## 5. Reset 采样方案

对当前 env，已知当前地形行 `r`、列 `c`。

先计算当前 tile 的 `$x$` 边界：

$$
x_{\min}=8r,\quad x_{\max}=8(r+1)
$$

再计算当前两列通道的 `$y$` 边界：

$$
y_{\mathrm{band,min}}=8c_{\mathrm{left}},\quad
y_{\mathrm{band,max}}=8(c_{\mathrm{right}}+1)
$$

reset 出生点建议为：

$$
x_{\mathrm{spawn}}=x_{\min}+1.0
$$

$$
y_{\mathrm{spawn}}\sim U(y_{\mathrm{band,min}}+3.0,\ y_{\mathrm{band,max}}-3.0)
$$

这里 `3.0 m` 来自：

$$
3.0=side\_margin+yaw\_clearance\_margin=2.0+1.0
$$

对于 `16 m` 宽的两列通道，`y_spawn` 的可采样宽度为：

$$
16.0-3.0-3.0=10.0\ \mathrm{m}
$$

reset 朝向：

$$
\psi_{\mathrm{reset}}\sim U(-5^\circ,\ 5^\circ)
$$

如果后续希望更严格，也可以使用动态限制：

$$
\psi_{\max}=\min\left(5^\circ,\ \arctan\frac{1.0}{6.0}\right)
$$

由于：

$$
\arctan(1.0/6.0)\approx 9.46^\circ
$$

所以第一版固定 `5°` 是安全的。它在 `6 m` 前进距离上造成的横向漂移约为：

$$
6.0\tan(5^\circ)\approx 0.52\ \mathrm{m}
$$

小于预留的 `1.0 m` yaw 横向余量。

reset 示意图：

```text
单个 row 内的两列地形通道，俯视图

          y_band_max
              |
              v
        +--------------------------------+
        |            禁止区 2 m          |
        +--------------------------------+
        |                                |
        |   y_spawn 可采样区域 10 m      |
        |                                |
        |        o  robot spawn          |
        |        |                       |
        |        | yaw in [-5°, 5°]      |
        |        +-----> +x              |
        |                                |
        +--------------------------------+
        |            禁止区 2 m          |
        +--------------------------------+
              ^
              |
          y_band_min

        x_min + 1 m                 x_max - 1 m
        reset 后部安全边界           通过判定线
```

## 6. 方向目标点生成方案

Stage1 的目标点不再按“小车当前 yaw + 随机摆角”生成。

不再使用：

$$
target=start+20[\cos(\psi+\phi),\ \sin(\psi+\phi)]
$$

因为当前 `goal_distance = 20 m`、`goal_direction_max = 18.43°` 时，最大横向偏移为：

$$
20\sin(18.43^\circ)\approx 6.3\ \mathrm{m}
$$

这在单列 `8 m` tile 或边缘区域都容易把目标点生成到其它地形。

建议改为通道内前方目标：

$$
x_{\mathrm{target}}=x_{\max}-1.0
$$

$$
y_{\mathrm{target}}=\mathrm{clip}
\left(
y_{\mathrm{spawn}}+\Delta y,\ 
y_{\mathrm{band,min}}+2.0,\ 
y_{\mathrm{band,max}}-2.0
\right)
$$

其中：

$$
\Delta y\sim U(-1.0,\ 1.0)
$$

目标朝向固定为：

$$
\psi_{\mathrm{target}}=0
$$

这样目标点永远在当前两列地形通道内部。

示意图：

```text
俯视图：目标点只在当前 terrain band 内生成

             y_band_max
                 |
                 v
          +-----------------------------+
          |          side margin        |
          |-----------------------------|
          |                             |
          |  spawn                      |
          |    o-----------------> x    |
          |     \                       |
          |      \                      |
          |       * target              |
          |                             |
          |-----------------------------|
          |          side margin        |
          +-----------------------------+
                 ^
                 |
             y_band_min

          x_min + 1 m            x_max - 1 m
          spawn line             target / pass line
```

## 7. 边缘 tile 处理

边缘问题主要有三类：

1. 最后一行 row 19：目标不能超过地图前边界。
2. 最左通道 col 0-1：目标不能小于地图左边界。
3. 最右通道 col 8-9：目标不能大于地图右边界。

上述公式天然解决这些问题：

| 边缘情况 | 约束 |
|---|---|
| 最后一行 row 19 | `$x_{\mathrm{target}}=160-1=159 m$`，不会超过地图 |
| 最左通道 col 0-1 | `$y_{\mathrm{target}}\ge 0+2=2 m$` |
| 最右通道 col 8-9 | `$y_{\mathrm{target}}\le 80-2=78 m$` |

row 19, col 8-9 的例子：

| 项 | 数值 |
|---|---:|
| `$x_{\min}$` | `152 m` |
| `$x_{\max}$` | `160 m` |
| `$y_{\mathrm{band,min}}$` | `64 m` |
| `$y_{\mathrm{band,max}}$` | `80 m` |
| `$x_{\mathrm{spawn}}$` | `153 m` |
| `$y_{\mathrm{spawn}}$` | `U(67, 77) m` |
| `$x_{\mathrm{target}}$` | `159 m` |
| `$y_{\mathrm{target}}$` | clipped to `[66, 78] m` |
| `reset yaw` | `[-5°, 5°]` |

因此即使在地图最右上角，目标点也不会出地图。

## 8. 出界与通过判定

只限制目标点还不够，因为策略仍可能横向漂移。因此 Stage1 应增加通道边界终止。

建议第一版判定：

| 条件 | 判定 | 数值 |
|---|---|---|
| `$x \ge x_{\max}-1.0$` | 通过当前 tile | 通过线 |
| `$x < x_{\min}-0.5$` | 失败 | 后退越界 |
| `$y < y_{\mathrm{band,min}}+0.5$` | 失败 | 左侧越界 |
| `$y > y_{\mathrm{band,max}}-0.5$` | 失败 | 右侧越界 |
| 翻车、球铰超限 | 失败 | 沿用现有终止逻辑 |
| 时间达到 `16 s` | timeout | 未通过则不升级 |

注意：

- `side_margin = 2.0 m` 是目标点和 reset 的安全边界。
- `0.5 m` 是真正的通道越界判定边界。
- 二者不要混用，否则策略会因为稍微偏离中心线就过早失败。

示意图：

```text
两列地形通道内的安全区和失败边界

          y_band_max
              |
              v
      +----------------------------------+  实际地形边界
      |  0.5 m failure guard            |
      |  +----------------------------+ |
      |  |  2.0 m command margin      | |
      |  |  +----------------------+  | |
      |  |  |                      |  | |
      |  |  |  normal driving zone |  | |
      |  |  |                      |  | |
      |  |  +----------------------+  | |
      |  |  2.0 m command margin      | |
      |  +----------------------------+ |
      |  0.5 m failure guard            |
      +----------------------------------+  实际地形边界
              ^
              |
          y_band_min
```

## 9. 课程升级和降级建议

Stage1 curriculum 不应继续使用“距离 tile 原点多远”作为主要标准。

建议改为沿前进方向的实际通过距离：

$$
d_x=x_{\mathrm{current}}-x_{\mathrm{spawn}}
$$

第一版课程规则：

| 条件 | 结果 |
|---|---|
| `$d_x \ge 5.0 m$` 且没有出界、翻车、球铰超限 | 升级 |
| `$d_x < 2.0 m$` | 降级 |
| 出界、翻车、球铰超限 | 降级 |
| `2.0 m \le d_x < 5.0 m` 且未失败 | 保持当前难度 |

数值含义：

- `5.0 m` 升级阈值低于完整通过距离 `6.0 m`，避免因为最后 `1 m` 边界误差导致升级过严。
- `2.0 m` 降级阈值表示小车基本没有有效通过地形。
- `16 s` 内走过 `5.0 m` 的平均速度要求为 `0.3125 m/s`，对早期课程不过分苛刻。

## 10. 与现有 waypoint 任务的区别

| 项 | 当前 waypoint 口径 | 建议 Stage1 口径 |
|---|---|---|
| 目标含义 | 必须接近的目标点 | 前方方向引导点 |
| 成功依据 | 距离 waypoint 小于阈值 | 沿当前通道通过足够距离 |
| 目标生成 | 当前 yaw 加随机摆角 | 当前地形通道内 `$+x$` 前方点 |
| 横向约束 | 无显式通道边界 | 目标、reset、终止共享通道边界 |
| 课程升级 | 离 tile 原点距离够远 | 沿 `$+x$` 前进距离够远且未失败 |
| 对论文解释 | 偏路径到达 | 更接近复杂地形通过能力 |

## 11. 需要修改的代码位置

后续如果确认该方案，建议按最短路径修改以下位置：

1. `terrain_runtime.py`
   - 增加根据 `terrain_levels`、`terrain_types` 返回当前 tile / band 边界的函数。
   - 输出每个 env 的 `$x_{\min}$`、`$x_{\max}$`、`$y_{\mathrm{band,min}}$`、`$y_{\mathrm{band,max}}$`。

2. `mdp/resets.py` 或 `env.py`
   - Stage1 reset 使用通道感知采样。
   - 设置 `x_spawn = x_min + 1.0`。
   - 设置 `y_spawn` 在 `[y_band_min + 3.0, y_band_max - 3.0]` 内采样。
   - 设置 `reset_yaw` 在 `[-5°, 5°]` 内采样。

3. `mdp/commands.py`
   - 为 Stage1 增加方向目标采样逻辑。
   - 目标点固定在 `x_max - 1.0` 附近。
   - 目标点横向限制在 `[y_band_min + 2.0, y_band_max - 2.0]`。

4. `mdp/terminations.py`
   - 增加 `terrain_passed` 和 `out_of_terrain_band`。
   - `terrain_passed` 不等同于 waypoint hit。

5. `mdp/curriculum.py`
   - 使用 `$d_x=x_{\mathrm{current}}-x_{\mathrm{spawn}}$` 判断升级 / 降级。
   - 不再使用相对目标剩余距离判断降级。

6. `base/env.py`
   - 保存每个 episode 的 `x_spawn`，供 reward、termination 和 curriculum 统一使用。
   - 后续可加入按地形类型分组日志。

## 12. 第一版推荐固定参数

如果后续直接实现，建议第一版先使用下表，不再同时引入更多自由参数：

| 参数 | 推荐值 |
|---|---:|
| 单 tile 长度 | `8.0 m` |
| 单 tile 宽度 | `8.0 m` |
| 通道宽度 | `16.0 m` |
| `rear_margin` | `1.0 m` |
| `front_margin` | `1.0 m` |
| `side_margin` | `2.0 m` |
| `yaw_clearance_margin` | `1.0 m` |
| `target_y_offset_max` | `1.0 m` |
| `reset_yaw_max_deg` | `5.0°` |
| 有效通过距离 | `6.0 m` |
| curriculum 升级距离 | `5.0 m` |
| curriculum 降级距离 | `2.0 m` |
| episode 时长 | `16.0 s` |
| 通过所需平均速度 | `0.375 m/s` |
| 升级所需平均速度 | `0.3125 m/s` |

## 13. 结论

Stage1 的核心修改不是把 waypoint 半径或摆角调小，而是把任务从“追点”改成“通道内方向通过”。

最重要的设计原则是：

> reset 出生点、reset 朝向、方向目标点、出界终止、课程升级必须使用同一套地形通道边界。

这样才能保证小车是在当前地形上训练，而不是因为目标点生成方式错误而被引导到其它地形或地图外。
