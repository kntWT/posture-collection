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
import { Eular, PostOrientation, Quaternion } from '../types/Sensor';

@Component({
  selector: 'app-video',
  templateUrl: './video.component.html',
  styleUrls: ['./video.component.scss'],
  standalone: true,
  imports: [MatButtonModule, MatIconModule, NgIf, OverlayModule],
})

export class VideoComponent implements OnInit, OnDestroy {
  videoEl: HTMLVideoElement | null = null;
  videoRecorder: MediaRecorder | null = null;
  width: number = 320;
  height: number = 640;
  // standardNeckLength: number | null = null;
  // postureScore: PostureScore = {neckLength: -1, headAngle: -1};
  calibrateFlag: boolean = false;
  isPlaying: boolean = true;
  isPlayable: boolean = false;
  deviceSensor: DeviceSensor | null = null;
  showOverlay: boolean = true;
  allowCameraPermission: boolean = false;
  allowOrientationPermission: boolean = false;
  allowMotionPermission: boolean = false;

  subscriptions: Subscription[] = [];

  userId: number = 0;
  setId: number = 0;
  maxSetId: number = 6;
  toPostOrientations: PostOrientation[] = [];

  readonly fps: number = 30;

  constructor(
    private router: Router,
    private userFacade: UserFacade,
    private postureService: PostureService,
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
            this.removeAllSubscriptions();
            return;
          }
          if (alert("ログインしてから再度アクセスしてください．") === undefined) {
            this.router.navigate(["/"]);
            this.removeAllSubscriptions();
          }
        })
      });
      this.subscriptions.push(subscription);
      if (this.userId !== 0) {
        this.removeAllSubscriptions();
      }
  }

  ngOnDestroy(): void {
      this.removeAllSubscriptions();
  }

  removeAllSubscriptions() {
    this.subscriptions.forEach(subscription => subscription.unsubscribe());
    this.subscriptions = [];
  }

  handleOnUpdateFrame(): void {
    this.videoEl?.requestVideoFrameCallback(this.handleOnUpdateFrame.bind(this));
    if (this.videoEl?.paused) return;
    if (!this.isPlaying) return;
    if (this.showOverlay) return;

    this.addToPostOrientations(this.calibrateFlag);
    this.calibrateFlag = false;
  }

  public handlePlay(): void {
    this.videoEl?.play();
    this.videoRecorder?.start();
    this.toPostOrientations = [];
    this.addToPostOrientations();
    this.isPlaying = true;
    this.isPlayable = true;
  }
  
  public async handlePause(): Promise<void> {
    this.videoEl?.pause();
    this.videoRecorder?.stop();
    await this.postureService.postOrientations(this.toPostOrientations);
    this.toPostOrientations = [];
    this.isPlaying = false;
    this.isPlayable = false;
  }

  writeVideo(chunks: Blob[]): File | null {
    const blob = new Blob(chunks, {type: "video/mp4"});
    // const blob = new Blob(chunks, {type: "video/webm"});
    const fileName = this.toPostOrientations?.[0]?.createdAt
      .replaceAll("/", "-")
      .replaceAll(" ", "_")
      ?? "_error";
    const file = new File([blob], `${fileName}.mp4`);

    return file;
  }

  handleOpenOverlay(): void {
    this.showOverlay = !(
      this.allowCameraPermission
      && this.allowOrientationPermission
      && this.allowMotionPermission
    );
    if (!this.showOverlay) {
      this.handlePlay();
    }
  }

  async handleAllowCameraPermission(): Promise<void> {
    if (this.videoEl === null) {
      this.allowCameraPermission = true;
      console.log("failed to get video element");
      return
    }
    const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
            facingMode: "user",
            width: {min: 0, max: this.width},
            frameRate: this.fps,
        }
    });
    this.videoEl.srcObject = stream;
    this.videoEl.requestVideoFrameCallback(this.handleOnUpdateFrame.bind(this));
    this.videoRecorder = new MediaRecorder(stream, {
      videoBitsPerSecond: 25000000,
      mimeType: "video/mp4",
      // mimeType: "video/webm",
    });
    this.videoRecorder.ondataavailable = async (e: BlobEvent) => {
      if (e.data.size > 0) {
        const vidoe: File | null = this.writeVideo([e.data]);
        if (vidoe === null) return;

        await this.postureService.postVideo(this.userId, vidoe);
        this.isPlayable = true;
      }
    };

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
    return `${date.toLocaleString("jp-JP", {timeZone: "Asia/Tokyo"})}.${date.getMilliseconds().toString().padStart(3, "0")}`
  }

  getOrientation(calibrateFlag: boolean, now: Date): PostOrientation | null {
    const eular: Eular = this.deviceSensor?.eular || {pitch: 0, roll: 0, yaw: 0};
    if (Object.values(eular).some(value => value === 0)) return null;

    const orientationWithUserId = {
      userId: this.userId,
      setId: this.setId,
      alpha: eular.roll,
      beta: eular.pitch,
      gamma: eular.yaw,
      calibrateFlag: calibrateFlag,
      createdAt: this.dateFormat(now)
    }
    return orientationWithUserId;
  }

  async postPosture(calibrateFlag: boolean = false): Promise<Posture | null> {
    const now = new Date();
    const file = await this.getFrameAsFile(now);
    if (file === null) return null;

    const orientationWithUserId = this.getOrientation(calibrateFlag, now);
    if (orientationWithUserId === null) return null;

    return  await this.postureService.postInternalPosture(orientationWithUserId, file);
  }

  addToPostOrientations(calibrateFlag: boolean = false): void {
    const now = new Date();
    const orientationWithUserId = this.getOrientation(calibrateFlag, now);
    if (orientationWithUserId === null) return;

    this.toPostOrientations.push(orientationWithUserId);
  }

  async postOrientation(calibrateFlag: boolean = false): Promise<Posture | null> {
    const now = new Date();
    const orientationWithUserId = this.getOrientation(calibrateFlag, now);
    if (orientationWithUserId === null) return null;

    return  await this.postureService.postOrientation(orientationWithUserId);
  }

  async calibrate():Promise<void> {
    // const posture = await this.postPosture(true);
    // if (posture === null) return;

    this.calibrateFlag = true;

    // this.userFacade.calibrate({
    //   id: this.userId,
    //   neckToNose: posture.neck_to_nose,
    //   neckToNoseStandard: posture.standard_dist,
    //   internalPostureCalibrationId: posture.id,
    // })
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

  incrementSetId(): void {
    if (this.disableIncrementSetId()) return;
    this.setId++;
  }

  disableIncrementSetId(): boolean {
    return this.setId >= this.maxSetId;
  }

  decrementSetId(): void {
    if (this.disableDecrementSetId()) return;
    this.setId--;
  }

  disableDecrementSetId(): boolean {
    return this.setId <= 0;
  }
}
