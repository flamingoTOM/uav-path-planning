# pragma once

#include <Eigen/Dense>
#include <Eigen/src/Core/Matrix.h>
#include <fcl/narrowphase/collision_object.h>
#include <fstream>
#include <memory>
#include <octomap/OcTree.h>
#include <octomap/octomap.h>
#include <octomap/ColorOcTree.h>
#include <octomap/octomap_types.h>
#include <rclcpp/publisher_base.hpp>
#include <string>
#include <type_traits>
#include <vector>
#include <deque>
#include <cmath>
#include <algorithm>
#include <functional>
#include "Map.h"
#include "tif_reader.h"
#include "Constraint.h"
#include <fcl/fcl.h>
#include <fcl/geometry/octree/octree.h>
#include <fcl/broadphase/broadphase_dynamic_AABB_tree.h>

class Evaluator;

struct Node 
{
    double x, y, z;                 // 三维坐标
    double g_cost;                  // 从起点到该节点的代价
    double h_cost;                  // 该节点到目标的估计代价
    //double d_cost;                // 节点安全距离
    double height;                  // 飞行高度
    double yaw_d;                   // 偏航距离
    double f_cost;                  // f = g + h，总代价 
    std::shared_ptr<Node> parent;   // 父节点

    Node() : x(0), y(0), z(0), g_cost(0), h_cost(0), f_cost(0) {}
    Node(double x_, double y_, double z_, double g_cost_, double h_cost_, double height_, double yaw_d_)
         : x(x_), y(y_), z(z_), g_cost(g_cost_), h_cost(h_cost_), height(height_), yaw_d(yaw_d_)
    {
        parent = nullptr;
        // f_cost = 0.0;
    }

    void fcostCalculate(double w0, double wh, double wd, double dis = 1.0, double max_h = 1.0, double max_yaw = 1.0)
    {
        f_cost = w0 * (g_cost + h_cost) / dis - wh * height / max_h + wd * yaw_d / max_yaw;
    }

    bool operator==(const Node& other) const
    {
        int ax = static_cast<int>(std::round(x * 1000));
        int ay = static_cast<int>(std::round(y * 1000));
        int az = static_cast<int>(std::round(z * 1000));

        int bx = static_cast<int>(std::round(other.x * 1000));
        int by = static_cast<int>(std::round(other.y * 1000));
        int bz = static_cast<int>(std::round(other.z * 1000));

        return ax == bx && ay == by && az == bz;

        // return x == other.x && y == other.y && z == other.z;
    }

    // double SafeDistance()
    // {
        
    // }
    // bool operator>(const Node& other) const {
    //     return f_cost > other.f_cost;  // 用于优先队列的排序
    // }
};

struct Compare
{
    bool operator()(const Node& node1, const Node& node2)
    {
        if (node1.f_cost != node2.f_cost)
            return node1.f_cost > node2.f_cost;
        else
            return node1.g_cost > node2.g_cost;
    }
};

// struct NodeHash
// {
//     size_t operator()(const Node& n) const
//     {
//         size_t hash_x = std::hash<double>()(n.x);
//         size_t hash_y = std::hash<double>()(n.y);
//         size_t hash_z = std::hash<double>()(n.z);
//         size_t hash_parent = std::hash<Node*>()(n.parent);

//         return hash_x ^ (hash_y << 1) ^ (hash_z << 2) ^ (hash_parent);
//     }
// };

// struct NodeHash
// {
//     size_t operator()(const Node& n) const
//     {
//         int ix = static_cast<int>(std::round(n.x * 1000));
//         int iy = static_cast<int>(std::round(n.y * 1000));
//         int iz = static_cast<int>(std::round(n.z * 1000));

//         return std::hash<int>()(ix) ^ (std::hash<int>()(iy) << 1) ^ (std::hash<int>()(iz) << 2);
//     }
// };

struct NodeHash {
    static size_t hash(const Node& n) {
        size_t h1 = std::hash<double>()(n.x);
        size_t h2 = std::hash<double>()(n.y);
        size_t h3 = std::hash<double>()(n.z);
        return h1 ^ (h2 << 1) ^ (h3 << 2);
    }

    static bool equal(const Node& a, const Node& b) {
        return a.x == b.x && a.y == b.y && a.z == b.z;
    }
};

struct NodeEqual 
{
    bool operator()(const Node& a, const Node& b) const noexcept 
    {
        return a.x == b.x && a.y == b.y && a.z == b.z;
    }
};

class Planner
{
public:
    // 构造函数，输入Map和约束
    Planner(Map map_, PathConstraint constraint);

    // 设置约束方式
    void setConstraintMethod(std::string method_)
    {
        method = method_;
    }

    // 获取路径
    std::vector<Node> getPath(Eigen::Vector3d start_point, Eigen::Vector3d goal_point);

    // 获取可视化路径
    std::vector<Eigen::Vector3d> getViewPath(std::vector<Node> path);

    // Theta*算法
    bool ThetaStar(Node& start_node, Node& goal_node, std::vector<Node>& path);

    // 节点可行性判断
    bool isConstraint(octomap::point3d point);

    // 可视性检查
    bool LineOfSight(octomap::point3d node1, octomap::point3d node2);

    // 父节点更新
    void NodeParentUpdate(Node& node);

    // 高度约束计算
    void setConstraint()
    {
        constraint.setMap(map.getGlobalTifData(), tifdata);
    }

    // 起终点处理
    void NodeUpdate(Eigen::Vector3d& strat, Eigen::Vector3d& goal);

    // 路径简化
    std::vector<Node> pathSimplify(std::vector<Node> path);

    // 保存路径文件
    template<typename T>
    void writePath(std::string filename, std::vector<T> path)
    {
        std::ofstream outFile(filename);
        for (int i = 0; i < path.size(); ++i)
        {
            double x, y, z;
            if constexpr (std::is_same_v<T, Eigen::Vector3d>)
            {
                x = path[i].x();
                y = path[i].y();
                z = path[i].z();
            }
            else if constexpr (std::is_same_v<T, Node>)
            {
                x = path[i].x;
                y = path[i].y;
                z = path[i].z;
            }
            outFile << x << " " << y << " " << z << std::endl;
        }
        outFile.close();
    }

    Map getMap()
    {
        return map;
    }

    PathConstraint getConstraint()
    {
        return constraint;
    }

    // 计算节点距离地面高度
    double getFlightHeight(Eigen::Vector3d point);

    // 计算节点偏航距离
    double getYawDistance(Eigen::Vector3d point);

    // 获取Open List
    std::vector<Node> getOpenList()
    {
        return open;
    }

    // 获取Close List
    std::vector<Node> getCloseList()
    {
        return close;
    }

    void setWeight(double w0_, double wh_, double wd_)
    {
        w0 = w0_;
        wh = wh_;
        wd = wd_;
    }

    void clearOpenList()
    {
        open.clear(); 
    }

    void clearCloseList()
    {
        close.clear();
    }

    double getPlanningTime()
    {
        return time_planning;
    }

private:
    Map map;
    octomap::OcTree tree;
    TIFData tifdata;
    std::vector<double> resolution;
    PathConstraint constraint;
    std::shared_ptr<fcl::CollisionObjectd> uav_obj;
    std::string method;
    Eigen::Vector3d start;
    Eigen::Vector3d goal;
    std::vector<Node> close;
    std::vector<Node> open;
    double w0, wd, wh;
    double distance;
    double time_planning;

    std::shared_ptr<fcl::CollisionObjectd> FclInit();

    double heuristic(Node& a, Node& b) 
    {
        return std::sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y) + (a.z - b.z) * (a.z - b.z));
    }
};