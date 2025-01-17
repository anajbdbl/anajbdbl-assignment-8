# logistic_regression.py
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from scipy.spatial.distance import cdist
import os
import matplotlib
matplotlib.use('Agg')  # Use the non-interactive Agg backend


result_dir = "results"
os.makedirs(result_dir, exist_ok=True)

def generate_ellipsoid_clusters(distance, n_samples=100, cluster_std=0.5):
    np.random.seed(0)
    covariance_matrix = np.array([[cluster_std, cluster_std * 0.8], 
                                   [cluster_std * 0.8, cluster_std]])
    
    # Generate the first cluster (class 0)
    X1 = np.random.multivariate_normal(mean=[1, 1], cov=covariance_matrix, size=n_samples)
    y1 = np.zeros(n_samples)

    # Generate the second cluster (class 1) and shift it
    X2 = np.random.multivariate_normal(mean=[1 + distance, 1 + distance], cov=covariance_matrix, size=n_samples)
    y2 = np.ones(n_samples)

    # Combine the clusters into one dataset
    X = np.vstack((X1, X2))
    y = np.hstack((y1, y2))
    return X, y

def fit_logistic_regression(X, y):
    model = LogisticRegression()
    model.fit(X, y)
    beta0 = model.intercept_[0]
    beta1, beta2 = model.coef_[0]
    return model, beta0, beta1, beta2

def logistic_loss(model, X, y):
    probabilities = model.predict_proba(X)[:, 1]
    loss = -np.mean(y * np.log(probabilities) + (1 - y) * np.log(1 - probabilities))
    return loss

def do_experiments(start, end, step_num):
    shift_distances = np.linspace(start, end, step_num)
    beta0_list, beta1_list, beta2_list, slope_list, intercept_list, loss_list, margin_widths = [], [], [], [], [], [], []
    sample_data = {}

    n_samples = len(shift_distances)
    n_cols = 2
    n_rows = (n_samples + n_cols - 1) // n_cols
    plt.figure(figsize=(20, n_rows * 10))

    for i, distance in enumerate(shift_distances, 1):
        X, y = generate_ellipsoid_clusters(distance=distance)
        model, beta0, beta1, beta2 = fit_logistic_regression(X, y)
        
        # Record logistic loss and other model parameters
        loss = logistic_loss(model, X, y)
        slope = -beta1 / beta2
        intercept = -beta0 / beta2

        beta0_list.append(beta0)
        beta1_list.append(beta1)
        beta2_list.append(beta2)
        slope_list.append(slope)
        intercept_list.append(intercept)
        loss_list.append(loss)

        # Calculate margin width
        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))
        Z = model.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]
        Z = Z.reshape(xx.shape)

        contour_levels = [0.7, 0.8, 0.9]
        alphas = [0.05, 0.1, 0.15]
        for level, alpha in zip(contour_levels, alphas):
            class_1_contour = plt.contourf(xx, yy, Z, levels=[level, 1.0], colors=['red'], alpha=alpha)
            class_0_contour = plt.contourf(xx, yy, Z, levels=[0.0, 1 - level], colors=['blue'], alpha=alpha)
            if level == 0.7:
                distances = cdist(class_1_contour.collections[0].get_paths()[0].vertices, 
                                  class_0_contour.collections[0].get_paths()[0].vertices, 
                                  metric='euclidean')
                min_distance = np.min(distances)
                margin_widths.append(min_distance)

        # Plot data points and decision boundary
        plt.subplot(n_rows, n_cols, i)
        plt.scatter(X[y == 0][:, 0], X[y == 0][:, 1], color="blue", label="Class 0")
        plt.scatter(X[y == 1][:, 0], X[y == 1][:, 1], color="red", label="Class 1")
        plt.plot(xx[0, :], slope * xx[0, :] + intercept, 'k--', label="Decision Boundary")
        plt.title(f"Shift Distance = {distance:.2f}")
        plt.legend()

    plt.tight_layout()
    plt.savefig(f"{result_dir}/dataset.png")

    # Plot parameters vs shift distance
    plt.figure(figsize=(18, 15))

    # Plot beta0
    plt.subplot(3, 3, 1)
    plt.plot(shift_distances, beta0_list, label="Beta0")
    plt.title("Beta0 vs Shift Distance")
    plt.xlabel("Shift Distance")
    plt.ylabel("Beta0")

    # Plot beta1
    plt.subplot(3, 3, 2)
    plt.plot(shift_distances, beta1_list, label="Beta1 (x1 coefficient)")
    plt.title("Beta1 vs Shift Distance")
    plt.xlabel("Shift Distance")
    plt.ylabel("Beta1")

    # Plot beta2
    plt.subplot(3, 3, 3)
    plt.plot(shift_distances, beta2_list, label="Beta2 (x2 coefficient)")
    plt.title("Beta2 vs Shift Distance")
    plt.xlabel("Shift Distance")
    plt.ylabel("Beta2")

    # Plot logistic loss
    plt.subplot(3, 3, 4)
    plt.plot(shift_distances, loss_list, label="Logistic Loss")
    plt.title("Logistic Loss vs Shift Distance")
    plt.xlabel("Shift Distance")
    plt.ylabel("Loss")

    plt.tight_layout()
    plt.savefig(f"{result_dir}/parameters_vs_shift_distance.png")

if __name__ == "__main__":
    start = 0.25
    end = 2.0
    step_num = 8
    do_experiments(start, end, step_num)
