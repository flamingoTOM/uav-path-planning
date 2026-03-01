#include "Visualization.h"
#include "nav_msgs/msg/path.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "visualization_msgs/msg/marker_array.hpp"
#include <Eigen/src/Core/Matrix.h>
#include <geometry_msgs/msg/point.hpp>
#include <rclcpp/duration.hpp>
#include <rclcpp/time.hpp>
#include <string>

Visualizer::Visualizer(std::shared_ptr<rclcpp::Node> node_) : node(node_)
{
    map_pub = node->create_publisher<visualization_msgs::msg::MarkerArray>("Map", 10);
    poly_pub = node->create_publisher<visualization_msgs::msg::MarkerArray>("Corridor", 10);
    path_pub = node -> create_publisher<visualization_msgs::msg::MarkerArray>("Path", 10);
    traj_pub = node -> create_publisher<visualization_msgs::msg::MarkerArray>("Trajectory", 10);
}

void Visualizer::publishMap(octomap::OcTree tree, const std::string& ns, std::vector<double> color, double transparency)
{
    visualization_msgs::msg::MarkerArray marker_array;
    visualization_msgs::msg::Marker marker;

    marker.header.frame_id = "map";
    marker.header.stamp = node-> get_clock() ->now();
    marker.ns = ns;
    marker.type = visualization_msgs::msg::Marker::CUBE;
    marker.action = visualization_msgs::msg::Marker::ADD;
    marker.color.a = transparency;
    marker.color.r = color[0];
    marker.color.g = color[1];
    marker.color.b = color[2];
    marker.lifetime = rclcpp::Duration(0, 0);

    int id = 0;
        for (octomap::OcTree::leaf_iterator it = tree.begin_leafs(),
                                            end = tree.end_leafs();
             it != end; ++it)
        {
            if (tree.isNodeOccupied(*it))
            {
                marker.id = id++;
                marker.pose.position.x = it.getX();
                marker.pose.position.y = it.getY();
                marker.pose.position.z = it.getZ();
                marker.scale.x = it.getSize();
                marker.scale.y = it.getSize();
                marker.scale.z = it.getSize();
                marker.pose.orientation.w = 1.0;
                marker_array.markers.push_back(marker);
            }
        }

        map_pub -> publish(marker_array);
}

void Visualizer::publishPathPoints(std::vector<Eigen::Vector3d> path, int marker_id, std::vector<double> color, std::vector<double> scale)
{
    visualization_msgs::msg::MarkerArray marker_array;
    visualization_msgs::msg::Marker line;
    line.header.frame_id = "map";
    line.header.stamp = node->get_clock()->now();
    line.ns = "path" + std::to_string(marker_id);
    line.id = marker_id;
    line.type = line.LINE_STRIP;
    line.action = line.ADD;
    line.scale.x = scale[0];  // 路径线宽度
    line.scale.y = scale[1];
    line.scale.z = scale[2];
    line.color.r = color[0];
    line.color.g = color[1];
    line.color.b = color[2];
    line.color.a = 1.0;
    line.lifetime = rclcpp::Duration(0, 0);

    for (const auto& pt : path) {
        geometry_msgs::msg::Point p;
        p.x = pt.x();
        p.y = pt.y();
        p.z = pt.z();
        line.points.push_back(p);
    }

    marker_array.markers.push_back(line);
    path_pub->publish(marker_array);
}

void Visualizer::publishPolyhedron(std::vector<Polyhedron> polys, std::vector<double> color, double transparency)
{
    visualization_msgs::msg::MarkerArray arr;
    rclcpp::Time now = node -> get_clock() -> now();

    for (int i = 0; i < polys.size(); ++i)
    {
        const auto poly = polys[i];
        visualization_msgs::msg::Marker marker;

        marker.header.frame_id = "map";
        marker.header.stamp = now;
        marker.ns = "polyhedron_" + std::to_string(i);
        marker.id = 0;                                   
        marker.type = visualization_msgs::msg::Marker::TRIANGLE_LIST;
        marker.action = visualization_msgs::msg::Marker::ADD;
        marker.pose.orientation.w = 1.0;
        marker.scale.x = marker.scale.y = marker.scale.z = 1.0;
        marker.color.r = color[0]; 
        marker.color.g = color[1]; 
        marker.color.b = color[2]; 
        marker.color.a = transparency;
        marker.lifetime = rclcpp::Duration(0, 0);

        for (int j = 0; j < poly.faces.size(); ++j)
        {
            for (int k = 0; k < 3; ++k)
            {
                Eigen::Vector3d pt = poly.faces[j][k];
                geometry_msgs::msg::Point p;
                p.x = pt.x(); p.y = pt.y(); p.z = pt.z();
                marker.points.push_back(p);
            }
        }
        
        // for (size_t j = 0; j + 2 < poly.indices.size(); j += 3) {
        //     for (size_t k = 0; k < 3; ++k) {
        //         size_t idx = poly.indices[j + k];
        //         auto pt = poly.vertices[idx];
        //         geometry_msgs::msg::Point p;
        //         p.x = pt.x; p.y = pt.y; p.z = pt.z;
        //         marker.points.push_back(p);
        //     }
        // }
        arr.markers.push_back(marker);
    }
    poly_pub->publish(arr);
    
}


void Visualizer::publishTrajectory(std::vector<Eigen::Vector3d> traj_points, std::vector<double> color, std::vector<double> scale)
{
    visualization_msgs::msg::MarkerArray marker_array;
    visualization_msgs::msg::Marker line;
    line.header.frame_id = "map";
    line.header.stamp = node->get_clock()->now();
    line.ns = "path";
    line.id = 1;
    line.type = line.LINE_STRIP;
    line.action = line.ADD;
    line.scale.x = scale[0];  // 路径线宽度
    line.scale.y = scale[1];
    line.scale.z = scale[2];
    line.color.r = color[0];
    line.color.g = color[1];
    line.color.b = color[2];
    line.color.a = 1.0;
    line.lifetime = rclcpp::Duration(0, 0);

    for (const auto& pt : traj_points) {
        geometry_msgs::msg::Point p;
        p.x = pt(0);
        p.y = pt(1);
        p.z = pt(2);
        line.points.push_back(p);
    }

    marker_array.markers.push_back(line);
    traj_pub->publish(marker_array);
}