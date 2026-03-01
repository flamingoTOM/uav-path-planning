#include "PathPlanning.h"
#include "Constraint.h"
#include "tif_reader.h"
#include <Eigen/src/Core/Matrix.h>
#include <chrono>
#include <cmath>
#include <fcl/common/types.h>
#include <fcl/narrowphase/collision_object.h>
#include <fcl/narrowphase/collision_request.h>
#include <fcl/narrowphase/collision_result.h>
#include <fcl/narrowphase/continuous_collision.h>
#include <memory>
#include <octomap/OcTree.h>
#include <octomap/OcTreeNode.h>
#include <octomap/octomap_types.h>
#include <oneapi/tbb/concurrent_unordered_set.h>

Planner::Planner(Map map_, PathConstraint constraint_) :
    map(map_),
    tree(map_.getTree()),
    tifdata(map_.getTifdata()),
    resolution(map_.getResolution()),
    constraint(constraint_),
    uav_obj(FclInit())
{}

std::vector<Node> Planner::getPath(Eigen::Vector3d start_point, Eigen::Vector3d goal_point)
{
    // 起终点的验证和更新
    NodeUpdate(start_point, goal_point);

    start = start_point;
    goal = goal_point;
    distance = (goal - start).norm();

    // 起终点
    std::vector<Node> path;
    Node start_node(start.x(), start.y(), start.z(), 0.0, (start - goal).norm(), getFlightHeight(start), std::abs(getYawDistance(start)));
    start_node.fcostCalculate(w0, wh, wd, distance, constraint.getMaxFlightHeight(), constraint.getYawDistance());

    Node goal_node(goal.x(), goal.y(), goal.z(), 0.0, 0.0, getFlightHeight(goal), std::abs(getYawDistance(goal)));
    goal_node.fcostCalculate(w0, wh, wd, distance, constraint.getMaxFlightHeight(), constraint.getYawDistance());

    // 路径规划
    auto start_time = std::chrono::steady_clock::now();
    bool get_path = ThetaStar(start_node, goal_node, path);
    auto end_time = std::chrono::steady_clock::now();

    // 规划时间
    std::chrono::duration<double> elapsed_time = end_time - start_time;
    time_planning = elapsed_time.count();
    path = pathSimplify(path);

    // 路径规划
    if (get_path)
    {
        std::cout << "Successful! The time of planning: " << elapsed_time.count() << std::endl;
        std::cout << "Number of nodes: " << path.size() << std::endl;
        std::cout << "Final cost: " << path.back().f_cost << std::endl;
    }
    else 
    {
        std::cout << "Fail!" << std::endl;
    }

    std::string filename = "Result/Path" + method + ".txt";
    writePath(filename, path);
    
    return path;
}

std::vector<Node> Planner::pathSimplify(std::vector<Node> path)
{
    std::vector<Node> path_simp;
    path_simp.push_back(path[0]);
    for (int i = 1; i < path.size() - 1; ++i)
    {
        Eigen::Vector3d p0(path[i - 1].x, path[i - 1].y, path[i - 1].z);
        Eigen::Vector3d p1(path[i].x, path[i].y, path[i].z);
        Eigen::Vector3d p2(path[i + 1].x, path[i + 1].y, path[i + 1].z);

        Eigen::Vector3d a = p1 - p0;
        Eigen::Vector3d b = p2 - p0;
        Eigen::Vector3d crossProduct = a.cross(b);
        if (crossProduct.norm() < 1e-8)
        {
            continue;
        }
        path_simp.push_back(path[i]);
    }
    path_simp.push_back(path.back());
    return path_simp;
}

std::vector<Eigen::Vector3d> Planner::getViewPath(std::vector<Node> path)
{
    std::vector<Eigen::Vector3d> view_path;
    for (int i = 0; i < path.size(); ++i) 
    {
        double x = path[i].x - tifdata.start[0] * resolution[0];
        double y = path[i].y - tifdata.start[1] * resolution[1];
        double z = path[i].z - tifdata.pixelData.minCoeff();
        view_path.emplace_back(x, y, z);
    }

    std::string filename_view = "Result/Path" + method + "_View.txt";
    writePath(filename_view, view_path);

    return view_path;
}

bool Planner::ThetaStar(Node &start_node, Node &goal_node, std::vector<Node> &path)
{
    // if (method == "Height")
    // {
    //     setConstraint();
    // }

    // 26个邻居节点
    int dx[26], dy[26], dz[26];
    int motion_num = 0;
    for (int xx = -1; xx <= 1; xx++)
    {
        for (int yy = -1; yy <= 1; yy++)
        {
            for (int zz = -1; zz <= 1; zz++)
            {
                if (xx == 0 && yy == 0 && zz == 0)
                    continue;
                dx[motion_num] = xx * resolution[0];
                dy[motion_num] = yy * resolution[1];
                dz[motion_num] = zz * resolution[2];
                motion_num ++;
            }
        }
    }

    Eigen::VectorXf hcost_list;
    std::deque<Node> Current_nodelist;
    tbb::concurrent_priority_queue<Node, Compare> open_list;
    // std::unordered_set<Node, NodeHash> open_list_set;
    tbb::concurrent_unordered_set<Node, NodeHash> open_list_set;
    tbb::concurrent_hash_map<Node, bool, NodeHash> open_list_map;
    tbb::concurrent_unordered_map<int, tbb::concurrent_unordered_map<int, tbb::concurrent_unordered_map<double, bool>>> closed_list;
    
    // std::mutex mtx;

    open_list.push(start_node);

    octomap::point3d start_point(start_node.x, start_node.y, start_node.z);
    //bool start_collision = Collision(start_point);

    octomap::point3d goal_point(goal_node.x, goal_node.y, goal_node.z);
    //bool goal_collision = Collision(goal_point);

    while (!open_list.empty()) 
    {
        Node current;
        open_list.try_pop(current);
        octomap::point3d current_point(current.x,current.y, current.z);
        // fcl::CollisionObjectd current_box = BoxGeneration(current_point);
        if (!isConstraint(current_point) || closed_list[current.x][current.y][current.z])
        {
            //open_list.pop();
            continue;
        }
        Current_nodelist.push_back(current);
        close.push_back(current);
        //open_list.pop();

        //hcost_list.push_back(current.h_cost);
        hcost_list.conservativeResize(hcost_list.size() + 1);
        hcost_list[hcost_list.size() - 1] = current.h_cost;
        double minh = hcost_list.minCoeff();
        // 如果当前节点是目标节点，生成路径并返回
        if (current.x == goal_node.x && current.y == goal_node.y && current.z == goal_node.z)
        {
            //std::vector<Node> path;
            //Node* node = &came_from[current.x][current.y][current.z];
            Node* node = &Current_nodelist.back();
            while (node != nullptr)
            {
                path.push_back(*node);
                node = node->parent.get();
            }
            std::reverse(path.begin(), path.end());  // 翻转路径

            // 取出元素到open中
            Node node_pop;
            while (open_list.try_pop(node_pop)) 
            {
                open.push_back(node_pop);
            }

            return true;
        }

        // 标记当前节点为已访问
        closed_list[current.x][current.y][current.z] = true;
        //came_from[current.x][current.y][current.z] = current;

        std::vector<Node> neighbor_nodes(26);
        for (int i = 0; i < 26; i++)
        {
            neighbor_nodes[i].x = current.x + dx[i];
            neighbor_nodes[i].y = current.y + dy[i];
            neighbor_nodes[i].z = current.z + dz[i];
        }
        
        tbb::parallel_for_each(neighbor_nodes.begin(), neighbor_nodes.end(), [&](Node& neighbor_node)
        {
            octomap::point3d neighbor_point(neighbor_node.x, neighbor_node.y, neighbor_node.z);    
            std::vector<int> neighbor_point_pixel = {0, 0};
            neighbor_point_pixel[0] = (int)std::floor(neighbor_point.x() / resolution[0]) - (int)tifdata.start[0];
            neighbor_point_pixel[1] = (int)std::floor(neighbor_point.y() / resolution[1]) - (int)tifdata.start[1];
            
            if (neighbor_point_pixel[0] < 0 || neighbor_point_pixel[0] >= tifdata.width || neighbor_point_pixel[1] < 0 || neighbor_point_pixel[1] >= tifdata.height)
            {
                return;
            }
            

            if (!isConstraint(neighbor_point) ||closed_list[neighbor_node.x][neighbor_node.y][neighbor_node.z])
            {
                return;
            }
            
            double dcost =neighbor_point.distance(current_point);
            double tentative_g_cost = current.g_cost + dcost;
            double h_cost = heuristic(neighbor_node, goal_node);

            Node neighbor(neighbor_node.x, neighbor_node.y, neighbor_node.z, tentative_g_cost, h_cost, 
                getFlightHeight(Eigen::Vector3d(neighbor_node.x, neighbor_node.y, neighbor_node.z)),
                std::abs(getYawDistance(Eigen::Vector3d(neighbor_node.x, neighbor_node.y, neighbor_node.z))));
            neighbor.parent = std::make_shared<Node>(Current_nodelist.back());
            neighbor.fcostCalculate(w0, wh, wd, distance, constraint.getMaxFlightHeight(), constraint.getYawDistance());

            if (current.parent != nullptr)
            {
                NodeParentUpdate(neighbor);
            }
            
            // if (open_list_set.insert(neighbor).second)
            // {
            //     open_list.push(neighbor);
            // }  

            // auto [it, inserted] = open_list_set.insert(neighbor);
            // if (inserted)
            // {
            //     open_list.push(neighbor);
            // }
            // else
            // {
            //     if (it->g_cost > neighbor.g_cost)
            //     {
            //         open_list_set.erase(it);
            //         open_list_set.insert(neighbor);
            //         open_list.push(neighbor);
            //     }
            // }

            tbb::concurrent_hash_map<Node, bool, NodeHash>::accessor acc;
            bool inserted = open_list_map.insert(acc, neighbor);
            if (inserted)
            {
                open_list.push(neighbor);
            }
            else
            {
                if (acc->first.g_cost > neighbor.g_cost)
                {
                    // 删除旧的
                    open_list_map.erase(acc);

                    // 插入新的
                    tbb::concurrent_hash_map<Node, bool, NodeHash>::accessor new_acc;
                    open_list_map.insert(new_acc, neighbor);

                    open_list.push(neighbor);
                }
            }
        }); 
        
    }

    return false;  // 如果没有路径，返回false
}

bool Planner::isConstraint(octomap::point3d point)
{
    if (method == "None")
    {
        octomap::OcTreeNode* node = tree.search(point);
        return !(node != nullptr && node -> getOccupancy() > 0.5);
    }
    else if (method == "Height")
    {
        return constraint.getConstraint(point);
    }
    else if (method == "Box")
    {
        fcl::Transform3d box_tf = fcl::Transform3d::Identity();
        auto box = std::dynamic_pointer_cast<const fcl::Boxd>(uav_obj -> collisionGeometry());
        auto box_size = box -> side;
        box_tf.translation() = Eigen::Vector3d(point.x(), point.y(), point.z() - 0.5 * box_size[2]);

        uav_obj -> setTransform(box_tf);
        uav_obj -> computeAABB();

        fcl::CollisionRequestd request;
        fcl::CollisionResultd result;

        auto callback = [](fcl::CollisionObjectd* o1, fcl::CollisionObjectd* o2, void* cdata) 
        {
            fcl::CollisionResultd* result = static_cast<fcl::CollisionResultd*>(cdata);

            fcl::CollisionRequestd request;
            fcl::collide(o1, o2, request, *result);
            return result->isCollision();  // true 表示可以提早终止碰撞检测
        };

        request.num_max_contacts = 1;
        request.enable_contact = false;
        request.gjk_solver_type = fcl::GJKSolverType::GST_LIBCCD;

        fcl::collide(map.getFCLTree().get(), uav_obj.get(), request, result);
        return (!result.isCollision()) && constraint.getConstraint(point) ;
    }
    else 
    {
        std::cout << "The Constraint Method is Wrong!" << std::endl;
        return false;
    }
}

bool Planner::LineOfSight(octomap::point3d node1, octomap::point3d node2)
{
    if (!isConstraint(node1) || !isConstraint(node2))
    {
        return false;
    }
    double LOS_res = 0.05;//*std::min_element(resolution.begin(), resolution.end());
    double dis = std::sqrt(std::pow(node1.x()-node2.x(), 2) + std::pow(node1.y()-node2.y(), 2) + std::pow(node1.z()-node2.z(), 2));
    
    int numSteps = static_cast<int>(dis / LOS_res);
    double stepX = (node2.x() - node1.x()) / numSteps;
    double stepY = (node2.y() - node1.y()) / numSteps;
    double stepZ = (node2.z() - node1.z()) / numSteps;

    std::atomic<bool> isBlocked(false);
    tbb::task_group tg;

    tbb::parallel_for(0, numSteps, [&](int i) {
        if (isBlocked.load()) tg.cancel();  // 发现障碍物，立即终止

        double check_x = node1.x() + i * stepX;
        double check_y = node1.y() + i * stepY;
        double check_z = node1.z() + i * stepZ;

        check_x = std::floor(check_x / resolution[0]) * resolution[0];
        check_y = std::floor(check_y / resolution[1]) * resolution[1];
        check_z = std::floor(check_z / resolution[2]) * resolution[2];

        octomap::point3d node_check(check_x, check_y, check_z);

        if (!isConstraint(node_check)) 
        {
            isBlocked.store(true);
            tg.cancel();
        }
    });

    return !isBlocked.load();
}

void Planner::NodeParentUpdate(Node &node)
{
    std::shared_ptr<Node> p = node.parent;
    std::shared_ptr<Node> pp = p->parent;
    octomap::point3d node_point(node.x, node.y, node.z);
    octomap::point3d node_parent(pp->x, pp->y, pp->z);
    bool LOS = LineOfSight(node_point, node_parent);
    if (LOS)
    {
        double gcost_new = pp->g_cost + heuristic(*pp, node);
        if (gcost_new <= node.g_cost)
        {
            Node node1(node.x, node.y, node.z, gcost_new, node.h_cost, 
                getFlightHeight(Eigen::Vector3d(node.x, node.y, node.z)),
                std::abs(getYawDistance(Eigen::Vector3d(node.x, node.y, node.z))));
            node1.parent = pp;
            node1.fcostCalculate(w0, wh, wd, distance, constraint.getMaxFlightHeight(), constraint.getYawDistance());
            node = node1;
        }       
    }
}

void Planner::NodeUpdate(Eigen::Vector3d &start, Eigen::Vector3d &goal)
{
    Eigen::Vector3d res(resolution[0], resolution[1], resolution[2]);
    start = ((start.array() / res.array()).floor() * res.array()).matrix();
    goal = ((goal.array() / res.array()).floor() * res.array()).matrix();

    octomap::point3d start_point(start.x(), start.y(), start.z());
    octomap::point3d goal_point(goal.x(), goal.y(), goal.z());
    double dz = resolution[2];

    if (!isConstraint(start_point)) 
    {
        std::cout << "Start point doesn't meet constraint!" << std::endl;

        std::vector<int> start_pixel = constraint.Position2Pixel(start_point);

        std::cout << "The Max Z of start point: " << tifdata.max_z(start_pixel[0], start_pixel[1]) << std::endl;
        std::cout << "The Min Z of start poitnL " << tifdata.min_z(start_pixel[0], start_pixel[1]) << std::endl;
        start_point.z() = std::ceil(0.5 * (tifdata.max_z(start_pixel[0], start_pixel[1]) + tifdata.min_z(start_pixel[0], start_pixel[1])) / res.z()) * res.z();

        // while(!isConstraint(start_point))
        // {
        //     std::vector<int> pixel_position = constraint.Position2Pixel(start_point);
        //     start_point.z() += dz * ((start_point.z() < tifdata.max_z(pixel_position[0], pixel_position[1])) ? 1 : -1);
        // }
        //std::cout << "(" << start_point.x() << "," << start_point.y() << "," << start_point.z() << ")" << std::endl;
        std::cout << "Advised Start Point: (" << start_point.x() << "," << start_point.y() << "," << start_point.z() << ")" << std::endl;

        start = Eigen::Vector3d(start_point.x(), start_point.y(), start_point.z());
    }

    if (!isConstraint(goal_point)) 
    {
        // std::cout << "Goal point doesn't meet constraint, Change Point: ";

        std::cout << "Goal point doesn't meet constraint!" << std::endl;

        std::vector<int> goal_pixel = constraint.Position2Pixel(goal_point);

        std::cout << "The Max Z of goal point: " << tifdata.max_z(goal_pixel[0], goal_pixel[1]) << std::endl;
        std::cout << "The Min Z of goal poitnL " << tifdata.min_z(goal_pixel[0], goal_pixel[1]) << std::endl;
        goal_point.z() = std::ceil(0.5 * (tifdata.max_z(goal_pixel[0], goal_pixel[1]) + tifdata.min_z(goal_pixel[0], goal_pixel[1])) / res.z()) * res.z();

        // while(!isConstraint(goal_point))
        // {
        //     std::vector<int> pixel_position = constraint.Position2Pixel(goal_point);
        //     goal_point.z() += dz * ((start_point.z() < tifdata.max_z(pixel_position[0], pixel_position[1])) ? 1 : -1);
        // }
        // std::cout << "(" << goal_point.x() << "," << goal_point.y() << "," << goal_point.z() << ")" << std::endl;
        std::cout << "Advised Goal Point: (" << goal_point.x() << "," << goal_point.y() << "," << goal_point.z() << ")" << std::endl;
        goal = Eigen::Vector3d(goal_point.x(), goal_point.y(), goal_point.z());
    }
}

std::shared_ptr<fcl::CollisionObjectd> Planner::FclInit()
{
    double box_x = constraint.getDetectorSize()[0] + 6 * constraint.getErrorPosition()[0];
    double box_y = constraint.getDetectorSize()[1] + 6 * constraint.getErrorPosition()[1];
    double box_z = constraint.getDetectorSize()[2] + 3 * constraint.getErrorPosition()[2] 
        + 3 * constraint.getRMSE() + constraint.getMinHeight();
    auto box_shape = std::make_shared<fcl::Boxd>(box_x, box_y, box_z);

    fcl::Transform3d box_tf = fcl::Transform3d::Identity();
    
    auto obb_obj = std::make_shared<fcl::CollisionObjectd>(box_shape, box_tf);
    obb_obj -> computeAABB();

    return obb_obj;
}

double Planner::getFlightHeight(Eigen::Vector3d point)
{
    int row = point.y() / resolution[1] - map.getTifdata().start[1];
    int col = point.x() / resolution[0] - map.getTifdata().start[0];
    double z_d = map.getTifdata().pixelData(row, col);

    double z1 = point.z();
    double h = z1 - z_d;

    return h;
}

double Planner::getYawDistance(Eigen::Vector3d point)
{
    // double d = std::abs((goal.x() - start.x()) * (start.y() - point.y()) - (start.x() - point.x()) * (goal.y() - start.y())) / 
    //     std::sqrt(std::pow(goal.x() - start.x(), 2.0) + std::pow(goal.y() - start.y(), 2.0));

    double d = ((goal.x() - start.x()) * (start.y() - point.y()) - (start.x() - point.x()) * (goal.y() - start.y())) / 
        std::sqrt(std::pow(goal.x() - start.x(), 2.0) + std::pow(goal.y() - start.y(), 2.0));

    return d;
}