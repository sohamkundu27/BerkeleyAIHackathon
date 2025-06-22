import math
import numpy as np
import pybullet as p
import pybullet_data
# import imageio_ffmpeg
# from base64 import b64encode
# from IPython.display import HTML


p.connect(p.GUI)  # or p.GUI for graphical version
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -10)

plane_id = p.loadURDF("plane.urdf")
kuka_id = p.loadURDF("kuka_iiwa/model_vr_limits.urdf", 1.400000, -
                     0.200000, 0.600000, 0.000000, 0.000000, 0.000000, 1.000000)
kuka_gripper_id = p.loadSDF(
    "gripper/wsg50_one_motor_gripper_new_free_base.sdf")[0]
table_id = p.loadURDF(
    "table/table.urdf", basePosition=[1.0, -0.2, 0.0], baseOrientation=[0, 0, 0.7071, 0.7071])
cube_id = p.loadURDF("cube.urdf", basePosition=[
                     0.85, -0.2, 0.65], globalScaling=0.05)
new_cube_id = p.loadURDF("cube.urdf", basePosition=[
                         0.7, 0.0, 0.65], globalScaling=0.05)


# attach gripper to kuka arm
kuka_cid = p.createConstraint(kuka_id, 6, kuka_gripper_id, 0, p.JOINT_FIXED, [
                              0, 0, 0], [0, 0, 0.05], [0, 0, 0])
kuka_cid2 = p.createConstraint(kuka_gripper_id, 4, kuka_gripper_id, 6, jointType=p.JOINT_GEAR, jointAxis=[
                               1, 1, 1], parentFramePosition=[0, 0, 0], childFramePosition=[0, 0, 0])
p.changeConstraint(kuka_cid2, gearRatio=-1, erp=0.5,
                   relativePositionTarget=0, maxForce=100)

# reset kuka
jointPositions = [-0.000000, -0.000000, 0.000000,
                  1.570793, 0.000000, -1.036725, 0.000001]
for jointIndex in range(p.getNumJoints(kuka_id)):
    p.resetJointState(kuka_id, jointIndex, jointPositions[jointIndex])
    p.setJointMotorControl2(kuka_id, jointIndex,
                            p.POSITION_CONTROL, jointPositions[jointIndex], 0)

# reset gripper
p.resetBasePositionAndOrientation(kuka_gripper_id, [
                                  0.923103, -0.200000, 1.250036], [-0.000000, 0.964531, -0.000002, -0.263970])
jointPositions = [0.000000, -0.011130, -0.206421,
                  0.205143, -0.009999, 0.000000, -0.010055, 0.000000]
for jointIndex in range(p.getNumJoints(kuka_gripper_id)):
    p.resetJointState(kuka_gripper_id, jointIndex, jointPositions[jointIndex])
    p.setJointMotorControl2(kuka_gripper_id, jointIndex,
                            p.POSITION_CONTROL, jointPositions[jointIndex], 0)

num_joints = p.getNumJoints(kuka_id)
kuka_end_effector_idx = 6

# camera parameters
cam_target_pos = [.95, -0.2, 0.2]
cam_distance = 2.05
cam_yaw, cam_pitch, cam_roll = -60, -40, 0
cam_width, cam_height = 480, 360

cam_up, cam_up_axis_idx, cam_near_plane, cam_far_plane, cam_fov = [
    0, 0, 1], 2, 0.01, 100, 60

# video = cv2.VideoWriter('vid.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (cam_width, cam_height)) # Does not seem to support h264!
# vid = imageio_ffmpeg.write_frames('vid.mp4', (cam_width, cam_height), fps=30)
# vid.send(None)  # seed the video writer with a blank frame

# video


# def capture_frame(t):
#     if t % 8 == 0:
#         view_matrix = p.computeViewMatrixFromYawPitchRoll(
#             cam_target_pos, cam_distance, cam_yaw, cam_pitch, cam_roll, cam_up_axis_idx
#         )
#         proj_matrix = p.computeProjectionMatrixFOV(
#             cam_fov, cam_width / cam_height, cam_near_plane, cam_far_plane
#         )

#         # Use TINY_RENDERER for reliability in p.DIRECT or headless mode
#         width, height, rgb_pixels, *_ = p.getCameraImage(
#             cam_width, cam_height, view_matrix, proj_matrix,
#             renderer=p.ER_TINY_RENDERER
#         )

#         # Reshape to (H, W, 4), force dtype, slice RGB
#         image = np.array(rgb_pixels, dtype=np.uint8).reshape(
#             (height, width, 4))[:, :, :3]

#         Write frame to video
#         vid.send(np.ascontiguousarray(image))


# Expose functions
def move_arm(target_pos, target_orn=None):
    steps = 100
    if target_orn is None:
        target_orn = p.getQuaternionFromEuler([0, math.pi, 0])
    elif isinstance(target_orn, list) and len(target_orn) == 3:
        target_orn = p.getQuaternionFromEuler(target_orn)

    target_joint_poses = p.calculateInverseKinematics(
        kuka_id, kuka_end_effector_idx, target_pos, target_orn)

    # Get current joint positions
    current_joint_poses = [p.getJointState(
        kuka_id, j)[0] for j in range(num_joints)]

    for t in range(steps):
        frac = t / steps
        interp_poses = [
            (1 - frac) * current + frac * target
            for current, target in zip(current_joint_poses, target_joint_poses)
        ]

        for j in range(num_joints):
            p.setJointMotorControl2(
                bodyIndex=kuka_id,
                jointIndex=j,
                controlMode=p.POSITION_CONTROL,
                targetPosition=interp_poses[j]
            )

        # if t % 8 == 0:
        #     capture_frame(t)
        p.stepSimulation()


def open_gripper():
    steps = 100
    current_pos = p.getJointState(kuka_gripper_id, 4)[
        0]

    for t in range(steps):
        frac = t / steps
        interp_pos = (1 - frac) * current_pos + frac * 0.0

        p.setJointMotorControl2(
            kuka_gripper_id, 4, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)
        p.setJointMotorControl2(
            kuka_gripper_id, 6, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)

        # if t % 8 == 0:
        #     capture_frame(t)
        p.stepSimulation()


def close_gripper():
    steps = 100
    current_pos = p.getJointState(kuka_gripper_id, 4)[
        0]

    for t in range(steps):
        frac = t / steps
        interp_pos = (1 - frac) * current_pos + frac * 0.05

        p.setJointMotorControl2(
            kuka_gripper_id, 4, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)
        p.setJointMotorControl2(
            kuka_gripper_id, 6, p.POSITION_CONTROL, targetPosition=interp_pos, force=100)

        # if t % 8 == 0:
        #     capture_frame(t)
        p.stepSimulation()


# Example usage
move_arm([0.85, -0.2, 1.2], [0, math.pi, math.pi / 2])
move_arm([0.85, -0.2, 0.97], [0, math.pi, math.pi / 2])
close_gripper()
move_arm([0.85, -0.2, 1.2], [0, math.pi, math.pi / 2])
move_arm([0.85, -0.6, 1.2], [0, math.pi, math.pi / 2])
move_arm([0.85, -0.6, 0.97], [0, math.pi, math.pi / 2])
open_gripper()
move_arm([0.85, -0.6, 1.2])
move_arm([0.7, 0.0, 1.2])
move_arm([0.7, 0.0, 0.97])
close_gripper()
move_arm([0.7, 0.0, 1.2])
move_arm([0.85, -0.6, 1.2])
move_arm([0.85, -0.6, 1.03])
open_gripper()
move_arm([0.85, -0.2, 1.2])


# vid.close()
p.disconnect()

# Play recorded video
# os.system(f"ffmpeg -y -i vid.avi -vcodec libx264 vidc.mp4") # convert to mp4 to show in browser
# mp4 = open('vid.mp4', 'rb').read()
# data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
# HTML('<video width=480 controls><source src="%s" type="video/mp4"></video>' % data_url)
