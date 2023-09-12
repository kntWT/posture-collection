import { createAction, props, union } from '@ngrx/store';
import { User, UserBasicInfo, UserCalibrateion } from 'src/app/types/User';

export const signup = createAction(
	'[User] Signup',
	props<UserBasicInfo>(),
);
	
export const signupSuccess = createAction(
	'[User] Signup Success',
	props<{ user: User }>(),
);
	
export const signupFailure = createAction(
	'[User] Signup Failure',
	props<{ error: any }>(),
);

export const set = createAction(
  '[User] Set',
  props<{ user: User }>(),
)

export const login = createAction(
	'[User] Login',
	props<UserBasicInfo>(),
);

export const loginSuccess = createAction(
	'[User] Login Success',
	props<{ user: User }>(),
);

export const loginFailure = createAction(
	'[User] Login Failure',
	props<{ error: any }>(),
);

export const loginAsGuest = createAction(
  '[User] Login As Guest',
);

export const loginAsGuestSuccess = createAction(
  '[User] Login As Guest Success',
  props<{ user: User }>(),
);

export const loginAsGuestFailure = createAction(
  '[User] Login As Guest Failure',
  props<{ error: any }>()
);

export const logout = createAction(
	'[User] Logout'
);

export const calibrate = createAction(
	'[User] Calibrate',
  props<UserCalibrateion>(),
);

export const calibrateSuccess = createAction(
	'[User] Calibrate Success',
	props<{ user: User }>(),
);

export const calibrateFailure = createAction(
	'[User] Calibrate Failure',
	props<{ error: any }>(),
);

const actions = union({
	signup,
	signupSuccess,
	signupFailure,
  set,
	login,
	loginSuccess,
	loginFailure,
  loginAsGuest,
  loginAsGuestSuccess,
  loginAsGuestFailure,
	logout,
  calibrate,
  calibrateSuccess,
  calibrateFailure,
});

export type UserUnionActions = typeof actions;
