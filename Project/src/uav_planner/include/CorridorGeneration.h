#pragma once

#include <Eigen/Dense>
#include <Eigen/src/Core/Matrix.h>
#include <iostream>
#include <string>
#include <fstream>
#include <cmath>
#include <vector>
#include <Eigen/Eigen>
#include <unordered_set>
#include <QuickHull.hpp>

// #include <octomap/octomap.h>
// #include <quickhull/QuickHull.hpp>

#include "ConvexHull.hpp"
#include "Structs/VertexDataSource.hpp"
#include "tif_reader.h"
#include "Constraint.h"
#include "PathPlanning.h"


namespace std {
    template <>
    struct hash<Eigen::Vector3i> {
        size_t operator()(const Eigen::Vector3i& v) const {
            return ((hash<int>()(v.x()) ^ (hash<int>()(v.y()) << 1)) >> 1) ^ (hash<int>()(v.z()) << 1);
        }
    };
}

struct Polyhedron
{
    Eigen::MatrixXd A;
    Eigen::VectorXd b;
    quickhull::VertexDataSource<double> vertices;
    std::vector<size_t> indices;
    std::vector<std::vector<Eigen::Vector3d>> faces;
};

class CorridorGenerator
{
public:
    CorridorGenerator(Planner& planner_);

    // 根据路径点生成飞行走廊
    std::vector<Polyhedron> FlightCorridorGeneration_point(std::vector<Eigen::Vector3d> path);

    // 根据路径段生成飞行走廊
    std::vector<Polyhedron> FlightCorridorGeneration_line(std::vector<Eigen::Vector3d> path);

    // 生成可视化飞行走廊
    std::vector<Polyhedron> ViewCorridor(std::vector<Polyhedron> corridor)
    {
        std::vector<Polyhedron> corridor_view;
        for (int i = 0; i < corridor.size(); ++i)
        {
            Polyhedron poly;
            for (int j = 0; j < corridor[i].faces.size(); ++j)
            {
                std::vector<Eigen::Vector3d> face;
                for (int k = 0; k < 3; ++k)
                {
                    Eigen::Vector3d p = corridor[i].faces[j][k] - 
                        Eigen::Vector3d(planner.getMap().getTifdata().start[0] * resolution[0], 
                        planner.getMap().getTifdata().start[1] * resolution[1], 
                        planner.getMap().getTifdata().pixelData.minCoeff());    
                    face.push_back(p);
                }
                poly.faces.push_back(face);
            }
            corridor_view.push_back(poly);
        }

        return corridor_view;
    }
    
private:
    Planner planner;
    PathConstraint constraint;
    std::vector<double> resolution;
    quickhull::ConvexHull<double> hull;

    // 凸簇膨胀
    std::vector<Eigen::Vector3d> ConvexInflation(Eigen::Vector3d& seed_position);

    std::vector<Eigen::Vector3d> ConvexInflation(Eigen::Vector3d& point1, Eigen::Vector3d& point2);

    // 获取相邻体素
    std::vector<Eigen::Vector3i> getNeighbors(std::unordered_set<Eigen::Vector3i> cluster, std::unordered_set<Eigen::Vector3i> visited);

    // 检验连通性
    bool checkConvexity(Eigen::Vector3i voxel, std::unordered_set<Eigen::Vector3i> cluster);

    // 根据点集生成多面体
    Polyhedron buildConvexHull(std::vector<Eigen::Vector3d> cluster);

};

// struct Vector3fHash {
//     std::size_t operator()(const Eigen::Vector3f& v) const {
//         std::size_t h1 = std::hash<float>()(v.x());
//         std::size_t h2 = std::hash<float>()(v.y());
//         std::size_t h3 = std::hash<float>()(v.z());
//         return h1 ^ (h2 << 1) ^ (h3 << 2); // 简单组合哈希
//     }
// };

// class FlightCorridorGenerator
// {
// public:
//     octomap::OcTree tree;
//     TIFData tifdata;
//     std::vector<std::vector<float>> path;
//     std::vector<float> resolution;

//     FlightCorridorGenerator(octomap::OcTree tree, TIFData tifdata, std::vector<float> resolution);

//     bool ConvexInflation(Eigen::Vector3f seed, std::vector<Eigen::Vector3f> &inflatePointSet);

//     bool ConvexHullCompute(std::vector<Eigen::Vector3f> inflatePointSet, quickhull::ConvexHull<float> &pointConvex);

//     bool CorridorGenerate(std::vector<std::vector<float>> path);

//     std::unordered_set<Eigen::Vector3f, Vector3fHash> getNeighbor(std::unordered_set<Eigen::Vector3f, Vector3fHash> PointSet);

// };
