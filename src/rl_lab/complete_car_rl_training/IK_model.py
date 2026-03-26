import math
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict

def Rx(angle:float) ->np.ndarray:
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [1.0, 0.0, 0.0],
        [0.0, c, -s],
        [0.0, s, c],
    ],dtype=float)

def Ry(angle:float) ->np.ndarray:
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [c, 0.0, s],
        [0.0, 1.0, 0.0],
        [-s, 0.0, c],
    ],dtype=float)

def Rz(angle:float) ->np.ndarray:
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0],
    ],dtype=float)

def wrap_to_pi(angle: float) ->float:
    return(angle + math.pi)%(2.0*math.pi)-math.pi

@dataclass
class IKParams:
    alpha1: float = math.radians(90.0)
    alpha2: float = math.radians(90.0)
    beta: float = math.radians(54.75)
    gamma: float = math.radians(54.75)
    etas: Tuple[float,float,float] =(
        math.radians(0.0),
        math.radians(120.0),
        math.radians(240.0),
    )

class IK_3RRR_Spherical:
    def __init__(self,params: Optional[IKParams] = None):
        self.p = params if params is not None else IKParams()

    def R_01(self,eta: float) ->np.ndarray:
        return Rz(eta + math.pi /2.0)@Ry(math.pi /2.0 -self.p.gamma)
    
    def R_03(self, eta: float) ->np.ndarray:
        return Rz(eta + 5.0*math.pi/6.0)@Ry(self.p.beta -math.pi/2.0)
    
    def R_rpy(self, roll: float, pitch: float, yaw: float) ->np.ndarray:
        return Rz(yaw)@Ry(pitch)@Rx(roll)
    
    def w_i(self, eta: float, theta_i: float) ->np.ndarray:
        R_local = Rx(theta_i)@Rz(self.p.alpha1)
        R_w = self.R_01(eta)@R_local
        return R_w[:,0]
    
    def v_i(self, eta: float, roll: float, pitch: float, yaw:float) ->np.ndarray:
        R_v = self.R_rpy(roll, pitch, yaw)@ self.R_03(eta)
        return R_v[:,0]
    
    def abc_leg(
        self,
        eta: float,
        roll:float,
        pitch:float,
        yaw:float,
    ) -> Tuple[float,float,float]:
        v = self.v_i(eta,roll,pitch,yaw)
        vix,viy,viz= v.tolist()
        a = math.sin(self.p.alpha1) * (
              viz * math.sin(self.p.gamma)
              + viy * math.cos(eta) * math.cos(self.p.gamma)
              - vix * math.cos(self.p.gamma) * math.sin(eta)
          )

        b = -math.sin(self.p.alpha1) * (
              vix * math.cos(eta) + viy * math.sin(eta)
          )

        d = (
              viy * math.cos(self.p.alpha1) * math.cos(eta) * math.sin(self.p.gamma)
              - viz * math.cos(self.p.alpha1) * math.cos(self.p.gamma)
              - math.cos(self.p.alpha2)
              - vix * math.cos(self.p.alpha1) * math.sin(eta) * math.sin(self.p.gamma)
          )
        
        A = d-b
        B = 2.0*a
        C = b+d
        return A,B,C
    
    def solve_leg_all_branches(
        self,
        eta: float,
        roll:float,
        pitch:float,
        yaw:float,
        eps:float = 1e-12,
    ) -> Dict[str,object]:
        A,B,C = self.abc_leg(eta,roll,pitch,yaw)
        Delta = B*B -4.0*A*C

        result = {
            "A":A,
            "B":B,
            "C":C,
            "Delta":Delta,
            "roots_t":[],
            "roots_theta":[],
        }

        if Delta < -eps:
            return result
        
        Delta = max(Delta, 0.0)

        if abs(A) >eps:
            sqrtD = math.sqrt(Delta)
            t1 = (-B + sqrtD) /(2.0 *A)
            t2 = (-B - sqrtD) /(2.0 *A)

            th1 = wrap_to_pi(2.0*math.atan(t1))
            th2 = wrap_to_pi(2.0*math.atan(t2))

            result["roots_t"] = [t1,t2]
            result["roots_theta"] = [th1,th2]
            return result
        
        if abs(B) >eps:
            t = -C/B
            th = wrap_to_pi(2.0*math.atan(t))
            result["roots_t"] =[t]
            result["roots_theta"] = [th]
            return result

        return result
    
    def pick_branch(
        self,
        candidates: List[float],
        prev_q: Optional[float] =None,
        prefer: str = "first",
    ) ->float:
        if not candidates:
            raise ValueError("No valid IK branch for this leg.")
        
        if prev_q is not None:
            return min(candidates, key=lambda q: abs(wrap_to_pi(q-prev_q)))
        
        if prefer == "second" and len(candidates) >=2:
            return candidates[1]
        
        return candidates[0]
    
    def ik(
        self,
        roll:float,
        pitch:float,
        yaw:float,
        prev_q: Optional[List[float]] =None,
        prefer: str = "first",
    ) -> Dict[str, object]:
        qs= []
        all_info =[]

        for i, eta in enumerate(self.p.etas):
            info = self.solve_leg_all_branches(eta,roll,pitch,yaw)
            all_info.append(info)

            prev_i = None if prev_q is None else prev_q[i]
            q_i = self.pick_branch(
                info["roots_theta"],
                prev_q=prev_i,
                prefer= prefer,
            )
            qs.append(q_i)

        return {
            "q":qs,
            "all_branches":all_info
        }
    
    def compute_home_offsets(
        self,
        prefer: str = "first",
      ) -> List[float]:
        out = self.ik(0.0, 0.0, 0.0, prev_q=None, prefer=prefer)
        return out["q"]

    def map_to_sim_joints(
        self,
        q_math: List[float],
        q_home: List[float],
        signs: Tuple[int, int, int] = (1, 1, 1),
        biases: Tuple[float, float, float] = (0.0, 0.0, 0.0),
      ) -> List[float]:
        q_sim = []
        for i in range(3):
            q_sim_i = signs[i] * (q_math[i] - q_home[i]) + biases[i]
            q_sim.append(q_sim_i)
        return q_sim

    def residual(
        self,
        eta: float,
        theta_i: float,
        roll: float,
        pitch: float,
        yaw: float,
      ) -> float:
        w = self.w_i(eta, theta_i)
        v = self.v_i(eta, roll, pitch, yaw)
        return float(np.dot(w, v) - math.cos(self.p.alpha2))

    def verify_solution(
        self,
        q: List[float],
        roll: float,
        pitch: float,
        yaw: float,
      ) -> List[float]:
        residuals = []
        for eta, qi in zip(self.p.etas, q):
              r = self.residual(eta, qi, roll, pitch, yaw)
              residuals.append(r)
        return residuals




            

    




    


    
    
