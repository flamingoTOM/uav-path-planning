# pragma once

//#include <Eigen/src/Core/Matrix.h>
#include <gdal.h>
#include <gdal_priv.h>
#include <vector>
#include <Eigen/Dense>

// 定义结构体，存储TIF图像数据
struct TIFData 
{
    int width;              // 图像宽度
    int height;             // 图像高度
    int bands;              // 波段数
    //std::vector<std::vector<double>> pixelData; // 存储图像的像素数据
    Eigen::MatrixXd pixelData;
    std::vector<double> start;
    std::vector<double> res;
    Eigen::MatrixXd slope;
    Eigen::MatrixXd min_z, max_z;
};

// 声明读取TIF文件的函数
bool readTIF(const char *filename, TIFData &tifData);