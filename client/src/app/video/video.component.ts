import { Component, OnInit, OnDestroy } from '@angular/core';

@Component({
  selector: 'app-video',
  templateUrl: './video.component.html',
  styleUrls: ['./video.component.scss']
})
export class VideoComponent implements OnInit, OnDestroy {

  // videoEl: HTMLElement | null = null;
  videoEl: HTMLVideoElement | null = null;
  width: number = 640;
  height: number = 640;
  postureScore: number = 0;

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
  }

  ngOnDestroy(): void {
      this.videoEl?.removeEventListener("timeupdate", (e: Event) => this.handleOnPlay(e));
  }

  async handleOnPlay(e: Event): Promise<void> {
    this.postureScore = (await this.getPostureScore()) ?? 0;
    console.log(this.postureScore)
  }

  getFrameAsFile(): Promise<File | null> {
    return new Promise((resolve, reject) => {
      if (this.videoEl === null || this.videoEl.paused || this.videoEl.ended) {
        return null;
      }

      const canvas = document.createElement("canvas");
      canvas.width = this.videoEl.videoWidth;
      canvas.height = this.videoEl.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx?.drawImage(this.videoEl, 0, 0, this.videoEl.videoWidth, this.videoEl.videoHeight);
      let file: File | null = null;
      canvas.toBlob(blob => {
        if (blob === null) {
          reject();
          return;
        }
        
        file = new File([blob], `${new Date().toLocaleString("ja-JP-u-ca-japanese")}.jpeg`);
        resolve(file);
      }, "image/jpeg", 0.9);
      return null;
    })
  }

  async getPostureScore(): Promise<number | null> {
    const file = await this.getFrameAsFile();
    if (file === null) return null;

    const fd = new FormData();
    fd.append("file", file);
    return await (fetch("http://localhost:8000/neck", {
      method: "POST",
      body: fd,
    })
    .then(res => res.json())
    .catch(e => -1));
  }
}
