import math
import numpy as np
import pybullet_data
import pybullet as p
import time


class RobotSim:
    def __init__(self):
        objectspath = "objects/"
        p.connect(p.GUI)  # or p.GUI for graphical version
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -10)

        p.loadURDF("plane.urdf")
        self.kuka_id = p.loadURDF("kuka_iiwa/model_vr_limits.urdf", 1.400000, -
                                  0.200000, 0.600000, 0.000000, 0.000000, 0.000000, 1.000000)
        self.kuka_gripper_id = p.loadSDF(
            "gripper/wsg50_one_motor_gripper_new_free_base.sdf")[0]
        # Friction on the gripper fingers (assuming gripper has multiple links)
        for i in range(p.getNumJoints(self.kuka_gripper_id)):
            p.changeDynamics(self.kuka_gripper_id, i,
                             lateralFriction=0.9,   # Moderate friction
                             spinningFriction=0.07)
        table_id = p.loadURDF(
            "table/table.urdf", basePosition=[1.0, -0.2, 0.0], baseOrientation=[0, 0, 0.7071, 0.7071])
        # Set friction for the table
        p.changeDynamics(table_id, -1, lateralFriction=0.8,
                         spinningFriction=0.1, rollingFriction=0.01)

        apple_pos = [0.8, -0.3, 0.6849899910813102]
        p.loadURDF(objectspath + "apple.urdf",
                   basePosition=apple_pos, globalScaling=0.03)

        bottle_pos = [0.7, 0.1, 0.8]
        bottle_id = p.loadURDF(objectspath + "bottle.urdf",
                               basePosition=bottle_pos, globalScaling=0.05)
        # Add a little friction to the bottle
        p.changeDynamics(bottle_id, -1,  # -1 applies to all links
                         lateralFriction=0.5,      # Small amount of friction
                         spinningFriction=0.02,    # Very light spinning friction
                         rollingFriction=0.01)     # Very light rolling friction

        box_pos = [1, 0.1, 0.7]
        box_id = p.loadURDF(objectspath + "box.urdf",
                            basePosition=box_pos, globalScaling=0.05)

        banana_pos = [0.893, 0.313, 0.660]
        banana_orn = [0.997, 0.000, 0.030, -0.073]
        banana_id = p.loadURDF(objectspath + "banana.urdf", basePosition=banana_pos,
                               baseOrientation=banana_orn, globalScaling=0.035)

        container_pos = [0.9, -0.75, 0.73]
        container_id = p.loadURDF(objectspath + "container.urdf",
                                  basePosition=container_pos, globalScaling=0.05)

        hammer_pos = [1, -0.2, 0.7]
        hammer_orn = p.getQuaternionFromEuler(
            [math.pi/2, -math.pi/2, math.pi])  # Lay flat
        hammer_id = p.loadURDF(objectspath + "hammer.urdf",
                               basePosition=hammer_pos,
                               baseOrientation=hammer_orn,
                               globalScaling=0.05)

        # attach gripper to kuka arm
        p.createConstraint(self.kuka_id, 6, self.kuka_gripper_id, 0, p.JOINT_FIXED, [
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
        target_pos[2] += 0.25
        steps = 1000
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

            p.stepSimulation()

    def open_gripper(self):
        steps = 500
        current_pos = p.getJointState(self.kuka_gripper_id, 4)[
            0]

        for t in range(steps):
            frac = t / steps
            interp_pos = (1 - frac) * current_pos + frac * 0.0

            p.setJointMotorControl2(
                self.kuka_gripper_id, 4, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)
            p.setJointMotorControl2(
                self.kuka_gripper_id, 6, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)

            p.stepSimulation()

    def close_gripper(self):
        steps = 500
        current_pos = p.getJointState(self.kuka_gripper_id, 4)[
            0]

        for t in range(steps):
            frac = t / steps
            interp_pos = (1 - frac) * current_pos + frac * 0.05

            p.setJointMotorControl2(
                self.kuka_gripper_id, 4, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)
            p.setJointMotorControl2(
                self.kuka_gripper_id, 6, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)

            p.stepSimulation()
