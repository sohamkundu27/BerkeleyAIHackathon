import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="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",
)

def get_response(prompt):
    # 1. Analyzer pipeline
    # Data will be imported from the robotics environment
    # We will feed in data that looks like this:
    # data = [{
    # Object: "scissors"
    # Grasp point: [2,5,1]
    # },
    # Object: "scissors"
    # Grasp point:  [1,2,3] #coordinates
    # },
    # {}…]
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=20000,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": """Answer template: <start of analysis> <end of analysis> <start of description> 
                <end of analysis> 
                Remember: Think step by step and show the steps between <start of analysis> and <end of analysis>. 
                Return the key feature and its value between <start of description> and <end of description>. 
                The key features are the 3D spatial information that are not directly included in the [Scene Description] but needs further calculation. 
                In the following, I will provide you the task description."""
            }
        ]
    )
    Analyzer_content = message.content
    print(f"Analyzer: {Analyzer_content}")

    # 2. Planner pipeline
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=20000,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": """You must follow the following answer template:
 
                Given an object list [OBJECT1, OBJECT2, OBJECT3, OBJECT4, ...]
                <start of analysis>
                [OBJECT1]: ...
                [OBJECT2]: ...
                [OBJECT3]: ...
                [OBJECT4]: ...
                [OBJECT5]: ...
                [OBJECT6]: ...
                ...
                The spatial relationship between [OBJECT1] and [OBJECT2]: ...
                The spatial relationship between [OBJECT2] and [OBJECT3]: ... 
                The spatial relationship between [OBJECT1] and [OBJECT3]: ... 
                The spatial relationship between [OBJECT1] and [OBJECT4]: ... 
                The spatial relationship ...
                ...
                [Abstract Plan]: ...
                <end of analysis>

                Rules for analysis:
                * You must only choose [OBJECT] from the object list. 
                * You must show the physical properties of objects, their affordances, and their roles in completing the task.
                * You must reason about the relative positions of the objects along each axis. You must describe the spatial relationship between each pair of objects in the object list first based on numerical positions along each x, y and z axis. For example, whether the objects are in contact, and whether one object is on top of another object etc.

                Rules for [Abstract Plan]:
                * You must reason based on each object's properties and develop [Abstract Plan] with the highest confidence.
                * You must think about how to use [OBJECT] to finish the task.
                * You must think step by step and show the thinking process. For example, what objects you want to use, how to move them, in what order and cause what effect.
                * You must make ensure that the objects are in the right positions for you plan.
                * You must strictly adhere to the constraints provided in the numerical scene information.
                
                In the following, I will provide you the command and the scene information, and you will respond with the analysis. You must complete the task successfully using objects provided.

                You are a robot arm with a gripper as the end effector. The gripper is open initially.
                You are in a 3D world with x-axis pointing forward, y-axis pointing leftward, and z-axis pointing upward.
                You have a skill set containing the following skills:
                * 'move_to_position': Move the gripper to a position. It uses the goal-conditioned policy. You can use it to move to a target position. Moreover, you can use it with proper tools for manipulation tasks. You cannot rotate the gripper. You can only translate the gripper.
                * 'open_gripper': open the gripper before grasping an object.
                * 'close_gripper': close the gripper to grasp an object.
                * 'get_center': get the center position of an object.
                * 'get_graspable_point': get the graspable point of an object.

                Rules for detailed plan:
                * You must plan according to the analysis.
                * You must use existing skills.
                * You must make each plan step only call one skill at a time and be as atomic as possible.
                * You must not knock down any objects.
                * You must get the updated [OBJECT]'s position again if [OBJECT] has moved since the last 'get_center([OBJECT])'.
                * You must only query the object name provided in object list when using 'get_center' and 'get_graspable_point'.

                Individual rules with example answers for detailed plan:
                Rule: To use a grasped [OBJECT1] to move another [OBJECT2]: in the first step, you must make sure [OBJECT1]'s bounding box is adjacent to the [OBJECT2]'s bounding box to ensure that they are in contact. [OBJECT2]'s position does not change because of the contact. In the next step, you should move the grasped [OBJECT1] to push [OBJECT2].
                Example: 
                * Use the 'move_to_position' to move the grasped [OBJECT1] to make contact with [OBJECT2].
                * Use the 'move_to_position' to push the [OBJECT2] ...
                Rule: To push an [OBJECT] into the workspace, the xy position of [OBJECT] must be as close to [0.0, 0.0] as possible.
                Example:
                * Use the 'move_to_position' to push the [OBJECT] into the workspace.
                Rule: To grasp an [OBJECT], you must get the updated [OBJECT]'s graspable point first
                Example:
                * Use the 'get_graspable_point' to get the [OBJECT]'s graspable point.
                * Use the 'move_to_position' to move the gripper close to the graspable point before grasping it.
                * Use the 'close_gripper' to grasp the [OBJECT].

                Example answers for plan:
                <start of plan>
                * Use the [SKILL] to [SINGLE_TASK].
                <end of plan>"""
            }
        ]
    )
    Planner_content = message.content
    print(f"Planner: {Planner_content}")

    # 3. Calculator pipeline
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=20000,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": """This part is to calculate the 3D target positions.

                Common Rules:
                * Calculate step by step and show the calculation process between <start of description> and <end of description>.
                * Return the 3D position between <start of answer> and <end of answer>.
                * You must not assume any position and directly query the updated position of the objects.
                * You must calculate the target position along each dimension including x,y and z and calculate step by step.
                * The "get_position" and "get_size" do not need target positions. Return a space character between <start of answer> and <end of answer>.
                * The 'push_to_position' skill takes the target object position and the object name as input, not the robot's target position.
                * The 'walk_to_position' skill takes the target 3D position as input. Note that the z position does not matter since the skill itself will handle the climbing. You can fill in 0 for the z position.
                * When calculating the target position for the 'push_to_position' skill, you must consider the spatial relationship between the objects. For instances, the target position of [OBJECT1] may be dependent on the position of [OBJECT2] and [OBJECT3].

                Example 1: 
                <Current Step>: Use the "push_to_position" to push 'box' to the middle of object_1 and object_2 in x-axis.
                <start of description>
                * The target position can be computed by using values obtained by "get_position" from the last step. 
                <end of description>
                <start of answer>
                The 3D target position is [(object_1_pos[0] + object_2_pos[0])/2, object_2_pos[1], object_2_pos[2]].
                <end of answer>

                Example 2: 
                <Current Step>: Use the "push_to_position" to push object_1 next to object_2.
                <start of description>
                * Since object_3 is occupying the adjacent positive x direction of object_2, we can only push object_1 to the negative x direction of the object_2. The target position along the x-axis is object_2_pos[0] - object_2_size[0]/2 - object_1_size[0]/2.
                <end of description>
                <start of answer>
                The 3D target position is [object_2_pos[0] - object_2_size[0]/2 - object_1_size[0]/2, object_2_pos[1], object_1_pos[2]].
                <end of answer>

                In the following, you will see the plan and must follow the rules."""
            }
        ]
    )
    Calculator_content = message.content
    print(f"Calculator: {Calculator_content}")

    # 4. Coder pipeline
    message = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=20000,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": """You are a quadrupedal robot.
                The robot has a skill set: ['walk_to_position', 'push_to_position', 'get_position', 'get_size'].
                You have a description of the plan to finish a task. We want you to turn the plan into the corresponding program with following functions:
                ```
                def get_position(object_name):
                return object_position
                
                ```
                get_position returns the 3D position of the object's center. The center position is located in the middle of the object. 
                ```
                def get_size(object_name):
                return object_size
                ```
                object_size is the physical properties for the object.
                ```
                def walk_to_position(target_position):
                ```
                ```
                def push_to_position(object_name, target_object_position):
                ```
                object_name is the name of the object to push.
                target_object_position is the final target position of the object.

                Example answer code:
                ```
                # python
                import numpy as np  # import numpy because we are using it below

                # Always get a position of an object with the 'get_position' function before trying to move to an object.
                box_position = get_position('box')
                ```

                Rules:
                * Always format the code in code blocks.
                * You must not leave unimplemented code blocks in your response.
                * You must not leave undefined variables in your response.
                * The only allowed library is numpy. Do not import or use any other library. If you use np, be sure to import numpy.
                * If you are not sure what value to use, just use your best judge. Do not use None for anything.
                * Do not define new functions, and only use existing functions.

                In the following, I provide you the description and you respond with the code."""
            }
        ]
    )
    Coder_content = message.content
    print(f"Coder: {Coder_content}")