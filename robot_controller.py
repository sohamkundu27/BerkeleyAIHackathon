import math
import numpy as np
import pybullet_data
import pybullet as p
import time


class RobotSim:
    def __init__(self):
        p.connect(p.GUI)  # or p.GUI for graphical version
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -10)

        # load environment
        self.plane_id = p.loadURDF("plane.urdf")
        self.kuka_id = p.loadURDF("kuka_iiwa/model_vr_limits.urdf", 1.400000, -
                                  0.200000, 0.600000, 0.000000, 0.000000, 0.000000, 1.000000)
        self.kuka_gripper_id = p.loadSDF(
            "gripper/wsg50_one_motor_gripper_new_free_base.sdf")[0]
        self.table_id = p.loadURDF(
            "table/table.urdf", basePosition=[1.0, -0.2, 0.0], baseOrientation=[0, 0, 0.7071, 0.7071])
        self.cube_id = p.loadURDF("cube.urdf", basePosition=[
            0.85, -0.2, 0.65], globalScaling=0.05)
        self.new_cube_id = p.loadURDF("cube.urdf", basePosition=[
            0.7, 0.0, 0.65], globalScaling=0.05)

        # attach gripper to kuka arm
        kuka_cid = p.createConstraint(self.kuka_id, 6, self.kuka_gripper_id, 0, p.JOINT_FIXED, [
            0, 0, 0], [0, 0, 0.05], [0, 0, 0])
        kuka_cid2 = p.createConstraint(self.kuka_gripper_id, 4, self.kuka_gripper_id, 6, jointType=p.JOINT_GEAR, jointAxis=[
            1, 1, 1], parentFramePosition=[0, 0, 0], childFramePosition=[0, 0, 0])
        p.changeConstraint(kuka_cid2, gearRatio=-1, erp=0.5,
                           relativePositionTarget=0, maxForce=100)

        # reset kuka
        jointPositions = [-0.000000, -0.000000, 0.000000,
                          1.570793, 0.000000, -1.036725, 0.000001]
        for jointIndex in range(p.getNumJoints(self.kuka_id)):
            p.resetJointState(self.kuka_id, jointIndex,
                              jointPositions[jointIndex])
            p.setJointMotorControl2(self.kuka_id, jointIndex,
                                    p.POSITION_CONTROL, jointPositions[jointIndex], 0)

        # reset gripper
        p.resetBasePositionAndOrientation(self.kuka_gripper_id, [
            0.923103, -0.200000, 1.250036], [-0.000000, 0.964531, -0.000002, -0.263970])
        jointPositions = [0.000000, -0.011130, -0.206421,
                          0.205143, -0.009999, 0.000000, -0.010055, 0.000000]
        for jointIndex in range(p.getNumJoints(self.kuka_gripper_id)):
            p.resetJointState(self.kuka_gripper_id, jointIndex,
                              jointPositions[jointIndex])
            p.setJointMotorControl2(self.kuka_gripper_id, jointIndex,
                                    p.POSITION_CONTROL, jointPositions[jointIndex], 0)

        self.num_joints = p.getNumJoints(self.kuka_id)
        self.kuka_end_effector_idx = 6

    def move_arm(self, target_pos, target_orn=None):
        steps = 100
        if target_orn is None:
            target_orn = p.getQuaternionFromEuler([0, math.pi, 0])
        elif isinstance(target_orn, list) and len(target_orn) == 3:
            target_orn = p.getQuaternionFromEuler(target_orn)

        target_joint_poses = p.calculateInverseKinematics(
            self.kuka_id, self.kuka_end_effector_idx, target_pos, target_orn)

        # Get current joint positions
        current_joint_poses = [p.getJointState(
            self.kuka_id, j)[0] for j in range(self.num_joints)]

        for t in range(steps):
            frac = t / steps
            interp_poses = [
                (1 - frac) * current + frac * target
                for current, target in zip(current_joint_poses, target_joint_poses)
            ]

            for j in range(self.num_joints):
                p.setJointMotorControl2(
                    bodyIndex=self.kuka_id,
                    jointIndex=j,
                    controlMode=p.POSITION_CONTROL,
                    targetPosition=interp_poses[j]
                )

            if t % 8 == 0:
                time.sleep(0.05)
            p.stepSimulation()

    def open_gripper(self):
        steps = 100
        current_pos = p.getJointState(self.kuka_gripper_id, 4)[
            0]

        for t in range(steps):
            frac = t / steps
            interp_pos = (1 - frac) * current_pos + frac * 0.0

            p.setJointMotorControl2(
                self.kuka_gripper_id, 4, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)
            p.setJointMotorControl2(
                self.kuka_gripper_id, 6, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)

            if t % 8 == 0:
                time.sleep(0.05)
            p.stepSimulation()

    def close_gripper(self):
        steps = 100
        current_pos = p.getJointState(self.kuka_gripper_id, 4)[
            0]

        for t in range(steps):
            frac = t / steps
            interp_pos = (1 - frac) * current_pos + frac * 0.05

            p.setJointMotorControl2(
                self.kuka_gripper_id, 4, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)
            p.setJointMotorControl2(
                self.kuka_gripper_id, 6, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)

            if t % 8 == 0:
                time.sleep(0.05)
            p.stepSimulation()
