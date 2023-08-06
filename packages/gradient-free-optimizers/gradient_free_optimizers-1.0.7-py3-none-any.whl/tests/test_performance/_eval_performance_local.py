def warn(*args, **kwargs):
    pass


import warnings

warnings.warn = warn

warnings.filterwarnings("ignore")


import numpy as np
import pandas as pd

from functools import reduce
import plotly.express as px


from gradient_free_optimizers import (
    HillClimbingOptimizer,
    StochasticHillClimbingOptimizer,
    RepulsingHillClimbingOptimizer,
    SimulatedAnnealingOptimizer,
    DownhillSimplexOptimizer,
    RandomSearchOptimizer,
    GridSearchOptimizer,
    RandomRestartHillClimbingOptimizer,
    RandomAnnealingOptimizer,
    PowellsMethod,
    PatternSearch,
    ParallelTemperingOptimizer,
    ParallelAnnealingOptimizer,
    ParticleSwarmOptimizer,
    EvolutionStrategyOptimizer,
    BayesianOptimizer,
    TreeStructuredParzenEstimators,
    ForestOptimizer,
    EnsembleOptimizer,
)

from surfaces.test_functions import SphereFunction, AckleyFunction, RastriginFunction

n_iter_single_opt = 100
n_iter_pop_opt = 250
n_iter_smbo = 25

"""

"""

optimizer_setups = [
    (HillClimbingOptimizer, n_iter_single_opt),
    (StochasticHillClimbingOptimizer, n_iter_single_opt),
    (RepulsingHillClimbingOptimizer, n_iter_single_opt),
    (SimulatedAnnealingOptimizer, n_iter_single_opt),
    (DownhillSimplexOptimizer, n_iter_single_opt),
    (PowellsMethod, n_iter_single_opt),
    (RandomRestartHillClimbingOptimizer, n_iter_single_opt),
    (RandomAnnealingOptimizer, n_iter_single_opt),
    (PatternSearch, n_iter_single_opt),
    (ParallelTemperingOptimizer, n_iter_pop_opt),
    (ParallelAnnealingOptimizer, n_iter_pop_opt),
    (ParticleSwarmOptimizer, n_iter_pop_opt),
    (EvolutionStrategyOptimizer, n_iter_pop_opt),
    (BayesianOptimizer, n_iter_smbo),
    # (TreeStructuredParzenEstimators, n_iter_smbo),
    # (ForestOptimizer, n_iter_smbo),
    # (EnsembleOptimizer, n_iter_smbo),
]


def get_norm_scores(opt_class, obj_func, search_space, n_iter, opt_para={}, n_runs=3):
    dim_sizes_list = [len(array) for array in search_space.values()]
    ss_size = reduce((lambda x, y: x * y), dim_sizes_list)

    initialize = {"vertices": 2, "random": 8}
    random_state = np.random.randint(1, high=10)

    score_norm_rand_mean = []
    score_norm_grid_mean = []

    for nth_run in range(n_runs):
        random_state = random_state + nth_run

        opt = opt_class(search_space, initialize, random_state, **opt_para)
        opt.search(obj_func, n_iter=n_iter, verbosity=False)

        opt_rand = RandomSearchOptimizer(search_space, initialize, random_state)
        opt_rand.search(obj_func, n_iter=n_iter, verbosity=False)

        opt_grid = GridSearchOptimizer(
            search_space,
            initialize,
            random_state,
            step_size=int(ss_size / random_state),
        )
        opt_grid.search(obj_func, n_iter=n_iter, verbosity=False)

        best_score = opt.best_score
        best_score_rand = opt_rand.best_score
        best_score_grid = opt_grid.best_score

        score_norm_rand = (best_score_rand - best_score) / (
            best_score_rand + best_score
        )
        score_norm_grid = (best_score_grid - best_score) / (
            best_score_grid + best_score
        )

        if abs(best_score) < 0.00000001:
            score_norm_rand = 1
            score_norm_grid = 1

        score_norm_rand_mean.append(score_norm_rand)
        score_norm_grid_mean.append(score_norm_grid)

    score_norm_rand_mean = np.array(score_norm_rand_mean).mean() * 100
    score_norm_grid_mean = np.array(score_norm_grid_mean).mean() * 100

    return score_norm_rand_mean, score_norm_grid_mean


def run_test_setup(test_functions):
    score_norm_rand_mean = []
    score_norm_grid_mean = []

    for test_function in test_functions:
        score_norm_rand, score_norm_grid = get_norm_scores(
            opt_class=opt_class,
            n_iter=n_iter,
            **test_function,
            opt_para={},
            n_runs=10,
        )

        score_norm_rand_mean.append(score_norm_rand)
        score_norm_grid_mean.append(score_norm_grid)

    score_norm_rand_mean = np.array(score_norm_rand_mean).mean()
    score_norm_grid_mean = np.array(score_norm_grid_mean).mean()

    return score_norm_rand_mean, score_norm_grid_mean


data_d = {}

data_d["score norm"] = []
data_d["optimizer"] = []
data_d["test type"] = []


for optimizer_setup in optimizer_setups:
    opt_class = optimizer_setup[0]
    n_iter = optimizer_setup[1]

    print("\n")
    print(opt_class.name)

    sphere_2 = SphereFunction(n_dim=2, metric="score")
    sphere_3 = SphereFunction(n_dim=3, metric="score")

    ackley_function = AckleyFunction(metric="score")

    rastrigin_function_2 = RastriginFunction(n_dim=2, metric="score")
    rastrigin_function_3 = RastriginFunction(n_dim=3, metric="score")

    convex_test_1 = {"obj_func": sphere_2, "search_space": sphere_2.search_space()}
    convex_test_2 = {
        "obj_func": sphere_3,
        "search_space": sphere_3.search_space(step=0.5),
    }
    convex_test_3 = {
        "obj_func": sphere_2,
        "search_space": sphere_2.search_space(min=-9, max=1),
    }
    convex_test_4 = {
        "obj_func": sphere_3,
        "search_space": sphere_3.search_space(min=-1, max=9, step=0.5),
    }

    non_convex_test_1 = {
        "obj_func": rastrigin_function_2,
        "search_space": rastrigin_function_2.search_space(),
    }
    non_convex_test_2 = {
        "obj_func": rastrigin_function_3,
        "search_space": rastrigin_function_3.search_space(),
    }
    non_convex_test_3 = {
        "obj_func": rastrigin_function_2,
        "search_space": rastrigin_function_2.search_space(min=-9, max=1),
    }
    non_convex_test_4 = {
        "obj_func": rastrigin_function_3,
        "search_space": rastrigin_function_3.search_space(min=-1, max=9, step=0.5),
    }

    non_convex_test_5 = {
        "obj_func": ackley_function,
        "search_space": ackley_function.search_space(),
    }

    convex_tests = [
        convex_test_1,
        convex_test_2,
        convex_test_3,
        convex_test_4,
    ]
    non_convex_tests = [
        non_convex_test_1,
        non_convex_test_2,
        non_convex_test_3,
        non_convex_test_4,
        non_convex_test_5,
    ]

    test_setups = {
        "convex tests": convex_tests,
        "non-convex tests": non_convex_tests,
    }

    for test_name, test_setup in test_setups.items():
        print(" ", test_name)

        score_norm_rand, score_norm_grid = run_test_setup(test_setup)

        score_norm = np.mean([score_norm_rand, score_norm_grid], axis=0)

        data_d["score norm"].append(score_norm)
        data_d["optimizer"].append(opt_class.name)
        data_d["test type"].append(test_name)

        print("    rand norm score ", round(score_norm_rand, 1))
        print("    grid norm score ", round(score_norm_grid, 1))

data_df = pd.DataFrame(data_d)

fig = px.bar(
    data_df,
    x="optimizer",
    y="score norm",
    color="test type",
    barmode="group",
    height=800,
)
fig.show()
