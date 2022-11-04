from flask import request
from math import sqrt, acos, pi
import numpy as np
from scipy.optimize import minimize
from mealswap.controllers.controls import get_all_elements, Model, get_saved_items, get_ratings_count_by_user, \
    get_element_by_id


def get_float(key) -> float or None:
    """Helper function for getting arguments."""
    try:
        value = float(request.args.get(key))
    except TypeError:
        value = None
    return value


def get_similar_items(items, protein, carb, fat, calories, item_id) -> list:
    """Returns a list of similar items.
    Similarity of items is defined by cosine similarity of item vectors.
    Vector dimensions are macronutrient values.
    Function can work either with items saved in database or with values provided by app user in a form.

    :param items: selected items from database that we want to compare to our item/macronutrient values
    :param protein: protein content of input item/macronutrient values
    :param carb: carb content of input item/macronutrient values
    :param fat: fat content of input item/macronutrient values
    :param calories: calories of input item/macronutrient values
    :param item_id: id of selected item"""

    similarity_list = []
    for i in items:
        if item_id:
            # item_id provided - all macro data is known
            numerator = i.protein * protein + \
                        i.carb * carb + \
                        i.fat * fat
            denominator = sqrt(i.protein * i.protein + i.carb * i.carb + i.fat * i.fat) * sqrt(protein * protein + carb
                                                                                               * carb + fat * fat)
        else:
            # item_id not provided - some data might be missing, iterate through macronutrients and add them to equation
            # one by one
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
        except ZeroDivisionError and ValueError:
            # can be divided by 0 - skip it
            continue
        else:
            similarity = 1 - distance * 2 / pi
            similarity_list.append((similarity, i))

    # sort results based on similarity
    similarity_list.sort(key=lambda x: x[0], reverse=True)
    return similarity_list


def f(params, num_users, num_items, num_features, Y, R, lambda_):
    """Cost function for the collaborative filtering algorithm.

    :param params: joined matrices of parameters describing user features and item features
    :param num_users: number of users
    :param num_items: number of items (meals)
    :param num_features: number of features for each user/item
    :param Y: matrix of size (num_items, num_users) that stores rating for each item-user pair
    :param R: matrix of size (num_items, num_users) that stores 1 for each item-user pair if the item was rated,
    0 otherwise
    :param lambda_: regularization parameter (prevents overfitting)
    """
    params = np.reshape(params, (num_users + num_items, num_features))
    X, Theta = np.split(params, [num_items])
    cost = (np.sum(np.multiply(np.matmul(X, np.transpose(Theta)) - Y, R) ** 2)) / 2 + \
           lambda_ / 2 * (np.sum(Theta ** 2) + np.sum(X ** 2))
    return cost


def grad(params, num_users, num_items, num_features, Y, R, lambda_):
    """Gradient function for the collaborative filtering algorithm.

    :param params: joined matrices of parameters describing user features and item features
    :param num_users: number of users
    :param num_items: number of items (meals)
    :param num_features: number of features for each user/item
    :param Y: matrix of size (num_items, num_users) that stores rating for each item-user pair
    :param R: matrix of size (num_items, num_users) that stores 1 for each item-user pair if the item was rated,
    0 otherwise
    :param lambda_: regularization parameter (prevents overfitting)
    """
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
    # get data from database
    ratings = get_all_elements(Model.RATINGS)
    num_ratings = get_ratings_count_by_user(user)
    users = get_all_elements(Model.USER)
    items = get_saved_items()
    # initiate dimensions
    num_users = users[-1].id + 1
    num_items = items[-1].id + 1
    num_features = 10
    lambda_ = 10

    # create Y, R matrices
    Y = np.zeros((num_items, num_users), np.uint8)
    for rating in ratings:
        Y[rating.item_id, rating.user_id] = rating.rating
    R = np.where(Y > 0, 1, 0)

    # create matrices with randomized initial parameters
    X = np.random.rand(num_items, num_features)
    Theta = np.random.rand(num_users, num_features)
    initial_parameters = np.concatenate((X, Theta))
    initial_parameters = initial_parameters.flatten()

    # run minimization
    result = minimize(f, initial_parameters, args=(num_users, num_items, num_features, Y, R, lambda_),
                      method='Newton-CG', jac=grad)
    matrix = result.x

    # retrieve original matrices from flattened result
    result = np.reshape(matrix, (num_users + num_items, num_features))
    X, Theta = np.split(result, [num_items])

    # get prediction values for particular user
    predictions = np.matmul(X, np.transpose(Theta))
    R = np.invert(R.astype(np.bool)).astype(np.uint8)  # invert to get predictions for not rated items
    predictions = np.multiply(predictions, R)[:, user.id]
    indexed_predictions = [(predictions[i], i) for i in range(len(predictions))]
    indexed_predictions.sort(reverse=True, key=lambda x: x[0])  # get higher ratings first
    indices = [x[1] for x in indexed_predictions]
    indices = indices[:(len(indices) - num_ratings)]  # cut off zero values

    # add items that have valid indices (possible error from creating a meal and deleting it later)
    sorted_items = []
    for index in indices:
        item = get_element_by_id(Model.ITEM, index)
        if item:
            sorted_items.append(item)
        else:
            continue

    return sorted_items
