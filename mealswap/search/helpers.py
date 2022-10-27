from flask import request
from math import sqrt, acos, pi
import numpy as np
from scipy.optimize import minimize
from mealswap.controller.controls import get_all_elements, Model, get_saved_items, get_ratings_count_by_user, \
    get_element_by_id


def get_float(key) -> float or None:
    """Helper function for getting arguments."""
    try:
        value = float(request.args.get(key))
    except TypeError:
        value = None
    return value


def get_similar_items(items, protein, carb, fat, calories, item_id):
    """Returns a list of similar items.
    Similarity of items is defined by cosine similarity of item vectors.
    Vector dimensions are macronutrient values."""
    similarity_list = []
    for i in items:
        if item_id:
            numerator = i.protein * protein + \
                        i.carb * carb + \
                        i.fat * fat
            denominator = sqrt(i.protein * i.protein + i.carb * i.carb + i.fat * i.fat) * sqrt(protein * protein + carb
                                                                                               * carb + fat * fat)
        else:
            numerator = 0
            den1 = 0
            den2 = 0
            if protein:
                numerator += i.protein * protein
                den1 += i.protein * i.protein
                den2 += protein * protein
            if carb:
                numerator += i.carb * carb
                den1 += i.carb * i.carb
                den2 += carb * carb
            if fat:
                numerator += i.fat * fat
                den1 += i.fat * i.fat
                den2 += fat * fat
            if calories:
                numerator += i.calories * calories
                den1 += i.calories * i.calories
                den2 += calories * calories
            denominator = sqrt(den1) * sqrt(den2)
        try:
            distance = acos(numerator / denominator)
        except ZeroDivisionError:
            continue
        similarity = 1 - distance * 2 / pi
        similarity_list.append((similarity, i))
    similarity_list.sort(key=lambda x: x[0], reverse=True)
    return similarity_list


def f(params, num_users, num_items, num_features, Y, R, lambda_):
    """Cost function for the collaborative filtering algorithm."""
    params = np.reshape(params, (num_users + num_items, num_features))
    X, Theta = np.split(params, [num_items])
    cost = (np.sum(np.multiply(np.matmul(X, np.transpose(Theta)) - Y, R) ** 2)) / 2 + \
           lambda_ / 2 * (np.sum(Theta ** 2) + np.sum(X ** 2))
    return cost


def grad(params, num_users, num_items, num_features, Y, R, lambda_):
    """Gradient function for the collaborative filtering algorithm."""
    params = np.reshape(params, (num_users + num_items, num_features))
    X, Theta = np.split(params, [num_items])
    X_grad = np.matmul(np.multiply(np.matmul(X, np.transpose(Theta)) - Y, R), Theta) + lambda_ * X
    Theta_grad = np.matmul(np.transpose(np.multiply(np.matmul(X, np.transpose(Theta)) - Y, R)), X) \
                 + lambda_ * Theta
    g = np.concatenate((X_grad, Theta_grad))
    g = g.flatten()
    return g


def get_predictions(user):
    """Returns a list of predictions based on user's ratings."""
    ratings = get_all_elements(Model.RATINGS)
    num_ratings = get_ratings_count_by_user(user)
    users = get_all_elements(Model.USER)
    items = get_saved_items()
    num_users = users[-1].id + 1
    num_items = items[-1].id + 1
    num_features = 10
    lambda_ = 10

    Y = np.zeros((num_items, num_users), np.uint8)
    for rating in ratings:
        Y[rating.item_id, rating.user_id] = rating.rating
    R = np.where(Y > 0, 1, 0)

    X = np.random.rand(num_items, num_features)
    Theta = np.random.rand(num_users, num_features)
    initial_parameters = np.concatenate((X, Theta))
    initial_parameters = initial_parameters.flatten()

    result = minimize(f, initial_parameters, args=(num_users, num_items, num_features, Y, R, lambda_),
                      method='Newton-CG', jac=grad)
    matrix = result.x

    result = np.reshape(matrix, (num_users + num_items, num_features))
    X, Theta = np.split(result, [num_items])
    predictions = np.matmul(X, np.transpose(Theta))
    R = np.invert(R.astype(np.bool)).astype(np.uint8)
    predictions = np.multiply(predictions, R)[:, user.id]
    indexed_predictions = [(predictions[i], i) for i in range(len(predictions))]
    indexed_predictions.sort(reverse=True, key=lambda x: x[0])
    indices = [x[1] for x in indexed_predictions]
    indices = indices[:(len(indices) - num_ratings)]

    sorted_items = []
    for index in indices:
        item = get_element_by_id(Model.ITEM, index)
        if item:
            sorted_items.append(item)
        else:
            continue

    return sorted_items
