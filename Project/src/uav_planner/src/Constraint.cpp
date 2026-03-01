#include "Constraint.h"
#include <Eigen/src/Core/Matrix.h>
#include <cmath>
#include <memory>
#include <octomap/OcTree.h>
#include <octomap/OcTreeNode.h>
#include <octomap/octomap_types.h>

PathConstraint::PathConstraint(std::vector<double> uav_size_, std::vector<double> detector_size_, std::vector<double> err_position_, 
    double RMSE_DSM_, double max_height_, double min_height_, double max_angle_) : 
    uav_size(uav_size_), 
    detector_size(detector_size_), 
    err_position(err_position_), 
    RMSE_DSM(RMSE_DSM_), 
    max_height(max_height_), 
    min_height(min_height_),
    max_angle(max_angle_) 
{}

void PathConstraint::setMap(TIFData tifdata_map_, TIFData tifdata_cut_)
{
    tifdata_map = tifdata_map_;
    //std::cout << tifdata_map.pixelData << std::endl;
    tifdata_cut = tifdata_cut_;
    //std::cout << tifdata_cut.pixelData << std::endl;
    z_max.resize(tifdata_cut.height, tifdata_cut.width);
    // slope.resize(tifdata_cut.height, tifdata_cut.width);
    for (int i = 0; i < tifdata_cut.height; i++)
    {
        for (int j = 0; j < tifdata_cut.width; j++)
        {
            double x = (j + tifdata_cut.start[0]) * tifdata_cut.res[1];
            double y = (i + tifdata_cut.start[1]) * tifdata_cut.res[0];
            octomap::point3d point_position(x, y, 0);
            z_max(i, j) = getMaxHeight(point_position);
        }
    }
    
    slope_matrix = getSlope();
    lowest_height_matrix = getLowestHeight();
    tifdata_cut.min_z.resize(tifdata_cut.height, tifdata_cut.width);
    tifdata_cut.max_z.resize(tifdata_cut.height, tifdata_cut.width);
    for (int i = 0; i < tifdata_cut.height; i++)
    {
        for (int j = 0; j < tifdata_cut.width; j++)
        {
            tifdata_cut.min_z(i, j) = tifdata_cut.pixelData(i, j) + lowest_height_matrix(i, j);
            tifdata_cut.max_z(i, j) = tifdata_cut.pixelData(i, j) + max_height + detector_size[2] - 3 * RMSE_DSM - 3 * err_position[2];
        }
    }

    getPassableRegion();
}

void PathConstraint::writeSlope(std::string filename)
{
    std::ofstream outFlie_slope(filename);
    for (int i = 0; i < slope_matrix.rows(); i++)
    {
        for (int j = 0; j < slope_matrix.cols(); j++)
        {
            outFlie_slope << slope_matrix(i, j) * 180.0 /  M_PI << " ";
        }
        outFlie_slope << std::endl;
    }
    outFlie_slope.close();
}

void PathConstraint::writeLowestHeight(std::string filename)
{
    std::ofstream outFlie_lowest_height(filename);
    for (int i = 0; i < lowest_height_matrix.rows(); i++)
    {
        for (int j = 0; j < lowest_height_matrix.cols(); j++)
        {
            outFlie_lowest_height << lowest_height_matrix(i, j) << " ";
        }
        outFlie_lowest_height << std::endl;
    }
    outFlie_lowest_height.close();
}

bool PathConstraint::getConstraint(octomap::point3d position)
{
    // 直接高度判断
    std::vector<int> pixel_position = Position2Pixel(position);
    if (position.z() <= tifdata_cut.min_z(pixel_position[0], pixel_position[1]))
    {
        return false;
    }
    if (position.z() >= tifdata_cut.max_z(pixel_position[0], pixel_position[1]))
    {
        return false;
    }

    // 八叉树占用判断———有偏航距离约束
    octomap::OcTreeNode* node = passable_tree->search(position);
    if (!(node != nullptr && node -> getOccupancy() > 0.5)) 
    {
        return false;
    }

    // 八叉树占用判断——无偏航距离约束
    // octomap::OcTreeNode* node1 = passable_tree_all->search(position);
    // if (!(node1 != nullptr && node1 -> getOccupancy() > 0.5)) 
    // {
    //     return false;
    // }

    return true;
}

bool PathConstraint::getCorrectHeight(octomap::point3d &position)
{
    std::vector<int> pixel_position = Position2Pixel(position);
    if (tifdata_cut.min_z(pixel_position[0], pixel_position[1]) > tifdata_cut.max_z(pixel_position[0], pixel_position[1]))
    {
        std::cout << "Region not available!" << std::endl;
        return false;
    }
    std::cout << "Your input height: " << position.z() - tifdata_cut.pixelData(pixel_position[0], pixel_position[1]) << std::endl;
    std::cout << "Constraint height: [" << tifdata_cut.min_z(pixel_position[0], pixel_position[1]) << " , " << tifdata_cut.max_z(pixel_position[0], pixel_position[1]) << "]" << std::endl;
    std::cout << "Advised z: " << 0.5 * (tifdata_cut.max_z(pixel_position[0], pixel_position[1]) + tifdata_cut.min_z(pixel_position[0], pixel_position[1])) << ", change height(z) or not? (y for yes, n for no)" << std::endl;
    char change;
    std::cin >> change;
    if (change == 'y' || change == 'Y')
    {
        position.z() = 0.5 * (tifdata_cut.max_z(pixel_position[0], pixel_position[1]) + tifdata_cut.min_z(pixel_position[0], pixel_position[1]));
        std::cout << "Changed point: (" << position.x() << "," << position.y() << "," << position.z() << ")" << std::endl;
        return true;
    }
    else
    {
        return false;
    }    
}

void PathConstraint::CoverageExtension(octomap::point3d position, Eigen::MatrixXd &CoverageHeight)
{
    double x_min = position.x() - 0.5 * std::max(uav_size[0], detector_size[0]) - 3 * err_position[0];
    double x_max = position.x() + 0.5 * std::max(uav_size[0], detector_size[0]) + 3 * err_position[0];
    double y_min = position.y() - 0.5 * std::max(uav_size[1], detector_size[1]) - 3 * err_position[1];
    double y_max = position.y() + 0.5 * std::max(uav_size[1], detector_size[1]) + 3 * err_position[1];

    std::vector<int> position_pixel = {(int)std::floor(position.y() / tifdata_map.res[1]), (int)std::floor(position.x() / tifdata_map.res[0])};
    std::vector<int> min_pixel = {(int)std::floor(y_min / tifdata_map.res[1]), (int)std::floor(x_min / tifdata_map.res[0])};
    std::vector<int> max_pixel = {(int)std::floor(y_max / tifdata_map.res[1]), (int)std::floor(x_max / tifdata_map.res[0])};

    CoverageHeight.resize(max_pixel[0] - min_pixel[0] + 1, max_pixel[1] - min_pixel[1] + 1);
    int i = 0;
    for (int row = min_pixel[0]; row <= max_pixel[0]; row++, i++)
    {
        int j = 0;
        for (int col = min_pixel[1]; col <= max_pixel[1]; col++, j++)
        {
            double cover = tifdata_map.pixelData(row, col);
            CoverageHeight(i, j) = tifdata_map.pixelData(row, col);
        }       
    }
}

double PathConstraint::getMaxHeight(octomap::point3d position)
{
    Eigen::MatrixXd cover;
    CoverageExtension(position, cover);
    return std::ceil(cover.maxCoeff() / tifdata_map.res[2]) * tifdata_map.res[2];
}

Eigen::MatrixXd PathConstraint::getSlope()
{
    Eigen::MatrixXd slope;
    // z_max.resize(tifdata_cut.height, tifdata_cut.width);
    slope.resize(tifdata_cut.height, tifdata_cut.width);
    // for (int i = 0; i < tifdata_cut.height; i++)
    // {
    //     for (int j = 0; j < tifdata_cut.width; j++)
    //     {
    //         double x = (j + tifdata_cut.start[0]) * tifdata_cut.res[1];
    //         double y = (i + tifdata_cut.start[1]) * tifdata_cut.res[0];
    //         octomap::point3d point_position(x, y, 0);
    //         z_max(i, j) = getMaxHeight(point_position);
    //     }    
    // }
    
    for (int i = 0; i < tifdata_cut.height; i++)
    {
        for (int j = 0; j < tifdata_cut.width; j++)
        {
            Eigen::Matrix3f window;
            for (int m = 0; m < 3; m++)
            {
                for (int n = 0; n < 3; n++)
                {
                    if(i + m - 1 < 0 || i + m - 1 >= tifdata_cut.height || j + n - 1 < 0 || j + n -1 >= tifdata_cut.width)
                    {
                        window(m, n) = z_max(i, j);
                    }
                    else
                    {
                        window(m, n) = z_max(i + m - 1, j + n - 1);
                    }
                }    
            }

            // 可修改坡度计算方法
            double dz_dx = (window(0, 2) + 2 * window(1, 2) + window(2, 2) - window(0, 0) - 2 * window(1, 0) - window(2, 0)) / tifdata_cut.res[1] / 8.0;
            double dz_dy = (window(2, 0) + 2 * window(2, 1) + window(2, 2) - window(0, 0) - 2 * window(0, 1) - window(0, 2)) / tifdata_cut.res[0] / 8.0;

            slope(i, j) = std::atan(std::sqrt(std::pow(dz_dx, 2) + std::pow(dz_dy, 2)));
        }   
    }

    tifdata_cut.slope = slope;
    return slope;
}

double PathConstraint::getLowestHeightPosition(std::vector<int> position)
{
    int r = std::ceil(slope_r / tifdata_cut.res[0]);

    Eigen::MatrixXd region(2 * r + 1, 2 * r + 1);
    Eigen::MatrixXd lowest_height(2 * r + 1, 2 * r + 1);
    double z = z_max(position[0], position[1]);

    for (int i = 0; i < r * 2 + 1; ++i) 
    {
        for (int j = 0; j < 2 * r + 1; ++j) 
        {
            if (position[0] - r + i < 0 || position[1] - r + j < 0 || position[0] - r + i >= z_max.rows() || position[1] - r + j >= z_max.cols()) 
            {
                region(i, j) = z_max(position[0], position[1]);
            }
            else 
            {
                region(i, j) = z_max(position[0] - r + i, position[1] - r + j);
            }
            
            lowest_height(i, j) = region(i, j) - 
                std::sqrt(std::pow((r - i) * tifdata_cut.res[0] , 2) + std::pow((r - j) * tifdata_cut.res[1] , 2)) *
                std::tan(max_angle);
        }
    }

    return lowest_height.maxCoeff();
}



Eigen::MatrixXd PathConstraint::getLowestHeight()
{
    Eigen::MatrixXd lowest_height;
    lowest_height.resize(tifdata_cut.height, tifdata_cut.width);
    for (int i = 0; i < tifdata_cut.height; i++)
    {
        for (int j = 0; j < tifdata_cut.width; j++)
        {
            // double angle_limit = (std::tan(slope_matrix(i, j)) - std::tan(max_angle));
            // lowest_height(i, j) = std::sqrt(std::pow(tifdata_cut.res[0], 2) + std::pow(tifdata_cut.res[1], 2)) * 
            //     (angle_limit > 0 ? angle_limit : 0.0) + detector_size[2] + min_height + 3 * (err_position[2] + RMSE_DSM) + z_max(i, j) - tifdata_cut.pixelData(i,j);
            lowest_height(i, j) = getLowestHeightPosition({i, j}) + detector_size[2] + min_height + 
                3 * (err_position[2] + RMSE_DSM) - tifdata_cut.pixelData(i,j);
        } 
    }
    return lowest_height;   
}

std::vector<int> PathConstraint::Position2Pixel(octomap::point3d position)
{
    std::vector<int> pixel = {(int)std::floor(position.y() / tifdata_cut.res[0]) - (int)tifdata_cut.start[1], (int)std::floor(position.x() / tifdata_cut.res[0]) - (int)tifdata_cut.start[0]};
    return pixel;
}

void PathConstraint::getPassableRegion()
{
    octomap::OcTree tree(tifdata_cut.res[0]);
    octomap::OcTree tree_all(tifdata_cut.res[0]);
    octomap::OcTree tree_view(tifdata_cut.res[0]);
    octomap::OcTree tree_all_view(tifdata_cut.res[0]);

    int width = tifdata_cut.width;
    int height = tifdata_cut.height;

    for (int i = 0; i < height; ++i) 
    {
        for (int j = 0; j < width; ++j) 
        {
            // for (double h = std::floor(lowest_height_matrix(i, j) / tifdata_cut.res[0]) * tifdata_cut.res[0]; 
            //             h < max_height ; h += tifdata_cut.res[0]) 
            for (double z = tifdata_cut.min_z(i, j); z <= tifdata_cut.max_z(i, j); z += tifdata_cut.res[2])
            {
                // double z = tifdata_cut.pixelData(i, j) + h;
                double z_view = z - tifdata_cut.pixelData.minCoeff();

                z = std::floor(z / tifdata_cut.res[2]) * tifdata_cut.res[2];
                z_view = std::floor(z_view / tifdata_cut.res[2]) * tifdata_cut.res[2];

                tree_all.updateNode(octomap::point3d((j + tifdata_cut.start[0]) * tifdata_cut.res[0], (i + tifdata_cut.start[1]) * tifdata_cut.res[0], z), true);
                tree_all_view.updateNode(octomap::point3d(j * tifdata_cut.res[0], i * tifdata_cut.res[0], z_view), true);

                double x = (j + tifdata_cut.start[0]) * tifdata_cut.res[0];
                double y = (i + tifdata_cut.start[1]) * tifdata_cut.res[1];
                double d = std::abs((start.x() - goal.x()) * (goal.y() - y) - (goal.x() - x) * (start.y() - goal.y())) / 
                    std::sqrt(std::pow((start - goal).x(), 2) + std::pow((start - goal).y(), 2)) + 
                    3.0 * std::abs(err_position[0] * (start.y() - goal.y()) + err_position[1] * (goal.x() - start.x())) / 
                    std::sqrt(std::pow((start - goal).x(), 2) + std::pow((start - goal).y(), 2));

                if (d <= yaw_d) 
                {
                    tree.updateNode(octomap::point3d((j + tifdata_cut.start[0]) * tifdata_cut.res[0], (i + tifdata_cut.start[1]) * tifdata_cut.res[0], z), true);
                    tree_view.updateNode(octomap::point3d(j * tifdata_cut.res[0], i * tifdata_cut.res[0], z_view), true);
                }
            }
        }
    }
    // return tree;
    passable_tree = std::make_shared<octomap::OcTree>(tree);
    passable_tree_all = std::make_shared<octomap::OcTree>(tree_all);
    passable_tree_view = std::make_shared<octomap::OcTree>(tree_view);
    passable_tree_all_view = std::make_shared<octomap::OcTree>(tree_all_view);
    
}

Eigen::MatrixXi PathConstraint::getRegion()
{
    Eigen::MatrixXi region;
    region.resize(tifdata_cut.height, tifdata_cut.width);
    for (int i = 0; i < region.rows(); ++i) 
    {
        for (int j = 0; j < region.cols(); ++j) 
        {
            double x = (j + tifdata_cut.start[0]) * tifdata_cut.res[0];
            double y = (i + tifdata_cut.start[1]) * tifdata_cut.res[1];
            double d = std::abs((start.x() - goal.x()) * (goal.y() - y) - (goal.x() - x) * (start.y() - goal.y())) / 
                std::sqrt(std::pow((start - goal).x(), 2) + std::pow((start - goal).y(), 2)) + 
                3.0 * std::abs(err_position[0] * (start.y() - goal.y()) + err_position[1] * (goal.x() - start.x())) / 
                std::sqrt(std::pow((start - goal).x(), 2) + std::pow((start - goal).y(), 2));

            double height_range = tifdata_cut.max_z(i, j) - tifdata_cut.min_z(i, j);
            
            if (height_range >= range_threshold) 
            {
                if (d <= yaw_d) 
                {
                    region(i, j) = 2;
                }
                else 
                {
                    region(i, j) = 1;
                }
            }
            else 
            {
                region(i, j) = 0;
            }
        }
    }

    return region;
}



// std::vector<float> uav_size = {10, 4, 6};
// std::vector<float> detector_size = {15, 15 , 30};
// std::vector<float> err_position = {1.5, 1.5, 1};
// float RMSE_dsm = 1.5;
// float max_height = 25;
// float max_angle = 30.0 * M_PI / 180.0;

// void slope_calculate(TIFData& tifdata)
// {
//     tifdata.slope.resize(tifdata.height, tifdata.width);
//     tbb::parallel_for(0, tifdata.height, [&](int i)
//     {
//         for (int j = 0; j < tifdata.width; j++)
//         {
//             Eigen::Matrix3f window;
//             for (int m = 0; m < 3; m++)
//             {
//                 for (int n = 0; n < 3; n++)
//                 {
//                     if(i + m - 1 < 0 || i + m - 1 >= tifdata.height || j + n - 1 < 0 || j + n -1 >= tifdata.width)
//                     {
//                         window(m, n) = tifdata.pixelData(i, j);
//                     }
//                     else
//                     {
//                         window(m, n) = tifdata.pixelData(i + m - 1, j + n - 1);
//                     }
//                 }    
//             }
//             float dz_dx = (window(0, 2) + 2 * window(1, 2) + window(2, 2) - window(0, 0) - 2 * window(1, 0) - window(2, 0)) / tifdata.res[1] / 8.0;
//             float dz_dy = (window(2, 0) + 2 * window(2, 1) + window(2, 2) - window(0, 0) - 2 * window(0, 1) - window(0, 2)) / tifdata.res[0] / 8.0;

//             tifdata.slope(i, j) = std::atan(std::sqrt(std::pow(dz_dx, 2) + std::pow(dz_dy, 2)));
//         }
        
//     });
// }

// void z_constraint(TIFData& tifdata)
// {
//     tifdata.min_z.resize(tifdata.height, tifdata.width);
//     tifdata.max_z.resize(tifdata.height, tifdata.width);
//     tbb::parallel_for(0, tifdata.height, [&](int i)
//     {
//         for (int j = 0; j < tifdata.width; j++)
//         {
//             tifdata.max_z(i, j) = tifdata.pixelData(i, j) + max_height + detector_size[2] + 0.5 * uav_size[2] - 3 * (err_position[2] + RMSE_dsm);
//             float angel_limit = (std::tan(tifdata.slope(i, j)) - std::tan(max_angle));
//             tifdata.min_z(i, j) = tifdata.pixelData(i, j) + std::sqrt(std::pow(tifdata.res[0], 2) + std::pow(tifdata.res[1], 2)) * (angel_limit > 0 ? angel_limit : 0.0) + detector_size[2] + 0.5 * uav_size[2] +  3 * (err_position[2] + RMSE_dsm);
//         }    
//     });
// }

// bool xy_constraint(octomap::OcTree octree, octomap::point3d position)
// {
//     std::vector<float> nearest_xy = {std::numeric_limits<float>::infinity(), std::numeric_limits<float>::infinity()};

//     float z_low = position.z() - detector_size[2] - 0.5 * uav_size[2] - 3 * err_position[2];
//     float z_high = position.z() + 0.5 * uav_size[2] + 3 * err_position[2];

//     float x_min = position.x() - 0.5 * detector_size[0] - 0.5 * uav_size[0] - 3 * err_position[0];
//     float x_max = position.x() + 0.5 * detector_size[0] + 0.5 * uav_size[0] + 3 * err_position[0];

//     float y_min = position.y() - 0.5 * detector_size[1] - 0.5 * uav_size[1] - 3 * err_position[1];
//     float y_max = position.y() + 0.5 * detector_size[1] + 0.5 * uav_size[1] + 3 * err_position[1];

//     std::vector<octomap::OcTree::leaf_iterator> nodes;
//     for (octomap::OcTree::leaf_iterator it = octree.begin_leafs(), end = octree.end_leafs(); it != end; it++)
//     {
//         nodes.push_back(it);
//     }

//     int size = nodes.size();
//     //tbb::parallel_for(0, size, [&](int i)
//     for (int i = 0; i < size; i++)
//     {
//         octomap::OcTree::leaf_iterator node = nodes[i];
//         octomap::OcTreeKey key = node.getKey();
//         octomap::point3d coord = octree.keyToCoord(key);

//         int depth = node.getDepth();
//         double nodeSize = octree.getNodeSize(depth);

//         if (coord.z() >= z_low - 0.5 * nodeSize && coord.z() <= z_high + 0.5 * nodeSize)
//         {
//             if (coord.x() >= x_min - 0.5 * nodeSize && coord.x() <= x_max + nodeSize)
//             {
//                 float y_distance = std::abs(coord.y() - position.y()) - 0.5 * nodeSize;
//                 if (y_distance <= nearest_xy[1])
//                 {
//                     nearest_xy[1] = y_distance;
//                 }    
//             }
//             if (coord.y() >= y_min - 0.5 * nodeSize && coord.y() <= y_max + nodeSize)
//             {
//                 float x_distance = std::abs(coord.x() - position.x()) - 0.5 * nodeSize;
//                 if (x_distance <= nearest_xy[0])
//                 {
//                     nearest_xy[0] = x_distance;
//                 }    
//             }
//         }    
//     }

//     float x_limit = 0.5 * uav_size[0] + 0.5 * detector_size[0] + 3 * err_position[0];
//     float y_limit = 0.5 * uav_size[1] + 0.5 * detector_size[1] + 3 * err_position[1];
//     if (nearest_xy[0] <= x_limit || nearest_xy[1] <= y_limit)
//     {
//         return false;
//     }
//     return true;
// }

// bool zposition_constraint(TIFData tifdata, octomap::point3d position)
// {
//     float row = position.y() / tifdata.res[1] - tifdata.start[1];
//     float col = position.x() / tifdata.res[0] - tifdata.start[0];
//     if (row < 0 || col < 0 || row >= tifdata.height || col >= tifdata.width)
//     {
//         return false;
//     }
    
//     std::vector<float> zlimit = {tifdata.min_z((int)row, (int)col), tifdata.max_z((int)row, (int)col)}; 
//     if (position.z() >= tifdata.max_z((int)row, (int)col) || position.z() <= tifdata.min_z((int)row, (int)col))
//     {
//         return false;
//     }
//     return true;

// }