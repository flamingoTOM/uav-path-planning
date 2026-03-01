#include "TrajectoryPlanner.h"
// #include "Constraint.h"
#include "PathEvaluation.h"
#include "PathPlanning.h"
#include <Eigen/src/Core/Matrix.h>
#include <vector>

// -------------------------------------------------------------B-spline规划器-------------------------------------------------------
// 构造函数
// BsplineTrajectoryPlanner::BsplineTrajectoryPlanner(PathPlanner planner_, int order_, int control_points_num_) : 
//     planner(planner_), order(order_), control_points_num(control_points_num_)
// {
//     if (order_ > control_points_num_) 
//     {
//         std::cout << "Error! The Number of control points must be greater than order!" << std::endl;
//     }
// }

// 构造函数
BsplineTrajectoryPlanner::BsplineTrajectoryPlanner(int order_, int control_points_num_) : 
    order(order_), control_points_num(control_points_num_)
{
    if (order_ > control_points_num_) 
    {
        std::cout << "Error! The Number of control points must be greater than order!" << std::endl;
    }
}

// 设置路径点（根据Theta*算法规划的路径）
void BsplineTrajectoryPlanner::setWayPoints(std::vector<Node> path)
{
    for (int i = 0; i < path.size(); i++)
    {
        Eigen::Vector3d way_point(path[i].x, path[i].y, path[i].z);
        way_points.push_back(way_point);
    }
    segment_num = way_points.size() - 1;
}

void BsplineTrajectoryPlanner::setCorridor(std::vector<Polyhedron> corridor)
{
    constraint_corridor = corridor;
}

void BsplineTrajectoryPlanner::setDynamicConstraints(double max_vel, double max_acc)
{
    max_acceleration = max_acc;
    max_velocity = max_vel;
}

void BsplineTrajectoryPlanner::InitControlPoints()
{
    for (int i = 0; i < way_points.size(); ++i)
    {
        control_points[i].resize(control_points_num);
        for (int k = 0; k < control_points_num; ++k)
        {
            Eigen::Vector3d p = way_points[i] + (way_points[i + 1] - way_points[i]) * k / (control_points_num - 1);
            control_points[i].push_back(p);
        }
    }
}

double BsplineTrajectoryPlanner::computeCost(std::vector<Eigen::Vector3d> control, Planner planner)
{
    double lambda_smooth = 1.0;
    double lambda_safe = 1.0;
    double cost_smooth = 0.0;
    for (int i = 1; i < control.size() - 1; ++i)
    {
        Eigen::Vector3d Fi_ip1 = control[i + 1] - control[i];
        Eigen::Vector3d Fi_im1 = control[i - 1] - control[i];
        cost_smooth += (Fi_im1 + Fi_ip1).squaredNorm();
    }

    double cost_safe = 0.0;
    Evaluator control_eva(planner);
    for (int i = 0; i < control.size(); ++i)
    {
        cost_safe += control_eva.SafeDistance(control[i]);
    }
    return lambda_safe * cost_safe + lambda_smooth * cost_smooth;
}

// void BsplineTrajectoryPlanner::optimizeControlPoints()
// {
//     int num_segments = way_points.size() - 1;       // 路径段数
//     int overlap = order - 1;                        // 相邻段共享的控制点数
//     int unique_pts = control_points_num - overlap;  // 每段独立的控制点数
//     control_points.resize(num_segments);

//     for (int s = 0; s < num_segments; ++s)
//     {
//         std::vector<Eigen::Vector3d> control;

//         if (s > 0) 
//         {
//             for (int i = 0; i < overlap; ++i)
//             {

//             }
//         }
//     }

// }

double BsplineTrajectoryPlanner::deBoorBasis(int i, int k, double t, std::vector<double> knots)
{
    if (k == 0)
    {
        return (t >= knots[i] && t < knots[i + 1]) ? 1.0 : 0.0;
    }
    else 
    {
        double denom1 = knots[i + k] - knots[i];
        double denom2 = knots[i + k + 1] - knots[i + 1];
        double term1 = (denom1 != 0.0) ? ((t - knots[i]) / denom1) * deBoorBasis(i, k - 1, t, knots) : 0.0;
        double term2 = (denom2 != 0.0) ? ((knots[i + k + 1] - t) / denom2) * deBoorBasis(i + 1, k - 1, t, knots) : 0.0;
        return term1 + term2; 
    }
}


// 设置每一段路径的时间（根据总时间和每段路径长度分配）
void BsplineTrajectoryPlanner::setSegmentTimes(double total_time)
{
    double distance_total = 0;
    std::vector<double> distance(segment_num);
    times.resize(segment_num);
    for (int i = 0; i < segment_num; i++)
    {
        distance[i] = (way_points[i + 1] - way_points[i]).norm();
        distance_total += distance[i];
    }
    for (int i = 0; i < segment_num; i++)
    {
        times[i] = distance[i] / distance_total * total_time;
    }
}

Eigen::Vector3d BsplineTrajectoryPlanner::evaluateBSpline(double t, int degree,
                                const std::vector<double>& knots) 
{
    Eigen::Vector3d point(0.0, 0.0, 0.0);
    int n = way_points.size();
    for (int i = 0; i < n; ++i) 
    {
        double B = deBoorBasis(i, degree, t, knots);
        point += B * way_points[i];
    }
    return point;
}

std::vector<Eigen::Vector3d> BsplineTrajectoryPlanner::getSingleTrajetory()
{
    std::vector<Eigen::Vector3d> points;

    int m = segment_num + order + 1;
    std::vector<double> knots(m + 1);
    for (int i = 0; i <= m; ++i) {
        if (i <= order) knots[i] = 0.0;
        else if (i >= m - order) knots[i] = 1.0;
        else knots[i] = (double)(i - order) / (m - 2 * order);
    }

    int numSamples = 5000;
    for (int i = 0; i < numSamples; ++i) {
        double t = (double)i / numSamples;
        Eigen::Vector3d pt = evaluateBSpline(t, order, knots);
        //std::cout << pt.x() << ", " << pt.y() << ", " << pt.z() << std::endl;
        points.push_back(pt);
    }
    return points;
}

// -----------------------------------------------------------Minimun Snap规划器--------------------------------------------------------------

MinimumSnapTrajectoryPlanner::MinimumSnapTrajectoryPlanner(int poly_order_) 
    : poly_order(poly_order_), coeff_num(poly_order + 1), segment_num(0) {}

// 设置路径点（根据Theta*算法规划的路径）
void MinimumSnapTrajectoryPlanner::setWayPoints(std::vector<Node> path)
{
    for (int i = 0; i < path.size(); i++)
    {
        Eigen::Vector3d way_point(path[i].x, path[i].y, path[i].z);
        waypoints.push_back(way_point);
    }
    segment_num = path.size() - 1;
}

// 设置每一段路径的时间（根据总时间和每段路径长度分配）
void MinimumSnapTrajectoryPlanner::setSegmentTimes(double total_time)
{
    double distance_total = 0;
    std::vector<double> distance(segment_num);
    times.resize(segment_num);
    for (int i = 0; i < segment_num; i++)
    {
        distance[i] = (waypoints[i + 1] - waypoints[i]).norm();
        distance_total += distance[i];
    }
    for (int i = 0; i < segment_num; i++)
    {
        times[i] = distance[i] / distance_total * total_time;
    }
}

// 构建目标函数Q矩阵
void MinimumSnapTrajectoryPlanner::buidQAll()
{
    std::vector<Eigen::Triplet<double>> Q_Triplets;
    int q_num = coeff_num * segment_num;

    for (int k = 0; k < segment_num; k++)
    {
        double T_k = times[k];
        for (int i = 4; i < coeff_num; i++)
        {
            for (int j = 4; j < coeff_num; j++)
            {
                double Q_k_ij = i * (i - 1) * (i - 2) * (i - 3) * j * (j - 1) * (j - 2) * (j - 3) * std::pow(T_k, i + j - 7) / (i + j - 7);
                Q_Triplets.emplace_back(k * coeff_num + i, k * coeff_num + j, Q_k_ij);
            }    
        }
    }
    
    Q_all.resize(q_num, q_num);
    Q_all.setFromTriplets(Q_Triplets.begin(), Q_Triplets.end());
    f_all = Eigen::VectorXd::Zero(q_num);
}

// 构建约束矩阵A和约束上下界
void MinimumSnapTrajectoryPlanner::buildConstraints()
{
    std::vector<Eigen::SparseMatrix<double>> A_all(3);
    std::vector<Eigen::VectorXd> b_all(3);

    // 中间约束形式：0-无其他约束，仅有平滑性；1-路径点约束
    bool constraint_mode = true;

    // 导数-时间计算
    auto fillRow = [](Eigen::RowVectorXd& row, int deriv_order, double t, int offset, int coeff_num_) 
    {
        for (int j = deriv_order; j < coeff_num_; ++j) 
        {
            double val = 1.0;
            for (int k = 0; k < deriv_order; ++k)
                val *= (j - k);
            row(offset + j) = val * std::pow(t, j - deriv_order);
        }
    };

    for (int direction = 0; direction < A_all.size(); direction++)
    {
        // 路径点坐标
        std::vector<double> points;
        for (int i = 0; i < waypoints.size(); i++)
        {
            points.push_back(waypoints[i](direction));
        }
    
        int A_row = (segment_num + 1) * 4 + (constraint_mode ? (segment_num - 1) : 0);
        int A_col = coeff_num * segment_num;
        Eigen::MatrixXd A_dense = Eigen::MatrixXd::Zero(A_row, A_col);
        Eigen::VectorXd b = Eigen::VectorXd::Zero(A_row);

        // 起终点约束
        int constraint_idx = 0;
        for (int i = 0; i < 4; i++)
        {
            // 起点约束
            Eigen::RowVectorXd row_start = Eigen::RowVectorXd::Zero(A_col);
            fillRow(row_start, i, 0.0, 0, coeff_num);
            A_dense.row(constraint_idx) = row_start;
            if (i == 0)
            {
                b(constraint_idx) = points[0];
            }
            ++ constraint_idx;
            // 终点约束
            Eigen::RowVectorXd row_goal = Eigen::RowVectorXd::Zero(A_col);
            fillRow(row_goal, i, times.back(), (segment_num - 1) * coeff_num, coeff_num);
            A_dense.row(constraint_idx) = row_goal;
            if (i == 0)
            {
                b(constraint_idx) = points.back();
            }
            ++ constraint_idx;
        }

        // 控制点平滑性约束
        for (int i = 0; i < segment_num - 1; i++)
        {
            for (int j = 0; j < 4; j++)
            {
                Eigen::RowVectorXd row_segment1 = Eigen::RowVectorXd::Zero(A_col);
                Eigen::RowVectorXd row_segment2 = Eigen::RowVectorXd::Zero(A_col);

                // 前一段路径终点处的导数
                fillRow(row_segment1, j, times[i], i * coeff_num, coeff_num);
                // 后一段路径起点处的导数
                fillRow(row_segment2, j, 0.0, (i + 1) * coeff_num, coeff_num);

                A_dense.row(constraint_idx) = row_segment1 - row_segment2;
                ++ constraint_idx;
            }
            
        }

        // 控制点位置约束
        if (constraint_mode)
        {
            for (int i = 0; i < segment_num - 1; i++)
            {
                Eigen::RowVectorXd row_point = Eigen::RowVectorXd::Zero(A_col);
                fillRow(row_point, 0, times[i], i * coeff_num, coeff_num);
                A_dense.row(constraint_idx) = row_point;
                b(constraint_idx) = points[i + 1];
                ++ constraint_idx;
            }    
        }
        

        // A矩阵稀疏化
        std::vector<Eigen::Triplet<double>> A_Triplets;
        for (int i = 0; i < A_row; i++)
        {
            for (int j = 0; j < A_col; j++)
            {
                if (A_dense(i, j) != 0)
                {
                    A_Triplets.emplace_back(i, j, A_dense(i, j));
                }    
            }
        }
        
        // 最终结果
        A_all[direction].resize(A_row, A_col);
        A_all[direction].setFromTriplets(A_Triplets.begin(), A_Triplets.end());
        b_all[direction] = b;
    }
    
    // 不同方向
    A_all_x = A_all[0];
    A_all_y = A_all[1];
    A_all_z = A_all[2];
    lb_all_x = b_all[0];
    ub_all_x = b_all[0];
    lb_all_y = b_all[1];
    ub_all_y = b_all[1];
    lb_all_z = b_all[2];
    ub_all_z = b_all[2];

}

// 求解优化问题，获取轨迹参数
bool MinimumSnapTrajectoryPlanner::getSolution(std::vector<std::vector<Eigen::VectorXd>>& coeff_xyz)
{
    buidQAll();
    buildConstraints();

    OsqpEigen::Solver solver_x, solver_y, solver_z;
    solver_x.settings() -> setVerbosity(false);
    solver_x.settings() -> setWarmStart(true);
    solver_y.settings() -> setVerbosity(false);
    solver_y.settings() -> setWarmStart(true);
    solver_z.settings() -> setVerbosity(false);
    solver_z.settings() -> setWarmStart(true);

    // x方向轨迹参数求解
    solver_x.data() -> setNumberOfVariables(segment_num * coeff_num);
    solver_x.data() -> setNumberOfConstraints(lb_all_x.size());
    solver_x.data() -> setHessianMatrix(Q_all);
    solver_x.data() -> setGradient(f_all);
    solver_x.data() -> setLinearConstraintsMatrix(A_all_x);
    solver_x.data() -> setLowerBound(lb_all_x);
    solver_x.data() -> setUpperBound(ub_all_x);

    if (!solver_x.initSolver())
    {
        return false;
    }
    solver_x.solveProblem();
    Eigen::VectorXd solution_x = solver_x.getSolution();
    for (int i = 0; i < segment_num; i++)
    {
        coeff_all_x.push_back(solution_x.segment(i * coeff_num, coeff_num));
    }
    coeff_xyz.push_back(coeff_all_x);

    // y方向轨迹参数求解
    solver_y.data() -> setNumberOfVariables(segment_num * coeff_num);
    solver_y.data() -> setNumberOfConstraints(lb_all_y.size());
    solver_y.data() -> setHessianMatrix(Q_all);
    solver_y.data() -> setGradient(f_all);
    solver_y.data() -> setLinearConstraintsMatrix(A_all_y);
    solver_y.data() -> setLowerBound(lb_all_y);
    solver_y.data() -> setUpperBound(ub_all_y);

    if (!solver_y.initSolver())
    {
        return false;
    }
    solver_y.solveProblem();
    Eigen::VectorXd solution_y = solver_y.getSolution();
    for (int i = 0; i < segment_num; i++)
    {
        coeff_all_y.push_back(solution_y.segment(i * coeff_num, coeff_num));
    }
    coeff_xyz.push_back(coeff_all_y);

    // z方向轨迹参数求解
    solver_z.data() -> setNumberOfVariables(segment_num * coeff_num);
    solver_z.data() -> setNumberOfConstraints(lb_all_z.size());
    solver_z.data() -> setHessianMatrix(Q_all);
    solver_z.data() -> setGradient(f_all);
    solver_z.data() -> setLinearConstraintsMatrix(A_all_z);
    solver_z.data() -> setLowerBound(lb_all_z);
    solver_z.data() -> setUpperBound(ub_all_z);

    if (!solver_z.initSolver())
    {
        return false;
    }
    solver_z.solveProblem();
    Eigen::VectorXd solution_z = solver_z.getSolution();
    for (int i = 0; i < segment_num; i++)
    {
        coeff_all_z.push_back(solution_z.segment(i * coeff_num, coeff_num));
    }
    coeff_xyz.push_back(coeff_all_z);

    return true;
}

// --------------------------------------------------------------轨迹规划----------------------------------------------------------------------

// 轨迹规划构造函数
TrajectoryPlanner::TrajectoryPlanner(std::string planner_) : planner(planner_) {}

// 输入初始路径
void TrajectoryPlanner::setInitPath(std::vector<Node> path_)
{
    path = path_;
}

// 设置飞行速度
void TrajectoryPlanner::setVelocity(double velocity_)
{
    velocity = velocity_;
}

// 轨迹求解
void TrajectoryPlanner::TrajectoryGenerate(std::vector<Eigen::Vector3d>& trajectory_points)
{
    // MinimumSnap方法求解
    if (planner == "MinimumSnap")
    {
        MinimumSnapTrajectoryPlanner traj_planner(7);
        traj_planner.setWayPoints(path);
        double total_time = path.back().f_cost / velocity * 2.0;        // 总时间
        traj_planner.setSegmentTimes(total_time);

        // 轨迹求解
        // std::vector<std::vector<Eigen::VectorXd>> coeff;
        if (traj_planner.getSolution(coeff))
        {
            std::cout << "Trajectory Planning Successful!" << std::endl;
        }
        else
        {
            std::cout << "Trajectory Planning Fail!" << std::endl;
            return;
        }
        
        // 轨迹转换为路径点

        // 根据多项式系数计算对应时间的位置
        auto PositionCalculate = [](double t_input, Eigen::VectorXd coeff_input)
        {
            double position = 0;
            for (int i = 0; i < coeff_input.size(); i++)
            {
                position += (coeff_input(i) * std::pow(t_input, i));
            }
            return position;
        };

        double dt = 0.1;
        for (int i = 0; i < path.size() - 1; i++)
        {
            Eigen::VectorXd coeff_x = coeff[0][i];
            Eigen::VectorXd coeff_y = coeff[1][i];
            Eigen::VectorXd coeff_z = coeff[2][i];
            for (double t = 0; t < traj_planner.times[i]; t += dt)
            {
                double x = PositionCalculate(t, coeff_x);
                double y = PositionCalculate(t, coeff_y);
                double z = PositionCalculate(t, coeff_z);
                trajectory_points.emplace_back(x, y, z);
            }
        }
    }

    if (planner == "bspline")
    {
        BsplineTrajectoryPlanner Bspline_planner(3, 10);
        Bspline_planner.setWayPoints(path);
        trajectory_points = Bspline_planner.getSingleTrajetory();
    }
    
}


// void TrajectoryPlanner::setPathPlanner(PathPlanner pathplanner_)
// {
//     pathplanner = pathplanner_;
// }