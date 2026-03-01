#pragma once

#include "tif_reader.h"
#include <Eigen/src/Core/Matrix.h>
#include <fcl/narrowphase/collision_object.h>
#include <iostream>
#include <Eigen/Dense>
#include <memory>
#include <octomap/octomap.h>
#include <octomap/OcTree.h>
#include <unordered_set>
#include <tbb/tbb.h>
#include <tbb/concurrent_vector.h>

class Map
{
public:
    // 构造函数，无需输入
    Map(double res_);

    // 直接输入DSM数据
    void setTifData(TIFData tif, TIFData tif_global)
    {
        tifdata = tif;
        tifdata_global = tif_global;
    }

    // 从tif文件中读取DSM
    bool readTif(const char *filename)
    {
        tifdata.res = {res_tree, res_tree, res_tree};
        tifdata.start = {0.0, 0.0};

        bool read = readTIF(filename, tifdata);

        tifdata_global = tifdata;

        return read;
    }

    // 生成八叉树
    void octreeGeneration(bool output_file);

    // 地图裁剪
    TIFData cut(Eigen::Vector3d start, Eigen::Vector3d end);

    // 计算地形频率，range为坐标范围
    double computeFtrn(Eigen::Vector3d position, std::vector<double> range);

    // 二维空间傅里叶变换
    Eigen::MatrixXd computeFFT2D(Eigen::MatrixXd matrix);

    // 获取tif
    TIFData getTifdata()
    {
        return tifdata;
    }

    // 获取八叉树地图
    octomap::OcTree getTree()
    {
        return tree;
    }

    // 获取可视化中的八叉树地图
    octomap::OcTree getViewTree()
    {
        return tree_view;
    }

    // 获取fcl_tree
    std::shared_ptr<fcl::CollisionObjectd> getFCLTree()
    {
        return octree_obj;
    }

    std::vector<double> getResolution()
    {
        return res;
    }

    TIFData getGlobalTifData()
    {
        return tifdata_global;
    }

    // 生成八叉树中间过程：生成点云
    tbb::concurrent_vector<Eigen::Vector3d> PointCloudGeneration();

private:
    double res_tree;
    std::vector<double> res;
    TIFData tifdata;
    TIFData tifdata_global;
    octomap::OcTree tree;
    octomap::OcTree tree_view;
    std::shared_ptr<fcl::CollisionObjectd> octree_obj;


};


