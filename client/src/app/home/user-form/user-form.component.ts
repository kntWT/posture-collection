import { Component, EventEmitter, OnInit } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { Output, Input } from '@angular/core';

import { UserBasicInfo } from 'src/app/types/User';

@Component({
  selector: 'app-user-form',
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.scss'],
  standalone: true,
  imports: [MatButtonModule, ReactiveFormsModule],
})
export class UserFormComponent implements OnInit {

  ngOnInit(): void {}

  form = new FormGroup({
    name: new FormControl("", Validators.required),
    password: new FormControl("", Validators.required)
  })

  @Input() title: string = "";
  @Output() submitEvent = new EventEmitter<UserBasicInfo>();

  handleSubmit(): void {
    if (this.form.invalid) {
      alert("情報が不足しています");
      return;
    }
    this.submitEvent.emit(this.form.value as UserBasicInfo)
  }

}
