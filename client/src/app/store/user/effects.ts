import { Actions, createEffect, ofType } from "@ngrx/effects";
import { UserService } from '../../services/user';
import * as UserActions from "./actions";
import { catchError, concatMap, map, of } from "rxjs";
import { UserBasicInfo, UserCalibrateion } from "src/app/types/User";


export class UserEffects {

    constructor(private actions$: Actions, private userService: UserService){}

    siginup$ = createEffect(() => 
        this.actions$.pipe(
            ofType(UserActions.signup),
            concatMap((props: UserBasicInfo) =>
                this.userService.signup(props).pipe(
                    map(res => UserActions.signupSuccess({ user: res })),
                    catchError(error => of(UserActions.signupFailure({ error: error })))
                )
            )
        )
    )

    login$ = createEffect(() => 
        this.actions$.pipe(
            ofType(UserActions.login),
            concatMap((props: UserBasicInfo) =>
                this.userService.login(props).pipe(
                    map(res => UserActions.loginSuccess({ user: res })),
                    catchError(error => of(UserActions.loginFailure({ error: error })))
                )
            )
        )
    )

    loginAsGuest$ = createEffect(() =>
        this.actions$.pipe(
            ofType(UserActions.loginAsGuest),
            concatMap(() =>
                this.userService.loginAsGuest().pipe(
                    map(res => UserActions.loginAsGuestSuccess({ user: res })),
                    catchError(error => of(UserActions.loginAsGuestFailure({ error: error })))
                )
            )
        )
    )

    calibrate$ = createEffect(() => 
        this.actions$.pipe(
            ofType(UserActions.calibrate),
            concatMap((props: UserCalibrateion) =>
                this.userService.calibrate(props).pipe(
                    map(res => UserActions.calibrateSuccess({ user: res })),
                    catchError(error => of(UserActions.calibrateFailure({ error: error })))
                )
            )
        )
    )
}