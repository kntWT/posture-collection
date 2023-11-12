import { Component, OnInit, OnDestroy } from '@angular/core';
import { NgIf } from '@angular/common';
import {OverlayModule} from '@angular/cdk/overlay';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
// import { PostureScore, Posture } from '../types/PostureScore';
// import { DeviceOrientationDetector } from './plugins/DeviceOrientationDetector';
// import { DeviceMotionDetector } from "./plugins/DeviceMotionDetector";
import { DeviceSensor } from './plugins/DeviceSensor';
import { PostureService } from '../services/posture';
import { UserFacade } from '../store/user/facade';
import { Subscription, catchError } from 'rxjs';
import { Router } from '@angular/router';
import { Posture } from '../types/PostureScore';
import { Eular, Quaternion } from '../types/Sensor';
import { UserService } from '../services/user';

@Component({
  selector: 'app-video',
  templateUrl: './video.component.html',
  styleUrls: ['./video.component.scss'],
  standalone: true,
  imports: [MatButtonModule, MatIconModule, NgIf, OverlayModule],
})

export class VideoComponent implements OnInit, OnDestroy {
  videoEl: HTMLVideoElement | null = null;
  width: number = 320;
  height: number = 640;
  // standardNeckLength: number | null = null;
  // postureScore: PostureScore = {neckLength: -1, headAngle: -1};
  isPlaying: boolean = true;
  deviceSensor: DeviceSensor | null = null;
  openOverlay: boolean = true;
  allowCameraPermission: boolean = false;
  allowOrientationPermission: boolean = false;
  allowMotionPermission: boolean = false;

  subscriptions: Subscription[] = [];

  userId: number = 0;

  constructor(
    private router: Router,
    private userFacade: UserFacade,
    private postureService: PostureService,
    private userService : UserService
  ) {
    this.deviceSensor = new DeviceSensor();
  }

  ngOnInit():void {
      this.videoEl = document.getElementById("video") as HTMLVideoElement;
      this.width = this.videoEl.clientWidth;
      this.height = this.videoEl.clientHeight;

      const subscription = this.userFacade.loading$.subscribe(loading => {
        if (loading) return;
        this.userFacade.user$.subscribe(user => {
          if (user.id !== 0) {
            this.userId = user.id;
            return;
          }
          if (alert("ログインしてから再度アクセスしてください．") === undefined) {
            this.router.navigate(["/"]);
            this.removeAllSubscriptions();
          }
        })
      });
      this.subscriptions.push(subscription)
  }

  ngOnDestroy(): void {
      this.videoEl?.removeEventListener("timeupdate", (e: Event) => this.handleOnPlay(e));
      this.removeAllSubscriptions();
  }

  removeAllSubscriptions() {
    this.subscriptions.forEach(subscription => subscription.unsubscribe());
    this.subscriptions = [];
  }

  async handleOnPlay(e: Event): Promise<void> {
    if (this.videoEl?.paused) return;
    if (!this.isPlaying) return;
    if (this.openOverlay) return;
    this.postPosture();
  }

  public handlePlay(): void {
    this.videoEl?.play();
    this.isPlaying = true;
  }
  
  public handlePause(): void {
    this.videoEl?.pause();
    this.isPlaying = false;
  }

  handleOpenOverlay(): void {
    this.openOverlay = !(
      this.allowCameraPermission
      && this.allowOrientationPermission
      && this.allowMotionPermission
    );
    if (this.openOverlay) {
      this.handlePlay();
    }
  }

  async handleAllowCameraPermission(): Promise<void> {
    if (this.videoEl === null) {
      this.allowCameraPermission = true;
      console.log("failed to get video element");
      return
    }
    const ua = navigator.userAgent;
    const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
            facingMode: "user",
            width: {min: 0, max: this.width},
        }
    });
    this.videoEl.srcObject = stream;
    this.videoEl.addEventListener("timeupdate", (e: Event) => this.handleOnPlay(e));
    this.handlePause();

    this.allowCameraPermission = true;
    this.handleOpenOverlay();
  }

  async handleAllowOrientationPermission(): Promise<void> {
    await this.deviceSensor?.requestOrientationPermission();
    this.allowOrientationPermission = true;
    this.handleOpenOverlay()
  }

  async handleAllowMotionPermission(): Promise<void> {
    await this.deviceSensor?.requestMotionPermission();
    this.allowMotionPermission = true;
    this.handleOpenOverlay()
  }

  getFrameAsFile(now: Date): Promise<File | null> {
    return new Promise((resolve, reject) => {
      if (this.videoEl === null || this.videoEl.paused || this.videoEl.ended) {
        return null;
      }

      const canvas = document.createElement("canvas");
      canvas.width = this.videoEl.videoWidth;
      canvas.height = this.videoEl.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx?.drawImage(this.videoEl, 0, 0, canvas.width, canvas.height);
      let file: File | null = null;
      canvas.toBlob(blob => {
        if (blob === null) {
          reject();
          return;
        }
        
        const fileName: string = this.dateFormat(now)
          .replaceAll("/", "-")
          .replaceAll(" ", "_");
        file = new File([blob], `${fileName}.jpg`);
        resolve(file);
      }, "image/jpeg", 0.8);
      return null;
    })
  }

  dateFormat(date: Date):string {
    return `${date.toLocaleString("jp-JP", {timeZone: "Asia/Tokyo"})}.${date.getMilliseconds()}`
  }

  async postPosture(calibrateFlag: boolean = false): Promise<Posture | null> {
    const now = new Date();
    const file = await this.getFrameAsFile(now);
    if (file === null) return null;

    const eular: Eular = this.deviceSensor?.eular || {pitch: 0, roll: 0, yaw: 0};
    // if (Object.values(eular).every(v => v === 0)) return;

    const orientationWithUserId = {
      userId: this.userId,
      alpha: eular.roll,
      beta: eular.pitch,
      gamma: eular.yaw,
      calibrateFlag: calibrateFlag,
      createdAt: this.dateFormat(now)
    }
    return  await this.postureService.post(orientationWithUserId, file);
  }

  async calibrate():Promise<void> {
    const posture = await this.postPosture(true);
    if (posture === null) return;

    this.userService.calibrate({
      id: this.userId,
      // neckToNose: posture.neck_to_nose,
      // neckToNoseStandard: posture.standard_dist,
      internalPostureCalibrationId: posture.id,
    })
  }

  // async getPostureScore(): Promise<PostureScore | null> {
  //   const file = await this.getFrameAsFile();
  //   if (file === null) return null;

  //   const fd = new FormData();
  //   fd.append("file", file);
  //   this.postureService.post()
  // }

  // async calibrateNeckLength(): Promise<void> {
  //   this.userFacade.calibrate
  //   console.log("standard: " + this.standardNeckLength);
  // }
}
