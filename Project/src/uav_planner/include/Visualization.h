#pragma once

//#include <Eigen/src/Core/Matrix.h>
#include <Eigen/Dense>
#include <iostream>
#include <rclcpp/publisher.hpp>
#include <rclcpp/rclcpp.hpp>
#include <visualization_msgs/msg/marker_array.hpp>
#include <nav_msgs/msg/path.hpp>
#include "CorridorGeneration.h"
#include "PathPlanning.h"
#include "nav_msgs/msg/path.hpp"

class Visualizer
{
public:
    // 构造函数
    Visualizer(std::shared_ptr<rclcpp::Node> node_);

    // 发布三维栅格地图
    void publishMap(octomap::OcTree tree, 
        const std::string& ns = "octomap",
        std::vector<double> color = {0.1, 0.5, 0.9}, 
        double transparency = 1.0);

    // 发布路径
    void publishPathPoints(std::vector<Eigen::Vector3d> path, 
        int marker_id = 1,
        std::vector<double> color = {0.85, 0.325, 0.098},
        std::vector<double> scale = {1.5, 1.5, 1.5}
        );

    // 发布多面体飞行走廊
    void publishPolyhedron(std::vector<Polyhedron> polys, 
        std::vector<double> color = {0.929, 0.694, 0.125}, 
        double transparency = 0.1);

    // 发布轨迹
    void publishTrajectory(std::vector<Eigen::Vector3d> traj_points, 
        std::vector<double> color = {0.466, 0.674, 0.188},
        std::vector<double> scale = {1.5, 1.5, 1.5});

private:
    std::shared_ptr<rclcpp::Node> node;
    // Map发布器
    rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr map_pub;
    // Corridor发布器
    rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr poly_pub;
    // Path发布器
    rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr path_pub;
    // Trajectory发布器
    rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr traj_pub;

};