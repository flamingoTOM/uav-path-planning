#include "tif_reader.h"
#include <iostream>
#include <stdexcept>

bool readTIF(const char *filename, TIFData &tifData) 
{
    // 初始化GDAL库
    GDALAllRegister();

    // 打开TIF文件
    GDALDataset *dataset = (GDALDataset *) GDALOpen(filename, GA_ReadOnly);
    
    if (dataset == nullptr) 
    {
        std::cerr << "无法打开文件: " << filename << std::endl;
        return false; // 打开文件失败，返回false
    }

    // 获取图像的基本信息
    tifData.width = dataset->GetRasterXSize();
    tifData.height = dataset->GetRasterYSize();
    tifData.bands = dataset->GetRasterCount();

    // std::cout << "图像宽度: " << tifData.width << std::endl;
    // std::cout << "图像高度: " << tifData.height << std::endl;
    // std::cout << "波段数: " << tifData.bands << std::endl;

    // 为每个波段分配空间并读取数据
    //tifData.pixelData.resize(tifData.bands);
    for (int b = 0; b < tifData.bands; b++) 
    {
        GDALRasterBand *band = dataset->GetRasterBand(b + 1);
        if (band != nullptr) 
        {
            // 创建一个临时数组存储像素数据
            //std::vector<std::vector<double>> bandData(tifData.width);
            Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> bandData(tifData.height, tifData.width);
            CPLErr err = band->RasterIO(GF_Read, 0, 0, tifData.width, tifData.height, bandData.data(), tifData.width, tifData.height, GDT_Float64, 0, 0);
            if (err != CE_None) {
                std::cerr << "读取波段 " << b + 1 << " 数据时出错!" << std::endl;
                GDALClose(dataset);
                return false; // 读取数据失败，返回false
            }
            tifData.pixelData = bandData.cast<double>();
        } 
        else 
        {
            std::cerr << "波段 " << b + 1 << " 不存在!" << std::endl;
            GDALClose(dataset);
            return false; // 波段不存在，返回false
        }
    }

    // 清理资源
    GDALClose(dataset);
    
    return true; // 成功读取，返回true
}