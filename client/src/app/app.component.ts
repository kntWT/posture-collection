import { Component, HostListener, OnDestroy, OnInit } from '@angular/core';
import { UserFacade } from './store/user/facade';
import { User } from './types/User';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy {
  title = '姿勢矯正デモ';

  constructor(private userFacade: UserFacade) {}

  ngOnInit(): void {
      const userJson = localStorage.getItem("user");
      if (userJson === null) return;
      const userObj: User = JSON.parse(userJson);
      this.userFacade.login(userObj);
  }

  ngOnDestroy(): void {
    this.registerUser();
  }

  registerUser() {
      const subscription = this.userFacade.user$.subscribe(user => {
        localStorage.setItem("user", JSON.stringify(user))
      });
      subscription.unsubscribe();
  }

  @HostListener("window:unload", ["$event"])
  handleUnload(_: any) {
    this.registerUser();
  }

  @HostListener("window:beforeunload", ["$event"])
  handleBeforeUnload(_: any) {
    this.registerUser();
  }
}
