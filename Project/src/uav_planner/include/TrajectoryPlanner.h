#pragma once


#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <algorithm>
#include <OsqpEigen/OsqpEigen.h>
#include "CorridorGeneration.h"
#include "PathPlanning.h"

class BsplineTrajectoryPlanner
{
public:
    // 构造函数
    //BsplineTrajectoryPlanner(PathPlanner planner_, int order_, int control_points_num_);
    BsplineTrajectoryPlanner(int order_, int control_points_num_);

    // 设置路径点（根据Theta*算法规划的路径）
    void setWayPoints(std::vector<Node> path);

    // 设置飞行走廊约束
    void setCorridor(std::vector<Polyhedron> corridor);

    // 设置动力学约束
    void setDynamicConstraints(double max_vel, double max_acc);

    // 根据控制点获取轨迹
    std::vector<Eigen::Vector3d> getTrajectoryPoints();

    // 初始化控制点位置
    void InitControlPoints();

    // 计算代价函数
    double computeCost(std::vector<Eigen::Vector3d> control, Planner planner);

    // 优化控制点分布
    void optimizeControlPoints();

    // 设置每一段路径的时间（根据总时间和每段路径长度分配）
    void setSegmentTimes(double total_time);

    // 获取一段轨迹
    std::vector<Eigen::Vector3d> getSingleTrajetory();

private:
    //PathPlanner planner;
    int order;                                      // B样条阶数
    int control_points_num;                         // 每段轨迹的控制点数量
    int segment_num;                                // 路径段数
    std::vector<double> times;

    std::vector<Eigen::Vector3d> way_points;        // 初始路径点（由Theta*算法生成）
    std::vector<Polyhedron> constraint_corridor;    // 飞行走廊约束
    std::vector<std::vector<double>> knot_vectors;  // 节点向量
    std::vector<std::vector<Eigen::Vector3d>> control_points;   // 控制点

    double max_velocity;                            // 最大飞行速度
    double max_acceleration;                        // 最大飞行加速度

    // 递归实现B样条函数
    double deBoorBasis(int i, int k, double t, std::vector<double> knots);

    Eigen::Vector3d evaluateBSpline(double t, int degree, const std::vector<double>& knots);
};

class MinimumSnapTrajectoryPlanner
{
public:
    // 构造函数，设置多项式阶数
    MinimumSnapTrajectoryPlanner(int poly_order_);

    // 设置路径点（根据Theta*算法规划的路径）
    void setWayPoints(std::vector<Node> path);

    // 设置每一段路径的时间（根据总时间和每段路径长度分配）
    void setSegmentTimes(double total_time);

    // 求解优化问题，获取轨迹参数
    bool getSolution(std::vector<std::vector<Eigen::VectorXd>>& coeff_xyz);

    std::vector<double> times;      // 每段路径的时间

private:
    int poly_order;     //多项式阶数
    int coeff_num;      //轨迹多项式系数数量
    int segment_num;    //路径段数

    std::vector<Eigen::Vector3d> waypoints;     //所有路径点位置

    // 目标函数：最小化snap
    Eigen::SparseMatrix<double> Q_all;      // 全局目标函数的Q矩阵
    Eigen::VectorXd f_all;      // 全局目标函数线性项系数
    
    // 约束，考虑起终点位置和
    Eigen::SparseMatrix<double> A_all_x, A_all_y, A_all_z;      // 全局约束矩阵
    Eigen::VectorXd lb_all_x, ub_all_x, lb_all_y, ub_all_y, lb_all_z, ub_all_z;     //全局约束上下界

    std::vector<Eigen::VectorXd> coeff_all_x, coeff_all_y, coeff_all_z;     //全部路径段的系数

    // 构建目标函数Q矩阵
    void buidQAll();

    // 构建约束矩阵A和约束上下界
    void buildConstraints();
};

class TrajectoryPlanner
{
public:
    // 轨迹规划构造函数
    TrajectoryPlanner(std::string planner_);

    // 输入初始路径
    void setInitPath(std::vector<Node> path_);

    // 设置飞行速度
    void setVelocity(double velocity_);

    // 轨迹求解
    void TrajectoryGenerate(std::vector<Eigen::Vector3d>& trajectory_points);

    //void setPathPlanner(PathPlanner pathplanner_);

private:
    std::vector<std::vector<Eigen::VectorXd>> coeff;        // 多项式轨迹参数
    std::vector<Node> path;     // 初始路径点
    std::string planner;        // 规划方法
    //PathPlanner pathplanner;
    double velocity;        // 飞行速度

};