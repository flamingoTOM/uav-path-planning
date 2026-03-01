#pragma once

#include <fcl/narrowphase/collision_object.h>
#include <iostream>
#include <memory>
#include <octomap/OcTree.h>
#include "Constraint.h"
#include "Map.h"
#include "PathPlanning.h"
#include "tif_reader.h"

struct Node;

struct check_node
{
    double x, y, z;
    double height;
    double map_height;
    double g_cost;
    double obstacle_distance;
    double frequency_trn;
    double yaw_d;
};

class Evaluator
{
public:
    // 构造函数
    Evaluator(Planner planner_);

    // 路径安全性评估
    std::vector<check_node> pathSafetyEvaluation(std::vector<Node> path);

    // 计算某一位置Box与地形障碍之间的最近距离（安全距离）
    double SafeDistance(Eigen::Vector3d point);

    std::shared_ptr<fcl::CollisionObjectd> UAVfclInit()
    {
        double box_x = constraint.getDetectorSize()[0];
        double box_y = constraint.getDetectorSize()[1];
        double box_z = constraint.getDetectorSize()[2];
        auto box_shape = std::make_shared<fcl::Boxd>(box_x, box_y, box_z);

        fcl::Transform3d box_tf = fcl::Transform3d::Identity();
    
        auto obb_obj = std::make_shared<fcl::CollisionObjectd>(box_shape, box_tf);
        obb_obj -> computeAABB();

        return obb_obj;
    }

    void writeEvaluation(std::string filename, std::vector<check_node> path);

private:
    Planner planner;
    Map map;
    octomap::OcTree tree;
    TIFData tifdata;
    std::vector<double> resolution;
    PathConstraint constraint;
    std::shared_ptr<fcl::CollisionObjectd> fcl_tree;
    std::shared_ptr<fcl::CollisionObjectd> uav_obj;

};