#include "PathEvaluation.h"
#include "tif_reader.h"
#include <Eigen/src/Core/Matrix.h>
#include <fstream>

Evaluator::Evaluator(Planner planner_) :
    planner(planner_),
    map(planner_.getMap()),
    tree(planner_.getMap().getTree()),
    tifdata(planner_.getMap().getTifdata()),
    resolution(planner_.getMap().getResolution()),
    constraint(planner_.getConstraint()),
    fcl_tree(planner_.getMap().getFCLTree()),
    uav_obj(UAVfclInit())
{}

std::vector<check_node> Evaluator::pathSafetyEvaluation(std::vector<Node> path)
{
    std::vector<check_node> eva_path;

    Eigen::Vector3d start_point(path[0].x, path[0].y, path[0].z);
    Eigen::Vector3d goal_point(path.back().x, path.back().y, path.back().z);

    double dis_res = 1.0;
    check_node node;

    for (int i = 0; i < path.size() - 1; ++i) 
    {
        Eigen::Vector3d point1(path[i].x, path[i].y, path[i].z);
        Eigen::Vector3d point2(path[i + 1].x, path[i + 1].y, path[i + 1].z);

        // 评估路径点采样间隔
        double dis = (point1 - point2).norm();

        // 采样
        for (double d = 0; d < dis; d += dis_res) 
        {
            node.x = (point2(0) - point1(0)) * d / dis + point1(0);                     // x位置
            node.y = (point2(1) - point1(1)) * d / dis + point1(1);                     // y位置
            node.z = (point2(2) - point1(2)) * d / dis + point1(2);                     // z位置
            node.g_cost = path[i].g_cost + d;                                           // 已走过的路径长度
            int row = std::floor(node.y / resolution[1]) - tifdata.start[1];
            int col = std::floor(node.x / resolution[0]) - tifdata.start[0];
            double map_height = tifdata.pixelData(row, col);                            // x,y对应的地图高度
            node.height = node.z - map_height;                                          // 无人机飞行高度
            node.map_height = map_height;

            Eigen::Vector3d point(node.x, node.y, node.z);
            node.obstacle_distance = SafeDistance(point);                               // 安全距离
            
            node.frequency_trn = map.computeFtrn(Eigen::Vector3d(node.x, node.y, node.z), {50, 50});
            
            node.yaw_d = planner.getYawDistance(point);

            eva_path.push_back(node);
        }
    }

    if (path.size() == 1)
    {
        node.x = path[0].x;
        node.y = path[0].y;
        node.z = path[0].z;
        node.g_cost = path[0].g_cost;
        int row = std::floor(node.y / resolution[1]) - tifdata.start[1];
        int col = std::floor(node.x / resolution[0]) - tifdata.start[0];
        double map_height = tifdata.pixelData(row, col);                            // x,y对应的地图高度
        node.height = node.z - map_height;                                          // 无人机飞行高度
        node.map_height = map_height;

        Eigen::Vector3d point(node.x, node.y, node.z);
        node.obstacle_distance = SafeDistance(point);                               // 安全距离
            
        node.frequency_trn = map.computeFtrn(Eigen::Vector3d(node.x, node.y, node.z), {50, 50});
            
        node.yaw_d = planner.getYawDistance(point);

        eva_path.push_back(node);
    }

    return eva_path;
}

double Evaluator::SafeDistance(Eigen::Vector3d point)
{
    // 根据点的位置确定无人机box的位置
    fcl::Transform3d box_tf = fcl::Transform3d::Identity();
    box_tf.translation() = Eigen::Vector3d(point.x(), point.y(), point.z() - 0.5 * constraint.getDetectorSize()[2]);

    uav_obj -> setTransform(box_tf);
    uav_obj -> computeAABB();

    // 计算距离
    fcl::DistanceRequestd request;
    fcl::DistanceResultd result;
    request.enable_nearest_points = true;

    double safe_distance = fcl::distance(fcl_tree.get(), uav_obj.get(), request, result);

    return safe_distance;
}

void Evaluator::writeEvaluation(std::string filename, std::vector<check_node> path)
{
    std::ofstream outFile(filename);
    for (int i = 0; i < path.size(); ++i) 
    {
        check_node node = path[i];
        outFile << node.x << " " << node.y << " " << node.z << " ";
        outFile << node.height << " " << node.map_height << " ";
        outFile << node.g_cost << " ";
        outFile << node.obstacle_distance << " ";
        outFile << node.frequency_trn << " ";
        outFile << node.yaw_d << std::endl;
    }
    outFile.close();
}