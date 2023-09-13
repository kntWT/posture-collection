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
  allowPermission: boolean = false;

  userIdSubscription: Subscription | undefined;

  constructor(private router: Router, private userFacade: UserFacade, private postureService: PostureService) {}

  ngOnInit():void {
      this.width = window.innerWidth;
      this.height = window.innerHeight;

      this.userFacade.loading$.subscribe(loading => {
        if (loading) return;
        this.userFacade.user$.subscribe(user => {
          if (user.id !== 0) return;
          if (alert("ログインしてから再度アクセスしてください．") === undefined) {
            this.router.navigate(["/"]);
          }
        })
      })
  }

  ngOnDestroy(): void {
      this.videoEl?.removeEventListener("timeupdate", (e: Event) => this.handleOnPlay(e));
      this.userIdSubscription?.unsubscribe();
  }

  async handleOnPlay(e: Event): Promise<void> {
    if (this.videoEl?.paused) return;
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

  async handleAllowPermission(): Promise<void> {
    this.videoEl = document.getElementById("video") as HTMLVideoElement;
    if (this.videoEl === null) {
      console.log("failed to get video element");
      return
    }
    const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
            facingMode: "user",
            width: {min: 0, max: this.width},
            height: {min: 0, max: this.height},
        }
    });
    this.videoEl.srcObject = stream;
    this.videoEl.addEventListener("timeupdate", (e: Event) => this.handleOnPlay(e));
    this.videoEl?.play();

    this.allowPermission = true;
    this.deviceOrientationDetector = new DeviceOrientationDetector();
    
    this.openOverlay = false;
  }

  getFrameAsFile(): Promise<File | null> {
    return new Promise((resolve, reject) => {
      if (this.videoEl === null || this.videoEl.paused || this.videoEl.ended) {
        return null;
      }

      const canvas = document.createElement("canvas");
      canvas.width = this.videoEl.videoWidth * 2;
      canvas.height = this.videoEl.videoHeight * 2;
      const ctx = canvas.getContext("2d");
      ctx?.drawImage(this.videoEl, 0, 0, canvas.width, canvas.height);
      let file: File | null = null;
      canvas.toBlob(blob => {
        if (blob === null) {
          reject();
          return;
        }
        
        const now = new Date();
        const fileName: string = `${now.toLocaleString("ja-JP-u-ca-japanese")}:${now.getMilliseconds()}`
          .replaceAll("/", "_")
          .replaceAll(" ", "_");
        file = new File([blob], `${fileName}.jpeg`);
        resolve(file);
      }, "image/jpeg", 0.5);
      return null;
    })
  }

  async postPosture(): Promise<void> {
    const file = await this.getFrameAsFile();
    if (file === null) return;
    const orientation = this.deviceOrientationDetector?.orientation ?? {alpha: null, beta: null, gamma: null}
    // if (!orientation || Object.values(orientation).some(v => v === null)) return;

    this.userIdSubscription = this.userFacade.user$.subscribe(user => {
      const orientationWithUserId = {
        userId: user.id,
        alpha: orientation.alpha ?? -1,
        beta: orientation.beta ?? -1,
        gamma: orientation.gamma ?? -1
      }
      this.postureService.post(orientationWithUserId, file).subscribe(res => {
        console.log(res)
      })
    });
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
