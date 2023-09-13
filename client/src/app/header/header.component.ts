import { CommonModule, NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { UserFacade } from '../store/user/facade';
import { Observable } from 'rxjs';
import { User } from '../types/User';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
  standalone: true,
  imports: [MatToolbarModule, NgIf, CommonModule],
})
export class HeaderComponent {
  isLoggedIn$: Observable<boolean>;
  user$: Observable<User>;

  constructor(private userFacade: UserFacade) {
    this.isLoggedIn$ = this.userFacade.isLoggedIn$;
    this.user$ = this.userFacade.user$;
  }

  handleLogout() {
    this.userFacade.logout();
  }
}
