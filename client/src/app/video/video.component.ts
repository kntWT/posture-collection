import { Component, OnInit, OnDestroy } from '@angular/core';
import { NgIf } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { PostureScore } from './types/PostureScore';
import { DeviceOrientationDetector } from './plugins/DeviceOrientationDetector';

@Component({
  selector: 'app-video',
  templateUrl: './video.component.html',
  styleUrls: ['./video.component.scss'],
  standalone: true,
  imports: [MatButtonModule, MatIconModule, NgIf],
})

export class VideoComponent implements OnInit, OnDestroy {
  videoEl: HTMLVideoElement | null = null;
  width: number = 320;
  height: number = 640;
  standardNeckLength: number | null = null;
  postureScore: PostureScore = {neckLength: -1, headAngle: -1};
  isPlaying: boolean = true;
  deviceOrientationDetector: DeviceOrientationDetector | null = null;

  constructor() {
  }

  async ngOnInit(): Promise<void> {
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
      this.deviceOrientationDetector = new DeviceOrientationDetector();
  }

  ngOnDestroy(): void {
      this.videoEl?.removeEventListener("timeupdate", (e: Event) => this.handleOnPlay(e));
  }

  async handleOnPlay(e: Event): Promise<void> {
    if (this.videoEl?.paused) return;
    this.postureScore =  (await this.getPostureScore()) ?? {neckLength: -1, headAngle: -1};
    console.log(this.postureScore)
  }

  public handlePlay(): void {
    this.videoEl?.play();
    this.isPlaying = true;
  }
  
  public handlePause(): void {
    this.videoEl?.pause();
    this.isPlaying = false;
  }

  getFrameAsFile(): Promise<File | null> {
    return new Promise((resolve, reject) => {
      if (this.videoEl === null || this.videoEl.paused || this.videoEl.ended) {
        return null;
      }

      const canvas = document.createElement("canvas");
      canvas.width = this.videoEl.videoWidth / 2;
      canvas.height = this.videoEl.videoHeight / 2;
      const ctx = canvas.getContext("2d");
      ctx?.drawImage(this.videoEl, 0, 0, this.videoEl.videoWidth / 2, this.videoEl.videoHeight / 2);
      let file: File | null = null;
      canvas.toBlob(blob => {
        if (blob === null) {
          reject();
          return;
        }
        
        file = new File([blob], `${new Date().toLocaleString("ja-JP-u-ca-japanese")}.jpeg`);
        resolve(file);
      }, "image/jpeg", 0.5);
      return null;
    })
  }

  async getPostureScore(): Promise<PostureScore | null> {
    const file = await this.getFrameAsFile();
    if (file === null) return null;

    const fd = new FormData();
    fd.append("file", file);
    return await (fetch("https://localhost:8000/score", {
      method: "POST",
      body: fd,
    })
    .then(res => res.json())
    .catch(e => -1));
  }

  async calibrateNeckLength(): Promise<void> {
    this.standardNeckLength = (await this.getPostureScore())?.neckLength ?? null;
    console.log("standard: " + this.standardNeckLength);
  }
}
