import numpy as np
import numpy.testing as npt

from ampligraph.latent_features import TransE, DistMult, ComplEx, HolE
from ampligraph.datasets import load_wn18
from ampligraph.latent_features.misc import get_entity_triples
from ampligraph.latent_features import save_model, restore_model

import importlib
import tensorflow as tf

import shutil

def test_fit_predict_transE():

    model = TransE(batches_count=1, seed=555, epochs=20, k=10, loss='pairwise', loss_params={'margin':5})
    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])
    model.fit(X)
    y_pred, _ = model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
    print(y_pred)
    assert y_pred[0] > y_pred[1]

def test_generate_approximate_embeddings():

    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])

    AUX = np.array([['h', 'y', 'b'],
                    ['h', 'y', 'c'],
                    ['c', 'y', 'h']])

    OOKG_e = 'h'

    k = 10
    model = TransE(batches_count=1, seed=555, epochs=20, k=k, loss='pairwise', loss_params={'margin':5})

    model.fit(X)

    neighbouring_triples = get_entity_triples(OOKG_e, AUX)

    emb_approx = model.generate_approximate_embeddings(OOKG_e, neighbouring_triples)

    emb_returned = model.get_embeddings(OOKG_e, type='entity')

    assert('h' in model.ent_to_idx.keys())          # assert OOKG is now in model entity dict
    assert(np.all(emb_approx == emb_returned))      # assert approximate embedding is same as embedding returned from model
    assert(len(emb_approx) == k)                    # assert approximate embedding is of length k


def test_fit_predict_DistMult():
    model = DistMult(batches_count=2, seed=555, epochs=20, k=10, loss='pairwise', loss_params={'margin':5})
    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])
    model.fit(X)
    y_pred, _ = model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
    print(y_pred)
    assert y_pred[0] > y_pred[1]


def test_fit_predict_CompleEx():
    model = ComplEx(batches_count=1, seed=555, epochs=20, k=10, 
                    loss='pairwise', loss_params={'margin':1}, regularizer='L2', regularizer_params={'lambda':0.1})
    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])
    model.fit(X)
    y_pred, _ = model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
    print(y_pred)
    assert y_pred[0] > y_pred[1]

def test_fit_predict_HolE():
    model = HolE(batches_count=1, seed=555, epochs=20, k=10, 
                    loss='pairwise', loss_params={'margin':1}, regularizer='L2', regularizer_params={'lambda':0.1})
    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])
    model.fit(X)
    y_pred, _ = model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
    print(y_pred)
    assert y_pred[0] > y_pred[1]
    
def test_retrain():
    model = ComplEx(batches_count=1, seed=555, epochs=20, k=10, 
                    loss='pairwise', loss_params={'margin':1}, regularizer='L2', regularizer_params={'lambda':0.1})
    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])
    model.fit(X)
    y_pred_1st, _ = model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
    model.fit(X)
    y_pred_2nd, _ = model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
    np.testing.assert_array_equal(y_pred_1st, y_pred_2nd)

def test_fit_predict_wn18_TransE():

    X = load_wn18()
    model = TransE(batches_count=1, seed=555, epochs=5, k=100, norm=1, loss='pairwise', loss_params={'margin':5}, verbose=True)
    model.fit(X['train'])
    y, _ = model.predict(X['test'][:1])

    print(y)


def test_fit_predict_wn18_ComplEx():

    X = load_wn18()
    model = ComplEx(batches_count=1, seed=555, epochs=5, k=100,  
                    loss='pairwise', loss_params={'margin':1}, regularizer='L2', regularizer_params={'lambda':0.1})
    model.fit(X['train'])
    y = model.predict(X['test'][:1])
    print(y)


def test_lookup_embeddings():
    model = DistMult(batches_count=2, seed=555, epochs=20, k=10, loss='pairwise', loss_params={'margin':5})
    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])
    model.fit(X)
    model.get_embeddings(['a', 'b'], type='entity')

def test_save_and_restore_model():
    models = ('ComplEx', 'TransE', 'DistMult')

    for model_name in models:
        module = importlib.import_module("ampligraph.latent_features.models")
        
        print('Doing save/restore testing for model class: ', model_name)
        
        class_ = getattr(module, model_name)

        model = class_(batches_count=2, seed=555, epochs=20, k=10)

        X = np.array([['a', 'y', 'b'],
                    ['b', 'y', 'a'],
                    ['a', 'y', 'c'],
                    ['c', 'y', 'a'],
                    ['a', 'y', 'd'],
                    ['c', 'y', 'd'],
                    ['b', 'y', 'c'],
                    ['f', 'y', 'e']])
        
        model.fit(X)

        EXAMPLE_LOC = 'unittest_save_and_restore_models'
        save_model(model, EXAMPLE_LOC)
        loaded_model = restore_model(EXAMPLE_LOC)

        assert loaded_model != None
        assert loaded_model.all_params == model.all_params
        assert loaded_model.is_fitted == model.is_fitted
        assert loaded_model.ent_to_idx == model.ent_to_idx
        assert loaded_model.rel_to_idx == model.rel_to_idx

        for i in range(len(loaded_model.trained_model_params)):
            npt.assert_array_equal(loaded_model.trained_model_params[i], model.trained_model_params[i])
        

        y_pred_before, _ = model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
        y_pred_after, _ = loaded_model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
        npt.assert_array_equal(y_pred_after, y_pred_before)

        npt.assert_array_equal(loaded_model.get_embeddings(['a', 'b'], type='entity'), model.get_embeddings(['a', 'b'], type='entity'))

        shutil.rmtree(EXAMPLE_LOC)
        