import { createReducer, on } from '@ngrx/store';
import { User } from 'src/app/types/User';
import * as UserActions from "./actions"

export const userFeatureKey = 'user';

export interface State {
    loading: boolean;
    isLoggedIn: boolean;
    user: User;
}

const defaultUser: User = {
    id: 0,
    name: "",
    password: "",
    createdAt: ""
};

const loginAs = (user: User): State => {
    return {
        loading: false,
        isLoggedIn: true,
        user: user
    }
}

export const initialState: State = {
    loading: false,
    isLoggedIn: false,
    user: defaultUser,
};

export const reducer = createReducer(
    initialState,
    on(UserActions.signup, state => ({...state, loading: true})),
    on(UserActions.signupSuccess, (state, { user }) => (loginAs(user))),
    on(UserActions.signupFailure, () => initialState),
    on(UserActions.login, state => ({ ...state, loading: true })),
    on(UserActions.loginSuccess, (state, { user }) => (loginAs(user))),
    on(UserActions.loginFailure, () => initialState),
    on(UserActions.loginAsGuest, state => ({ ...state, loading: true})),
    on(UserActions.loginAsGuestSuccess, (state, { user }) => loginAs(user)),
    on(UserActions.loginAsGuestFailure, () => initialState),
    on(UserActions.logout, () => initialState),
    on(UserActions.calibrate, state => ({ ...state, loading: true })),
    on(UserActions.calibrateSuccess, (state, { user }) => ({ ...state, loading: false, user })),
    on(UserActions.calibrateFailure, state => ({ ...state, loading: false })),
);