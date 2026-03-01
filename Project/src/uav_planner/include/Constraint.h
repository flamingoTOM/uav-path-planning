#pragma once

#include <Eigen/Dense>
#include <Eigen/src/Core/Matrix.h>
#include <iostream>
#include <ctime>
#include <chrono>
#include <algorithm>
#include <memory>
#include <octomap/OcTree.h>
#include <octomap/octomap_types.h>
#include "tif_reader.h"
// #include "Map.h"
//#include "PathPlanning.h"
//#include "PathEvaluation.h"

class PathConstraint
{
public:
    // 构造函数，输入约束条件
    PathConstraint(std::vector<double> uav_size_, std::vector<double> detector_size_, std::vector<double> err_position_, 
        double RMSE_DSM_, double max_height_, double min_height_, double max_angle_);

    // 输入地图数据，计算slope和最低飞行高度
    void setMap(TIFData tifdata_map_, TIFData tifdata_cut_);

    // 写slope到文件中
    void writeSlope(std::string filename);

    // 写最低飞行高度到文件中
    void writeLowestHeight(std::string filename);

    // 判断点是否满足约束条件
    bool getConstraint(octomap::point3d position);

    // 不满足约束条件的点，调整高度至合适位置
    bool getCorrectHeight(octomap::point3d &position);

    // 获取无人机占用范围内（xy）的地形高程矩阵
    void CoverageExtension(octomap::point3d position, Eigen::MatrixXd &CoverageHeight);

    // 获取占用范围内最高高程
    double getMaxHeight(octomap::point3d position);

    // 坐标值与像素位置之间转换
    std::vector<int> Position2Pixel(octomap::point3d position);

    // 获取slope
    Eigen::MatrixXd getSlope();

    // 获取最低飞行高度矩阵
    Eigen::MatrixXd getLowestHeight();

    // 获取某一位置下的最低飞行高度
    double getLowestHeightPosition(std::vector<int> position);

    // 获取可通行区域
    void getPassableRegion();

    TIFData getTifData()
    {
        return tifdata_map;
    }

    std::vector<double> getDetectorSize()
    {
        return detector_size;
    }

    std::vector<double> getErrorPosition()
    {
        return err_position;
    }

    double getRMSE()
    {
        return RMSE_DSM;
    }

    double getMinHeight()
    {
        return min_height;
    }

    TIFData getTifDataCut()
    {
        return tifdata_cut;
    }

    void setSlopeRadius(double r)
    {
        slope_r = r;
    }

    void setYawDistance(double d)
    {
        yaw_d = d;
    }

    void setStart(Eigen::Vector3d start_)
    {
        start = start_;
    }

    void setGoal(Eigen::Vector3d goal_)
    {
        goal = goal_;
    }

    octomap::OcTree& getPassableTree()
    {
        return *passable_tree;
    }

    octomap::OcTree& getPassableTreeAll()
    {
        return *passable_tree_all;
    }

    octomap::OcTree& getPassableTreeView()
    {
        return *passable_tree_view;
    }

    octomap::OcTree& getPassableTreeAllView()
    {
        return *passable_tree_all_view;
    }

    Eigen::MatrixXd getZmax()
    {
        return z_max;
    }

    Eigen::MatrixXi getRegion();

    void setRangeThreshold(double threshold)
    {
        range_threshold = threshold;
    }

    double getMaxFlightHeight()
    {
        return max_height + detector_size[2] - 3 * err_position[2];
    }
    
    double getYawDistance()
    {
        return yaw_d;
    }

private:
    std::vector<double> uav_size;                   // 无人机尺寸
    std::vector<double> detector_size;              // 挂载探测器尺寸
    std::vector<double> err_position;               // 无人机飞行位置误差
    double RMSE_DSM;                                // DSM地图高程误差
    double max_height;                              // 探测器最高探测高度
    double min_height;                              // 探测器最低安全高度
    double max_angle;                               // 无人机最大爬升角

    TIFData tifdata_map;                            // 全局DSM地图
    TIFData tifdata_cut;                            // 起终点范围内DSM地图
    Eigen::MatrixXd z_max;                          // 每个位置邻域内的最大高度

    Eigen::MatrixXd slope_matrix;                   // 坡度矩阵
    Eigen::MatrixXd lowest_height_matrix;           // 最低飞行高度矩阵

    double slope_r;                                 // 计算地形坡度时考虑的范围半径
    double yaw_d;                                   // 飞行方向上的最大偏航距离
    Eigen::Vector3d start, goal;                    // 起终点
    std::shared_ptr<octomap::OcTree> passable_tree;                  // 起点到终点方向一定偏航距离的可通行区域
    std::shared_ptr<octomap::OcTree> passable_tree_all;              // 地图范围内可通行区域（高度决定）
    std::shared_ptr<octomap::OcTree> passable_tree_view;             // 可视化起点到终点方向一定偏航距离的可通行区域
    std::shared_ptr<octomap::OcTree> passable_tree_all_view;         // 可视化地图范围内可通行区域（高度决定）

    double range_threshold;                         // 判断区域可行性的高度范围最小值
};






// extern std::vector<float> uav_size;
// extern std::vector<float> detector_size;
// extern std::vector<float> err_position;
// extern float RMSE_dsm;
// extern float max_height;
// extern float max_angle;

// void slope_calculate(TIFData& tifdata);

// void z_constraint(TIFData& tifdata);

// bool xy_constraint(octomap::OcTree octree, octomap::point3d position);

// bool zposition_constraint(TIFData tifdata, octomap::point3d position);

