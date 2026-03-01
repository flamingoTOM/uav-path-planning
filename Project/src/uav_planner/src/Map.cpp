#include "Map.h"
#include "tif_reader.h"
#include <Eigen/src/Core/Matrix.h>
#include <oneapi/tbb/concurrent_vector.h>
#include <tbb/tbb.h>
#include <tbb/concurrent_vector.h>
#include <mutex>
#include <fcl/geometry/octree/octree.h>
#include <fftw3.h>


Map::Map(double res_) : res_tree(res_), tree(res_), tree_view(res_)
{
    res = {res_, res_, res_};
}

void Map::octreeGeneration(bool output_file)
{
    tbb::concurrent_vector<Eigen::Vector3d> point_cloud = PointCloudGeneration();

    std::mutex tree_mutex;

    tbb::parallel_for_each(point_cloud.begin(), point_cloud.end(), [&](const Eigen::Vector3d& point)
    {
        double node_x = std::floor(point.x() / tifdata.res[0]) * tifdata.res[0];
        double node_y = std::floor(point.y() / tifdata.res[1]) * tifdata.res[1];
        double node_z = std::floor(point.z() / tifdata.res[2]) * tifdata.res[2];
        octomap::point3d p(node_x, node_y, node_z);
        {
            std::lock_guard<std::mutex> lock(tree_mutex);  
            tree.updateNode(p, true);
        }
    });

    auto tree_ptr = std::make_shared<octomap::OcTree>(tree);
    auto fcl_tree = std::make_shared<fcl::OcTreed>(tree_ptr);
    fcl::Transform3d tf_octree = fcl::Transform3d::Identity();
    octree_obj = std::make_shared<fcl::CollisionObjectd>(fcl_tree, tf_octree);
    
    std::cout << "Number of tree nodes: " << tree.size() << std::endl;

    std::mutex tree_view_mutex;

    tbb::parallel_for_each(point_cloud.begin(), point_cloud.end(), [&](const Eigen::Vector3d& view_point)
    {
        double view_x = std::floor(view_point.x() / tifdata.res[0]) * tifdata.res[0] - tifdata.start[0] * tifdata.res[0];
        double view_y = std::floor(view_point.y() / tifdata.res[1]) * tifdata.res[1] - tifdata.start[1] * tifdata.res[1];
        double view_z = std::ceil((view_point.z() - tifdata.pixelData.minCoeff()) / tifdata.res[2]) * tifdata.res[2];
        octomap::point3d p_view(view_x, view_y, view_z);
        {
            std::lock_guard<std::mutex> lock(tree_view_mutex);
            tree_view.updateNode(p_view, true);
        }
        
    });

    // 输出Octree到文件
    if (output_file)
    {
        tree.writeBinary("octree.bt");
        tree_view.writeBinary("Octree.bt");
    }

}

TIFData Map::cut(Eigen::Vector3d start, Eigen::Vector3d end)
{
    TIFData tif_cut;
    tif_cut.bands = tifdata.bands;
    double start_cut_row = std::max((double)0.0, std::min(start[1], end[1])-10);
    double start_cut_col = std::max((double)0.0, std::min(start[0], end[0])-10);
    tif_cut.height = std::abs(start[1] - end[1]) + 20;
    tif_cut.width = std::abs(start[0] - end[0]) + 20;
    tif_cut.start = {start_cut_col, start_cut_row};
    tif_cut.res = tifdata.res;

    tif_cut.pixelData.resize(tif_cut.height, tif_cut.width);

    tbb::parallel_for(0, tif_cut.height, [&](int i) 
    {
        for (int j = 0; j < tif_cut.width; j++) 
        {
            double pixel = tifdata_global.pixelData((int)start_cut_row + i, (int)start_cut_col + j);//*(tif_source.pixelData.data() + ((int)start_cut_row + i) * tif_source.width + (int)start_cut_col + j);
            tif_cut.pixelData(i, j) = pixel;
        }
    });

    return tif_cut;
}

double Map::computeFtrn(Eigen::Vector3d position, std::vector<double> range)    // range为坐标范围
{
    double f_trn;

    std::vector<int> range_pixel = {(int)std::ceil(range[0] / res[0]), (int)std::ceil(range[1] / res[1])};
    Eigen::Vector3d coord(std::floor(position.x() / res[0]), std::floor(position.y() / res[1]), position.z());
    
    if (range_pixel[0] % 2 == 0)    range_pixel[0]++;
    if (range_pixel[1] % 2 == 0)    range_pixel[1]++;

    range_pixel[0] = (range_pixel[0] - 1) / 2;
    range_pixel[1] = (range_pixel[1] - 1) / 2;

    Eigen::Vector3d start(coord.x() - range_pixel[0], coord.y() - range_pixel[1],  coord.z());
    Eigen::Vector3d goal(coord.x() + range_pixel[0], coord.y() + range_pixel[1],  coord.z());

    TIFData tif_range = cut(start, goal);
    Eigen::MatrixXd matrix = tif_range.pixelData;

    Eigen::MatrixXd fft = computeFFT2D(matrix);

    int cx = fft.cols() / 2;
    int cy = fft.rows() / 2;

    double numerator = 0.0;
    double denominator = 0.0;
    for (int i = 0; i < fft.rows(); ++i)
    {
        int v = i - cy;
        for (int j = 0; j < fft.cols(); ++j)
        {
            int u = j - cx;
            double f_uv = fft(i, j);
            numerator += f_uv * std::sqrt(u * u + v * v);
            denominator += f_uv;
        }
    }

    f_trn = numerator / (denominator * std::sqrt(fft.rows() * fft.rows() * res[1] * res[1] + fft.cols() * fft.cols() * res[0] * res[0]));
    return f_trn;
}

Eigen::MatrixXd Map::computeFFT2D(Eigen::MatrixXd matrix)
{
    int rows = matrix.rows();
    int cols = matrix.cols();

    // 分配 FFT 输入输出空间
    fftw_complex* in = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * rows * cols);
    fftw_complex* out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * rows * cols);

    // 拷贝 matrix 到 in
    for (int i = 0; i < rows; ++i)
    {
        for (int j = 0; j < cols; ++j) 
        {
            int idx = i * cols + j;
            in[idx][0] = matrix(i, j);  // 实部
            in[idx][1] = 0.0;           // 虚部
        }
    }

    // 执行傅里叶变换
    fftw_plan plan = fftw_plan_dft_2d(rows, cols, in, out, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(plan);

    Eigen::MatrixXd spectrum(rows, cols);
    for (int i = 0; i < rows; ++i)
    {
        for (int j = 0; j < cols; ++j) 
        {
            int idx = i * cols + j;
            double real = out[idx][0];
            double imag = out[idx][1];
            spectrum(i, j) = std::sqrt(real * real + imag * imag); // 模值
        }
    }

    // 清理资源
    fftw_destroy_plan(plan);
    fftw_free(in);
    fftw_free(out);

    return spectrum;
}

tbb::concurrent_vector<Eigen::Vector3d> Map::PointCloudGeneration()
{
    double GroundLevel = tifdata.pixelData.minCoeff();

    tbb::concurrent_vector<Eigen::Vector3d> PointCloud;
    tbb::parallel_for(0, tifdata.width, [&](int i)
    {
        double x = (i + tifdata.start[0]) * tifdata.res[0];
        std::vector<Eigen::Vector3d> local_points;
        for (int j = 0; j < tifdata.height; j++)
        {            
            double y = (j + tifdata.start[1]) * tifdata.res[1];
            double z = std::ceil((*(tifdata.pixelData.data() +  i * tifdata.height + j))/ tifdata.res[2]) * tifdata.res[2];
            if (z != 0)
            {
                for (double currentZ = z; currentZ >= GroundLevel; currentZ -= tifdata.res[2])
                {
                    local_points.push_back({static_cast<double>(x), static_cast<double>(y), currentZ});
                }
            }
        }
        if (!local_points.empty())
        {
            PointCloud.grow_by(local_points.begin(), local_points.end());
        }
    });

    return PointCloud;
}