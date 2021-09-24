import sys, os
import numpy as np
from scipy.optimize import linprog
import keyboard
from typing import List

sys.path.append(os.path.dirname(__file__))
from grasp_functions import get_rank
from class_jacobian import Jacobian
from class_grasp import Grasp


def friction_form_closure(grasp):
    assert isinstance(grasp, Grasp), "grasp argument must be of type Grasp"
    G = grasp.Gt.transpose()
    L = grasp.l

    if get_rank(G) != 6:
        # print("Friction Form Closure does not Exist: Rank of G < 6")
        return -1, np.zeros((L,))
    graspable = grasp.graspable
    if not graspable:
        # print("Friction Form Closure does not Exist: G not graspable")
        return -1, np.zeros((L,))
    not_hf = False
    for contact in grasp.contact_points:
        if contact.type != "HF":
            not_hf = True
            break
    if not_hf:
        # print(
        #    "ERROR: Original definition of contact models is not Hard Finger for all contacts"
        # )
        return -1, np.zeros((L,))
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
        if abs(opt.fun) != 0:
            # print("Friction Form Closure Exist with d =", abs(opt.fun))
            lambdas = []
            for i, var in enumerate(opt.x, 0):
                if i == 0:
                    pass
                else:
                    lambdas.append(var)
            lambdas = np.array(lambdas)
            return abs(opt.fun), lambdas
        else:
            # print("Friction Form Closure does not Exist: d = 0")
            lambdas = []
            for i, var in enumerate(opt.x, 0):
                if i == 0:
                    pass
                else:
                    lambdas.append(var)
            lambdas = np.array(lambdas)
            return 0, lambdas
    else:
        # print(
        #    "Friction Form Closure does not Exist: Linear Programming Problem doesn't have a solution"
        # )
        return -1, np.zeros((L,))


def force_closure(grasp, jacobian):
    assert isinstance(grasp, Grasp), "grasp argument must be of type Grasp"
    assert isinstance(jacobian, Jacobian), "jacobian argument must be of type Jacobian"
    nc = grasp.nc
    L = grasp.l

    d, l = friction_form_closure(grasp)
    if d <= 0:
        print(
            "Force Closure does not Exist because Friction Form Closure does not Exist"
        )
        return np.zeros((L,))
    else:
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
            return l
        else:
            print("Force Closure does not Exist")
            return np.zeros((L,))


def alpha_from_direction(grasp, d_ext, fc_max=10):
    assert isinstance(grasp, Grasp), "grasp argument must be of type Grasp"
    G = grasp.Gt.transpose()
    L = grasp.l
    if get_rank(G) != 6:
        # print("ERROR: rank of G is not equal to 6")
        # print("Cant Calculate Alpha")
        return np.zeros((L + 1,))
    if not grasp.graspable:
        # print("ERROR: G is not Graspable")
        # print("Friction Form Closure does not Exist")
        return np.zeros((L + 1,))
    not_hf = False
    for contact in grasp.contact_points:
        if contact.type != "HF":
            not_hf = True
            break
    if not_hf:
        print(
            "ERROR: Original definition of contact models is not Hard Finger for all contacts"
        )
        return np.zeros((L + 1,))

    if not isinstance(d_ext, np.ndarray):
        d_ext = np.array(d_ext)

    F = grasp.F
    lF = np.shape(F)[0]

    obj = np.zeros((L + 1, 1))
    obj[0] = -1

    lhs_ineq = np.concatenate(
        (np.zeros((lF, 1)), -F), axis=1
    )  # 0*alpha - F*fc <= 0 (F*fc > 0)
    rhs_ineq = -sys.float_info.epsilon * np.ones((lF, 1)).flatten()

    lhs_eq = np.concatenate(
        (
            d_ext.reshape(6, 1),
            G,
        ),
        axis=1,
    )  # dWext*alpha + G*fc = 0
    rhs_eq = np.zeros((6,))

    bnd_alpha = (0, None)
    bnd_fcn = (sys.float_info.epsilon, fc_max)
    bnd_fct = (None, None)

    bnd = []
    bnd.append(bnd_alpha)

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
        bounds=bnd,
        method="revised simplex",
    )
    if opt.success:
        # print("Metric exists with alpha =", abs(opt.fun))
        return opt.x[0], opt.x[1:]
    else:
        # print("Task Metric does not Exist")
        return np.zeros((L + 1,))


def fc_from_g_dep(grasp, g, start=0.1, end=100, step=0.1):
    G = grasp.Gt.transpose()
    L = grasp.l
    assert (
        start > 0 and end > 0 and step > 0
    ), "start, end and step must be greater than 0"
    if get_rank(G) != 6:
        # print("ERROR: rank of G is not equal to 6")
        # print("Cant Calculate Fc")
        return -1, np.zeros((L,))
    if not grasp.graspable:
        # print("ERROR: G is not Graspable")
        # print("Fc cant be found")
        return -1, np.zeros((L,))
    not_hf = False
    for contact in grasp.contact_points:
        if contact.type != "HF":
            not_hf = True
            break
    if not_hf:
        print(
            "ERROR: Original definition of contact models is not Hard Finger for all contacts"
        )
        return -1, np.zeros((L,))
    if not isinstance(g, np.ndarray):
        g = np.array(g)

    F = grasp.F
    lF = np.shape(F)[0]

    obj = np.zeros((L, 1))
    # obj = -1 * np.ones((L, 1))  # negative for max, positive for min
    for i in range(L):
        if i % 3 == 0:
            # pass
            obj[i] = 1  # for only fcn

    lhs_ineq = -F  # F*fc <= 0 (F*fc > 0)
    rhs_ineq = -sys.float_info.epsilon * np.ones((1, lF)).flatten()

    lhs_eq = G  # G*fc = -g (G*fc + alpha*dext = 0)
    rhs_eq = -g

    finished = False
    fc_max = start
    while not finished:
        bnd_fcn = (0, fc_max)
        bnd_fct = (None, None)

        bnd = []

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
            bounds=bnd,
            method="revised simplex",
        )
        finished = opt.success
        fc_max += step
        if fc_max > end:
            finished = True
        if keyboard.is_pressed("q"):
            return -2.5, np.zeros((L,))
        if keyboard.is_pressed("s"):
            return -3.5, np.zeros((L,))

    if opt.success:
        # print("fc found")
        return fc_max - step, opt.x
    else:
        # print("Task Metric does not Exist")
        return -1.1, np.zeros((L,))


def forces_from_perturbation(grasp: Grasp, perturbation: List) -> List:
    G = grasp.Gt.transpose()
    L = grasp.l
    if get_rank(G) != 6:
        # print("ERROR: rank of G is not equal to 6")
        # print("Cant Calculate Fc")
        return -1, np.zeros((L,))
    if not grasp.graspable:
        # print("ERROR: G is not Graspable")
        # print("Fc cant be found")
        return -1, np.zeros((L,))
    not_hf = False
    for contact in grasp.contact_points:
        if contact.type != "HF":
            not_hf = True
            break
    if not_hf:
        print(
            "ERROR: Original definition of contact models is not Hard Finger for all contacts"
        )
        return -1, np.zeros((L,))
    F = grasp.F
    lF = np.shape(F)[0]
    g = np.array(g).flatten()
    obj = np.zeros((L + 1, 1))
    obj[0] = -1

    lhs_ineq = np.block([[np.zeros((lF, 1)), -F], [np.ones((L, 1)), -1 * np.eye(L)]])
    # F*fc <= 0 (F*fc > 0)
    rhs_ineq = np.zeros((lF + L,))
    lhs_eq = np.concatenate(
        (np.zeros((6, 1)), G), axis=1
    )  # G*fc = -g (G*fc + alpha*dext = 0)
    rhs_eq = -g

    for fmax in FMAXS:
        bnd = []
        bnd.append((None, None))
        bnd_fcn = (0, fmax)
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
            bounds=bnd,
            method="revised simplex",
        )

        if opt.success:
            # print("fc found", fmax)
            # print("z", opt.fun)
            return fmax, opt.x[1:]
        if keyboard.is_pressed("Q"):
            return -2.5, np.zeros((L,))
        if keyboard.is_pressed("S"):
            return -3.5, np.zeros((L,))

    # print("Task Metric does not Exist")
    return -10, np.zeros((L,))


def main():
    val = (
        __file__.replace(os.path.dirname(__file__), "")[1:]
        + " is meant to be imported not executed"
    )
    print(f"\033[91m {val}\033[00m")


if __name__ == "__main__":
    main()
