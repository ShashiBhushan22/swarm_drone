import os
from glob import glob
from setuptools import setup

package_name = 'single_drone_flight'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name, f'{package_name}.controller', f'{package_name}.controller.missions'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*launch.[pxy][yma]*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Simple ROS2 package to fly a single drone to 5 meters height using PX4 offboard control',
    license='BSD-3',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'single_drone_control = single_drone_flight.controller.single_drone_control:main',
            'box_mission = single_drone_flight.controller.missions.box_mission:main',  # ADD THIS LINE
            'figure8_mission = single_drone_flight.controller.missions.figure8_mission:main',    # ADD THIS LINE
            'spiral_mission = single_drone_flight.controller.missions.spiral_mission:main',      # ADD THIS LINE
        ],
    },
)
