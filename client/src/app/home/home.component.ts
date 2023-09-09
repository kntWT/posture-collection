import { Component, OnDestroy, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';

import { UserFacade } from '../store/user/facade';
import { UserFormComponent } from './user-form/user-form.component';
import { Subscription } from 'rxjs';
import { UserBasicInfo } from '../types/User';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  standalone: true,
  imports: [MatCardModule, MatDividerModule, MatButtonModule, UserFormComponent],
})
export class HomeComponent implements OnInit, OnDestroy {

  private subscriptions: Subscription[] = [];

  constructor(private router: Router, private userFacade: UserFacade){}
  
  ngOnInit(): void {}

  ngOnDestroy(): void {
    this.subscriptions.forEach(subscription => subscription.unsubscribe());
  }

  handleLogin(userBasicInfo: UserBasicInfo) {
    this.userFacade.login(userBasicInfo);
    this.tryNavigate("/measure", "ログインに失敗しました")
  }

  handleSignup(userBasicInfo: UserBasicInfo) {
    this.userFacade.signup(userBasicInfo);
    this.tryNavigate("/measure", "ユーザ登録に失敗しました")
  }

  handleLoginAsGuest(): void {
    this.userFacade.loginAsGuest();
    this.tryNavigate("/measure", "ログインに失敗しました")
  }

  tryNavigate(path: string, errorMessage: string): void {
    const loadingSubscription:Subscription = this.userFacade.loading$.subscribe(loading => {
      if (loading) return;

      const isLoggedInSubscription: Subscription = this.userFacade.isLoggedIn$.subscribe(isLoggedIn => {
        if (isLoggedIn) {
          this.router.navigate([path]);
        } else {
          alert(errorMessage)
        }
      });
      this.subscriptions.push(isLoggedInSubscription);
    });
    this.subscriptions.push(loadingSubscription);
  }

  

}
