import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HeaderComponent } from './header/header.component';
import { VideoComponent } from './video/video.component';
import { HomeComponent } from './home/home.component';
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import { UserFacade } from './store/user/facade';
import { UserFormComponent } from './home/user-form/user-form.component';
import * as UserReducer from './store/user/reducer';
import { UserStoreModule } from './store/user/module';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  declarations: [
    AppComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HeaderComponent,
    VideoComponent,
    HomeComponent,
    HttpClientModule,
    UserFormComponent,
    UserStoreModule,
    StoreModule.forRoot({ [UserReducer.userFeatureKey]: UserReducer.reducer }),
    EffectsModule.forRoot([]),
  ],
  providers: [UserFacade],
  bootstrap: [AppComponent]
})
export class AppModule { }
