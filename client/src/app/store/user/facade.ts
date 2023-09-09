import { Injectable } from '@angular/core';
import { Store, select } from '@ngrx/store';

import { UserBasicInfo, UserCalibrateion } from 'src/app/types/User';
import { State } from './reducer';
import * as UserSelectors from './selector';
import * as UserActions from './actions';
import { UserStoreModule } from './module';

@Injectable({
  providedIn: UserStoreModule,
})
export class UserFacade {
  loading$ = this.store.pipe(select(UserSelectors.getLoading));
  user$ = this.store.pipe(select(UserSelectors.getUser));

  constructor(private store: Store<State>) {}

  signup(props: UserBasicInfo) {
    this.store.dispatch(UserActions.signup(props));
  }

  login(props: UserBasicInfo) {
    this.store.dispatch(UserActions.login(props));
  }

  loginAsGuest() {
    this.store.dispatch(UserActions.loginAsGuest())
  }

  logout() {
    this.store.dispatch(UserActions.logout());
  }

  calibrate(props: UserCalibrateion) {
    this.store.dispatch(UserActions.calibrate(props));
  }
}