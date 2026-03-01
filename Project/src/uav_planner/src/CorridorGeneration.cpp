#include "CorridorGeneration.h"
#include "Constraint.h"
#include "PathPlanning.h"
#include "QuickHull.hpp"
#include "Structs/Vector3.hpp"
#include <Eigen/src/Core/Matrix.h>
#include <octomap/octomap_types.h>
#include <unordered_set>


CorridorGenerator::CorridorGenerator(Planner& planner_) : 
    planner(planner_), 
    constraint(planner_.getConstraint()),
    resolution(planner_.getMap().getResolution())
{}

std::vector<Polyhedron> CorridorGenerator::FlightCorridorGeneration_point(std::vector<Eigen::Vector3d> path)
{
    std::vector<Polyhedron> corridor;
    for (int i = 0; i < path.size(); ++i)
    {
        Eigen::Vector3d path_point = path[i];
        std::vector<Eigen::Vector3d> cluster = ConvexInflation(path_point);
        Polyhedron poly = buildConvexHull(cluster);
        corridor.push_back(poly);
    }
    return corridor;
}

std::vector<Polyhedron> CorridorGenerator::FlightCorridorGeneration_line(std::vector<Eigen::Vector3d> path)
{
    std::vector<Polyhedron> corridor;
    auto start_time_corridor = std::chrono::steady_clock::now();
    for (int i = 0; i < path.size() - 1; ++i)
    {
        Eigen::Vector3d path_point_1 = path[i];
        Eigen::Vector3d path_point_2 = path[i + 1];
        std::vector<Eigen::Vector3d> cluster = ConvexInflation(path_point_1, path_point_2);
        Polyhedron poly = buildConvexHull(cluster);
        corridor.push_back(poly);
    }
    auto end_time_corridor = std::chrono::steady_clock::now();
    std::chrono::duration<double> elapsed_time_corridor = end_time_corridor - start_time_corridor;
    std::cout << "Corridor generation time:" << elapsed_time_corridor.count() << std::endl; 
    return corridor;
}

// 凸簇膨胀
std::vector<Eigen::Vector3d> CorridorGenerator::ConvexInflation(Eigen::Vector3d& seed_position)
{
    std::unordered_set<Eigen::Vector3i> C;      // 当前体素集合
    std::unordered_set<Eigen::Vector3i> C_star;     // 本轮加入的体素
    std::unordered_set<Eigen::Vector3i> C_plus;     // 候选邻居
    std::unordered_set<Eigen::Vector3i> C_all;

    Eigen::Vector3i seed_voxel(static_cast<int>(seed_position.x() / resolution[0]), 
        static_cast<int>(seed_position.y() / resolution[1]), 
        static_cast<int>(seed_position.z() / resolution[2]));

    C.insert(seed_voxel);
    C_all.insert(seed_voxel);

    auto initial_neighbors = getNeighbors(C, C_all);
    C_plus.insert(initial_neighbors.begin(), initial_neighbors.end());

    C_star.clear();

    while (!C_plus.empty()) 
    {
        for (const auto& p_candidate : C_plus) 
        {
            if (checkConvexity(p_candidate, C)) 
            {
                C.insert(p_candidate);
                C_star.insert(p_candidate);
                C_all.insert(p_candidate);
            }
        }

        C_plus.clear();

        auto new_neighbors = getNeighbors(C_star, C_all);
        C_plus.insert(new_neighbors.begin(), new_neighbors.end());

        C_star.clear();
    }

    std::vector<Eigen::Vector3d> C_vector;
    for (const auto& p : C) 
    {
        C_vector.emplace_back(p.x() * resolution[0], p.y() * resolution[1], p.z() * resolution[2]);
    }

    return C_vector;
}

std::vector<Eigen::Vector3d> CorridorGenerator::ConvexInflation(Eigen::Vector3d& point1, Eigen::Vector3d& point2)
{
    std::unordered_set<Eigen::Vector3i> line;
    double sample_res = 0.1;
    double dis = (point1-point2).norm();
    for (double d = 0; d <= dis; d += sample_res)
    {
        Eigen::Vector3d point(point1.x() + (point2 - point1).x() * d / dis, 
            point1.y() + (point2 - point1).y() * d / dis, 
            point1.z() + (point2 - point1).z() * d / dis);
        Eigen::Vector3i point_i(static_cast<int>(point.x() / resolution[0]), 
        static_cast<int>(point.y() / resolution[1]), 
        static_cast<int>(point.z() / resolution[2]));
        line.insert(point_i);
    }


    std::unordered_set<Eigen::Vector3i> C = line;      // 当前体素集合
    std::unordered_set<Eigen::Vector3i> C_star;     // 本轮加入的体素
    std::unordered_set<Eigen::Vector3i> C_plus;     // 候选邻居
    std::unordered_set<Eigen::Vector3i> C_all = line;

    // Eigen::Vector3i seed_voxel(static_cast<int>(seed_position.x() / resolution[0]), 
    //     static_cast<int>(seed_position.y() / resolution[1]), 
    //     static_cast<int>(seed_position.z() / resolution[2]));

    // C.insert(line);
    // C_all.insert(seed_voxel);

    auto initial_neighbors = getNeighbors(C, C_all);
    C_plus.insert(initial_neighbors.begin(), initial_neighbors.end());

    C_star.clear();

    while (!C_plus.empty()) 
    {
        for (const auto& p_candidate : C_plus) 
        {
            if (checkConvexity(p_candidate, C)) 
            {
                C.insert(p_candidate);
                C_star.insert(p_candidate);
                C_all.insert(p_candidate);
            }
        }

        C_plus.clear();

        auto new_neighbors = getNeighbors(C_star, C_all);
        C_plus.insert(new_neighbors.begin(), new_neighbors.end());

        C_star.clear();
    }

    std::vector<Eigen::Vector3d> C_vector;
    for (const auto& p : C) 
    {
        C_vector.emplace_back(p.x() * resolution[0], p.y() * resolution[1], p.z() * resolution[2]);
    }

    return C_vector;
}

std::vector<Eigen::Vector3i> CorridorGenerator::getNeighbors(std::unordered_set<Eigen::Vector3i> cluster, std::unordered_set<Eigen::Vector3i> visited)
{
    const static std::vector<Eigen::Vector3i> directions = []
    {
        std::vector<Eigen::Vector3i> dirs;
        dirs.reserve(26);
        for (int i = -1; i <= 1; ++i) 
        {
            for (int j = -1; j <= 1; ++j)
            {
                for (int k = -1; k <= 1; k++)
                {
                    if (i == 0 && j == 0 && k == 0) continue;
                    dirs.emplace_back(i, j, k);
                }
            }
        }
        return dirs;
    }();
    

    std::unordered_set<Eigen::Vector3i> local_visited = cluster;
    std::vector<Eigen::Vector3i> neighbors;
    neighbors.reserve(cluster.size() * 26); 

    for (const auto& v : cluster)
    {
        for (const auto& dir : directions)
        {
            Eigen::Vector3i n = v + dir;

            if (n.x() >= planner.getMap().getTifdata().width + planner.getMap().getTifdata().start[0] || 
                n.y() >= planner.getMap().getTifdata().height + planner.getMap().getTifdata().start[1] || 
                n.x() < planner.getMap().getTifdata().start[0] || 
                n.y() < planner.getMap().getTifdata().start[1])
            {   
                continue;
            }

            if (visited.find(n) == visited.end() && local_visited.insert(n).second)
            {
                neighbors.push_back(n);
            }
            // if (visited.find(n) == visited.end())
            // {
            //     visited.insert(n);
            //     neighbors.push_back(n);
            // }
        }
    }

    return neighbors;
}

bool CorridorGenerator::checkConvexity(Eigen::Vector3i voxel, std::unordered_set<Eigen::Vector3i> cluster)
{
    octomap::point3d position(voxel.x() * resolution[0], voxel.y() * resolution[1], voxel.z() * resolution[2]);
    if (!planner.isConstraint(position)) 
    {
        return false;
    }

    for (const auto& v : cluster)
    {
        octomap::point3d p(v.x() * resolution[0], v.y() * resolution[1], v.z() * resolution[2]);

        bool los = planner.LineOfSight(p, position);
        
        if (!los)
        {
            return false;
        }
    }

    return true;
}

Polyhedron CorridorGenerator::buildConvexHull(std::vector<Eigen::Vector3d> cluster)
{
    std::vector<quickhull::Vector3<double>> points;
    for (int i = 0; i < cluster.size(); ++i) 
    {
        points.push_back({cluster[i].x(), cluster[i].y(), cluster[i].z()});
        for (double dx = -0.5 * resolution[0]; dx <= 0.5 * resolution[0]; dx += resolution[0])
        {
            for (double dy = -0.5 * resolution[1]; dy <= 0.5 * resolution[1]; dy += resolution[1])
            {
                for (double dz = -0.5 * resolution[2]; dz <= 0.5 * resolution[2]; dz += resolution[2])
                {
                    points.push_back({cluster[i].x() + dx, cluster[i].y() + dy, cluster[i].z() + dz});
                }
            }
        }
    }

    quickhull::QuickHull<double> qh;
    hull = qh.getConvexHull(points, true, false);
    auto vertices= hull.getVertexBuffer();
    auto indices = hull.getIndexBuffer();

    int num_faces = indices.size() / 3;
    Eigen::MatrixXd A(num_faces, 3);
    Eigen::VectorXd b(num_faces);

    std::vector<std::vector<Eigen::Vector3d>> faces;
    for (int i = 0; i < num_faces; ++i)
    {
        size_t i0 = indices[3 * i];
        size_t i1 = indices[3 * i + 1];
        size_t i2 = indices[3 * i + 2];

        const auto& p0 = vertices[i0];
        const auto& p1 = vertices[i1];
        const auto& p2 = vertices[i2];

        Eigen::Vector3d v0(p0.x, p0.y, p0.z);
        Eigen::Vector3d v1(p1.x, p1.y, p1.z);
        Eigen::Vector3d v2(p2.x, p2.y, p2.z);

        faces.push_back({v0, v1, v2});

        Eigen::Vector3d n = (v1 - v0).cross(v2 - v0).normalized();
        double d = n.dot(v0);

        A.row(i) = n.transpose();
        b(i) = d;
    }

    return {A, b, vertices, indices, faces};
}