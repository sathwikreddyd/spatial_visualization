Spatial Visualization
Dev: Nov 2022
Technologies: Scala, Apache Sedona, Spark, Django, HTML, CSS, Bootstrap, JS

Certainly! Here's an elaboration on the functionality of the three functions:

1. **getSpatialRange()**: This function retrieves trajectory data within a specified spatial range. Trajectory data typically consists of sequences of locations (latitude and longitude coordinates) recorded over time. The getSpatialRange() function takes input parameters defining a geographic area, such as a bounding box or a circular region with a center point and radius. It then queries the trajectory dataset to extract all trajectory points falling within this spatial range. The output is a subset of the original dataset containing only the trajectory points that lie within the specified geographic boundary.

2. **getSpatioTemporalRange()**: This function retrieves trajectory data within a specified spatio-temporal range. In addition to spatial constraints, this function also considers time constraints. Along with the spatial parameters defining the geographic area, getSpatioTemporalRange() takes time parameters specifying a time interval or range. It then filters the trajectory dataset to extract all trajectory points that fall within both the specified spatial and temporal constraints. The output is a subset of the original dataset containing trajectory points that satisfy both the spatial and temporal criteria.

3. **getKNNTrajectory()**: This function retrieves the K-nearest neighbor trajectories for a given trajectory point. Given a reference trajectory point, getKNNTrajectory() finds the K trajectories from the dataset that are closest to this reference point based on spatial distance. It calculates the spatial distance between the reference point and all other trajectory points in the dataset, then selects the K trajectories with the shortest distances. This function is useful for tasks such as identifying similar trajectories or finding nearby trajectories for a given location. The output is a list of K trajectories, each representing a sequence of locations similar to the reference trajectory point.
