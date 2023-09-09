import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StoreModule } from '@ngrx/store';
import * as UserReducer from './reducer';
import { EffectsModule } from '@ngrx/effects';
import { UserEffects } from './effects';

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    StoreModule.forFeature(UserReducer.userFeatureKey, UserReducer.reducer),
    EffectsModule.forFeature([UserEffects])
  ]
})
export class UserStoreModule {}