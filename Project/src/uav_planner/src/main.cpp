// #include "CorridorGeneration.h"
#include "PathEvaluation.h"
#include "Constraint.h"
#include "Map.h"
#include "PathPlanning.h"
// #include "TrajectoryPlanner.h"
#include "Visualization.h"
#include "tif_reader.h"
#include <Eigen/src/Core/Matrix.h>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <ios>
#include <iostream>
#include <memory>
#include <mutex>
#include <octomap/OcTree.h>
#include <rclcpp/node.hpp>
#include <sstream>
#include <string>
#include <vector>
#include <filesystem> 

std::vector<Eigen::Vector3d> loadPointsFromTxt(const std::string& filename) {
    std::ifstream infile(filename);
    if (!infile.is_open()) {
        std::cerr << "无法打开文件: " << filename << std::endl;
        return {};
    }

    std::vector<Eigen::Vector3d> points;
    double x, y, z;
    while (infile >> x >> y >> z) {
        points.emplace_back(x, y, z);
    }
    return points;
}

int main(int argc, char **argv)
{
    // DSM数据输入（.tif格式）
    const char *filename = "Data/Mt_EtnaDSM_Clip2.tif"; // TIF文件路径

    Map map_global(2.0);
    if (map_global.readTif(filename))
    {
        // 输出图像基本信息
        std::cout << "图像宽度: " << map_global.getTifdata().width << std::endl;
        std::cout << "图像高度: " << map_global.getTifdata().height << std::endl;
    }
    else 
    {
        std::cerr << "读取TIF文件失败!" << std::endl;
    }
    std::vector<double> resolution = map_global.getTifdata().res;

    // 起点和终点
    // 情况1
    Eigen::Vector3d start_point_pixel = {1584.00/2, 1500.00/2, 3200};
    Eigen::Vector3d goal_point_pixel = {1782.00/2, 1690.00/2, 3200};

    // 不可规划情况
    // Eigen::Vector3d start_point_pixel = {1742.00/2, 1092.00/2, 3200};
    // Eigen::Vector3d goal_point_pixel = {1840.00/2, 1286.00/2, 3200};

    // 情况2
    // Eigen::Vector3d start_point_pixel = {477.00, 784.00, 3200};
    // Eigen::Vector3d goal_point_pixel = {666.00, 610.00, 3200};

    // 情况3
    // Eigen::Vector3d start_point_pixel = {1022.00, 791.00, 3200};
    // Eigen::Vector3d goal_point_pixel = {865.00, 901.00, 3200};


    // 像素位置转换为坐标位置
    Eigen::Vector3d start_point = {start_point_pixel[0] * resolution[0], start_point_pixel[1] * resolution[1], start_point_pixel[2]};
    Eigen::Vector3d goal_point = {goal_point_pixel[0] * resolution[0], goal_point_pixel[1] * resolution[1], goal_point_pixel[2]};

    // 地图数据处理，将地图裁剪至起终点范围内
    Map map_planning(2.0);
    TIFData tifdata_planning = map_global.cut(start_point_pixel, goal_point_pixel);
    map_planning.setTifData(tifdata_planning, map_global.getTifdata());
    map_planning.octreeGeneration(true);

    // 建立约束
    std::vector<double> uav_size = {10, 4, 6};
    std::vector<double> detector_size = {10, 10, 15};
    std::vector<double> err_position = {2, 2, 2};
    double RMSE_dsm = 0;
    double min_height = 10;
    double max_height = 50;
    double max_angle = 45.0 * M_PI / 180.0;
    double slope_r = 20;
    double yaw_d = 10;

    PathConstraint constraint(uav_size, detector_size, err_position, 
        RMSE_dsm, max_height, min_height, max_angle);

    constraint.setSlopeRadius(slope_r);
    constraint.setYawDistance(yaw_d);
    constraint.setStart(start_point);
    constraint.setGoal(goal_point);

    constraint.setMap(map_global.getTifdata(), map_planning.getTifdata());
    map_planning.setTifData(constraint.getTifDataCut(), map_global.getTifdata());

    constraint.setRangeThreshold(0.0);
    Eigen::MatrixXi region = constraint.getRegion();

    std::ofstream region_file("region.txt");
    for (int i = 0; i < region.rows(); ++i) 
    {
        for (int j = 0; j < region.cols(); ++j) 
        {
            region_file << region(i, j) << " ";
        }
        region_file << std::endl;
    }
    region_file.close();

    // 最低允许的飞行高度（飞行方向上）
    std::vector<double> z_min;
    std::vector<double> dd;
    double d_start_goal = (start_point - goal_point).norm();
    for (double d = 0; d < d_start_goal; d += 0.1) 
    {
        double x = start_point.x() + d / d_start_goal * (goal_point.x() - start_point.x());
        double y = start_point.y() + d / d_start_goal * (goal_point.y() - start_point.y());
        int row = std::floor(y / map_planning.getTifdata().res[0]) - map_planning.getTifdata().start[1];
        int col = std::floor(x / map_planning.getTifdata().res[1]) - map_planning.getTifdata().start[0];
        z_min.push_back(map_planning.getTifdata().min_z(row, col));
        dd.push_back(d);
    }

    // std::reverse(z_min.begin(), z_min.end());
    // std::reverse(dd.begin(), dd.end());

    std::ofstream z_min_file("z_min.txt");
    for (int i = 0; i < z_min.size(); i++) 
    {
        z_min_file << dd[i] << " " << z_min[i] << std::endl;
    }
    z_min_file.close();

    TIFData dsm_expand;
    dsm_expand.pixelData = constraint.getZmax();
    dsm_expand.bands = 1;
    dsm_expand.height = dsm_expand.pixelData.rows();
    dsm_expand.width = dsm_expand.pixelData.cols();
    dsm_expand.res = tifdata_planning.res;
    dsm_expand.start = tifdata_planning.start;

    Map map_expand(2.0);
    map_expand.setTifData(dsm_expand, map_global.getTifdata());
    map_expand.octreeGeneration(false);

    double lowest = tifdata_planning.pixelData.minCoeff();
    // Eigen::Vector3d view_dsm_expand;
    // view_dsm_expand.resize(dsm_expand.height, dsm_expand.width);
    // for (int i = 0; i < view_dsm_expand.rows(); ++i) 
    // {
    //     for (int j = 0; j < view_dsm_expand.cols(); ++j) 
    //     {
    //         view_dsm_expand(i, j) = view_dsm_expand(i, j) - view_dsm_expand.minCoeff() + lowest;
    //     }
    // }
    octomap::OcTree view_tree_expand(2.0);
    tbb::concurrent_vector<Eigen::Vector3d> point_cloud = map_expand.PointCloudGeneration();
    std::mutex tree_mutex;
    tbb::parallel_for_each(point_cloud.begin(), point_cloud.end(), [&](const Eigen::Vector3d& view_point)
    {
        double view_x = std::floor(view_point.x() / dsm_expand.res[0]) * dsm_expand.res[0] - dsm_expand.start[0] * dsm_expand.res[0];
        double view_y = std::floor(view_point.y() / dsm_expand.res[1]) * dsm_expand.res[1] - dsm_expand.start[1] * dsm_expand.res[1];
        double view_z = std::ceil((view_point.z() - lowest) / dsm_expand.res[2]) * dsm_expand.res[2];
        octomap::point3d p_view(view_x, view_y, view_z);
        {
            std::lock_guard<std::mutex> lock(tree_mutex);
            view_tree_expand.updateNode(p_view, true);
        }
        
    });

    std::ofstream dsm_file("dsm.txt");
    for (int i = 0; i < tifdata_planning.pixelData.rows(); ++i) 
    {
        for (int j = 0; j < tifdata_planning.pixelData.cols(); ++j) 
        {
            dsm_file << tifdata_planning.pixelData(i, j) << " ";
        }
        dsm_file << std::endl;
    }
    dsm_file.close();

    std::ofstream dsm_expand_file("dsm_expand.txt");
    for (int i = 0; i < dsm_expand.height; ++i) 
    {
        for (int j = 0; j < dsm_expand.width; ++j) 
        {
            dsm_expand_file << dsm_expand.pixelData(i, j) << " ";
        }
        dsm_expand_file << std::endl;
    }
    dsm_expand_file.close();

    Planner planner(map_planning, constraint);          // 路径规划对象


    // 直接规划并评估
    planner.setWeight(1.0, 0.0, 0.0);
    planner.setConstraintMethod("Height");
    std::vector<Node> path = planner.getPath(start_point, goal_point);
    planner.writePath("Path.txt", path);
    std::vector<Eigen::Vector3d> path_view = planner.getViewPath(path);
    planner.writePath("PathView.txt", path_view);

    Evaluator evaluation(planner);                  // 路径评估对象
    std::vector<check_node> path_eva = evaluation.pathSafetyEvaluation(path);
    std::string filename_eva = "PathEvaluation.txt";
    evaluation.writeEvaluation(filename_eva, path_eva);

    std::vector<Node> path_m;
    for (int i = 1; i < path.size() - 1; ++i)
    {
        path_m.push_back(path[i]);
    }
    planner.writePath("PathM.txt", path_m);
    std::vector<check_node> path_eva_m = evaluation.pathSafetyEvaluation(path_m);

    //std::vector<check_node> path_eva_m;
    for (int i = 0; i < path_eva.size(); ++i) 
    {
        check_node node_m = path_eva[i];
        double d_eva = node_m.g_cost;
        double d_clip = 0.1 * path_eva.back().g_cost;
        if (d_eva >= 0.2 * path_eva.back().g_cost && d_eva <= 0.8 * path_eva.back().g_cost)
        {
            path_eva_m.push_back(node_m);
        }
    }
    evaluation.writeEvaluation("PathEvaluationM.txt", path_eva_m);

    std::vector<Node> open_list = planner.getOpenList();
    std::vector<Node> close_list = planner.getCloseList();

    open_list.insert(open_list.end(), close_list.begin(), close_list.end());
    
    std::vector<Eigen::Vector3d> path_eigen;
    for (int i = 0; i < path.size(); ++i) 
    {
        path_eigen.emplace_back(path[i].x, path[i].y, path[i].z);
    }

    std::ofstream open_list_file("OpenList.txt");
    for (int i = 0; i < open_list.size(); ++i) 
    {
        Node open_node = open_list[i];
        open_list_file << open_node.x << " " << open_node.y << " " << open_node.z << " " << open_node.height << " " << open_node.yaw_d << " " << open_node.f_cost << std::endl;
    }

    std::ofstream close_list_file("CloseList.txt");
    for (int i = 0; i < close_list.size(); ++i) {
        Node close_node = close_list[i];
        close_list_file << close_node.x << " " << close_node.y << " " << close_node.z << " " << close_node.height << " " << close_node.yaw_d << " " << close_node.f_cost << std::endl;
    }

    // // 代价函数高度项、偏航距离项变参实验
    // std::vector<double> wd_set;
    // std::vector<double> wh_set;
    // double wh_step = 0.1;
    // double wh_start = 0.0;
    // double wh_end = 1.0;

    // double wd_step = 0.01;
    // double wd_start = 0.00;
    // double wd_end = 0.20;

    // int wh_digit = 3;
    // int wd_digit = 3;

    // Eigen::MatrixXd time_matrix(int((wh_end - wh_start) / wh_step + 1), int((wd_end - wd_start) / wd_step + 1));

    // int row = 0;
    // for (double w_h = wh_start; w_h <= wh_end; w_h += wh_step) 
    // {
    //     wh_set.push_back(w_h);

    //     std::ostringstream oss_wh;
    //     oss_wh << std::fixed << std::setprecision(1) << w_h;
    //     std::string s_wh = oss_wh.str();

    //     size_t pos_wh = s_wh.find('.');
    //     if (pos_wh != std::string::npos) 
    //     {
    //         s_wh.erase(pos_wh, 1);  // 删除小数点
    //     }

    //     while (s_wh.size() < wh_digit)
    //     {
    //         s_wh.insert(s_wh.begin(), '0');
    //     }

    //     int col = 0;
    //     for (double w_d = wd_start; w_d <= wd_end; w_d += wd_step) 
    //     {
    //         wd_set.push_back(w_d);

    //         std::ostringstream oss_wd;
    //         oss_wd << std::fixed << std::setprecision(2) << w_d;
    //         std::string s_wd = oss_wd.str();

    //         size_t pos_wd = s_wd.find('.');
    //         if (pos_wd != std::string::npos) 
    //         {
    //             s_wd.erase(pos_wd, 1);  // 删除小数点
    //         }

    //         while (s_wd.size() < wd_digit)
    //         {
    //             s_wd.insert(s_wd.begin(), '0');
    //         }

    //         std::string filename = "wh_" + s_wh + "_wd_" + s_wd;
    //         std::filesystem::create_directories(filename);

    //         planner.setConstraintMethod("Height");
    //         planner.setWeight(1.0, w_h, w_d);
    //         std::vector<Node> path = planner.getPath(start_point, goal_point);
    //         planner.writePath(filename + "/Path.txt", path);
    //         std::vector<Eigen::Vector3d> path_view = planner.getViewPath(path);
    //         planner.writePath(filename + "/PathView.txt", path_view);

    //         Evaluator evaluation(planner);                  // 路径评估对象
    //         std::vector<check_node> path_eva = evaluation.pathSafetyEvaluation(path);
    //         std::string filename_eva = filename + "/PathEvaluation.txt";
    //         evaluation.writeEvaluation(filename_eva, path_eva);

    //         std::vector<Node> open_list = planner.getOpenList();
    //         std::vector<Node> close_list = planner.getCloseList();

    //         open_list.insert(open_list.end(), close_list.begin(), close_list.end());

    //         std::ofstream open_list_file(filename + "/OpenList.txt");
    //         for (int i = 0; i < open_list.size(); ++i) 
    //         {
    //             Node open_node = open_list[i];
    //             open_list_file << open_node.x << " " << open_node.y << " " << open_node.z << " " << open_node.height << " " << open_node.yaw_d << " " << open_node.f_cost << std::endl;
    //         }

    //         std::ofstream close_list_file(filename + "/CloseList.txt");
    //         for (int i = 0; i < close_list.size(); ++i) 
    //         {
    //             Node close_node = close_list[i];
    //             close_list_file << close_node.x << " " << close_node.y << " " << close_node.z << " " << close_node.height << " " << close_node.yaw_d << " " << close_node.f_cost << std::endl;
    //         }


    //         planner.clearCloseList();
    //         planner.clearOpenList();

    //         time_matrix(row, col) = planner.getPlanningTime();

    //         col += 1;
    //     }
    //     row += 1;

    // }

    // // 记录规划时间
    // std::ofstream time_file("planning_time.txt");
    // for (int i = 0; i < time_matrix.rows(); ++i) 
    // {
    //     for (int j = 0; j < time_matrix.cols(); ++j) 
    //     {
    //         time_file << time_matrix(i, j) << " ";
    //     }
    //     time_file << std::endl;
    // }
    // time_file.close();

    // CorridorGenerator corridor_generation(planner);
    // std::vector<Polyhedron> corridor = corridor_generation.FlightCorridorGeneration_line(path_eigen);
    // std::vector<Polyhedron> corridor_view = corridor_generation.ViewCorridor(corridor);

    // TrajectoryPlanner traj_planner("bspline");
    // traj_planner.setInitPath(path);

    // std::vector<Eigen::Vector3d> traj;
    // traj_planner.TrajectoryGenerate(traj);
    // Eigen::Vector3d strat_position(tifdata_planning.start[0]*2, tifdata_planning.start[1]*2, tifdata_planning.pixelData.minCoeff());
    // std::vector<Eigen::Vector3d> traj_view;
    // for (int i = 0; i < traj.size(); ++i) 
    // {
    //     traj_view.emplace_back(traj[i] - strat_position);
    // }


    // // 不同约束方法进行路径规划并评估
    // std::vector<std::string> constraint_method = {"None", "Height", "Box"};
    // std::vector<std::vector<Node>> path_set;                            // 路径
    // std::vector<std::vector<Eigen::Vector3d>> path_view_set;            // 可视化路径
    // std::vector<std::vector<check_node>> path_eva_set;                  // 路径评估结果
    // std::vector<std::vector<Polyhedron>> corridor_set;                  // 飞行走廊
    // std::vector<std::vector<Polyhedron>> corridor_view_set;             // 可视化飞行走廊
    // std::vector<std::vector<Eigen::Vector3d>> traj_set;                 // 轨迹
    // std::vector<std::vector<Eigen::Vector3d>> traj_view_set;            // 可视化轨迹     

    // for (int i = 0; i < constraint_method.size(); ++i) 
    // {
    //     std::string method = constraint_method[i];
    //     planner.setConstraintMethod(method);

    //     // 路径规划
    //     std::vector<Node> path = planner.getPath(start_point, goal_point);
    //     path_set.push_back(path);

    //     // 路径变量类型转换
    //     std::vector<Eigen::Vector3d> path_eigen;                        
    //     for (int i = 0; i < path.size(); ++i)
    //     {
    //         path_eigen.emplace_back(path[i].x, path[i].y, path[i].z);
    //     }

    //     // 获取可视化路径
    //     std::vector<Eigen::Vector3d> path_view = planner.getViewPath(path);
    //     path_view_set.push_back(path_view);

    //     // 路径安全性评估
    //     std::vector<check_node> path_eva = evaluation.pathSafetyEvaluation(path);
    //     path_eva_set.push_back(path_eva);

    //     // 路径安全性评估结果写入文件
    //     std::string filename_eva = "Result/PathEvaluation_" + method + ".txt";
    //     evaluation.writeEvaluation(filename_eva, path_eva);

    //     // 安全飞行走廊生成
    //     // CorridorGenerator corridor_generation(planner);

    //     // std::vector<Polyhedron> corridor = corridor_generation.FlightCorridorGeneration_line(path_eigen);          // 走廊生成
    //     // std::vector<Polyhedron> corridor_view = corridor_generation.ViewCorridor(corridor);                             // 可视化走廊生成

    //     // corridor_set.push_back(corridor);
    //     // corridor_view_set.push_back(corridor_view);

    //     // 轨迹规划

    // }

    // std::vector<Eigen::Vector3d> pathView0 = loadPointsFromTxt("PathView0.txt");
    // std::vector<Eigen::Vector3d> pathView1 = loadPointsFromTxt("PathView1.txt");
    // std::vector<Eigen::Vector3d> pathView2 = loadPointsFromTxt("PathView2.txt");
    // std::vector<Eigen::Vector3d> pathView3 = loadPointsFromTxt("PathView3.txt");

    octomap::OcTree passable_tree_view = constraint.getPassableTreeView();
    octomap::OcTree passable_tree_all_view = constraint.getPassableTreeAllView();

    // 可视化
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("visualization");
    auto visualize = std::make_shared<Visualizer>(node);
    // std::vector<std::vector<double>> color_set;
    // std::vector<double> grey = {124.0/255.0, 121.0/255.0, 121.0/255.0}; color_set.push_back(grey);
    // std::vector<double> red = {236.0/255.0, 110.0/255.0, 102.0/255.0}; color_set.push_back(red);
    // std::vector<double> green = {181.0/255.0, 206.0/255.0, 78.0/255.0}; color_set.push_back(green);

    octomap::OcTree view_tree = map_planning.getViewTree();

    auto timer = node -> create_wall_timer(std::chrono::milliseconds(1000), [=]()
    {
        visualize -> publishMap(view_tree, "octomap");
        visualize -> publishMap(passable_tree_view, "passable tree", {0xAA / 255.0, 0XD3 / 255.0, 0xB3 / 255.0}, 0.5);
        visualize -> publishMap(passable_tree_all_view, "passable tree all", {0.9, 0.9, 0.9}, 0.2);
        // visualize -> publishMap(view_tree_expand, "octomap expand", {0.9, 0.9, 0.9}, 0.2);
        // for (int i =0; i < 3; ++i)
        // {
        //     visualize -> publishPathPoints(path_view_set[i], i, color_set[i]);
        // }
        // visualize -> publishPathPoints(path_view);
        // visualize -> publishPolyhedron(corridor_view); 
        // visualize -> publishTrajectory(traj_view); 
        // visualize -> publishPathPoints(path_view, 1);
        // visualize -> publishPathPoints(pathView2, 2, {0.93, 0.69, 0.13});
        // visualize -> publishPathPoints(pathView3, 3, {0.47, 0.67, 0.19});
        

    });

    rclcpp::spin(node);
    rclcpp::shutdown();


    // // 变参实验1：Box约束方法下改变最低高度（3，5，8，10，15），最高高度50
    // std::vector<double> h = {3.0, 5.0, 8.0, 10.0, 15.0};
    // double h_m = 50.0;
    // for (int i = 0; i < h.size(); ++i)
    // {
    //     PathConstraint constraint_min(uav_size, detector_size, err_position, 
    //         RMSE_dsm, h_m, h[i], max_angle);
    //     constraint_min.setMap(map_global.getTifdata(), map_planning.getTifdata());
    //     map_planning.setTifData(constraint.getTifDataCut(), map_global.getTifdata());
        
    //     Planner planner_min(map_planning, constraint_min);
    //     planner_min.setConstraintMethod("Box");

    //     std::vector<Node> path = planner_min.getPath(start_point, goal_point);

    //     std::ostringstream oss;
    //     oss << std::fixed << std::setprecision(0) << h[i];
    //     std::string filename_path = "Result/box/min/path/" + oss.str()  + "_50.txt";

    //     planner_min.writePath(filename_path, path);

    //     Evaluator eva(planner_min);
    //     std::vector<check_node> path_eva = evaluation.pathSafetyEvaluation(path);

    //     std::string filename_eva = "Result/box/min/eva/" + oss.str()  + "_50.txt";
    //     evaluation.writeEvaluation(filename_eva, path_eva);

    // }

    // // 变参实验2：高度约束方法下改变最低高度（3，5，8，10，15），最高高度50
    // for (int i = 0; i < h.size(); ++i)
    // {
    //     PathConstraint constraint_min(uav_size, detector_size, err_position, 
    //         RMSE_dsm, h_m, h[i], max_angle);
    //     constraint_min.setMap(map_global.getTifdata(), map_planning.getTifdata());
    //     map_planning.setTifData(constraint.getTifDataCut(), map_global.getTifdata());
        
    //     Planner planner_min(map_planning, constraint_min);
    //     planner_min.setConstraintMethod("Height");

    //     std::vector<Node> path = planner_min.getPath(start_point, goal_point);

    //     std::ostringstream oss;
    //     oss << std::fixed << std::setprecision(0) << h[i];
    //     std::string filename_path = "Result/height/min/path/" + oss.str()  + "_50.txt";

    //     planner_min.writePath(filename_path, path);

    //     Evaluator eva(planner_min);
    //     std::vector<check_node> path_eva = evaluation.pathSafetyEvaluation(path);

    //     std::string filename_eva = "Result/height/min/eva/" + oss.str()  + "_50.txt";
    //     evaluation.writeEvaluation(filename_eva, path_eva);

    // }

    // // 变参实验3：Box约束方法下改变最高高度（30，40，50），最低高度10
    // std::vector<double> hmax = {30.0, 40.0, 50.0};
    // double hmin = 10.0;
    // for (int i = 0; i < hmax.size(); ++i)
    // {
    //     PathConstraint constraint_min(uav_size, detector_size, err_position, 
    //         RMSE_dsm, hmax[i], hmin, max_angle);
    //     constraint_min.setMap(map_global.getTifdata(), map_planning.getTifdata());
    //     map_planning.setTifData(constraint.getTifDataCut(), map_global.getTifdata());
        
    //     Planner planner_min(map_planning, constraint_min);
    //     planner_min.setConstraintMethod("Box");

    //     std::vector<Node> path = planner_min.getPath(start_point, goal_point);

    //     std::ostringstream oss;
    //     oss << std::fixed << std::setprecision(0) << hmax[i];
    //     std::string filename_path = "Result/box/max/path/10_" + oss.str()  + ".txt";

    //     planner_min.writePath(filename_path, path);

    //     Evaluator eva(planner_min);
    //     std::vector<check_node> path_eva = evaluation.pathSafetyEvaluation(path);

    //     std::string filename_eva = "Result/box/max/eva/10_" + oss.str()  + ".txt";
    //     evaluation.writeEvaluation(filename_eva, path_eva);

    // }

    // // 变参实验4：Height约束方法下改变最高高度（30，40，50），最低高度10
    // for (int i = 0; i < hmax.size(); ++i)
    // {
    //     PathConstraint constraint_min(uav_size, detector_size, err_position, 
    //         RMSE_dsm, hmax[i], hmin, max_angle);
    //     constraint_min.setMap(map_global.getTifdata(), map_planning.getTifdata());
    //     map_planning.setTifData(constraint.getTifDataCut(), map_global.getTifdata());
        
    //     Planner planner_min(map_planning, constraint_min);
    //     planner_min.setConstraintMethod("Height");

    //     std::vector<Node> path = planner_min.getPath(start_point, goal_point);

    //     std::ostringstream oss;
    //     oss << std::fixed << std::setprecision(0) << hmax[i];
    //     std::string filename_path = "Result/height/max/path/10_" + oss.str()  + ".txt";

    //     planner_min.writePath(filename_path, path);

    //     Evaluator eva(planner_min);
    //     std::vector<check_node> path_eva = evaluation.pathSafetyEvaluation(path);

    //     std::string filename_eva = "Result/height/max/eva/10_" + oss.str()  + ".txt";
    //     evaluation.writeEvaluation(filename_eva, path_eva);

    // } 

    return 0;

}