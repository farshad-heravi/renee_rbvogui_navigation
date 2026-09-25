import glob
import os
from setuptools import find_packages, setup

package_name = 'renee_rbvogui_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob.glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob.glob('config/*.rviz')),
        (os.path.join('share', package_name, 'mesh'), glob.glob('mesh/*')),
        (os.path.join('share', package_name, 'world'), glob.glob('world/*.sdf')),
        (os.path.join('share', package_name, 'world/texture'), glob.glob('world/texture/*')),
        (os.path.join('share', package_name, 'config', 'behavior_trees'), glob.glob('config/behavior_trees/*.xml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Farshad Nozad Heravi',
    maintainer_email='f.n.heravi@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'collision_mode = renee_rbvogui_navigation.collision_mode:main',
        ],
    },
)
