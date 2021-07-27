import math
from scipy.optimize import linprog
import numpy as np
from math_tools import get_rank, gen_F
from class_grasp import Grasp


def friction_form_closure(grasp, ng=8, mu=0.3):
    G = grasp.getGt().transpose()
    if get_rank(G) != 6:
        print("ERROR: rank of G is not equal to 6")
        print("Friction Form Closure does not Exist")
        return -1, -1
    graspable = grasp.GraspClassification(False)[1]
    if not graspable:
        print("ERROR: G is not Graspable")
        print("Friction Form Closure does not Exist")
        return -1, -1
    notH = False
    for hi in grasp.h:
        if hi != "H":
            notH = True
            break
    if notH:
        print(
            "ERROR: Original definition of contact models is not Hard Finger for all contacts"
        )
        return -1, -1
    nc = grasp.C.shape[0]

    L = 3 * nc
    F = gen_F(nc, ng, mu)
    e = []
    for i in range(nc):
        e.append([1, 0, 0])
    e = np.array(e).flatten()

    obj = np.concatenate((-1 * np.ones((1, 1)), np.zeros((1, L))), axis=1).flatten()

    lhs_ineq = np.block(
        [
            [np.ones((F.shape[0], 1)), -F],
            [-1 * np.ones(1), np.zeros((1, L))],
            [np.zeros(1), e],
        ]
    )

    rhs_ineq = np.concatenate(
        (np.zeros((1, F.shape[0] + 1)), 10 * nc * np.ones((1, 1))), axis=1
    ).flatten()

    lhs_eq = np.concatenate((np.zeros((6, 1)), G), axis=1)

    rhs_eq = np.zeros((6, 1)).flatten()

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
    if opt.success:
        print("Friction Form Closure Exist with d =", abs(opt.fun))
        lambdas = []
        for i, var in enumerate(opt.x, 0):
            if i == 0:
                pass
            else:
                lambdas.append(var)
        lambdas = np.array(lambdas)
        return abs(opt.fun), lambdas
    else:
        print("Friction Form Closure does not Exist")
        return -1, np.zeros((1, L))


def Force_closure(grasp, jacobian):
    assert isinstance(grasp, Grasp), "grasp must be an object of type Grasp"
    nc = grasp.C.shape[0]
    L = 3 * nc

    d, l = friction_form_closure(grasp)
    if d <= 0:
        print(
            "Force Closure does not Exist because Friction Form Closure does not Exist"
        )
        return np.zeros((1, L))
    else:
        G = grasp.getGt().transpose()
        Jt = jacobian.getJ().transpose()
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
            return l
        else:
            print("Force Closure does not Exist")
            return np.zeros((1, L))


def task_oriented(grasp, dExt, fcmax=2, ng=8, mu=0.3):
    nc = grasp.C.shape[0]
    L = 3 * nc
    G = grasp.get_grasp_matrix_t().transpose()
    if not isinstance(dExt, np.ndarray):
        dExt = np.array(dExt)
    L = np.shape(G)[1]
    F = gen_F(nc, ng, mu)
    lF = np.shape(F)[0]
    obj = (
        np.concatenate((-1 * np.ones((1, 1)), np.zeros((1, L))), axis=1)
        .flatten()
        .reshape(L + 1, 1)
    )
    fcn_helper = np.zeros((L, L))
    for i in range(L):
        if i % 3 == 0:
            fcn_helper[i, i] = -1

    lhs_ineq = np.block(
        [
            [np.zeros((lF, 1)), -F],
            [np.zeros((L, 1)), np.eye(L)],
            [-1 * np.ones(1), np.zeros((1, L))],
            [np.zeros((L, 1)), fcn_helper],
        ]
    )

    rhs_ineq = np.concatenate(
        (
            np.zeros((1, lF)),
            fcmax * np.ones((1, L)),
            np.zeros((1, 1)),
            np.zeros((1, L)),
        ),
        axis=1,
    ).flatten()

    lhs_eq = np.concatenate((dExt.reshape(6, 1), G), axis=1)
    rhs_eq = np.zeros((6, 1)).flatten()

    bnd = (None, None)
    opt = linprog(
        c=obj,
        A_ub=lhs_ineq,
        b_ub=rhs_ineq,
        A_eq=lhs_eq,
        b_eq=rhs_eq,
        bounds=bnd,
    )

    if opt.success:
        # print("Task Metric Exists with alpha =", abs(opt.fun))
        fc = np.zeros((L, 1))
        for i in range(L):
            if i % 3 == 0:
                fc[i] = abs(opt.x[i + 1])
            else:
                fc[i] = abs(opt.x[i + 1])
        return abs(opt.fun), fc
    else:
        # print("Task Metric does not Exist")
        return -1, np.zeros((1, L))
