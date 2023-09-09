import { createFeatureSelector, createSelector } from '@ngrx/store';
import { State, userFeatureKey } from './reducer';

const getState = createFeatureSelector<State>(userFeatureKey);

export const getLoading = createSelector(
  getState,
  state => state.loading
);

export const getIsLoggedIn = createSelector(
    getState,
    state => state.isLoggedIn
)

export const getUser = createSelector(
  getState,
  state => state.user
);