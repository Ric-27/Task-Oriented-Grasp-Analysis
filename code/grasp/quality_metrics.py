from __future__ import annotations
import sys, os
import numpy as np
from scipy.optimize import linprog
from scipy.linalg import LinAlgWarning
from typing import List, Tuple, Union
import warnings

warnings.filterwarnings(action="ignore", category=LinAlgWarning, module="scipy")

sys.path.append(os.path.dirname(__file__))
from grasp_functions import is_grasp_valid
from class_jacobian import Jacobian
from class_grasp import Grasp


def friction_form_closure(grasp: "Grasp") -> Tuple(int, np.ndarray):
    G = grasp.Gt.transpose()
    L = grasp.l
    if not is_grasp_valid(grasp):
        return 0, np.zeros((L,))
    nc = grasp.nc

    F = grasp.F
    e = []
    for i in range(nc):
        e.append([1, 0, 0])
    e = np.array(e).flatten()

    obj = np.concatenate((-1 * np.ones((1, 1)), np.zeros((1, L))), axis=1).flatten()

    lhs_ineq = np.block(
        [
            [np.ones((F.shape[0], 1)), -F],
            [np.zeros(1), e],
        ]
    )

    rhs_ineq = np.concatenate(
        (np.zeros((1, F.shape[0])), 10 * nc * np.ones((1, 1))), axis=1
    ).flatten()

    lhs_eq = np.concatenate((np.zeros((6, 1)), G), axis=1)

    rhs_eq = np.zeros((6, 1)).flatten()

    bnd_d = (0, None)
    bnd_lambda = (None, None)

    bnd = []
    bnd.append(bnd_d)

    for i in range(L):
        bnd.append(bnd_lambda)
    try:
        opt = linprog(
            c=obj,
            A_ub=lhs_ineq,
            b_ub=rhs_ineq,
            A_eq=lhs_eq,
            b_eq=rhs_eq,
            bounds=bnd,
            method="revised simplex",
        )
    except Exception:
        pass
    if opt.success and abs(opt.fun) != 0:
        lambdas = []
        for i, var in enumerate(opt.x, 0):
            if i == 0:
                pass
            else:
                lambdas.append(var)
        return abs(opt.fun), np.array(lambdas)
    return 0, np.zeros((L,))


def force_closure(grasp: "Grasp", jacobian: "Jacobian") -> bool:
    assert isinstance(jacobian, Jacobian), "jacobian argument must be of type Jacobian"
    L = grasp.l
    if not friction_form_closure(grasp)[0]:
        print(
            "Force Closure does not Exist because Friction Form Closure does not Exist"
        )
        return False
    nc = grasp.nc
    G = grasp.Gt.transpose()
    Jt = jacobian.J.transpose()
    e = []
    E = np.array([1, 0, 0]).reshape(1, 3)
    for _ in range(nc):
        e.append([1, 0, 0])
        Etemp = np.concatenate(
            (np.zeros((1, E.shape[1])).flatten(), np.array([1, 0, 0]))
        ).reshape(1, E.shape[1] + 3)
        E = np.concatenate((E, np.zeros((E.shape[0], 3))), axis=1)
        E = np.concatenate((E, Etemp), axis=0)
    e = np.array(e).flatten()
    E = E[0:-1, 0:-3]
    obj = np.concatenate((-1 * np.ones((1, 1)), np.zeros((1, L))), axis=1).flatten()

    lhs_ineq = np.block(
        [
            [np.ones((E.shape[0], 1)), -E],
            [-1 * np.ones(1), np.zeros((1, L))],
            [np.zeros(1), e],
        ]
    )

    rhs_ineq = np.concatenate(
        (np.zeros((1, E.shape[0] + 1)), 10 * nc * np.ones((1, 1))), axis=1
    ).flatten()

    lhs_eq = np.block(
        [
            [np.zeros((6, 1)), G],
            [np.zeros((jacobian.nq, 1)), Jt],
        ]
    )
    print(lhs_eq)
    rhs_eq = np.zeros((6 + jacobian.nq, 1)).flatten()

    bnd = [(None, None)]

    opt = linprog(
        c=obj,
        A_ub=lhs_ineq,
        b_ub=rhs_ineq,
        A_eq=lhs_eq,
        b_eq=rhs_eq,
        bounds=bnd,
        method="revised simplex",
    )
    if opt.success and abs(opt.fun) == 0:
        print("Force Closure Exist")
        return True
    else:
        print("Force Closure does not Exist")
        return False


def alpha_from_direction(
    grasp: "Grasp", d_ext: List, fc_max: int = 10
) -> Tuple(float, np.ndarray):
    G = grasp.get_Gt().transpose()
    L = grasp.l
    if not is_grasp_valid(grasp):
        return 0, np.zeros((L,))

    if not isinstance(d_ext, np.ndarray):
        d_ext = np.array(d_ext)

    F = grasp.F
    lF = np.shape(F)[0]

    obj = np.zeros((L + 1, 1))
    obj[0] = -1

    # 0*alpha - F*fc <= 0 (F*fc > 0)
    lhs_ineq = np.concatenate((np.zeros((lF, 1)), -F), axis=1)
    rhs_ineq = -sys.float_info.epsilon * np.ones((lF, 1)).flatten()

    # dWext*alpha + G*fc = 0
    lhs_eq = np.concatenate(
        (
            d_ext.reshape(6, 1),
            G,
        ),
        axis=1,
    )
    rhs_eq = np.zeros((6,))

    lower_bound = []
    for val in grasp.contact_points:
        lower_bound.append(val.fa)

    bnd = []
    bnd.append((0, None))  # alpha

    for i in range(L):
        if i % 3 == 0:
            low = (
                sys.float_info.epsilon
                if lower_bound[i // 3] == 0
                else -lower_bound[i // 3]
            )
            bnd.append((low, fc_max))  # fcn
        else:
            bnd.append((None, None))  # fct
    print(bnd)
    exit
    opt = linprog(
        c=obj,
        A_ub=lhs_ineq,
        b_ub=rhs_ineq,
        A_eq=lhs_eq,
        b_eq=rhs_eq,
        bounds=bnd,
        method="revised simplex",
    )
    if opt.success:
        return opt.x[0], opt.x[1:]
    else:
        return 0, np.zeros((L,))


def forces_from_perturbation(grasp: Grasp, perturbation: List) -> Union(float, List):
    L = grasp.l
    if not is_grasp_valid(grasp):
        return np.zeros((L,))

    if not isinstance(perturbation, np.ndarray):
        perturbation = np.array(perturbation)

    G = grasp.Gt.transpose()
    F = grasp.F
    lF = np.shape(F)[0]

    # min(z)
    obj = np.zeros((L + 1, 1))
    obj[0] = 1

    # -F*fc <= 0 (F*fc > 0)
    # fc - z <= (fc <= z)
    fcn_coef = np.zeros((L, L))
    for i in range(L):
        fcn_coef[i, i] = 1 if not i % 1 else 0  # when one equiv to eye
    lhs_ineq = np.block([[np.zeros((lF, 1)), -F], [-1 * np.ones((L, 1)), fcn_coef]])
    rhs_ineq = np.zeros((lF + L,))
    # G*fc = -g (G*fc + alpha*dext = 0)
    lhs_eq = np.concatenate((np.zeros((6, 1)), G), axis=1)
    rhs_eq = -perturbation

    bnd = []
    bnd.append((0, None))
    bnd_fcn = (0.1, None)
    bnd_fct = (None, None)

    for i in range(L):
        if i % 3 == 0:
            bnd.append(bnd_fcn)
        else:
            bnd.append(bnd_fct)

    opt = linprog(
        c=obj,
        A_ub=lhs_ineq,
        b_ub=rhs_ineq,
        A_eq=lhs_eq,
        b_eq=rhs_eq,
        bounds=(None, None),
        method="revised simplex",
    )

    if opt.success:
        return opt.x[1:]
    return np.zeros((L,))


def main():
    val = (
        __file__.replace(os.path.dirname(__file__), "")[1:]
        + " is meant to be imported not executed"
    )
    print(f"\033[91m {val}\033[00m")


if __name__ == "__main__":
    main()
