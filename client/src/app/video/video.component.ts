import { Component, OnInit, OnDestroy } from '@angular/core';
import { NgIf } from '@angular/common';
import {OverlayModule} from '@angular/cdk/overlay';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
// import { PostureScore } from '../types/PostureScore';
import { DeviceOrientationDetector } from './plugins/DeviceOrientationDetector';
import { PostureService } from '../services/posture';
import { UserFacade } from '../store/user/facade';
import { calibrate } from '../store/user/actions';
import { Subscription } from 'rxjs';
import { Router } from '@angular/router';

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
  deviceOrientationDetector: DeviceOrientationDetector | null = null;
  openOverlay: boolean = true;
  allowCameraPermission: boolean = false;
  allowOrientationPermission: boolean = false;

  subscriptions: Subscription[] = [];

  constructor(private router: Router, private userFacade: UserFacade, private postureService: PostureService) {}

  ngOnInit():void {
      this.videoEl = document.getElementById("video") as HTMLVideoElement;
      this.width = this.videoEl.clientWidth;
      this.height = this.videoEl.clientHeight;

      const subscription = this.userFacade.loading$.subscribe(loading => {
        if (loading) return;
        this.userFacade.user$.subscribe(user => {
          if (user.id !== 0) return;
          if (alert("ログインしてから再度アクセスしてください．") === undefined) {
            this.router.navigate(["/"]);
          }
        })
      });
      this.subscriptions.push(subscription)
  }

  ngOnDestroy(): void {
      this.videoEl?.removeEventListener("timeupdate", (e: Event) => this.handleOnPlay(e));
      this.subscriptions.forEach(subscription => subscription.unsubscribe());
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
    this.openOverlay = !(this.allowCameraPermission && this.allowOrientationPermission);
    if (this.openOverlay) {
      this.handlePlay();
    }
  }

  async handleAllowCameraPermission(): Promise<void> {
    if (this.videoEl === null) {
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

  handleAllowOrientationPermission(): void {
    this.deviceOrientationDetector = new DeviceOrientationDetector();
    this.deviceOrientationDetector.requestPermission();
    this.allowOrientationPermission = true;
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
        file = new File([blob], `${fileName}.jpeg`);
        resolve(file);
      }, "image/jpeg", 0.8);
      return null;
    })
  }

  dateFormat(date: Date):string {
    return `${date.toLocaleString("jp")}.${date.getMilliseconds()}`
  }

  async postPosture(): Promise<void> {
    const now = new Date();
    const file = await this.getFrameAsFile(now);
    if (file === null) return;

    const orientation = this.deviceOrientationDetector?.orientation ?? {alpha: null, beta: null, gamma: null}
    // if (!orientation || Object.values(orientation).some(v => v === null)) return;

    const subscription = this.userFacade.user$.subscribe(user => {
      const orientationWithUserId = {
        userId: user.id,
        alpha: orientation.alpha ?? -1,
        beta: orientation.beta ?? -1,
        gamma: orientation.gamma ?? -1,
        createdAt: now
      }
      this.postureService.post(orientationWithUserId, file).subscribe(res => {
        console.log(res)
      })
    });
    this.subscriptions.push(subscription);
  }

  async calibrate() {}

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
