<<<<<<< HEAD
cmake_minimum_required(VERSION 2.8.3)

project(Singel_car)

find_package(catkin REQUIRED)

catkin_package()

find_package(roslaunch)

foreach(dir config launch meshes urdf)
	install(DIRECTORY ${dir}/
		DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${dir})
endforeach(dir)
=======
cmake_minimum_required(VERSION 2.8.3)

project(Single_car)

find_package(catkin REQUIRED)

catkin_package()

find_package(roslaunch)

foreach(dir config launch meshes urdf)
	install(DIRECTORY ${dir}/
		DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${dir})
endforeach(dir)
>>>>>>> 37fd97bbbe9a74ce69c40f79d2a6611117683e62
